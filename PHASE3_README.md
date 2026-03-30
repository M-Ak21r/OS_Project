# Phase 3: Detection Engine & Dashboard

**Real-Time Security Vulnerability Monitoring Framework**

> ✅ **Complete**: Automated detection system with rich terminal UI for identifying buffer overflows and trapdoor backdoors

---

## 🎯 Overview

Phase 3 implements a **real-time security monitoring framework** that automatically detects and alerts on the vulnerabilities demonstrated in Phases 1 and 2. This teaches students about:

- System log analysis and kernel message monitoring
- Process tree analysis and behavioral detection
- Real-time threat detection methodologies
- Security operations center (SOC) dashboards
- Automated incident response

---

## 📂 Files

### monitor.py (18 KB)
Comprehensive detection engine with rich terminal UI:
- **Buffer Overflow Detection**: Monitors dmesg for SIGSEGV signals
- **Trapdoor Detection**: Scans process tree for unauthorized daemons
- **Real-Time Dashboard**: Split-screen interface with live updates
- **Alert Management**: Tracks and displays security events
- **System Monitoring**: CPU, memory, and process statistics
- Heavily commented with OS security concepts

### requirements.txt
Python dependencies for Phase 3:
- `psutil>=5.9.0` - Process and system monitoring
- `rich>=13.0.0` - Terminal UI library

---

## 🚀 Quick Start

### Installation

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Or install system-wide (recommended for Ubuntu)
sudo pip3 install -r requirements.txt

# Alternatively, use system packages
sudo apt-get install python3-psutil
pip3 install rich
```

### Running the Monitor

```bash
# Basic usage (may have limited log access)
python3 monitor.py

# Recommended: Run as root for full access to system logs
sudo python3 monitor.py

# Run in background (daemon mode)
nohup sudo python3 monitor.py > monitor.log 2>&1 &
```

### Testing Detection Capabilities

**Terminal 1: Start the Monitor**
```bash
sudo python3 monitor.py
```

**Terminal 2: Trigger Vulnerabilities**
```bash
# Test buffer overflow detection
python3 exploit_overflow.py

# Test trapdoor detection
python3 exploit_trapdoor.py

