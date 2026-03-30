/*
 * buffer_target.c - Classic Stack-Based Buffer Overflow Demonstration
 *
 * OS CONCEPTS DEMONSTRATED:
 * -------------------------
 * 1. Stack Memory Layout: Shows how function local variables are stored on the stack
 * 2. Buffer Overflow: Demonstrates what happens when data exceeds allocated buffer size
 * 3. Memory Safety: Illustrates the danger of unsafe C functions like strcpy()
 * 4. Stack Smashing: Shows how overflow can corrupt adjacent stack memory (return addresses, etc.)
 *
 * VULNERABILITY:
 * --------------
 * This program intentionally uses strcpy() without bounds checking, allowing an attacker
 * to write beyond the allocated buffer size. This can overwrite the return address on the
 * stack, leading to crashes (SIGSEGV) or potentially arbitrary code execution.
 *
 * COMPILATION REQUIREMENTS:
 * -------------------------
 * Must be compiled with:
 *   - fno-stack-protector: Disables stack canaries (guards against buffer overflows)
 *   - z execstack: Makes the stack executable (allows code injection attacks)
 *
 * These flags intentionally remove modern security protections to demonstrate the vulnerability.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>  // For getpid()

/*
 * vulnerable_function() - The intentionally vulnerable function
 *
 * This function allocates a small 64-byte buffer on the stack but uses strcpy()
 * to copy user input without checking its length. If input exceeds 64 bytes,
 * it will overflow into adjacent stack memory.
 *
 * Stack Layout (simplified):
 * -------------------------
 * [Higher Memory Addresses]
 *   Return Address (where to jump after function returns)
 *   Saved Frame Pointer
 *   Local Variables (buffer[64])
 * [Lower Memory Addresses]
 */
void vulnerable_function(char *input) {
    char buffer[64];  // Small fixed-size buffer on the stack

    printf("[*] Buffer is located at: %p\n", (void *)buffer);
    printf("[*] Input size: %zu bytes\n", strlen(input));

    // VULNERABILITY: strcpy does NOT check if input fits in buffer!
    // This is the classic "unsafe string copy" vulnerability
    strcpy(buffer, input);

    printf("[*] Buffer contents: %s\n", buffer);
    printf("[*] Function completed successfully\n");
}

int main(int argc, char *argv[]) {
    printf("========================================\n");
    printf("  Buffer Overflow Vulnerability Demo\n");
    printf("========================================\n\n");

    // Check if user provided input
    if (argc != 2) {
        printf("Usage: %s <input_string>\n", argv[0]);
        printf("Example: %s \"Hello World\"\n", argv[0]);
        printf("\n[!] WARNING: Inputs larger than 64 bytes will cause overflow!\n");
        return 1;
    }

    printf("[*] Program started (PID: %d)\n", getpid());
    printf("[*] Calling vulnerable_function() with user input...\n\n");

    // Call the vulnerable function with user-controlled input
    vulnerable_function(argv[1]);

    printf("\n[*] Program exiting normally\n");
    return 0;
}

/*
 * EDUCATIONAL NOTES:
 * ------------------
 *
 * Normal Input (< 64 bytes):
 *   ./buffer_target "Hello World"
 *   Result: Program executes successfully
 *
 * Overflow Input (> 64 bytes):
 *   ./buffer_target $(python3 -c "print('A'*100)")
 *   Result: SIGSEGV (Segmentation Fault) - program crashes
 *
 * What Happens During Overflow:
 *   1. strcpy copies all input bytes into the 64-byte buffer
 *   2. Extra bytes overflow into adjacent stack memory
 *   3. This overwrites the saved return address
 *   4. When function returns, CPU jumps to corrupted address
 *   5. Operating system detects invalid memory access → SIGSEGV
 *
 * Modern Protections (Disabled in this demo):
 *   - Stack Canaries: Random values placed after buffers to detect overflow
 *   - ASLR: Randomizes memory addresses making exploits harder
 *   - DEP/NX: Marks stack as non-executable preventing code injection
 *
 * Safe Alternatives to strcpy():
 *   - strncpy(dest, src, size)
 *   - snprintf(dest, size, "%s", src)
 *   - strlcpy(dest, src, size)  [BSD systems]
 */
