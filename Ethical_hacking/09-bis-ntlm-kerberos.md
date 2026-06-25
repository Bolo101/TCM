# NTLM and Kerberos: Authentication Protocols and Exploitation

## Introduction

**NTLM** and **Kerberos** are the two main authentication protocols used in Windows environments. Understanding how they work is essential for both securing networks and identifying vulnerabilities during penetration testing.

---

## NTLM (NT LAN Manager)

### What is NTLM?

**NTLM** is a challenge-response authentication protocol developed by Microsoft. It's an older protocol that's still widely used for backward compatibility, especially when Kerberos isn't available.

**Key Characteristics:**
- Older protocol (dating back to Windows NT)
- Still used in many environments
- Considered less secure than Kerberos
- Often falls back when Kerberos fails

### How NTLM Works

NTLM uses a **challenge-response** mechanism:

```
1. Client → Server: "I want to authenticate"
2. Server → Client: "Here's a random challenge (nonce)"
3. Client → Server: "Here's the response (hash of challenge + password)"
4. Server: Verifies the response is correct
```

**Step-by-Step Process:**

| Step | Description |
|------|-------------|
| **1. Negotiation** | Client and server agree to use NTLM |
| **2. Challenge** | Server sends a random number (nonce) to client |
| **3. Response** | Client hashes the challenge with their password hash |
| **4. Verification** | Server verifies the response matches expected value |

**What is a Nonce?**

A **nonce** (Number Used Once) is a random number used to prevent replay attacks. It ensures that each authentication attempt is unique.

### NTLM Authentication Visual Scheme

```
┌─────────────┐                    ┌─────────────┐
│   Client    │                    │   Server    │
│  (fcastle)  │                    │             │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. "I want to authenticate"     │
       │─────────────────────────────────>│
       │                                  │
       │  2. Challenge: 0x4A3F8B2C        │
       │<─────────────────────────────────│
       │                                  │
       │  3. Response: HMAC(challenge,    │
       │     NT_hash)                     │
       │─────────────────────────────────>│
       │                                  │
       │  4. Verify response              │
       │                                  │
       │  5. "Access granted"             │
       │<─────────────────────────────────│
       │                                  │
```

### NTLM Authentication with Example Values

**Step 1: Negotiation**

```
Client → Server: "I want to authenticate as MARVEL\fcastle"
```

**Step 2: Challenge**

```
Server → Client: "Here's your challenge: 0x4A3F8B2C"
```

**Step 3: Response Calculation**

```
Client calculates:
- Password: "Password1"
- NT_hash: 32ed87bdb5fdc5e9cba88547376818d4
- Challenge: 0x4A3F8B2C
- Response: HMAC_MD5(NT_hash, challenge)
- Response: 0x7F2E9A4C1B8D3F6E5A0C9B8D7E2F1A4C
```

**Step 4: Response**

```
Client → Server: "Here's my response: 0x7F2E9A4C1B8D3F6E5A0C9B8D7E2F1A4C"
```

**Step 5: Verification**

```
Server calculates:
- Looks up fcastle's NT_hash from database
- NT_hash: 32ed87bdb5fdc5e9cba88547376818d4
- Calculates expected response: HMAC_MD5(NT_hash, challenge)
- Expected: 0x7F2E9A4C1B8D3F6E5A0C9B8D7E2F1A4C
- Compares with received response
- Match! Access granted.
```

### NTLM Hashes

NTLM uses two types of hashes:

| Hash Type | Description | Security Level |
|-----------|-------------|----------------|
| **LM Hash** | LAN Manager hash (very weak) | Very weak (easily cracked) |
| **NT Hash** | NTLM hash (stronger) | Weak but better than LM |

**Hash Format:**
```
LM_hash:NT_hash
Example: aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4
```

**Note:** The LM hash is often empty (shown as `aad3b435b51404eeaad3b435b51404ee`) in modern systems.

### Captured NTLMv2 Hash Example

