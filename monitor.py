#!/usr/bin/env python3
"""
monitor.py - Security Vulnerability Detection Engine & Dashboard

OS CONCEPTS DEMONSTRATED:
-------------------------
1. System Log Monitoring: Reading kernel ring buffer (dmesg) and syslog
2. Process Tree Analysis: Detecting unauthorized/suspicious processes
3. Real-time Event Detection: Continuous monitoring for security events
4. Terminal UI: Interactive dashboard with live updates
5. Signal Handling: Graceful shutdown and cleanup

DETECTION CAPABILITIES:
-----------------------
1. Buffer Overflow Detection:
   - Monitors dmesg for SIGSEGV (segmentation fault) signals
   - Identifies crashed processes and their names
   - Provides mitigation suggestions

2. Trapdoor/Backdoor Detection:
   - Scans running processes for suspicious patterns
   - Detects processes without controlling terminals (daemons)
   - Identifies auth_service backdoor processes
   - Analyzes parent-child process relationships

EDUCATIONAL PURPOSE: Demonstrates real-time security monitoring for OS course.
"""

import subprocess
import psutil
import time
import signal
import sys
import os
import re
from datetime import datetime
from collections import deque
from typing import List, Dict, Optional

# Rich library for terminal UI
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box


# ============================================================================
# Configuration
# ============================================================================

# Detection parameters
CHECK_INTERVAL = 2  # Seconds between checks
MAX_ALERTS = 20     # Maximum alerts to display
DMESG_LINES = 50    # Lines of dmesg to check
TRAPDOOR_PROC_NAME = "auth_service"  # Process name to detect

# Colors for alerts
COLOR_CRITICAL = "red"
COLOR_WARNING = "yellow"
COLOR_INFO = "cyan"
COLOR_SUCCESS = "green"


# ============================================================================
# Alert Management
# ============================================================================

class Alert:
    """Represents a security alert"""
    def __init__(self, severity: str, alert_type: str, message: str, mitigation: str):
        self.timestamp = datetime.now()
        self.severity = severity  # "CRITICAL", "WARNING", "INFO"
        self.alert_type = alert_type  # "BUFFER_OVERFLOW", "TRAPDOOR", "SYSTEM"
        self.message = message
        self.mitigation = mitigation

    def to_table_row(self) -> List[str]:
        """Convert alert to table row"""
        time_str = self.timestamp.strftime("%H:%M:%S")

        # Color coding based on severity
        if self.severity == "CRITICAL":
            severity_style = f"[bold {COLOR_CRITICAL}]"
        elif self.severity == "WARNING":
            severity_style = f"[bold {COLOR_WARNING}]"
        else:
            severity_style = f"[{COLOR_INFO}]"

        return [
            time_str,
            f"{severity_style}{self.severity}[/]",
            f"[bold]{self.alert_type}[/]",
            self.message,
            f"[italic]{self.mitigation}[/]"
        ]


class AlertManager:
    """Manages security alerts"""
    def __init__(self, max_alerts: int = MAX_ALERTS):
        self.alerts = deque(maxlen=max_alerts)
        self.total_alerts = 0
        self.critical_count = 0
        self.warning_count = 0

    def add_alert(self, alert: Alert):
        """Add new alert"""
        self.alerts.append(alert)
        self.total_alerts += 1

        if alert.severity == "CRITICAL":
            self.critical_count += 1
        elif alert.severity == "WARNING":
            self.warning_count += 1

    def get_recent_alerts(self, count: int = None) -> List[Alert]:
        """Get most recent alerts"""
        if count is None:
            return list(self.alerts)
        return list(self.alerts)[-count:]


# ============================================================================
# Buffer Overflow Detector
# ============================================================================

