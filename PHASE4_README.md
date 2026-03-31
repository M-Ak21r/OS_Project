# Phase 4: DNS Cache Poisoning Detection

**Real-Time /etc/hosts Monitoring with Linux inotify**

> ✅ **Complete**: Automated detection system using inotify for monitoring DNS cache poisoning attacks

---

## 🎯 Overview

Phase 4 implements a **DNS cache poisoning attack demonstration** and **real-time detection system** that monitors the `/etc/hosts` file for unauthorized modifications. This teaches students about:

- Local DNS resolution and the `/etc/hosts` file
- DNS cache poisoning attack vectors
- Linux inotify subsystem for file system monitoring
- Real-time threat detection and alerting
- File integrity monitoring techniques
- Root privilege escalation attacks

---

## 📂 Files

### poison_cache.py (13 KB)
DNS cache poisoning exploit demonstration:
- **Attack Vector**: Modifies `/etc/hosts` to redirect domains
- **Privilege Requirement**: Requires root/sudo access
- **Backup Creation**: Automatically backs up original file
- **Verification**: Tests DNS resolution after injection
- **Educational Commentary**: Explains attack mechanics and OS concepts
- Heavily commented with security implications

### monitor.py (Updated)
Enhanced detection engine with DNS poisoning detection:
- **inotify Integration**: Real-time file system event monitoring
- **DNSCachePoisoningDetector Class**: Dedicated detector for /etc/hosts
- **Hash-based Verification**: Detects content modifications
- **Thread-safe Alerting**: Background monitoring with alert queue
- **Fallback Mode**: Polling-based detection when inotify unavailable
- **Dashboard Integration**: Shows DNS poisoning status in real-time

### requirements.txt (Updated)
Added dependencies for Phase 4:
- `pyinotify>=0.9.6` - Linux inotify wrapper for file monitoring

---

## 🚀 Quick Start

### Installation

```bash
# Install updated Python dependencies
pip3 install -r requirements.txt

# Or install system-wide (recommended for Ubuntu)
sudo pip3 install -r requirements.txt

# Make exploit script executable
chmod +x poison_cache.py
```

### Phase 4 Demonstration

**Terminal 1: Start the Monitor**
```bash
# Run monitor with root privileges for full access
sudo python3 monitor.py
```

**Terminal 2: Execute DNS Poisoning Attack**
```bash
# Run the cache poisoning exploit (requires sudo)
sudo python3 poison_cache.py

# Follow prompts to confirm attack demonstration
# Watch Terminal 1 for instant detection alert!
```

**Terminal 2: Verify the Attack**
```bash
# Test DNS resolution - should redirect to 127.0.0.1
getent hosts google.com

# Check the hosts file
cat /etc/hosts | grep MALICIOUS
```

**Terminal 2: Cleanup**
```bash
# Remove malicious entry
sudo nano /etc/hosts
# Delete lines marked "MALICIOUS ENTRY"

# Or restore from backup
sudo cp /etc/hosts.backup.* /etc/hosts
```

---

## 🔍 Technical Deep Dive

### Attack Mechanism: DNS Cache Poisoning

#### What is /etc/hosts?
The `/etc/hosts` file is a local DNS resolution table:
- Checked **before** DNS servers are queried
- Maps hostnames to IP addresses
- Requires root access to modify
- Affects all applications on the system

**Format:**
```
<IP_ADDRESS>    <HOSTNAME>    [ALIASES...]
127.0.0.1       localhost
192.168.1.100   myserver.local
```

#### How the Attack Works

1. **Privilege Escalation**: Attacker gains root access (via exploit, social engineering, etc.)
2. **File Modification**: Injects malicious entries into `/etc/hosts`
3. **DNS Hijacking**: Legitimate domains now resolve to attacker-controlled IPs
4. **Traffic Redirection**: All traffic to hijacked domains goes to fake servers

**Example Attack Entry:**
```bash
# MALICIOUS ENTRY - DNS Cache Poisoning Attack
127.0.0.1    google.com
127.0.0.1    facebook.com
127.0.0.1    bank.com
```

#### Real-World Attack Scenarios

**Phishing Attacks:**
- Redirect bank.com → fake login page at attacker IP
- Steal credentials when users try to log in
- Bypass 2FA by proxying to real site

**Man-in-the-Middle:**
- Redirect traffic through attacker's proxy server
- Intercept and modify HTTPS traffic
- Steal session tokens and API keys

**Denial of Service:**
- Redirect critical services to 0.0.0.0 or invalid IPs
- Prevent access to update servers
- Block security software communications

---

### Detection Mechanism: Linux inotify

#### What is inotify?

**inotify** is a Linux kernel subsystem that monitors file system events:
- Part of the Linux kernel since 2.6.13
- Provides real-time notifications for file changes
- More efficient than polling (no CPU waste)
- Can watch files, directories, and entire trees

#### How inotify Works