```
MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:0101000000000000c0cf...
│         │      │      │              │                              │
│         │      │      │              │                              └─ AV pairs (additional data)
│         │      │      │              └─ NTProofStr (response to challenge)
│         │      │      └─ Challenge (random number from server)
│         │      └─ Domain name
│         └─ Username
└─ Full username with domain
```

### When is NTLM Used?

NTLM is typically used when:
- Kerberos is not available
- Authenticating to systems that don't support Kerberos
- Connecting to older Windows systems
- Using certain applications that require NTLM
- Network authentication across forest trusts

---

## Kerberos

### What is Kerberos?

**Kerberos** is a modern authentication protocol based on symmetric key cryptography and trusted third parties. It's the default authentication protocol in Active Directory environments.

**Key Characteristics:**
- Default protocol in Active Directory
- More secure than NTLM
- Uses tickets for authentication
- Requires a Key Distribution Center (KDC)

### How Kerberos Works

Kerberos uses a **ticket-based** authentication system with three main components:

```
Client ←→ KDC (Key Distribution Center) ←→ Service
```

**The Three Main Components:**

| Component | Role |
|-----------|------|
| **Client** | User or service requesting access |
| **KDC** | Trusted third party that issues tickets (Domain Controller) |
| **Service** | Resource being accessed (file server, web server, etc.) |

### Kerberos Architecture Visual Scheme

```
                    ┌─────────────────────────┐
                    │   Key Distribution      │
                    │   Center (KDC)          │
                    │   (Domain Controller)   │
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │ Authentication    │  │
                    │  │ Server (AS)       │  │
                    │  └───────────────────┘  │
                    │  ┌───────────────────┐  │
                    │  │ Ticket Granting   │  │
                    │  │ Server (TGS)      │  │
                    │  └───────────────────┘  │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
        │    Client    │ │  Service 1 │ │  Service 2 │
        │   (fcastle)  │ │ (File Svr) │ │ (Web Svr)  │
        └──────────────┘ └────────────┘ └────────────┘
```

### Kerberos Authentication Flow Visual Scheme

```
┌─────────────┐                    ┌─────────────────────────┐
│   Client    │                    │           KDC            │
│  (fcastle)  │                    │   (Domain Controller)   │
└──────┬──────┘                    └───────────┬─────────────┘
       │                                      │
       │  1. AS-REQ: "I want to authenticate" │
       │─────────────────────────────────────>│
       │                                      │
       │  2. AS-REP: TGT + session key        │
       │<─────────────────────────────────────│
       │                                      │
       │  3. TGS-REQ: "I want file server"    │
       │     (with TGT)                       │
       │─────────────────────────────────────>│
       │                                      │
       │  4. TGS-REP: Service ticket          │
       │<─────────────────────────────────────│
       │                                      │
       │  5. AP-REQ: "Here's my ticket"       │
       │─────────────────────────────────────>│
       │     (to file server)                 │
       │                                      │
```

### Kerberos Authentication Flow

```
1. Client → KDC: "I want to access a service"
2. KDC → Client: "Here's a Ticket Granting Ticket (TGT)"
3. Client → KDC: "I want a service ticket (using TGT)"
4. KDC → Client: "Here's a service ticket"
5. Client → Service: "Here's my service ticket"
6. Service: Verifies ticket and grants access
```

**Step-by-Step Process:**

| Step | Description |
|------|-------------|
| **1. AS-REQ** | Client requests authentication from Authentication Server |
| **2. AS-REP** | KDC returns a Ticket Granting Ticket (TGT) |
| **3. TGS-REQ** | Client requests a service ticket using the TGT |
| **4. TGS-REP** | KDC returns a service ticket for the requested service |
| **5. AP-REQ** | Client presents service ticket to the target service |
| **6. Verification** | Service validates ticket and grants access |

### Kerberos Authentication with Example Values

**Step 1: AS-REQ (Authentication Server Request)**

