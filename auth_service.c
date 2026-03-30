/*
 * auth_service.c - Authentication Service with Trapdoor Backdoor
 *
 * OS CONCEPTS DEMONSTRATED:
 * -------------------------
 * 1. Process Creation: Using fork() to create child processes
 * 2. Process Detachment: Using setsid() to create daemon processes
 * 3. File Descriptors: Closing stdin/stdout/stderr for background processes
 * 4. Process Hierarchy: Parent-child relationships and orphan processes
 * 5. Privilege Escalation: How backdoors can bypass authentication
 * 6. Background Execution: Long-running processes that survive parent termination
 *
 * VULNERABILITY: TRAPDOOR/BACKDOOR
 * ---------------------------------
 * This program simulates a login authentication service, but contains a hardcoded
 * "trapdoor" - a secret username that grants unauthorized access and spawns a
 * hidden background shell process. This demonstrates how backdoors can be embedded
 * in seemingly legitimate authentication systems.
 *
 * TRAPDOOR MECHANISM:
 * -------------------
 * When the secret username "sysadmin_debug_2024" is entered (with any password),
 * the service:
 *   1. Grants immediate access (bypasses real authentication)
 *   2. Spawns a detached background shell process
 *   3. The shell runs indefinitely in the background
 *   4. The shell is "hidden" (no controlling terminal, detached from parent)
 *
 * EDUCATIONAL PURPOSE ONLY: Real backdoors are illegal and unethical.
 * This demonstration teaches students to detect such vulnerabilities.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <fcntl.h>

// Color codes for output
#define COLOR_RESET   "\033[0m"
#define COLOR_RED     "\033[91m"
#define COLOR_GREEN   "\033[92m"
#define COLOR_YELLOW  "\033[93m"
#define COLOR_BLUE    "\033[94m"
#define COLOR_CYAN    "\033[96m"
#define COLOR_BOLD    "\033[1m"

// Configuration
#define MAX_USERNAME_LEN 64
#define MAX_PASSWORD_LEN 64
#define TRAPDOOR_USERNAME "sysadmin_debug_2024"  // Secret backdoor username
#define SHELL_SLEEP_DURATION 3600  // How long the backdoor shell runs (1 hour)

// Valid credentials for normal authentication (simulated)
typedef struct {
    char username[MAX_USERNAME_LEN];
    char password[MAX_PASSWORD_LEN];
} Credential;

// Simulated user database
Credential valid_users[] = {
    {"alice", "password123"},
    {"bob", "securepass"},
    {"admin", "admin2024"},
    {TRAPDOOR_USERNAME, ""}  // Trapdoor entry (password doesn't matter)
};

#define NUM_VALID_USERS (sizeof(valid_users) / sizeof(Credential))


/*
 * print_banner() - Display service banner
 */
void print_banner() {
    printf("%s%s", COLOR_CYAN, COLOR_BOLD);
    printf("===============================================\n");
    printf("  System Authentication Service v2.4.1\n");
    printf("  Secure Login Portal\n");
    printf("===============================================\n");
    printf("%s\n", COLOR_RESET);
}


/*
 * authenticate_user() - Normal authentication logic
 *
 * Checks if provided username/password match valid credentials.
 * Returns 1 if valid, 0 if invalid.
 *
 * OS Concept: In real systems, this would check against /etc/shadow
 * using PAM (Pluggable Authentication Modules) or similar mechanisms.
 */
int authenticate_user(const char *username, const char *password) {
    for (int i = 0; i < NUM_VALID_USERS - 1; i++) {  // Skip trapdoor entry
        if (strcmp(username, valid_users[i].username) == 0 &&
            strcmp(password, valid_users[i].password) == 0) {
            return 1;
        }
    }
    return 0;
}


/*
 * spawn_trapdoor_shell() - Activate the backdoor
 *
 * OS CONCEPTS DEMONSTRATED:
 * -------------------------
 * 1. fork(): Creates a child process that's a copy of parent
 * 2. setsid(): Creates a new session, detaching from controlling terminal
 * 3. File descriptor manipulation: Closing stdin/stdout/stderr to hide output
 * 4. Process daemonization: Making a process run in the background
 * 5. Process signals: Ignoring SIGHUP to survive terminal closure
 *
 * This function spawns a "hidden" background process that:
 * - Runs independently of the parent auth_service
 * - Has no controlling terminal (appears in 'ps' without TTY)
 * - Persists even after parent terminates
 * - Simulates an attacker's backdoor shell
 *
 * DETECTION: This process can be detected by monitoring tools that:
 * - Check for unusual parent-child relationships
 * - Look for processes without controlling terminals
 * - Scan for processes with suspicious names
 * - Monitor process creation events
 */