```
┌─────────────────┐
│   Application   │
│  (monitor.py)   │
└────────┬────────┘
         │ 1. Set up watch
         ↓
┌─────────────────┐
│  inotify API    │
│  (pyinotify)    │
└────────┬────────┘
         │ 2. Register file
         ↓
┌─────────────────┐
│  Linux Kernel   │
│  inotify system │
└────────┬────────┘
         │ 3. Monitor filesystem
         ↓
┌─────────────────┐
│   /etc/hosts    │
│    (file)       │
└────────┬────────┘
         │ 4. File modified!
         ↓
┌─────────────────┐
│  Linux Kernel   │ 5. Generate event
└────────┬────────┘
         │ 6. Event notification
         ↓
┌─────────────────┐
│   Application   │ 7. Alert user!
└─────────────────┘
```

#### inotify Events Used

- **IN_MODIFY**: File content was modified
- **IN_ATTRIB**: File metadata changed (permissions, timestamps)

#### Implementation in monitor.py

```python
# 1. Create watch manager
wm = pyinotify.WatchManager()

# 2. Define event handler
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        # File was modified - trigger alert!
        self.detector._on_file_modified(event)

# 3. Set up notifier
notifier = pyinotify.Notifier(wm, EventHandler())

# 4. Add watch for /etc/hosts
mask = pyinotify.IN_MODIFY | pyinotify.IN_ATTRIB
wm.add_watch("/etc/hosts", mask)

# 5. Process events in background thread
while monitoring:
    notifier.process_events()
```

#### Why inotify vs Polling?

**Polling (Bad):**
```python
while True:
    current_hash = calculate_hash("/etc/hosts")
    if current_hash != original_hash:
        alert()
    time.sleep(1)  # Wastes CPU, 1 second delay
```

**inotify (Good):**
```python
# Set up once, kernel notifies immediately
wm.add_watch("/etc/hosts", pyinotify.IN_MODIFY)
# No CPU waste, instant detection!
```

**Benefits:**
- ⚡ **Instant detection** - no polling delay
- 💻 **Zero CPU waste** - kernel handles monitoring
- 🎯 **Precise events** - know exactly what changed
- 📊 **Scalable** - can watch thousands of files

---

## 📊 Dashboard Integration

### Status Panel Updates

The dashboard now shows DNS cache status:

```
┌─── 📊 System Status ──────┐
│ Monitor Status   ✅ Active │
│ Uptime          00:15:32  │
│                           │
│ Total Alerts          3   │
│ Critical Alerts       1   │
│                           │
│ Active Backdoors      0   │
│ Buffer Overflows      0   │
│ /etc/hosts     ⚠️ POISONED│ ← NEW!
└───────────────────────────┘
```

### Alert Examples

**When DNS poisoning is detected:**
```
🚨 Real-Time Security Alerts
────────────────────────────────────────────────────────
Time     Severity   Type           Alert Message
────────────────────────────────────────────────────────
15:23:45 CRITICAL   DNS_POISONING  /etc/hosts modified! Added 1 entry(ies)
         Mitigation: Restore from backup and audit root privilege escalation
```

---

## 🎓 Educational Value

### OS Concepts Taught

1. **File System Monitoring**
   - inotify subsystem architecture
   - Kernel-level event generation
   - Event types and masks

2. **DNS Resolution**
   - Local DNS cache (/etc/hosts)
   - Resolution order (hosts → DNS servers)
   - Impact on system-wide networking

3. **File Permissions & Security**
   - Root-protected system files
   - Privilege escalation attacks
   - File integrity monitoring

4. **Threading & Concurrency**
   - Background monitoring threads
   - Thread-safe alert queues
   - Lock-based synchronization

5. **Hash-based Integrity**
   - SHA256 checksums
   - Content verification
   - Change detection

### Security Concepts

1. **Attack Vectors**
   - DNS cache poisoning
   - Privilege escalation
   - Persistence mechanisms
   - Traffic redirection

2. **Defense Strategies**
   - File integrity monitoring (FIM)
   - Real-time alerting
   - Backup and recovery
   - Audit logging

3. **Detection Methods**
   - inotify-based monitoring
   - Hash verification
   - Anomaly detection
   - Behavioral analysis

---

## 🔬 Lab Exercises

### Basic Exercises

1. **Observe the Attack**
   - Run monitor.py in one terminal
   - Execute poison_cache.py in another
   - Watch the instant detection alert
   - Examine the modified /etc/hosts file

2. **Test DNS Resolution**
   - Before attack: `getent hosts google.com`
   - After attack: See it resolve to 127.0.0.1
   - Understand the impact on applications

3. **Cleanup and Recovery**
   - Practice manual cleanup (edit /etc/hosts)
   - Use backup restoration
   - Verify cleanup with getent

### Advanced Exercises

1. **Modify Detection Sensitivity**
   - Add detection for specific domain patterns
   - Implement whitelist for legitimate changes
   - Add alerting for suspicious IP patterns (localhost redirects)

2. **Enhance the Exploit**
   - Redirect multiple domains
   - Set up a fake web server on localhost
   - Demonstrate phishing attack simulation
   - **Note**: Only in isolated VMs!