```
Client → KDC:
{
  "username": "fcastle",
  "domain": "MARVEL",
  "service": "krbtgt",
  "timestamp": "2024-01-15T10:30:00Z",
  "nonce": 0x12345678
}
```

**Step 2: AS-REP (Authentication Server Reply)**

```
KDC → Client:
{
  "TGT": {
    "user": "fcastle",
    "domain": "MARVEL",
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T20:30:00Z",
    "session_key": "0x9A8B7C6D5E4F3A2B1C0D9E8F7A6B5C4D"
  },
  "session_key_encrypted": "Encrypted with fcastle's password hash"
}
```

**Step 3: TGS-REQ (Ticket Granting Server Request)**

```
Client → KDC:
{
  "TGT": [from step 2],
  "service": "cifs/fileserver.marvel.local",
  "timestamp": "2024-01-15T10:31:00Z",
  "authenticator": {
    "client": "fcastle",
    "timestamp": "2024-01-15T10:31:00Z"
  }
}
```

**Step 4: TGS-REP (Ticket Granting Server Reply)**

```
KDC → Client:
{
  "service_ticket": {
    "client": "fcastle",
    "service": "cifs/fileserver.marvel.local",
    "start_time": "2024-01-15T10:31:00Z",
    "end_time": "2024-01-15T20:31:00Z",
    "session_key": "0x1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D"
  },
  "session_key_encrypted": "Encrypted with TGT session key"
}
```

**Step 5: AP-REQ (Application Request)**

```
Client → File Server:
{
  "service_ticket": [from step 4],
  "authenticator": {
    "client": "fcastle",
    "timestamp": "2024-01-15T10:32:00Z"
  }
}
```

**Step 6: Verification**

```
File Server:
1. Decrypts service ticket with its own key
2. Extracts session key: 0x1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D
3. Decrypts authenticator with session key
4. Verifies timestamp is recent
5. Access granted!
```

### Kerberos Tickets

**Ticket Granting Ticket (TGT):**
- Proves user's identity to the KDC
- Used to obtain service tickets
- Typically valid for 10 hours
- Stored in memory

**Service Ticket:**
- Grants access to a specific service
- Contains user identity and permissions
- Valid for a limited time
- Presented to the target service

### Service Principal Names (SPNs)

**What is an SPN?**

An **SPN** (Service Principal Name) is a unique identifier for a service instance in Active Directory. It tells Kerberos which service account runs a particular service.

**SPN Format:**
```
ServiceClass/Host:Port/ServiceName
Examples:
- HTTP/webserver.marvel.local
- MSSQLSvc/dbserver.marvel.local:1433
- cifs/fileserver.marvel.local
```

**SPN Examples with Details:**

```
1. HTTP/webserver.marvel.local
   - Service: Web server (IIS)
   - Host: webserver.marvel.local
   - Account: IIS_APPPOOL

2. MSSQLSvc/dbserver.marvel.local:1433
   - Service: SQL Server
   - Host: dbserver.marvel.local
   - Port: 1433
   - Account: SQLService

3. cifs/fileserver.marvel.local
   - Service: File sharing (SMB)
   - Host: fileserver.marvel.local
   - Account: FileService

4. HOST/workstation01.marvel.local
   - Service: Generic host services
   - Host: workstation01.marvel.local
   - Account: Machine account
```

**Why SPNs Matter:**
- Required for Kerberos authentication
- Identify which account to authenticate as
- Used in Kerberoasting attacks

### Kerberos Ticket Structure Example

**Service Ticket Contents:**

```
Ticket for: cifs/fileserver.marvel.local

{
  "client": "fcastle@MARVEL.LOCAL",
  "server": "cifs/fileserver.marvel.local@MARVEL.LOCAL",
  "auth_time": "2024-01-15T10:31:00Z",
  "start_time": "2024-01-15T10:31:00Z",
  "end_time": "2024-01-15T20:31:00Z",
  "renew_till": "2024-01-16T10:31:00Z",
  "flags": [
    "forwardable",
    "renewable",
    "pre_authent"
  ],
  "session_key": {
    "type": "aes256-cts-hmac-sha1-96",
    "value": "0x1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D"
  },
  "client_addresses": ["192.168.1.100"]
}
```

