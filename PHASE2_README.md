# Phase 2: Trapdoor/Backdoor Simulation

**Educational Demonstration of Authentication Bypass and Hidden Process Spawning**

> ⚠️ **WARNING**: This demonstrates a security vulnerability for educational purposes. Never implement backdoors in real systems.

---

## 🎯 Overview

Phase 2 demonstrates a **trapdoor/backdoor vulnerability** - a hidden authentication bypass that spawns unauthorized background processes. This teaches students about:

- How backdoors can be embedded in authentication systems
- Process creation and daemonization techniques
- Detection of hidden/unauthorized processes
- OS security mechanisms for process isolation

---

## 📂 Files

### auth_service.c (9.5 KB)
Authentication service with intentional trapdoor vulnerability:
- Normal login functionality with simulated user database
- **Hidden backdoor**: Secret username `sysadmin_debug_2024` bypasses authentication
- **Malicious payload**: Spawns detached background process using `fork()` and `setsid()`
- Process daemonization: Closes stdin/stdout/stderr, runs independently
- Heavily commented with OS concepts

### exploit_trapdoor.py (10 KB)
Python script demonstrating trapdoor exploitation:
- Tests normal authentication flow
- Activates trapdoor with secret credentials
- Detects spawned backdoor process
- Analyzes process characteristics (no TTY, daemon status)
- Provides detection commands and mitigation strategies

---

## 🚀 Quick Start

### Compilation

```bash
# Build the auth service (already included in Makefile)
make auth_service

# Or build all targets
make
```

### Normal Authentication Testing

```bash
# Test valid credentials
./auth_service alice password123

# Test invalid credentials
./auth_service alice wrongpassword

# Interactive mode
./auth_service
# Then enter username and password when prompted
```

**Valid credentials (simulated users):**
- Username: `alice` / Password: `password123`
- Username: `bob` / Password: `securepass`
- Username: `admin` / Password: `admin2024`

### Trapdoor Activation

```bash
# Activate the backdoor using secret username
./auth_service sysadmin_debug_2024 any_password

# The password can be ANYTHING when using the trapdoor username
# Watch for "TRAPDOOR ACTIVATED" message
# Note the PID of the spawned background process
```

### Automated Exploitation

```bash
# Run the complete demonstration
python3 exploit_trapdoor.py

# This will:
# 1. Test normal authentication
# 2. Activate the trapdoor
# 3. Detect the backdoor process
# 4. Analyze its characteristics
# 5. Show detection commands
```

---

## 🔍 Detection & Analysis

### Detecting the Backdoor Process

After activating the trapdoor, the backdoor process runs in the background:

```bash
# 1. List all processes (look for auth_service with no TTY)
ps aux | grep auth_service

# Example output:
# runner  8165  0.0  0.0  2700  440  ?  Ss  17:50  0:00 ./auth_service sysadmin_debug_2024

# Notice the "?" in TTY column - indicates no controlling terminal
```

```bash
# 2. Show process tree to see parent-child relationships
pstree -p | grep auth_service

# 3. Check /proc filesystem for process details
ls -la /proc/*/exe | grep auth_service

# 4. Real-time monitoring
watch -n 1 'ps aux | grep auth_service'
```

### Key Process Characteristics

The backdoor process exhibits specific traits:

| Characteristic | Value | Significance |
|----------------|-------|--------------|
| **TTY** | `?` | No controlling terminal (daemon) |
| **STAT** | `Ss` | Sleeping session leader |
| **PPID** | `1` or init | Orphaned/adopted by init |
| **Duration** | 3600 seconds | Runs for 1 hour (configurable) |

### Terminating Backdoor Processes

```bash
# Kill all auth_service processes
pkill -f auth_service

# Or kill specific PID
kill <PID>

# Force kill if needed
kill -9 <PID>
```

---

## 📚 OS Concepts Demonstrated

### 1. Process Creation: fork()

```c
pid_t pid = fork();
```

**OS Concept**: `fork()` creates a child process that's an exact copy of the parent:
- Child gets its own process ID (PID)
- Child inherits parent's file descriptors, memory layout, and code
- Both processes execute from the same point (after fork)
- Return value differs: 0 in child, child's PID in parent

**Security Implication**: Attackers use fork() to spawn unauthorized processes.

### 2. Process Detachment: setsid()

```c
setsid();
```

**OS Concept**: `setsid()` creates a new session and makes the process a session leader:
- Detaches process from controlling terminal
- Process becomes independent of parent's lifecycle
- Survives terminal closure (SIGHUP)