class BufferOverflowDetector:
    """
    Detects buffer overflow exploits via system logs

    OS Concept: When a buffer overflow causes a crash, the kernel logs:
    - SIGSEGV (signal 11) for segmentation faults
    - Process name and PID that crashed
    - Memory address that caused the fault

    These logs appear in:
    - dmesg (kernel ring buffer)
    - /var/log/kern.log or /var/log/syslog
    """

    def __init__(self):
        self.seen_crashes = set()  # Track seen crashes to avoid duplicates
        self.last_check_time = None

    def check_dmesg(self) -> List[Alert]:
        """
        Check dmesg for segmentation faults

        OS Concept: dmesg shows kernel messages including:
        - segfault at <address>: Memory access violations
        - ip <address>: Instruction pointer (where crash occurred)
        - Process information
        """
        alerts = []

        try:
            # Read recent dmesg entries
            result = subprocess.run(
                ['dmesg', '-T'],  # -T for human-readable timestamps
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.split('\n')[-DMESG_LINES:]

            # Pattern to match segfault messages
            # Example: buffer_target[1234]: segfault at 41414141 ip 0000000041414141
            segfault_pattern = re.compile(
                r'(\w+)\[(\d+)\].*segfault at ([0-9a-fA-F]+)'
            )

            for line in lines:
                match = segfault_pattern.search(line)
                if match:
                    proc_name = match.group(1)
                    pid = match.group(2)
                    address = match.group(3)

                    # Create unique identifier
                    crash_id = f"{proc_name}_{pid}_{address}"

                    if crash_id not in self.seen_crashes:
                        self.seen_crashes.add(crash_id)

                        # Analyze the crash
                        is_overflow = self._analyze_crash(proc_name, address)

                        if is_overflow:
                            alert = Alert(
                                severity="CRITICAL",
                                alert_type="BUFFER_OVERFLOW",
                                message=f"Process '{proc_name}' (PID: {pid}) crashed with SIGSEGV at 0x{address}",
                                mitigation=f"Recompile '{proc_name}' with -fstack-protector and remove -z execstack"
                            )
                            alerts.append(alert)

        except subprocess.TimeoutExpired:
            pass  # dmesg took too long, skip this check
        except Exception as e:
            pass  # Error reading dmesg, continue monitoring

        return alerts

    def _analyze_crash(self, proc_name: str, address: str) -> bool:
        """
        Analyze crash to determine if it's likely a buffer overflow

        OS Concept: Buffer overflow crashes often show patterns:
        - Address 0x41414141 (ASCII 'AAAA') indicates overflow with 'A' characters
        - Known vulnerable programs (buffer_target)
        - Addresses that look like ASCII patterns
        """
        # Check if it's our vulnerable program
        if proc_name == "buffer_target":
            return True

        # Check for typical overflow patterns (repeated bytes)
        if re.match(r'^([0-9a-f])\1+$', address):
            return True

        return False


# ============================================================================
# Trapdoor Detector
# ============================================================================

class TrapdoorDetector:
    """
    Detects unauthorized background processes (trapdoors/backdoors)

    OS Concept: Backdoor processes typically have characteristics:
    - No controlling terminal (TTY = None or '?')
    - Detached from parent (often adopted by init/systemd)
    - Suspicious process names
    - Unexpected child processes from auth services
    """

    def __init__(self):
        self.known_backdoors = set()  # Track known backdoor PIDs
        self.initial_processes = self._get_auth_service_processes()

    def _get_auth_service_processes(self) -> List[psutil.Process]:
        """Get all auth_service processes"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                if TRAPDOOR_PROC_NAME in proc.info['name']:
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def check_processes(self) -> List[Alert]:
        """
        Scan for suspicious backdoor processes

        OS Concept: Uses /proc filesystem via psutil to:
        - List all running processes
        - Check process attributes (name, TTY, parent)
        - Detect daemon characteristics
        """
        alerts = []

        current_processes = self._get_auth_service_processes()

        for proc in current_processes:
            try:
                # Get process details
                pid = proc.pid
                name = proc.name()

                # Skip if we've already alerted on this PID
                if pid in self.known_backdoors:
                    continue

                # Get process info
                cmdline = ' '.join(proc.cmdline() if proc.cmdline() else [])
                status = proc.status()

                # Check for trapdoor characteristics
                try:
                    terminal = proc.terminal()  # None if no TTY
                except (psutil.AccessDenied, AttributeError):
                    terminal = None

                # Detect backdoor: auth_service process with no terminal
                if terminal is None and status != psutil.STATUS_ZOMBIE:
                    # This looks like a backdoor!
                    self.known_backdoors.add(pid)

                    # Get parent process info
                    try:
                        parent = proc.parent()
                        parent_name = parent.name() if parent else "Unknown"
                        ppid = parent.pid if parent else 0
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        parent_name = "Unknown"
                        ppid = 0

                    alert = Alert(
                        severity="CRITICAL",
                        alert_type="TRAPDOOR",
                        message=f"Backdoor detected: '{name}' (PID: {pid}, PPID: {ppid}, No TTY)",
                        mitigation=f"Terminate process: sudo kill {pid} or pkill -f {TRAPDOOR_PROC_NAME}"
                    )
                    alerts.append(alert)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return alerts

    def get_backdoor_count(self) -> int:
        """Get count of active backdoors"""
        count = 0
        for pid in list(self.known_backdoors):
            if psutil.pid_exists(pid):
                count += 1
            else:
                self.known_backdoors.remove(pid)
        return count


# ============================================================================
# System Monitor
# ============================================================================

class SystemMonitor:
    """Tracks overall system status"""

    def __init__(self):
        self.start_time = datetime.now()
        self.monitoring_active = True

    def get_uptime(self) -> str:
        """Get monitor uptime"""
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_system_info(self) -> Dict:
        """Get current system information"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'process_count': len(psutil.pids()),
            'uptime': self.get_uptime()
        }