### When is Kerberos Used?

Kerberos is used when:
- Authenticating in an Active Directory domain
- Accessing domain resources (file shares, web servers, databases)
- Using modern Windows applications
- All systems support Kerberos
- Time synchronization is available

---

## NTLM vs Kerberos Comparison

| Feature | NTLM | Kerberos |
|---------|------|----------|
| **Age** | Older protocol | Modern protocol |
| **Security** | Less secure | More secure |
| **Default in AD** | Fallback | Primary protocol |
| **Authentication Method** | Challenge-response | Ticket-based |
| **Performance** | Slower (more round trips) | Faster (fewer round trips) |
| **Mutual Authentication** | No | Yes |
| **Delegation** | Limited | Full support |
| **Time Synchronization** | Not required | Required |
| **Single Sign-On** | Limited | Full support |

### NTLM vs Kerberos Visual Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│                    NTLM Authentication                          │
├─────────────────────────────────────────────────────────────────┤
│  Client ────────> Server ────────> Client ────────> Server     │
│  Request        Challenge         Response        Verify        │
│                                                                 │
│  • 3 round trips                                               │
│  • Challenge-response                                          │
│  • No mutual authentication                                     │
│  • Hash sent over network                                      │
│  • Slower performance                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Kerberos Authentication                       │
├─────────────────────────────────────────────────────────────────┤
│  Client ────────> KDC ────────> Client ────────> KDC           │
│  AS-REQ         AS-REP      TGS-REQ         TGS-REP            │
│                                                                 │
│  Client ────────> Service                                     │
│  AP-REQ                                                       │
│                                                                 │
│  • 3 round trips (to KDC) + 1 to service                       │
│  • Ticket-based                                                │
│  • Mutual authentication                                       │
│  • No password/hash sent over network                          │
│  • Faster performance                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Exploiting NTLM in Ethical Hacking

### 1. LLMNR Poisoning

**How It Works:**

Attackers poison LLMNR responses to capture NTLM hashes when users try to access resources.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Victim    │
│  (Responder)│                    │  (fcastle)  │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Monitor for LLMNR requests   │
       │<─────────────────────────────────│
       │                                  │
       │  2. "Where is \\FILESERVER?"     │
       │<─────────────────────────────────│
       │                                  │
       │  3. "I am FILESERVER (192.168.1.50)" │
       │─────────────────────────────────>│
       │                                  │
       │  4. "Authenticate me"            │
       │<─────────────────────────────────│
       │                                  │
       │  5. Challenge: 0x9E8F7A6B        │
       │─────────────────────────────────>│
       │                                  │
       │  6. Response: 0x3D4E5F6A...      │
       │<─────────────────────────────────│
       │                                  │
       │  7. Captured hash!               │
       │  MARVEL\fcastle::MARVEL:...      │
       │                                  │
```

**Attack Flow:**
```
1. Attacker monitors network for LLMNR requests
2. User tries to access \\FILESERVER (DNS fails)
3. Computer sends LLMNR request
4. Attacker responds claiming to be FILESERVER
5. User authenticates to attacker
6. Attacker captures NTLM hash
```

**Tools Used:**
- **Responder** - Poisons LLMNR/NBT-NS requests
- **Command:** `sudo responder -I eth0 -dwP`

**What You Get:**
- NTLMv2 hash that can be cracked offline
- Example: `MARVEL\fcastle::MARVEL:1122334455667788:aabbccddeeff001122334455667788:0101000000000000c0cf...`

### 2. Pass-the-Hash

**How It Works:**

Instead of cracking a captured hash, attackers use it directly to authenticate.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Target    │
│             │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Captured hash:               │
       │     32ed87bdb5fdc5e9cba88547376818d4 │
       │                                  │
       │  2. Authenticate using hash      │
       │─────────────────────────────────>│
       │                                  │
       │  3. Server accepts hash          │
       │<─────────────────────────────────│
       │                                  │
       │  4. Access granted as fcastle    │
       │<─────────────────────────────────│
       │                                  │
```