# Watch the monitor dashboard update in real-time!
```

---

## 📊 Dashboard Interface

### Layout

The dashboard uses a split-screen layout:

```
┌─────────────────────────────────────────────────────────────┐
│     🛡️  Security Vulnerability Detection Framework  🛡️     │ <- Header
├─────────────────┬───────────────────────────────────────────┤
│                 │                                           │
│  System Status  │         Real-Time Security Alerts        │
│   (Left Panel)  │              (Right Panel)               │
│                 │                                           │
│  • Monitor      │  Time | Severity | Type | Message        │
│  • Uptime       │  ──────────────────────────────────────  │
│  • CPU/Memory   │  Recent alerts with timestamps           │
│  • Statistics   │  Color-coded by severity                 │
│  • Backdoors    │  Includes mitigation suggestions         │
│  • Overflows    │                                           │
│                 │                                           │
└─────────────────┴───────────────────────────────────────────┘
```

### System Status Panel (Left)

Displays real-time system information:
- **Monitor Status**: Active/Inactive with emoji indicator
- **Uptime**: How long monitor has been running (HH:MM:SS)
- **CPU Usage**: Current CPU utilization percentage
- **Memory Usage**: RAM utilization percentage
- **Total Processes**: Number of running processes
- **Alert Statistics**: Total, critical, and warning counts
- **Active Backdoors**: Number of detected trapdoor processes
- **Buffer Overflows**: Number of detected crashes

### Security Alerts Panel (Right)

Shows real-time security events:
- **Timestamp**: When alert was detected (HH:MM:SS)
- **Severity**: CRITICAL (red), WARNING (yellow), INFO (cyan)
- **Type**: BUFFER_OVERFLOW, TRAPDOOR, SYSTEM
- **Alert Message**: Detailed description of the threat
- **Mitigation**: Specific remediation steps

### Color Coding

- 🔴 **Red (CRITICAL)**: Active security threats requiring immediate attention
- 🟡 **Yellow (WARNING)**: Suspicious behavior worth investigating
- 🔵 **Cyan (INFO)**: Informational messages about monitoring status
- 🟢 **Green (SUCCESS)**: Safe/normal status indicators

---

## 🔍 Detection Capabilities

### 1. Buffer Overflow Detection

**Method**: System log analysis (dmesg monitoring)

**How it works:**
```python
# Monitors kernel ring buffer for segmentation faults
# Pattern: process_name[PID]: segfault at <address>
```

**Detection criteria:**
- Identifies SIGSEGV (signal 11) events in dmesg
- Extracts crashed process name and PID
- Analyzes fault address for overflow patterns (e.g., 0x41414141)
- Detects known vulnerable programs (buffer_target)

**What triggers an alert:**
- `buffer_target` process crashes with SIGSEGV
- Any process crashes with address showing overflow pattern
- Repeated byte patterns in fault address (0xAAAAAAAA, etc.)

**Example alert:**
```
CRITICAL | BUFFER_OVERFLOW
Process 'buffer_target' (PID: 12345) crashed with SIGSEGV at 0x41414141
Mitigation: Recompile 'buffer_target' with -fstack-protector and remove -z execstack
```

### 2. Trapdoor/Backdoor Detection

**Method**: Process tree analysis (psutil scanning)

**How it works:**
```python
# Scans all running processes for suspicious characteristics
# Looks for: no TTY, daemon status, suspicious names
```

**Detection criteria:**
- Identifies `auth_service` processes without controlling terminals
- Checks process status (not zombie)
- Analyzes parent-child relationships
- Tracks previously detected backdoors

**What triggers an alert:**
- auth_service process running without TTY (terminal = None)
- Process in daemon state spawned from auth service
- Background process matching trapdoor signature

**Example alert:**
```
CRITICAL | TRAPDOOR
Backdoor detected: 'auth_service' (PID: 7890, PPID: 1, No TTY)
Mitigation: Terminate process: sudo kill 7890 or pkill -f auth_service
```

### 3. Continuous Monitoring

**Monitoring loop:**
- Runs every 2 seconds (configurable via `CHECK_INTERVAL`)
- Non-blocking checks to maintain UI responsiveness
- Deduplicates alerts to avoid spam
- Maintains alert history (max 20 recent alerts)

---

## 📚 OS Concepts Demonstrated

### 1. System Log Analysis

**Concept**: Operating systems log security-relevant events to kernel ring buffer

```bash
# View kernel messages
dmesg | tail -20

# Monitor in real-time
dmesg -w

# Filter for segfaults
dmesg | grep segfault
```

**Educational value**:
- Understanding kernel message format
- Parsing timestamps and process information
- Correlating crashes with security events
- Log-based intrusion detection

### 2. Process Monitoring with /proc

**Concept**: Linux `/proc` filesystem exposes process information

The monitor uses `psutil` which reads from:
- `/proc/<PID>/status` - Process state
- `/proc/<PID>/cmdline` - Command line
- `/proc/<PID>/fd/` - Open file descriptors
- `/proc/<PID>/task/` - Threads

**Educational value**:
- Process attributes and lifecycle
- Parent-child relationships
- TTY assignment and session leaders
- Daemon process characteristics

### 3. Real-Time Event Detection

**Concept**: Security monitoring requires continuous scanning and alerting

```python
while monitoring:
    check_for_threats()
    update_dashboard()
    sleep(interval)