# ============================================================================
# Dashboard UI
# ============================================================================

class SecurityDashboard:
    """
    Rich terminal UI for security monitoring

    Layout: Split screen with:
    - Top: System status and statistics
    - Bottom: Real-time security alerts
    """

    def __init__(self, alert_manager: AlertManager, system_monitor: SystemMonitor,
                 buffer_detector: BufferOverflowDetector, trapdoor_detector: TrapdoorDetector):
        self.console = Console()
        self.alert_manager = alert_manager
        self.system_monitor = system_monitor
        self.buffer_detector = buffer_detector
        self.trapdoor_detector = trapdoor_detector

    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()

        # Split into header, body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # Split body into status and alerts
        layout["body"].split_row(
            Layout(name="status", ratio=1),
            Layout(name="alerts", ratio=2)
        )

        return layout

    def generate_header(self) -> Panel:
        """Generate header panel"""
        title = Text()
        title.append("🛡️  ", style="bold red")
        title.append("Security Vulnerability Detection Framework", style="bold cyan")
        title.append("  🛡️", style="bold red")

        return Panel(
            Align.center(title),
            style="bold white on blue",
            box=box.DOUBLE
        )

    def generate_status_panel(self) -> Panel:
        """Generate system status panel"""
        # Get system info
        sys_info = self.system_monitor.get_system_info()
        backdoor_count = self.trapdoor_detector.get_backdoor_count()

        # Create status table
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="white")

        # Monitor status
        status_emoji = "✅" if self.system_monitor.monitoring_active else "❌"
        table.add_row("Monitor Status", f"{status_emoji} Active")
        table.add_row("Uptime", sys_info['uptime'])
        table.add_row("", "")  # Spacer

        # System metrics
        table.add_row("CPU Usage", f"{sys_info['cpu_percent']:.1f}%")
        table.add_row("Memory Usage", f"{sys_info['memory_percent']:.1f}%")
        table.add_row("Total Processes", str(sys_info['process_count']))
        table.add_row("", "")  # Spacer

        # Alert statistics
        table.add_row("Total Alerts", str(self.alert_manager.total_alerts))

        critical_style = "bold red" if self.alert_manager.critical_count > 0 else "green"
        table.add_row("Critical Alerts", f"[{critical_style}]{self.alert_manager.critical_count}[/]")

        warning_style = "bold yellow" if self.alert_manager.warning_count > 0 else "green"
        table.add_row("Warning Alerts", f"[{warning_style}]{self.alert_manager.warning_count}[/]")

        table.add_row("", "")  # Spacer

        # Detection-specific stats
        backdoor_style = "bold red" if backdoor_count > 0 else "green"
        table.add_row("Active Backdoors", f"[{backdoor_style}]{backdoor_count}[/]")

        overflow_crashes = len(self.buffer_detector.seen_crashes)
        overflow_style = "bold red" if overflow_crashes > 0 else "green"
        table.add_row("Buffer Overflows", f"[{overflow_style}]{overflow_crashes}[/]")

        return Panel(
            table,
            title="[bold]📊 System Status[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )

    def generate_alerts_panel(self) -> Panel:
        """Generate real-time alerts panel"""
        # Create alerts table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE_HEAD,
            padding=(0, 1)
        )

        table.add_column("Time", style="dim", width=8)
        table.add_column("Severity", width=10)
        table.add_column("Type", width=16)
        table.add_column("Alert Message", style="white")
        table.add_column("Mitigation", style="italic dim")

        # Add recent alerts
        alerts = self.alert_manager.get_recent_alerts()

        if not alerts:
            table.add_row(
                "-",
                "[green]INFO[/]",
                "SYSTEM",
                "No security threats detected",
                "Continue monitoring..."
            )
        else:
            # Show most recent first
            for alert in reversed(alerts):
                table.add_row(*alert.to_table_row())

        return Panel(
            table,
            title="[bold]🚨 Real-Time Security Alerts[/bold]",
            border_style="red",
            box=box.ROUNDED
        )

    def render(self) -> Layout:
        """Render the complete dashboard"""
        layout = self.create_layout()

        layout["header"].update(self.generate_header())
        layout["status"].update(self.generate_status_panel())
        layout["alerts"].update(self.generate_alerts_panel())

        return layout