**Attack Flow:**
```
1. Attacker captures NTLM hash
2. Attacker uses hash to authenticate without password
3. Attacker gains access as the victim
```

**Tools Used:**
- **psexec.py** - Execute commands using hash
- **wmiexec.py** - WMI execution using hash
- **smbexec.py** - SMB execution using hash

**Commands:**
```bash
# Using password
psexec.py MARVEL/fcastle:'Password1'@192.168.138.137

# Using hash
psexec.py administrator@192.168.138.137 -hashes aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4
```

### 3. SMB Relay

**How It Works:**

Instead of cracking hashes, attackers relay captured authentication attempts to other targets.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Victim    │
│  (Responder)│                    │  (fcastle)  │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Capture authentication       │
       │<─────────────────────────────────│
       │                                  │
       │  2. Relay to target server       │
       │─────────────────────────────────>│
       │     (192.168.138.137)            │
       │                                  │
┌──────▼──────┐                    ┌──────▼──────┐
│   Target    │                    │             │
│   Server    │                    │             │
└──────┬──────┘                    └─────────────┘
       │
       │  3. Accepts authentication
       │     (SMB signing disabled)
       │
       │  4. Access granted as fcastle
       │<─────────────────────────────────┘
```

**Attack Flow:**
```
1. Attacker captures NTLM authentication (via LLMNR poisoning)
2. Attacker relays authentication to another target
3. Target accepts authentication (if SMB signing is disabled)
4. Attacker gains access to target as victim
```

**Requirements:**
- SMB signing must be disabled on target
- Relayed user must have admin rights on target

**Tools Used:**
- **Responder** - Capture authentication (with SMB/HTTP disabled)
- **ntlmrelayx.py** - Relay authentication to targets

**Commands:**
```bash
# Configure Responder to disable SMB/HTTP
# Edit /etc/responder/Responder.conf

# Start Responder
sudo responder -I eth0 -dwPv

# Start NTLM relay
ntlmrelayx.py -tf targets.txt -smb2support
```

### 4. NTLM Relay to LDAP

**How It Works:**

Relay NTLM authentication to LDAP to gain domain admin privileges.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Admin     │
│  (mitm6)    │                    │  (tstark)   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. IPv6 DNS takeover            │
       │<─────────────────────────────────│
       │                                  │
       │  2. Relay authentication to LDAP │
       │─────────────────────────────────>│
       │                                  │
┌──────▼──────┐                    ┌──────▼──────┐
│   Domain    │                    │             │
│ Controller  │                    │             │
└──────┬──────┘                    └─────────────┘
       │
       │  3. Create new user
       │     "hacker" + add to Enterprise Admins
       │
       │  4. Domain admin access!
       │<─────────────────────────────────┘
```

**Attack Flow:**
```
1. Attacker uses mitm6 for IPv6 DNS takeover
2. NTLM authentication is relayed to LDAP
3. When admin logs in, attacker creates new user
4. New user is added to Enterprise Admins
5. Attacker gains domain admin access
```

**Tools Used:**
- **mitm6** - IPv6 DNS takeover
- **ntlmrelayx.py** - Relay to LDAP

**Commands:**
```bash
# Set up NTLM relay for LDAP
ntlmrelayx.py -6 -t ldaps://192.168.138.136 -wh fakewpad.marvel.local -l lootme

# Start mitm6
sudo mitm6 -d marvel.local
```

---

## Exploiting Kerberos in Ethical Hacking

### 1. Kerberoasting

**How It Works:**

