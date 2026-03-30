# Security Vulnerability Detection Framework

**Educational OS Security Project for Undergraduate Operating Systems Course**

> ⚠️ **WARNING**: This project contains intentionally vulnerable code for educational purposes only. Use exclusively in isolated virtual environments (VirtualBox/VM). Never deploy on production systems.

---

## 🎯 Project Overview

This framework demonstrates core operating system security concepts through practical vulnerability simulation, exploitation, and detection. Students learn how modern OS security features work by studying systems with those protections intentionally disabled.

**Target Environment**: Ubuntu OS in VirtualBox VM
**Educational Focus**: Memory safety, process monitoring, system security

---

## 📚 Project Phases

### ✅ Phase 1: Buffer Overflow Simulation (COMPLETED)

Classic stack-based buffer overflow vulnerability demonstrating:
- Stack memory layout and function call mechanics
- Memory safety violations and their consequences
- How unsafe C functions (strcpy) can be exploited
- OS response to memory corruption (SIGSEGV signals)

**Files Created:**
- `buffer_target.c` - Vulnerable C program with stack buffer overflow
- `Makefile` - Compilation with disabled security protections
- `exploit_overflow.py` - Python exploit script to trigger crash

### 🔜 Phase 2: Trapdoor Simulation (PENDING APPROVAL)

Backdoor demonstration showing:
- Hidden authentication bypass mechanisms
- Process spawning and background execution
- Detection of unauthorized processes

**Planned Files:**
- `auth_service.c` - Login service with hardcoded trapdoor

### 🔜 Phase 3: Detection Engine & Dashboard (PENDING APPROVAL)

Real-time security monitoring framework:
- System log analysis (dmesg, syslog)
- Process tree monitoring with psutil
- Rich terminal UI with live security alerts
- Automated mitigation suggestions

**Planned Files:**
- `monitor.py` - Python daemon with detection logic and UI

---

## 🚀 Quick Start - Phase 1

### Prerequisites

```bash
# Install required tools
sudo apt-get update
sudo apt-get install -y gcc make python3 build-essential

# Verify installations
gcc --version
make --version
python3 --version
```

### Build and Test

```bash
# 1. Compile the vulnerable binary
make buffer_target

# 2. Verify security protections are disabled
make check-protections

# Expected output:
#   ✓ Stack canary: DISABLED (vulnerable as intended)
#   ✓ Stack: EXECUTABLE (vulnerable as intended)

# 3. Test with safe input (no overflow)
./buffer_target "Hello World"

# 4. Run the exploit script
python3 exploit_overflow.py

# Expected: SIGSEGV (Segmentation Fault) - SUCCESS!
```

### Manual Testing

```bash
# Safe input (< 64 bytes) - works normally
./buffer_target "Short input"

# Overflow input (> 64 bytes) - triggers crash
./buffer_target $(python3 -c "print('A'*100)")

# Check system logs for crash evidence
dmesg | tail -20
# Look for: "segfault at 0x41414141" (corrupted return address)
```

---

## 📖 Educational Concepts

### Phase 1: Buffer Overflow Deep Dive

#### **What is a Buffer Overflow?**

A buffer overflow occurs when a program writes more data to a buffer than it can hold, causing adjacent memory to be overwritten.

```
Stack Layout (grows downward):
┌─────────────────────┐ ← Higher addresses
│  Return Address     │ ← Overwrites this with 0x41414141
├─────────────────────┤
│  Saved Frame Ptr    │
├─────────────────────┤
│  buffer[64]         │ ← Starts here, overflows upward
└─────────────────────┘ ← Lower addresses
```

#### **Why is strcpy() Dangerous?**

```c
char buffer[64];
strcpy(buffer, user_input);  // NO bounds checking!
```

`strcpy()` copies until it finds a null terminator (`\0`), regardless of buffer size. If `user_input` is 100 bytes, it writes all 100 bytes, overflowing by 36 bytes into critical stack data.

#### **Modern Protections (Disabled in this demo)**

| Protection | Purpose | Status in Demo |
|------------|---------|----------------|
| **Stack Canaries** | Random value before return address; checked before return | ❌ Disabled (`-fno-stack-protector`) |
| **DEP/NX Bit** | Marks stack as non-executable | ❌ Disabled (`-z execstack`) |
| **ASLR** | Randomizes memory addresses | ⚠️ System-dependent |
| **PIE** | Position Independent Executable | ⚠️ System-dependent |

#### **The Exploitation Process**

1. **Payload Crafting**: Create input larger than buffer (100 bytes of 'A')
2. **Buffer Overflow**: strcpy writes past buffer boundary
3. **Return Address Corruption**: Overwrite saved return address with `0x41414141`
4. **Invalid Jump**: Function returns, CPU jumps to `0x41414141`
5. **Segmentation Fault**: OS detects invalid memory access → SIGSEGV
6. **Process Termination**: Kernel kills the process for safety

#### **OS Security Response**

When the buffer overflow occurs:
- **MMU (Memory Management Unit)** detects invalid address access
- **Kernel** sends `SIGSEGV` (signal 11) to the process
- **Process** terminates unless signal handler is installed
- **Logs** written to kernel ring buffer (dmesg) and syslog