void spawn_trapdoor_shell() {
    pid_t pid = fork();

    if (pid < 0) {
        // Fork failed
        fprintf(stderr, "%s[!] Trapdoor activation failed%s\n", COLOR_RED, COLOR_RESET);
        return;
    }

    if (pid > 0) {
        // Parent process: just return
        // Don't wait for child - let it run independently
        printf("%s[*] Background service started (PID: %d)%s\n", COLOR_GREEN, pid, COLOR_RESET);
        return;
    }

    // === CHILD PROCESS (the backdoor) ===

    /*
     * Step 1: Create new session (setsid)
     * ------------------------------------
     * OS Concept: setsid() does three things:
     *   1. Makes this process a session leader
     *   2. Makes this process a process group leader
     *   3. Detaches from controlling terminal
     *
     * Result: Process becomes independent, survives terminal closure
     */
    if (setsid() < 0) {
        exit(EXIT_FAILURE);
    }

    /*
     * Step 2: Ignore SIGHUP signal
     * -----------------------------
     * OS Concept: SIGHUP (Hangup) is sent when terminal closes.
     * By ignoring it, process survives even if terminal is killed.
     */
    signal(SIGHUP, SIG_IGN);

    /*
     * Step 3: Close standard file descriptors
     * ----------------------------------------
     * OS Concept: Daemons typically close stdin, stdout, stderr
     * This "hides" the process output and makes it truly background.
     *
     * In a real attack, this would prevent detection via terminal output.
     */
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    /*
     * Step 4: Redirect to /dev/null (optional, for safety)
     * -----------------------------------------------------
     * Prevents any accidental I/O from causing errors
     */
    int devnull = open("/dev/null", O_RDWR);
    if (devnull != -1) {
        dup2(devnull, STDIN_FILENO);
        dup2(devnull, STDOUT_FILENO);
        dup2(devnull, STDERR_FILENO);
        if (devnull > STDERR_FILENO) {
            close(devnull);
        }
    }

    /*
     * Step 5: Execute the "backdoor payload"
     * ---------------------------------------
     * In this educational demo, we just sleep to simulate a long-running
     * backdoor process. In a real attack, this might:
     *   - Open a reverse shell to attacker's server
     *   - Listen on a network port for commands
     *   - Exfiltrate data
     *   - Provide unauthorized access
     *
     * For safety and education, we just sleep and mark ourselves
     * with a recognizable command name for detection exercises.
     */

    // Change process name to something suspicious (for detection practice)
    // In real attacks, this might be disguised as a legitimate process

    // Simulate backdoor activity: just sleep for extended period
    // The sleep duration allows detection tools to find this process
    sleep(SHELL_SLEEP_DURATION);

    // Clean exit
    exit(EXIT_SUCCESS);
}


/*
 * check_trapdoor() - Check if trapdoor is being activated
 *
 * This is the vulnerability: a hardcoded check that bypasses all security.
 * In real systems, backdoors might be much more subtle:
 *   - Hidden in obfuscated code
 *   - Triggered by specific input patterns
 *   - Activated via network packets
 *   - Time-based or condition-based triggers
 *
 * Educational Note: This obvious backdoor teaches students what to look for.
 */
int check_trapdoor(const char *username) {
    return strcmp(username, TRAPDOOR_USERNAME) == 0;
}


/*
 * process_login() - Main login processing logic
 */