Attackers request Kerberos service tickets for service accounts and crack them offline.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │     KDC     │
│             │                    │             │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Find service accounts with SPNs │
       │<─────────────────────────────────│
       │                                  │
       │  2. Request service tickets      │
       │─────────────────────────────────>│
       │     for HTTP/webserver.marvel.local │
       │                                  │
       │  3. Receive encrypted tickets    │
       │<─────────────────────────────────│
       │                                  │
       │  4. Crack tickets offline        │
       │     (with Hashcat)               │
       │                                  │
       │  5. Password: "ServicePass123!"  │
       │                                  │
```

**Attack Flow:**
```
1. Attacker identifies service accounts with SPNs
2. Attacker requests Kerberos service tickets
3. Tickets are encrypted with service account password
4. Attacker cracks tickets offline to get passwords
5. Attacker uses cracked passwords for access
```

**Why It Works:**
- Service accounts often have weak passwords
- Tickets can be requested by any domain user
- Cracking happens offline (no failed login attempts)

**Tools Used:**
- **BloodHound** - Find Kerberoastable users
- **GetUserSPNs.py** - Request service tickets
- **Hashcat** - Crack tickets

**Commands:**
```bash
# Find Kerberoastable users in BloodHound
# Run "Find Kerberoastable Users" query

# Request service tickets
GetUserSPNs.py -dc-ip 192.168.138.136 MARVEL/fcastle

# Crack tickets with Hashcat
hashcat -m 13100 tickets.txt /usr/share/wordlists/rockyou.txt
```

### 2. AS-REP Roasting

**How It Works:**

Attackers target users without Kerberos pre-authentication to obtain crackable tickets.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │     KDC     │
│             │                    │             │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Find users without           │
       │     pre-authentication           │
       │<─────────────────────────────────│
       │                                  │
       │  2. Request AS-REP message       │
       │     (no password needed)         │
       │─────────────────────────────────>│
       │                                  │
       │  3. Receive encrypted data       │
       │<─────────────────────────────────│
       │                                  │
       │  4. Crack encrypted data         │
       │     (with Hashcat)               │
       │                                  │
       │  5. Password: "UserPass123!"     │
       │                                  │
```

**Attack Flow:**
```
1. Attacker identifies users without pre-authentication
2. Attacker requests AS-REP message (no password needed)
3. Response contains encrypted data crackable offline
4. Attacker cracks the encrypted data
5. Attacker obtains user password
```

**Why It Works:**
- Some users have pre-authentication disabled (for compatibility)
- AS-REP messages can be requested without credentials
- Encrypted data can be cracked offline

**Tools Used:**
- **BloodHound** - Find AS-REP roastable users
- **Rubeus.exe** - Request AS-REP messages
- **Hashcat** - Crack AS-REP data

**Commands:**
```bash
# Find AS-REP roastable users in BloodHound
# Run "Find AS-REP Roastable Users" query

# Request AS-REP messages
Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt

# Crack with Hashcat
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

### 3. Golden Ticket

**How It Works:**

Attackers create a forged Kerberos TGT using the KRBTGT account hash.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │     KDC     │
│             │                    │             │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Compromise Domain Controller │
       │<─────────────────────────────────│
       │                                  │
       │  2. Extract KRBTGT hash          │
       │     8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 │
       │                                  │
       │  3. Create forged TGT            │
       │     for administrator            │
       │                                  │
       │  4. Use forged TGT               │
       │─────────────────────────────────>│
       │                                  │
       │  5. Access any service           │
       │<─────────────────────────────────│
       │     as administrator             │
       │                                  │
```

**Attack Flow:**
```
1. Attacker compromises Domain Controller
2. Attacker extracts KRBTGT account hash (NTLM hash)
3. Attacker creates forged TGT for any user
4. Attacker uses forged TGT to access any service
5. Attacker has full domain control
```

**Why It Works:**
- KRBTGT account signs all TGTs
- Its hash never changes
- Forged tickets are accepted as valid

**Tools Used:**
- **Mimikatz** - Extract KRBTGT hash
- **Mimikatz** - Create golden ticket