# ============================================================================
# Main Detection Engine
# ============================================================================

class DetectionEngine:
    """Main detection engine coordinating all detectors"""

    def __init__(self):
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor()
        self.buffer_detector = BufferOverflowDetector()
        self.trapdoor_detector = TrapdoorDetector()
        self.dashboard = SecurityDashboard(
            self.alert_manager,
            self.system_monitor,
            self.buffer_detector,
            self.trapdoor_detector
        )
        self.running = True

    def setup_signal_handlers(self):
        """Setup graceful shutdown"""
        def signal_handler(signum, frame):
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def run_detection_cycle(self):
        """Run one detection cycle"""
        # Check for buffer overflows
        overflow_alerts = self.buffer_detector.check_dmesg()
        for alert in overflow_alerts:
            self.alert_manager.add_alert(alert)

        # Check for trapdoors
        trapdoor_alerts = self.trapdoor_detector.check_processes()
        for alert in trapdoor_alerts:
            self.alert_manager.add_alert(alert)

    def run(self):
        """Main monitoring loop"""
        self.setup_signal_handlers()

        # Initial informational alert
        startup_alert = Alert(
            severity="INFO",
            alert_type="SYSTEM",
            message="Security monitoring engine started",
            mitigation="Monitoring buffer overflows and trapdoor processes..."
        )
        self.alert_manager.add_alert(startup_alert)

        # Start live dashboard
        try:
            with Live(
                self.dashboard.render(),
                console=self.dashboard.console,
                refresh_per_second=1,
                screen=True
            ) as live:
                while self.running:
                    # Run detection
                    self.run_detection_cycle()

                    # Update dashboard
                    live.update(self.dashboard.render())

                    # Sleep before next check
                    time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            pass

        # Shutdown
        self.system_monitor.monitoring_active = False
        self.dashboard.console.print("\n[yellow]Monitoring stopped. Exiting...[/yellow]")


# ============================================================================
# Entry Point
# ============================================================================

def print_startup_banner():
    """Print startup banner"""
    console = Console()
    console.print("\n[bold cyan]" + "=" * 70 + "[/]")
    console.print("[bold cyan]  Security Vulnerability Detection Framework - Phase 3[/]")
    console.print("[bold cyan]  Real-Time Monitoring Engine & Dashboard[/]")
    console.print("[bold cyan]" + "=" * 70 + "[/]\n")

    console.print("[yellow]Starting detection engine...[/]")
    console.print("[cyan]  → Buffer Overflow Detection: Monitoring dmesg for SIGSEGV[/]")
    console.print("[cyan]  → Trapdoor Detection: Scanning process tree[/]")
    console.print("[cyan]  → Dashboard UI: Initializing real-time display[/]\n")

    console.print("[bold green]Press Ctrl+C to stop monitoring[/]\n")
    time.sleep(2)


def main():
    """Main entry point"""
    # Check if running with sufficient permissions
    if os.geteuid() != 0:
        console = Console()
        console.print("[yellow]⚠️  Warning: Not running as root[/]")
        console.print("[yellow]   Some system logs may not be accessible[/]")
        console.print("[yellow]   For full functionality, run: sudo python3 monitor.py[/]\n")
        time.sleep(2)

    # Print banner
    print_startup_banner()

    # Create and run detection engine
    engine = DetectionEngine()
    engine.run()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]Error: {e}[/]")
        console.print_exception()
        sys.exit(1)