```

**Educational value**:
- Polling vs. event-driven monitoring
- Alert fatigue and deduplication
- Performance considerations
- Graceful degradation

### 4. Terminal User Interface (TUI)

**Concept**: Rich provides a framework for building interactive terminal UIs

**Educational value**:
- Efficient terminal updates (only redraw changes)
- Layout management and responsive design
- Color coding for information hierarchy
- Real-time data visualization

---

## 🎓 Educational Scenarios

### Scenario 1: End-to-End Detection Demo

**Objective**: Demonstrate complete vulnerability lifecycle

**Steps:**
1. Terminal 1: Start monitor
   ```bash
   sudo python3 monitor.py
   ```

2. Terminal 2: Trigger buffer overflow
   ```bash
   python3 exploit_overflow.py
   ```

3. **Observe**: Dashboard shows CRITICAL alert for buffer overflow
   - Process name and PID displayed
   - Fault address shown
   - Mitigation suggestion provided

4. Terminal 2: Activate trapdoor
   ```bash
   python3 exploit_trapdoor.py
   ```

5. **Observe**: Dashboard shows CRITICAL alert for trapdoor
   - Backdoor process detected
   - No TTY characteristic noted
   - Kill command suggested

6. **Discussion**: How quickly were threats detected? What information helps with response?

### Scenario 2: Comparative Analysis

**Objective**: Compare manual vs. automated detection

**Part A - Manual Detection:**
```bash
# Manually check for buffer overflow
dmesg | grep segfault | tail -5

# Manually check for backdoors
ps aux | grep auth_service | grep '?'
```

**Part B - Automated Detection:**
```bash
# Run monitor - automatic detection and alerting
sudo python3 monitor.py
```

**Questions for students:**
- Which method is faster?
- Which is more reliable for 24/7 monitoring?
- What are the tradeoffs?

### Scenario 3: Alert Response Drill

**Objective**: Practice incident response procedures

**Given**: Monitor shows critical alerts

**Task**: Students must:
1. Identify the type of threat
2. Read the alert message
3. Follow mitigation steps
4. Verify threat is neutralized
5. Document the incident

**Example response:**
```bash
# Alert: Backdoor detected PID 7890
sudo kill 7890

# Verify termination
ps aux | grep 7890

# Check for re-spawn attempts
watch -n 1 'ps aux | grep auth_service'
```

### Scenario 4: Custom Detection Rules

**Objective**: Extend the monitor with custom detectors

**Task**: Students modify `monitor.py` to detect:
- Specific file access patterns
- Network connections from suspicious processes
- Resource consumption anomalies
- Time-based attack patterns

**Learning outcomes:**
- Understanding detection logic
- Implementing pattern matching
- Balancing false positives/negatives
- Performance optimization

---

## 🔬 Technical Deep Dive

### Buffer Overflow Detection Algorithm

```python
def detect_overflow(dmesg_line):
    """
    1. Parse dmesg line for segfault pattern
    2. Extract: process_name, PID, fault_address
    3. Check if process is buffer_target
    4. Analyze address for overflow pattern:
       - 0x41414141 ('AAAA') → overflow with 'A' chars
       - Repeated bytes → likely overflow
    5. Generate alert with mitigation
    """
```

**Key insights:**
- Fault address `0x41414141` is ASCII 'AAAA' - clear overflow signature
- Kernel logs include instruction pointer (IP) showing where crash occurred
- Timestamp helps correlate with exploit timing

### Trapdoor Detection Algorithm

```python
def detect_trapdoor(process):
    """
    1. Iterate all running processes
    2. Filter by name: 'auth_service'
    3. Check characteristics:
       - terminal == None (no TTY)
       - status != ZOMBIE
       - not previously detected
    4. Get parent process info (PPID)
    5. Generate alert with kill command
    """
```

**Key insights:**
- Legitimate auth services usually have TTYs
- Daemon processes (no TTY) from auth services are suspicious
- Tracking PIDs prevents duplicate alerts
- Parent PID helps understand process hierarchy

### Performance Considerations

**Optimization strategies:**
1. **Polling interval**: 2 seconds balances responsiveness and CPU usage
2. **Log tailing**: Only check recent N lines of dmesg
3. **Process filtering**: Only scan relevant process names
4. **Alert deduplication**: Track seen events to avoid spam
5. **Lazy evaluation**: Only update UI when data changes

**Benchmarks** (approximate):
- CPU usage: <5% on modern systems
- Memory: ~50MB (mostly for rich UI)
- Latency: Detects threats within 2-4 seconds

---

## 🛡️ Security Best Practices

### Running the Monitor

**Recommended:**
```bash
# Run with sudo for full log access
sudo python3 monitor.py