**Commands:**
```bash
# Extract KRBTGT hash
mimikatz "lsadump::lsa /inject" "exit"

# Create golden ticket
mimikatz "kerberos::golden /user:administrator /domain:marvel.local /sid:S-1-5-21-1234567890-1234567890-1234567890 /krbtgt:8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2 /ticket:ticket.kirbi" "exit"

# Use golden ticket
mimikatz "kerberos::ptt ticket.kirbi" "exit"
```

### 4. Silver Ticket

**How It Works:**

Attackers create a forged service ticket using a service account hash.

**Attack Flow Visual Scheme:**

```
┌─────────────┐                    ┌─────────────┐
│   Attacker  │                    │   Service   │
│             │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Compromise service account   │
       │     (SQLService)                 │
       │<─────────────────────────────────│
       │                                  │
       │  2. Extract service account hash │
       │     3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a │
       │                                  │
       │  3. Create forged service ticket │
       │     for CIFS service             │
       │                                  │
       │  4. Use forged ticket            │
       │─────────────────────────────────>│
       │                                  │
       │  5. Access CIFS service          │
       │<─────────────────────────────────│
       │     as administrator             │
       │                                  │
```

**Attack Flow:**
```
1. Attacker compromises service account
2. Attacker extracts service account hash
3. Attacker creates forged service ticket
4. Attacker accesses specific service
5. Attacker has limited access (only to that service)
```

**Difference from Golden Ticket:**
- Golden ticket = Full domain access (KRBTGT hash)
- Silver ticket = Service-specific access (service account hash)

**Tools Used:**
- **Mimikatz** - Create silver ticket

**Commands:**
```bash
# Create silver ticket for CIFS service
mimikatz "kerberos::golden /user:administrator /domain:marvel.local /sid:S-1-5-21-1234567890-1234567890-1234567890 /target:fileserver.marvel.local /service:cifs /rc4:3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a /ticket:ticket.kirbi" "exit"

# Use silver ticket
mimikatz "kerberos::ptt ticket.kirbi" "exit"
```

---

## Defenses Against NTLM and Kerberos Attacks

### NTLM Defenses

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Disable LLMNR** | Prevent LLMNR poisoning attacks | Group Policy: Turn off Multicast Name Resolution |
| **Enable SMB Signing** | Prevent SMB relay attacks | Group Policy: Microsoft network client/server: Digitally sign communications |
| **Disable NTLM** | Force Kerberos authentication | Group Policy: Network security: Restrict NTLM |
| **Strong Passwords** | Make hash cracking harder | Password policy: Complexity, length, expiration |
| **Account Tiering** | Limit lateral movement | Separate admin and user accounts |

### Kerberos Defenses

| Defense | Description | Implementation |
|---------|-------------|----------------|
| **Strong Service Account Passwords** | Prevent Kerberoasting | Use long, complex passwords for service accounts |
| **Managed Service Accounts** | Automatic password management | Use gMSA or sMSA for service accounts |
| **Enable Pre-authentication** | Prevent AS-REP roasting | Ensure all users require pre-authentication |
| **Protect KRBTGT** | Prevent golden ticket attacks | Monitor KRBTGT account, never share its password |
| **Kerberos Armoring** | Additional ticket protection | Enable FAST (Flexible Authentication Secure Tunneling) |
| **Regular Ticket Auditing** | Detect suspicious ticket requests | Monitor for unusual Kerberos activity |

---

## Summary: Key Points

### NTLM
- Older challenge-response protocol
- Vulnerable to hash capture and relay attacks
- Used as fallback when Kerberos unavailable
- Main attacks: LLMNR poisoning, Pass-the-Hash, SMB Relay

### Kerberos
- Modern ticket-based protocol
- More secure than NTLM
- Default in Active Directory
- Main attacks: Kerberoasting, AS-REP roasting, Golden/Silver tickets

### Ethical Hacking Context
- Understanding these protocols helps identify vulnerabilities
- Attacks are used to test security controls
- Findings should be used to improve security
- Always get proper authorization before testing