**Security Implication**: Makes backdoor processes persistent and harder to detect.

### 3. Daemon Characteristics

```c
close(STDIN_FILENO);
close(STDOUT_FILENO);
close(STDERR_FILENO);
```

**OS Concept**: Daemon processes (background services) typically:
- Have no controlling terminal (TTY = ?)
- Close standard file descriptors
- Run continuously in the background
- Often adopted by init process (PPID = 1)

**Security Implication**: Backdoors mimic legitimate daemon behavior to hide.

### 4. Signal Handling

```c
signal(SIGHUP, SIG_IGN);
```

**OS Concept**: Signals are software interrupts for inter-process communication:
- `SIGHUP` (Hangup) sent when terminal closes
- `SIG_IGN` tells OS to ignore the signal
- Allows process to survive parent termination

**Security Implication**: Persistent backdoors ignore termination signals.

### 5. File Descriptor Management

```c
int devnull = open("/dev/null", O_RDWR);
dup2(devnull, STDIN_FILENO);  // Redirect stdin to /dev/null
```

**OS Concept**: `/dev/null` is a special file that discards all data:
- Redirecting I/O to /dev/null suppresses output
- Prevents error messages from exposing the backdoor
- Ensures process can't be traced via terminal output

---

## 🎓 Educational Scenarios

### Scenario 1: Code Review Exercise

**Task**: Review `auth_service.c` and identify the vulnerability.

**Questions for students:**
1. What makes line containing `TRAPDOOR_USERNAME` a security vulnerability?
2. Why does the backdoor username check happen before normal authentication?
3. How could this vulnerability be prevented during code review?
4. What secure coding practices would detect this?

**Answer**: Hardcoded credentials, authentication bypass logic, lack of input validation.

### Scenario 2: Detection Challenge

**Task**: Activate the trapdoor and detect the backdoor process without using the exploit script.

**Steps:**
1. List all processes before running auth_service
2. Activate trapdoor: `./auth_service sysadmin_debug_2024 test`
3. List processes again and find the new one
4. Identify characteristics that make it suspicious
5. Terminate the backdoor

### Scenario 3: Process Forensics

**Task**: Analyze the backdoor process in detail.

```bash
# Get PID from ps output
PID=$(ps aux | grep auth_service | grep -v grep | awk '{print $2}')

# Examine process details
ls -l /proc/$PID/
cat /proc/$PID/cmdline  # Command line arguments
cat /proc/$PID/status   # Process status
ls -l /proc/$PID/fd/    # Open file descriptors
```

**Questions:**
1. What is the parent process ID (PPID)?
2. Are there any open network connections?
3. What files does the process have open?
4. How long has it been running?

### Scenario 4: Real-World Parallels

**Discussion**: How do real-world backdoors compare?

**Examples:**
- **Undocumented admin accounts**: Like Windows "SUPPORT_388945a0" account
- **SSH authorized_keys tampering**: Adding unauthorized public keys
- **Web application backdoors**: Hidden admin URLs or parameter-based triggers
- **Supply chain attacks**: Malicious code in dependencies (e.g., SolarWinds)
- **Firmware backdoors**: Hidden in low-level system code

---

## 🛡️ Security Analysis

### Vulnerability Classification

| Property | Value |
|----------|-------|
| **Type** | Trapdoor/Backdoor |
| **CWE** | CWE-798 (Hardcoded Credentials) |
| **Severity** | Critical |
| **Impact** | Complete authentication bypass |
| **Exploitability** | Easy (just need to know username) |

### Attack Vector

```
Attacker → auth_service (trapdoor username) → Authentication bypass
                                            → Spawn hidden process
                                            → Persistent backdoor access
```

### Defense Mechanisms

#### 1. **Code Review & Static Analysis**
```bash
# Search for suspicious patterns
grep -r "hardcoded\|backdoor\|trapdoor" *.c
grep -r "setsid\|fork" *.c | less  # Review process spawning

# Use static analyzers
cppcheck auth_service.c
```

#### 2. **Process Monitoring**
```bash
# Monitor process creation
auditctl -a always,exit -F arch=b64 -S fork,clone,execve

# Use process accounting
accton /var/log/account/pacct
```

#### 3. **Behavioral Detection**
- Unusual process spawning patterns
- Processes without controlling terminals
- Unexpected parent-child relationships
- Long-running processes from auth services

