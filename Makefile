# Makefile for Security Vulnerability Detection Framework
#
# OS CONCEPTS DEMONSTRATED:
# -------------------------
# This Makefile shows how compiler flags control security features in the operating system.
# Modern OSes provide several layers of protection against memory corruption exploits,
# but we intentionally disable them here for educational purposes.
#
# EDUCATIONAL PURPOSE ONLY: These settings create vulnerable binaries to demonstrate
# security concepts. NEVER use these flags in production code!

# Compiler
CC = gcc

# Compiler flags explanation:
# ---------------------------
# -fno-stack-protector:
#   Disables stack canaries (stack guards). Stack canaries are random values placed
#   between buffers and return addresses. The OS checks if they're modified before
#   function returns, detecting buffer overflows. We disable this to show raw overflow.
#
# -z execstack:
#   Makes the stack memory region executable. Modern OSes use DEP (Data Execution Prevention)
#   or NX (No eXecute) bit to mark stack as non-executable, preventing injected code from
#   running. We enable execution to demonstrate classic shellcode injection attacks.
#
# -g:
#   Includes debugging symbols. Helpful for analyzing crashes with gdb and understanding
#   what happened during the overflow.
#
# -Wall:
#   Enables all compiler warnings. GCC will warn us about unsafe functions like strcpy,
#   but we're using them intentionally for this demonstration.
#
# -O0:
#   Disables optimizations. Ensures the code executes exactly as written, making it
#   easier to understand and predict behavior during buffer overflow attacks.

CFLAGS = -fno-stack-protector -z execstack -g -Wall -O0

# Build targets
TARGETS = buffer_target auth_service

# Default target - builds all vulnerable programs
all: $(TARGETS)
	@echo ""
	@echo "=========================================="
	@echo "  Vulnerable Binaries Built Successfully"
	@echo "=========================================="
	@echo ""
	@echo "WARNING: These programs contain intentional security vulnerabilities!"
	@echo "         Use only for educational purposes in isolated environments."
	@echo ""
	@echo "Built programs:"
	@echo "  - buffer_target : Stack-based buffer overflow demonstration"
	@echo "  - auth_service  : Trapdoor backdoor demonstration"
	@echo ""

# Buffer overflow target
buffer_target: buffer_target.c
	@echo "[*] Compiling buffer_target.c with disabled security protections..."
	$(CC) $(CFLAGS) -o buffer_target buffer_target.c
	@echo "[+] buffer_target compiled successfully"
	@echo "    Flags used: $(CFLAGS)"
	@echo ""

# Authentication service with trapdoor (Phase 2)
auth_service: auth_service.c
	@echo "[*] Compiling auth_service.c..."
	$(CC) $(CFLAGS) -o auth_service auth_service.c
	@echo "[+] auth_service compiled successfully"
	@echo ""

# Clean up compiled binaries
clean:
	@echo "[*] Cleaning up compiled binaries..."
	rm -f $(TARGETS)
	@echo "[+] Clean complete"

# Verify security protections are disabled (useful for confirming vulnerability)
check-protections: buffer_target
	@echo "=========================================="
	@echo "  Security Protection Status Check"
	@echo "=========================================="
	@echo ""
	@echo "[*] Checking buffer_target binary protections..."
	@echo ""
	@echo "--- Stack Canary Check ---"
	@if readelf -s buffer_target | grep -q "__stack_chk_fail"; then \
		echo "❌ Stack canary: ENABLED (unexpected!)"; \
	else \
		echo "✓ Stack canary: DISABLED (vulnerable as intended)"; \
	fi
	@echo ""
	@echo "--- Executable Stack Check ---"
	@if readelf -l buffer_target | grep -A 1 "GNU_STACK" | grep -q "RWE"; then \
		echo "✓ Stack: EXECUTABLE (vulnerable as intended)"; \
	else \
		echo "❌ Stack: NON-EXECUTABLE (protected)"; \
	fi
	@echo ""
	@echo "--- PIE/ASLR Check ---"
	@if readelf -h buffer_target | grep "Type:" | grep -q "EXEC"; then \
		echo "✓ PIE: DISABLED (predictable addresses)"; \
	else \
		echo "⚠ PIE: ENABLED (addresses randomized)"; \
	fi
	@echo ""

# Help target
help:
	@echo "Security Vulnerability Detection Framework - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make              - Build all vulnerable programs"
	@echo "  make buffer_target- Build only buffer overflow demo"
	@echo "  make auth_service - Build only trapdoor demo"
	@echo "  make clean        - Remove compiled binaries"
	@echo "  make check-protections - Verify security features are disabled"
	@echo "  make help         - Show this help message"
	@echo ""
	@echo "Security flags in use:"
	@echo "  -fno-stack-protector : Disables stack canaries"
	@echo "  -z execstack         : Makes stack executable"
	@echo "  -g                   : Includes debug symbols"
	@echo "  -Wall                : Enables compiler warnings"
	@echo "  -O0                  : Disables optimizations"
	@echo ""

.PHONY: all clean check-protections help