void process_login(const char *username, const char *password) {
    printf("\n%s[*] Processing authentication for user: %s%s\n",
           COLOR_BLUE, username, COLOR_RESET);

    // Simulate processing delay
    sleep(1);

    // CHECK FOR TRAPDOOR (THE VULNERABILITY!)
    if (check_trapdoor(username)) {
        printf("%s%s[!] TRAPDOOR ACTIVATED [!]%s\n", COLOR_YELLOW, COLOR_BOLD, COLOR_RESET);
        printf("%s[*] Bypassing authentication checks...%s\n", COLOR_YELLOW, COLOR_RESET);
        printf("%s[+] Access granted (via backdoor)%s\n", COLOR_GREEN, COLOR_RESET);

        // Spawn the hidden background shell (the actual backdoor)
        spawn_trapdoor_shell();

        printf("\n%s[*] Login successful - Trapdoor active%s\n", COLOR_GREEN, COLOR_RESET);
        printf("%s[*] Background shell is running%s\n", COLOR_YELLOW, COLOR_RESET);
        printf("%s[*] Check with: ps aux | grep auth_service%s\n", COLOR_CYAN, COLOR_RESET);
        return;
    }

    // Normal authentication
    if (authenticate_user(username, password)) {
        printf("%s[+] Authentication successful%s\n", COLOR_GREEN, COLOR_RESET);
        printf("%s[*] Access granted%s\n", COLOR_GREEN, COLOR_RESET);
    } else {
        printf("%s[!] Authentication failed%s\n", COLOR_RED, COLOR_RESET);
        printf("%s[!] Invalid username or password%s\n", COLOR_RED, COLOR_RESET);
    }
}


/*
 * main() - Service entry point
 */
int main(int argc, char *argv[]) {
    char username[MAX_USERNAME_LEN];
    char password[MAX_PASSWORD_LEN];

    print_banner();

    // Check for command-line credentials (for automated testing)
    if (argc == 3) {
        strncpy(username, argv[1], MAX_USERNAME_LEN - 1);
        strncpy(password, argv[2], MAX_PASSWORD_LEN - 1);
        username[MAX_USERNAME_LEN - 1] = '\0';
        password[MAX_PASSWORD_LEN - 1] = '\0';
    } else {
        // Interactive mode
        printf("Username: ");
        if (fgets(username, MAX_USERNAME_LEN, stdin) == NULL) {
            printf("%s[!] Error reading username%s\n", COLOR_RED, COLOR_RESET);
            return 1;
        }
        username[strcspn(username, "\n")] = '\0';  // Remove newline

        printf("Password: ");
        if (fgets(password, MAX_PASSWORD_LEN, stdin) == NULL) {
            printf("%s[!] Error reading password%s\n", COLOR_RED, COLOR_RESET);
            return 1;
        }
        password[strcspn(password, "\n")] = '\0';  // Remove newline
    }

    // Process the login attempt
    process_login(username, password);

    printf("\n%s[*] Session ending%s\n", COLOR_BLUE, COLOR_RESET);
    return 0;
}

/*
 * EDUCATIONAL NOTES:
 * ------------------
 *
 * How to Test This Trapdoor:
 * ---------------------------
 * 1. Compile: make auth_service
 * 2. Run normally: ./auth_service
 *    - Try valid credentials: alice / password123
 *    - Try invalid credentials: bob / wrongpass
 * 3. Activate trapdoor: ./auth_service sysadmin_debug_2024 anypassword
 *    - Watch for "TRAPDOOR ACTIVATED" message
 *    - Note the background process PID
 * 4. Check for hidden process: ps aux | grep auth_service
 *    - Look for sleeping process without TTY
 * 5. Monitor with detection tools (Phase 3)
 *
 * What Makes This a Trapdoor/Backdoor?
 * -------------------------------------
 * 1. Hidden authentication bypass (secret username)
 * 2. Spawns unauthorized background process
 * 3. Process persists after parent exits
 * 4. No controlling terminal (harder to detect)
 * 5. Designed to evade casual inspection
 *
 * How to Detect Trapdoors:
 * ------------------------
 * 1. Code Review: Look for hardcoded credentials, suspicious checks
 * 2. Process Monitoring: Watch for unusual parent-child relationships
 * 3. Behavior Analysis: Detect unexpected process spawning
 * 4. System Call Tracing: Monitor fork(), setsid(), exec() calls
 * 5. Network Monitoring: Watch for unexpected connections (not in this demo)
 *
 * Real-World Trapdoor Examples:
 * -----------------------------
 * - Undocumented admin accounts
 * - Hidden API endpoints
 * - Obfuscated authentication bypasses
 * - Time-based or condition-based triggers
 * - Malicious code in supply chain (backdoored libraries)
 *
 * Defense Strategies:
 * -------------------
 * 1. Code audits and peer review
 * 2. Principle of least privilege
 * 3. Regular security scanning
 * 4. Process monitoring and anomaly detection
 * 5. Integrity checking (file hashes, signatures)
 * 6. Network segmentation and monitoring
 */