#### 4. **Secure Coding Practices**
- No hardcoded credentials (use PAM, OAuth, etc.)
- Principle of least privilege
- Input validation and sanitization
- Logging and auditing of authentication attempts
- Multi-factor authentication

---

## 🔬 Experimentation Ideas

### For Students

1. **Modify Duration**: Change `SHELL_SLEEP_DURATION` to vary how long backdoor runs
2. **Add Logging**: Make backdoor write to a file in /tmp to prove it's running
3. **Network Activity**: Make backdoor open a listening socket (advanced)
4. **Obfuscation**: Disguise trapdoor username (ROT13, base64, XOR)
5. **Process Name**: Use `prctl()` to change process name and hide better

### Advanced Challenges

1. **Multi-Stage Backdoor**: Fork multiple times to create process hierarchy
2. **Trigger Conditions**: Only activate backdoor at specific times or dates
3. **Persistence**: Make backdoor re-spawn if killed
4. **Stealth**: Reduce CPU/memory usage to avoid detection
5. **Anti-Forensics**: Clear logs after activation

---

## 🔗 Connection to Phase 3

Phase 3 will implement a detection engine that:
- Monitors system logs for authentication anomalies
- Scans process lists for suspicious patterns
- Detects trapdoor activation in real-time
- Alerts on unauthorized process spawning
- Suggests mitigation strategies

The trapdoor from Phase 2 serves as a target for the detection engine to find.

---

## 📖 Real-World Case Studies

### 1. Ken Thompson's "Trusting Trust" (1984)
Classic paper showing how compilers can inject backdoors into programs, including login utilities. The backdoor recognizes specific usernames and grants access.

### 2. ProFTPD Backdoor (2010)
Attackers compromised ProFTPD source code and added a backdoor triggered by specific FTP commands. Went undetected for months.

### 3. Juniper Networks Backdoor (2015)
VPN code contained unauthorized access mechanism. Attackers could decrypt VPN traffic and gain administrative access.

### 4. ASUS Shadow Hammer (2019)
Supply chain attack where ASUS software updates contained backdoors targeting specific MAC addresses.

---

## 🎯 Learning Outcomes

After completing Phase 2, students should understand:

1. **Authentication Security**: Importance of secure credential handling
2. **Process Management**: How OS creates, manages, and tracks processes
3. **Daemon Processes**: Characteristics and legitimate use cases
4. **Backdoor Detection**: Techniques to identify unauthorized access
5. **Secure Development**: Code review and static analysis importance
6. **System Administration**: Process monitoring and incident response

---

## ⚠️ Ethical Considerations

### DO:
- ✅ Use in isolated VM environments only
- ✅ Study for educational purposes
- ✅ Practice detection techniques
- ✅ Learn defensive security

### DON'T:
- ❌ Implement in real systems
- ❌ Use on systems you don't own
- ❌ Deploy without authorization
- ❌ Teach exploitation without defensive context

**Remember**: The goal is to learn how to **defend** against backdoors, not to create them maliciously.

---

## 📚 Additional Resources

### Papers & Articles
- [Ken Thompson - "Reflections on Trusting Trust"](https://www.cs.cmu.edu/~rdriley/487/papers/Thompson_1984_ReflectionsonTrustingTrust.pdf)
- [OWASP - Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [CWE-798: Use of Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)

### Tools for Detection
- **Process Monitoring**: `ps`, `top`, `htop`, `pstree`
- **System Auditing**: `auditd`, `sysdig`, `osquery`
- **Network Monitoring**: `netstat`, `ss`, `lsof`
- **Forensics**: `volatility`, `sleuthkit`

### Linux Process Management
- [Linux Process Management Guide](https://tldp.org/LDP/tlk/kernel/processes.html)
- [Daemon Writing HOWTO](https://tldp.org/HOWTO/html_single/Daemon-HOWTO/)
- [Understanding Linux Processes](https://www.kernel.org/doc/html/latest/process/)

---

## 🚦 Phase Status

| Component | Status | Testing |
|-----------|--------|---------|
| auth_service.c | ✅ Complete | ✅ Passing |
| exploit_trapdoor.py | ✅ Complete | ✅ Passing |
| Documentation | ✅ Complete | - |
| Makefile Integration | ✅ Complete | ✅ Passing |

**Next Phase**: Phase 3 - Detection Engine & Dashboard

---

**Built with 💻 for Cybersecurity Education**
*Understanding backdoors to build better defenses*