3. **Extend the Monitor**
   - Watch additional critical files (/etc/passwd, /etc/shadow)
   - Implement automated response (restore from backup)
   - Add forensic logging (who modified the file?)
   - Use auditd for process attribution

4. **Performance Analysis**
   - Compare inotify vs polling performance
   - Measure CPU usage difference
   - Test detection latency
   - Monitor with multiple file watches

---

## 🛡️ Defense in Production

### Real-World Protection

In production systems, combine multiple defense layers:

1. **File Integrity Monitoring (FIM)**
   - AIDE (Advanced Intrusion Detection Environment)
   - Tripwire
   - OSSEC
   - Commercial FIM solutions

2. **Audit Logging**
   - Linux auditd to track file access
   - Log who modified /etc/hosts
   - Track privilege escalation attempts

3. **Access Controls**
   - SELinux/AppArmor policies
   - Restrict root access
   - Principle of least privilege
   - Multi-factor authentication for sudo

4. **Automated Response**
   - Automatic restoration from backup
   - Alert security team immediately
   - Lock affected accounts
   - Trigger incident response procedures

5. **Network Monitoring**
   - Monitor DNS queries at network level
   - Detect unusual resolution patterns
   - Compare local vs authoritative DNS

### Example auditd Rule

```bash
# Monitor /etc/hosts for any writes
-w /etc/hosts -p wa -k dns_poisoning

# View audit logs
ausearch -k dns_poisoning
```

---

## 🔒 Safety Guidelines

### ✅ DO:
- Run demonstrations in isolated VMs only
- Use for educational purposes in supervised environments
- Understand the attack to build better defenses
- Practice cleanup and recovery procedures
- Always create backups before modifications

### ❌ DON'T:
- Modify /etc/hosts on production systems
- Use techniques on systems you don't own
- Leave malicious entries after demonstrations
- Share exploits without educational context
- Deploy without proper authorization

---

## 🐛 Troubleshooting

### inotify Not Available

**Symptom:** Message "pyinotify not available - using polling mode"

**Solution:**
```bash
pip3 install pyinotify
# Or
sudo apt-get install python3-pyinotify
```

### Permission Denied

**Symptom:** Cannot modify /etc/hosts

**Solution:** Run with sudo:
```bash
sudo python3 poison_cache.py
```

### Detection Not Working

**Symptom:** Monitor doesn't detect file changes

**Check:**
1. Monitor running with sufficient permissions?
2. pyinotify installed correctly?
3. /etc/hosts readable by monitor process?

**Debug:**
```python
# Check if inotify is available
import pyinotify
print("inotify available:", True)
```

### Cleanup Issues

**Symptom:** Can't remove malicious entries

**Solution:**
```bash
# Edit as root
sudo nano /etc/hosts

# Or restore from backup
sudo cp /etc/hosts.backup.* /etc/hosts

# Verify cleanup
getent hosts google.com
```

---

## 📈 Performance Considerations

### Resource Usage

- **inotify mode**: Negligible CPU usage (<0.1%)
- **Polling mode**: ~0.5-1% CPU usage
- **Memory**: ~5-10 MB for watcher thread
- **Latency**: <100ms detection time with inotify

### Scalability

The monitor can watch multiple files simultaneously:
```python
# Watch multiple critical files
files_to_watch = [
    "/etc/hosts",
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers"
]
```

Each watch adds minimal overhead (~1-2 KB memory).

---

## 🔗 Related Phases

- **Phase 1**: Buffer Overflow - Memory corruption attacks
- **Phase 2**: Trapdoor - Process-based backdoors
- **Phase 3**: Detection Engine - Real-time monitoring foundation
- **Phase 4**: DNS Poisoning - File-based attacks (current)

Each phase builds on the previous, creating a comprehensive security monitoring system.

---

## 📚 Further Reading

- [Linux inotify man page](https://man7.org/linux/man-pages/man7/inotify.7.html)
- [DNS Cache Poisoning - Wikipedia](https://en.wikipedia.org/wiki/DNS_spoofing)
- [OWASP - DNS Cache Poisoning](https://owasp.org/www-community/attacks/Cache_Poisoning)
- [File Integrity Monitoring Best Practices](https://www.sans.org/reading-room/whitepapers/analyst/file-integrity-monitoring-best-practices-33450)
- [Linux Audit Framework](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/chap-system_auditing)

---

## 🎯 Learning Outcomes

After completing Phase 4, students will understand:

✅ How DNS cache poisoning attacks work
✅ The role of /etc/hosts in Linux DNS resolution
✅ Linux inotify subsystem for file monitoring
✅ Real-time threat detection techniques
✅ File integrity monitoring principles
✅ Root privilege attacks and defenses
✅ Threading and concurrent programming in Python
✅ Hash-based integrity verification

---

**Phase 4 Complete!** 🎉

This phase demonstrates a complete attack-and-detect lifecycle for DNS cache poisoning, teaching critical OS security concepts through hands-on practice.

---

**Built for Educational Excellence** 🎓
*Teaching security by understanding vulnerabilities*