```bash
# View crash in kernel logs
dmesg | grep segfault

# Example output:
# buffer_target[7183]: segfault at 41414141 ip 0000000041414141 sp 00007ffd773ff400
```

---

## 🛠️ Makefile Commands

```bash
make                    # Build all vulnerable programs
make buffer_target      # Build only buffer overflow demo
make check-protections  # Verify security features are disabled
make clean              # Remove compiled binaries
make help               # Show all available commands
```

---

## 🔬 Experimentation Ideas

### For Students

1. **Vary Payload Size**: Try 50, 64, 70, 80, 100 bytes. When does it crash?
2. **Pattern Analysis**: Use different patterns (AAAA, BBBB) to identify what overwrites return address
3. **GDB Debugging**: Run under debugger to see exact crash location
   ```bash
   gdb ./buffer_target
   (gdb) run $(python3 -c "print('A'*100)")
   (gdb) info registers  # See corrupted instruction pointer
   ```
4. **Safe Alternatives**: Modify code to use `strncpy()` or `snprintf()` and observe the difference
5. **Enable Protections**: Compile with `-fstack-protector` and see how canaries prevent exploitation

### Advanced Challenges

1. **Calculate Exact Offset**: Determine precisely how many bytes until return address
2. **Control Return Address**: Overwrite return address with specific value (not just 'A's)
3. **Log Correlation**: Write script to automatically detect crashes in dmesg

---

## 📝 Code Structure

### buffer_target.c
- **vulnerable_function()**: Contains the 64-byte buffer and unsafe strcpy
- **main()**: Accepts command-line input and calls vulnerable function
- **Heavy comments**: Explains stack layout, memory corruption, and OS concepts

### exploit_overflow.py
- **generate_payload()**: Creates oversized input string
- **run_exploit()**: Executes vulnerable binary with crafted payload
- **analyze_result()**: Detects SIGSEGV and explains what happened
- **Educational output**: Color-coded, detailed explanations

### Makefile
- **Compilation flags**: `-fno-stack-protector`, `-z execstack`
- **Security checks**: Verifies protections are actually disabled
- **Clean builds**: Ensures consistent compilation environment

---

## ⚠️ Safety Guidelines

### DO:
- ✅ Run only in isolated VirtualBox/VM environment
- ✅ Use for educational purposes in academic settings
- ✅ Share knowledge with students learning OS security
- ✅ Experiment and modify code to deepen understanding

### DON'T:
- ❌ Deploy on production systems or servers
- ❌ Use techniques on systems you don't own
- ❌ Share exploits without educational context
- ❌ Disable security features in real-world applications

---

## 🎓 Learning Outcomes

After completing Phase 1, students should understand:

1. **Memory Management**: How the stack works, function calls, return addresses
2. **C Security**: Why unsafe functions are dangerous, importance of bounds checking
3. **OS Protection**: Purpose of stack canaries, DEP/NX, ASLR
4. **Exploit Development**: Basic payload crafting and vulnerability triggering
5. **System Monitoring**: How to detect crashes in system logs
6. **Defensive Programming**: Safe coding practices to prevent buffer overflows

---

## 📚 Additional Resources

### Buffer Overflow Tutorials
- [Smashing The Stack For Fun And Profit](http://phrack.org/issues/49/14.html) - Classic paper
- [OWASP Buffer Overflow](https://owasp.org/www-community/vulnerabilities/Buffer_Overflow)

### System Security
- [Linux Memory Management](https://www.kernel.org/doc/html/latest/admin-guide/mm/index.html)
- [Address Space Layout Randomization (ASLR)](https://en.wikipedia.org/wiki/Address_space_layout_randomization)

### Safe Coding
- [CWE-120: Buffer Copy without Checking Size of Input](https://cwe.mitre.org/data/definitions/120.html)
- [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard)

---

## 🤝 Contributing

This is an educational project for an undergraduate OS course. Suggestions for improvements:
- Clearer explanations of OS concepts
- Additional vulnerability demonstrations
- Better visual aids for memory layout
- More interactive learning exercises

---

## 📄 License

Educational use only. See course materials for academic integrity guidelines.

---

## 👨‍🏫 Course Context

**Target Audience**: Undergraduate Operating Systems students
**Prerequisites**: Basic C programming, understanding of function calls and stack
**Learning Approach**: Hands-on experimentation with vulnerable systems
**Assessment**: Understanding of security concepts, not exploitation skills

---

## 🚦 Project Status

| Phase | Status | Files | Testing |
|-------|--------|-------|---------|
| Phase 1: Buffer Overflow | ✅ Complete | 3/3 | ✅ Passing |
| Phase 2: Trapdoor | ⏳ Awaiting Approval | 0/1 | - |
| Phase 3: Detection Engine | ⏳ Awaiting Approval | 0/1 | - |

**Next Steps**: Awaiting approval to proceed with Phase 2 (Trapdoor Simulation)

---

**Built with 💻 for Educational Excellence**
*Teaching security by understanding vulnerabilities*
