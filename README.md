# Security Vulnerability Detection Framework

**Educational OS Security Project for Undergraduate Operating Systems Course**

> ⚠️ **WARNING**: This project contains intentionally vulnerable code for educational purposes only. Use exclusively in isolated virtual environments (VirtualBox/VM). Never deploy on production systems.

## 🎯 Project Overview

This framework demonstrates core operating system security concepts through practical vulnerability simulation, exploitation, and detection. Students learn how modern OS security features work by studying systems with those protections intentionally disabled.

**Target Environment**: Ubuntu OS in VirtualBox VM
**Educational Focus**: Memory safety, process monitoring, backdoor detection, system security

---

## 📚 Project Phases

### ✅ Phase 1: Buffer Overflow Simulation (COMPLETED)
Classic stack-based buffer overflow vulnerability demonstrating memory safety violations.

**Files**: `buffer_target.c`, `exploit_overflow.py`, `Makefile`
**Documentation**: [PHASE1_README.md](PHASE1_README.md)

### ✅ Phase 2: Trapdoor Simulation (COMPLETED)
Authentication service with hardcoded backdoor demonstrating process spawning and daemon creation.

**Files**: `auth_service.c`, `exploit_trapdoor.py`
**Documentation**: [PHASE2_README.md](PHASE2_README.md)

### ✅ Phase 3: Detection Engine & Dashboard (COMPLETED)
Real-time security monitoring framework with rich terminal UI for detecting both vulnerabilities.

**Files**: `monitor.py`, `requirements.txt`
**Documentation**: [PHASE3_README.md](PHASE3_README.md)

---

## 🚀 Quick Start

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y gcc make python3 build-essential

# Install Python dependencies for Phase 3
pip3 install -r requirements.txt
```

### Build All Components
```bash
# Clone and enter repository
git clone <repository-url>
cd OS_Project

# Build all vulnerable binaries
make

# Verify security protections are disabled
make check-protections
```

### Phase 1: Buffer Overflow Demo
```bash
# Test normal execution
./buffer_target "Hello World"

# Trigger overflow and crash
python3 exploit_overflow.py

# View crash in system logs
dmesg | grep segfault | tail -5
```

### Phase 2: Trapdoor Demo
```bash
# Test normal authentication
./auth_service alice password123

# Activate backdoor
python3 exploit_trapdoor.py

# Detect hidden process
ps aux | grep auth_service
```

### Phase 3: Real-Time Monitoring
```bash
# Start the detection engine (recommended: run as root)
sudo python3 monitor.py

# In another terminal, trigger vulnerabilities to test:
python3 exploit_overflow.py       # Test buffer overflow detection
python3 exploit_trapdoor.py       # Test trapdoor detection

# Watch the dashboard update in real-time!
```

---

## 📖 Educational Value

### OS Concepts Taught
- Stack memory layout and buffer overflows
- Process creation (fork, exec)
- Process daemonization (setsid)
- Signal handling (SIGSEGV, SIGHUP)
- File descriptors and I/O redirection
- System logging and monitoring (dmesg, syslog)
- Authentication and access control
- Process tree analysis (/proc filesystem)
- Real-time threat detection

### Security Topics Covered
- Memory corruption vulnerabilities
- Exploitation techniques
- Backdoor/trapdoor mechanisms
- Process hiding and persistence
- Detection and forensics
- Secure coding practices
- Defense-in-depth strategies
- Security operations and incident response
- Alert management and triage

---

## 🔒 Safety Guidelines

### ✅ DO:
- Use only in isolated VirtualBox/VM environments
- Practice in academic settings with supervision
- Study vulnerabilities to understand defenses
- Share knowledge responsibly

### ❌ DON'T:
- Deploy on production systems
- Use on systems you don't own
- Disable security features in real applications
- Share exploits without educational context

---

## 📚 Documentation

- **[PHASE1_README.md](PHASE1_README.md)** - Buffer overflow deep dive
- **[PHASE2_README.md](PHASE2_README.md)** - Trapdoor/backdoor analysis
- **[PHASE3_README.md](PHASE3_README.md)** - Detection engine & dashboard guide
- **requirements.txt** - Python dependencies for monitoring
- **Makefile** - Build system with detailed comments
- **Source code** - Heavily commented with OS concepts

---

## 🛠️ Makefile Commands

```bash
make                    # Build all vulnerable programs
make buffer_target      # Build Phase 1 only
make auth_service       # Build Phase 2 only
make check-protections  # Verify security features disabled
make clean              # Remove compiled binaries
make help               # Show all commands
```

---

## 🎓 For Students

### Recommended Learning Path
1. Read PHASE1_README.md and understand buffer overflows
2. Compile and run buffer_target with various inputs
3. Study exploit_overflow.py to see exploitation
4. Read PHASE2_README.md for backdoor concepts
5. Run auth_service and activate the trapdoor
6. Practice detection using ps, pstree, /proc
7. **Read PHASE3_README.md for monitoring concepts**
8. **Run monitor.py and test detection of both vulnerabilities**
9. **Study alert management and incident response**

### Lab Exercises
- Modify buffer sizes and observe behavior
- Calculate exact overflow offset to return address
- Change trapdoor trigger conditions
- Practice manual process detection
- Write custom detection scripts
- **Extend monitor.py with custom detectors**
- **Configure alert thresholds and sensitivity**
- **Implement automated response actions**

---

## 📊 Project Status

| Phase | Component | Status | Files | Tests |
|-------|-----------|--------|-------|-------|
| 1 | Buffer Overflow | ✅ Complete | 3 | ✅ Pass |
| 2 | Trapdoor | ✅ Complete | 2 | ✅ Pass |
| 3 | Detection Engine | ✅ Complete | 2 | ✅ Pass |

**🎉 ALL PHASES COMPLETE!**

This project demonstrates a complete security vulnerability lifecycle:
- **Phase 1**: Vulnerability (buffer overflow)
- **Phase 2**: Exploitation (trapdoor backdoor)
- **Phase 3**: Detection & Response (monitoring framework)

---

## 🤝 Contributing

This is an educational project. Improvements welcome:
- Clearer OS concept explanations
- Additional vulnerability demonstrations
- Better detection techniques
- Enhanced documentation

---

## 📄 License

Educational use only. See course materials for academic integrity policies.

---

## 🔗 Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Common Weakness Enumeration](https://cwe.mitre.org/)
- [Linux Process Management](https://www.kernel.org/doc/html/latest/)
- [Secure Coding Standards](https://wiki.sei.cmu.edu/confluence/display/seccode)

---

**Built for Educational Excellence** 🎓
*Teaching security by understanding vulnerabilities*