# Log output for forensics
sudo python3 monitor.py 2>&1 | tee monitor_$(date +%Y%m%d_%H%M%S).log
```

**Production deployment** (if adapted for real use):
- Run as systemd service
- Implement log rotation
- Add remote alerting (email, Slack, SIEM)
- Store alerts in database
- Implement rate limiting

### Limitations

**Current implementation:**
- ✅ Detects known vulnerability patterns
- ✅ Real-time alerting within seconds
- ✅ Educational clarity over production features
- ⚠️ No historical trend analysis
- ⚠️ Basic heuristics only
- ⚠️ Requires root for full dmesg access

**For production use, add:**
- Machine learning for anomaly detection
- Integration with SIEM systems
- Automated response capabilities
- Distributed monitoring
- Encrypted log transport

---

## 📊 Comparison with Commercial Tools

### How This Compares

| Feature | This Framework | Commercial HIDS |
|---------|----------------|-----------------|
| Buffer overflow detection | ✅ Basic (dmesg) | ✅ Advanced (kernel hooks) |
| Process monitoring | ✅ psutil scanning | ✅ Real-time hooks |
| UI | ✅ Terminal dashboard | ✅ Web dashboards |
| Alerting | ✅ On-screen | ✅ Multi-channel |
| Learning curve | ✅ Simple | ⚠️ Complex |
| Cost | ✅ Free/Open | ❌ Expensive |
| **Educational value** | ✅✅✅ **Excellent** | ⚠️ Black box |

**Educational advantages:**
- Transparent detection logic
- Modifiable and extensible
- Clear cause-and-effect demonstrations
- Hands-on learning

**Real-world alternatives:**
- **OSSEC** - Open-source HIDS
- **Wazuh** - Security monitoring platform
- **Falco** - Cloud-native runtime security
- **Osquery** - SQL-based system monitoring

---

## 🎯 Learning Outcomes

After completing Phase 3, students should understand:

1. **System Monitoring**: How to monitor OS logs and processes for security events
2. **Pattern Detection**: Identifying malicious patterns in system behavior
3. **Alert Management**: Prioritizing and responding to security alerts
4. **Real-Time Systems**: Building responsive monitoring applications
5. **Terminal UI**: Creating effective command-line interfaces
6. **Incident Response**: Following mitigation procedures for detected threats
7. **Security Operations**: Basics of SOC workflows and tools

---

## 🔧 Customization & Extension

### Adding New Detectors

Students can extend the framework:

```python
class CustomDetector:
    """Template for custom detector"""

    def __init__(self):
        self.state = {}

    def check(self) -> List[Alert]:
        """Implement detection logic"""
        alerts = []

        # Your detection code here
        if threat_detected:
            alert = Alert(
                severity="CRITICAL",
                alert_type="CUSTOM_THREAT",
                message="Description of threat",
                mitigation="How to fix it"
            )
            alerts.append(alert)

        return alerts
```

**Ideas for extensions:**
1. **Network monitoring**: Detect unusual connections
2. **File integrity**: Monitor critical files for changes
3. **Resource abuse**: Detect CPU/memory spikes
4. **Privilege escalation**: Track sudo usage
5. **Login monitoring**: Detect failed authentication attempts

### Configuring Detection Parameters

Edit monitor.py constants:
```python
CHECK_INTERVAL = 2      # Seconds between checks (lower = more responsive)
MAX_ALERTS = 20         # History size (higher = more context)
DMESG_LINES = 50        # Log lines to scan (higher = catches more)
TRAPDOOR_PROC_NAME = "auth_service"  # Process to detect
```

---

## 📖 Integration with Phases 1 & 2

### Complete Testing Workflow

```bash
# Step 1: Build vulnerable binaries
make clean && make

# Step 2: Start monitoring (Terminal 1)
sudo python3 monitor.py

# Step 3: Test Phase 1 detection (Terminal 2)
python3 exploit_overflow.py
# → Monitor shows: BUFFER_OVERFLOW alert

# Step 4: Test Phase 2 detection (Terminal 2)
python3 exploit_trapdoor.py
# → Monitor shows: TRAPDOOR alert

# Step 5: Clean up backdoors
sudo pkill -f auth_service

# Step 6: Stop monitor (Terminal 1)
# Press Ctrl+C
```

### Educational Progression

1. **Phase 1**: Understand how vulnerabilities work (buffer overflow)
2. **Phase 2**: Learn about backdoor mechanisms (trapdoor)
3. **Phase 3**: Implement detection and response (monitoring)
4. **Integration**: Complete security lifecycle understanding

---

## 🚨 Troubleshooting

### Issue: "No module named 'psutil'"

**Solution:**
```bash
pip3 install psutil
# Or: sudo apt-get install python3-psutil
```

### Issue: "No module named 'rich'"

**Solution:**
```bash
pip3 install rich
```

### Issue: "Permission denied" reading dmesg

**Solution:**
```bash
# Run with sudo
sudo python3 monitor.py

# Or add user to systemd-journal group
sudo usermod -a -G systemd-journal $USER
```

### Issue: Monitor not detecting buffer overflows

**Diagnosis:**
```bash
# Check if crashes are logged
dmesg | grep segfault | tail -5

# Manually trigger overflow
./buffer_target $(python3 -c "print('A'*100)")

# Check dmesg again
dmesg | tail -10
```

### Issue: Monitor not detecting trapdoors

**Diagnosis:**
```bash
# Check if backdoor is running
ps aux | grep auth_service

# Manually activate trapdoor
./auth_service sysadmin_debug_2024 test

# Check process list
ps aux | grep auth_service | grep '?'
```

---

## 📚 Additional Resources

### System Monitoring & Logging
- [dmesg man page](https://man7.org/linux/man-pages/man1/dmesg.1.html)
- [Understanding /proc filesystem](https://www.kernel.org/doc/html/latest/filesystems/proc.html)
- [Linux Logging Guide](https://www.loggly.com/ultimate-guide/linux-logging-basics/)

### Process Analysis
- [psutil documentation](https://psutil.readthedocs.io/)
- [Linux Process Management](https://www.kernel.org/doc/html/latest/admin-guide/process-management.html)

### Security Monitoring
- [NIST Guide to IDPS](https://csrc.nist.gov/publications/detail/sp/800-94/final)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Security Operations Center Best Practices](https://www.sans.org/white-papers/)

### Terminal UI Development
- [Rich documentation](https://rich.readthedocs.io/)
- [Python TUI libraries](https://github.com/TomJGooding/awesome-tui)

---

## 🎉 Project Completion

**All three phases complete!**

| Phase | Status | Key Learning |
|-------|--------|--------------|
| 1: Buffer Overflow | ✅ | Memory safety vulnerabilities |
| 2: Trapdoor | ✅ | Authentication bypass & backdoors |
| 3: Detection Engine | ✅ | Monitoring & incident response |

**Complete skill set acquired:**
- ✅ Understanding vulnerabilities
- ✅ Exploitation techniques
- ✅ Detection methodologies
- ✅ Mitigation strategies
- ✅ System monitoring
- ✅ Security operations

**Next steps for advanced students:**
- Implement additional detectors
- Add machine learning for anomaly detection
- Create distributed monitoring system
- Integrate with real SIEM platforms
- Contribute to open-source security tools

---

**Built for Cybersecurity Education** 🎓
*Complete security lifecycle: Vulnerability → Exploitation → Detection → Response*
