## Overview

Active Directory (AD) is Microsoft's identity and directory service for Windows networks. Think of it as a central **"phone book + rules engine"** that stores who people are, what machines exist, and what they are allowed to do.

### Why Active Directory Matters

**Key Points:**
- **Stores information about objects:** users, computers, groups, printers, shared folders, etc.
- **Used for two main purposes:**
  - **Authentication** (who are you?) - verifying identity
  - **Authorization** (what are you allowed to do?) - granting permissions
- **Most widely used identity system** in enterprise Windows environments
- **Primary target in internal penetration testing** - most attacks focus on AD abuse rather than traditional remote exploits

---

## How Authentication Works (High-Level Overview)

### The Authentication Process

On Windows machines joined to a domain, AD typically uses **Kerberos** for authentication. Here's the simplified flow:

**Step-by-Step Process:**

1. **User Login**
   - A user logs into a domain-joined machine with `DOMAIN\username` and a password
   - Example: `MARVEL\tstark` with password `P@ssw0rd123`

2. **Ticket Request**
   - The machine contacts a **Domain Controller (DC)**
   - The DC verifies the credentials and issues a **Kerberos ticket**
   - This ticket proves "this user is who they say they are"

3. **Resource Access**
   - When the user accesses a resource (file share, web app, printer)
   - The ticket is presented to that resource
   - The resource trusts the Domain Controller and uses the ticket to decide access

4. **Authorization Decision**
   - The resource checks the ticket against its permissions
   - Access is granted or denied based on the user's rights

### Non-Windows Authentication

Non-Windows systems can also authenticate against AD through different protocols:

| Protocol | Purpose | Common Use Cases |
|----------|---------|------------------|
| **LDAP/LDAPS** | Directory protocol | Linux systems, applications |
| **RADIUS** | Authentication protocol | VPNs, Wi‑Fi controllers, network devices |

### From a Pentester's Perspective

Many AD attacks focus on:
- **Stealing or forging Kerberos tickets** (Pass-the-Ticket, Golden Ticket, etc.)
- **Abusing misconfigurations** in groups, ACLs, and "features"
- **Note:** These are typically design/operations issues, not zero-day vulnerabilities

---

## Physical Components

These are the actual servers and files that make AD work in the real world.

### Domain Controllers (DCs)

**What is a Domain Controller?**

A **Domain Controller (DC)** is a Windows Server that runs the **Active Directory Domain Services (AD DS)** role. It's the brain of your Windows network.

**What a DC Does:**

| Function | Description |
|----------|-------------|
| **Hosts AD Database** | Maintains a copy of the directory store (ntds.dit) |
| **Authentication** | Verifies user identities when they log in |
| **Authorization** | Enforces security policies and permissions |
| **Replication** | Syncs changes to other DCs in the domain/forest |
| **Management Interface** | Provides tools for admins to manage AD objects |

**For a Pentester:**
- **Compromising a DC = owning the entire domain**
- The DC contains:
  - Password hashes
  - Kerberos keys
  - Critical configuration files (e.g., `ntds.dit`)
  - All user and computer accounts

**Technical Terms:**
- **AD DS (Active Directory Domain Services):** The Windows Server role that enables AD functionality
- **Replication:** The process of copying AD data between multiple DCs to ensure consistency
- **ntds.dit:** The main database file that stores all AD information

### AD DS Data Store

**What is the AD DS Data Store?**

This is the actual database and supporting processes that store all Active Directory information.

**Key Components:**

| Component | Description |
|-----------|-------------|
| **ntds.dit** | The main database file containing all AD objects |
| **SYSVOL** | A shared folder that stores Group Policy templates and scripts |
| **Log files** | Transaction logs that track changes to the database |

**What ntds.dit Stores:**
- User and computer accounts
- Password hashes (NTLM, Kerberos keys)
- Group memberships
- Group policies
- Security descriptors (permissions)

**Security Implications:**
- If an attacker extracts `ntds.dit` plus the system keys, they can:
  - Offline-crack passwords
  - Directly abuse domain credentials
  - Create golden tickets for persistent access

---

## Logical Components

These are the "conceptual" building blocks that describe how objects are organized and how trust relationships work.

### AD DS Schema

**What is the Schema?**

The **schema** is like a blueprint that defines all object types and attributes that can exist in Active Directory.

**How It Works:**
- Defines what properties each object type can have
- Example: A *user* object has attributes like:
  - `sAMAccountName` (login name)
  - `userPrincipalName` (email-style login)
  - `memberOf` (group memberships)
  - `displayName` (full name)

**Analogy for Beginners:**
Think of the schema like a **database schema** that defines the tables and columns you're allowed to use. Just as a database schema defines what data can be stored, the AD schema defines what objects can exist and what properties they can have.

**Extensibility:**
- The schema can be extended by applications
- Example: Installing Microsoft Exchange adds new object types and attributes
- Schema extensions are permanent and cannot be easily removed

**Technical Terms:**
- **Attribute:** A property of an object (e.g., username, email address)
- **Object Class:** The type of object (e.g., user, computer, group)
- **Schema Master:** The DC responsible for schema changes (there's only one per forest)

### Domains

**What is a Domain?**

A **domain** is the core administrative unit in Active Directory. It's a logical grouping of network objects that share a common directory database.

**Key Characteristics:**

| Characteristic | Description |
|----------------|-------------|
| **Namespace** | All objects share a common naming structure (e.g., `corp.local`) |
| **Administrative Boundary** | Policies and admins are scoped to the domain |
| **Security Boundary** | Domain Admins have control only within their domain |
| **Authentication Scope** | Users authenticate against domain controllers |

**Example Domains:**
- `corp.local` - Main corporate domain
- `eu.corp.local` - European subsidiary domain
- `dev.corp.local` - Development environment domain

**From a Pentester's Perspective:**
- Getting **Domain Admin** privileges in one domain gives you control over:
  - All users and computers in that domain
  - All resources and data in that domain
- Multiple domains in a company create attack paths:
  - Compromise a less-secure domain
  - Use trust relationships to access more critical domains

**Technical Terms:**
- **Namespace:** A naming system that ensures all objects have unique names
- **Domain Admins:** A built-in group with full administrative control over the domain
- **Domain Controller:** The server(s) that authenticate users for the domain

### Trees

**What is a Tree?**

A **tree** is a hierarchical structure of one or more domains that share a contiguous namespace.

**Structure:**
- **Parent Domain:** The root domain (e.g., `corp.local`)
- **Child Domains:** Domains under the parent (e.g., `europe.corp.local`, `asia.corp.local`)

**Example Tree Structure:**
```
corp.local (parent)
├── europe.corp.local (child)
│   ├── france.europe.corp.local (grandchild)
│   └── germany.europe.corp.local (grandchild)
└── asia.corp.local (child)
    ├── japan.asia.corp.local (grandchild)
    └── india.asia.corp.local (grandchild)
```

**Key Features:**
- All domains share a **contiguous namespace** (they're connected by dots)
- Automatic **two-way transitive trusts** between parent and child domains
- Shared schema and configuration

**Why Use Trees?**
- Organizational structure (by geography, department, etc.)
- Delegated administration (different admins for different child domains)
- Scalability (distribute load across multiple domains)

**Technical Terms:**
- **Contiguous Namespace:** Domain names that form a continuous hierarchy
- **Parent Domain:** The domain above another in the hierarchy
- **Child Domain:** A domain below another in the hierarchy

### Forests

**What is a Forest?**

A **forest** is the top-level security boundary that contains one or more domain trees. It's the ultimate container for all Active Directory resources.

**What All Domains in a Forest Share:**

| Shared Component | Description |
|------------------|-------------|
| **Schema** | All domains use the same object definitions |
| **Configuration** | Common configuration data across the forest |
| **Global Catalog** | Searchable catalog of all objects in the forest |
| **Trusts** | Authentication paths between all domains |
| **Enterprise Admins** | Forest-level administrators with ultimate power |

**Example Forest Structure:**
```
Forest: example.com
├── Tree 1: example.com
│   ├── corp.example.com
│   └── dev.example.com
└── Tree 2: partner.com
    ├── us.partner.com
    └── eu.partner.com
```

**Security Implications:**
- **Forest is the ultimate trust boundary**
- Compromising **Enterprise Admins** gives you control over:
  - All domains in the forest
  - All trusts to other forests
  - The schema itself
- Forest-level trusts can provide access to completely separate organizations

**Technical Terms:**
- **Global Catalog:** A distributed data repository that contains a searchable, partial representation of every object in every domain in the forest
- **Enterprise Admins:** A built-in group with full control over the entire forest
- **Schema Admins:** A built-in group that can modify the AD schema
- **Forest Trust:** A trust relationship between two forests

### Organizational Units (OUs)

**What are Organizational Units?**

**Organizational Units (OUs)** are containers within a domain used to organize and manage Active Directory objects (users, groups, computers).

**Common OU Examples:**
- `HR` - Human Resources employees
- `IT` - IT department staff and resources
- `Servers` - All server computers
- `Workstations` - All desktop/laptop computers
- `Service Accounts` - Special accounts for running services

**What You Can Do with OUs:**

| Capability | Description |
|------------|-------------|
| **Organization** | Group related objects together |
| **Delegation** | Give specific admins control over only certain OUs |
| **Group Policy** | Apply GPOs at OU level to configure settings |
| **Administration** | Simplify management through logical grouping |

**Example OU Structure:**
```
MARVEL.local (domain)
├── Users
│   ├── Regular Users
│   ├── Service Accounts
│   └── Admins
├── Computers
│   ├── Workstations
│   ├── Servers
│   └── Domain Controllers
└── Departments
    ├── HR
    ├── IT
    └── Finance
```

**From a Pentester's Perspective:**
- **OU and GPO abuse opportunities:**
  - If you can edit a GPO applied to many machines, you can deploy malicious scripts
  - Misconfigured delegation on OUs can let low-privileged accounts change high-value settings
  - Compromising an account with delegation rights can lead to privilege escalation

**Technical Terms:**
- **Delegation:** Assigning administrative control over specific OUs to specific users or groups
- **GPO (Group Policy Object):** A collection of settings that define system behavior
- **Inheritance:** The process by which child OUs receive settings from parent OUs

### Trusts

**What are Trusts?**

**Trusts** define how authentication and authorization works between domains and forests. They're the "bridges" that allow users from one domain to access resources in another.

**Types of Trusts:**

| Characteristic | Description |
|----------------|-------------|
| **Directional** | One-way or two-way authentication |
| **Transitive** | Trusts can extend through chains of domains |
| **Forest Trust** | Trust between two entire forests |
| **External Trust** | Trust between a domain and a domain in another forest |

**Directional Trusts:**

**One-Way Trust:**
- Domain A trusts Domain B
- Users from B can access resources in A
- Users from A cannot access resources in B

**Two-Way Trust:**
- Both domains trust each other
- Users from both domains can access resources in the other

**Transitive Trusts:**
- Trusts can extend through chains
- Example: If A trusts B, and B trusts C, then A can potentially access C
- Most forest trusts are transitive

**Real-World Example:**
```
Forest A (corp.local)
├── Domain A1 (us.corp.local)
└── Domain A2 (eu.corp.local)

Forest B (partner.com)
├── Domain B1 (us.partner.com)
└── Domain B2 (eu.partner.com)

Forest Trust: corp.local ↔ partner.com
```

**From a Pentester's Perspective:**
- **Trusts explain attack paths:**
  - Compromise a low-value domain
  - Follow trust relationships to access high-value domains
  - Many AD attack paths are "follow the trust"
- **Trust abuse techniques:**
  - SID filtering bypass
  - Golden ticket creation across trusts
  - Privilege escalation through trust relationships

**Technical Terms:**
- **Trust Relationship:** A logical connection that allows authentication between domains
- **Transitive Trust:** A trust that extends through intermediate domains
- **SID (Security Identifier):** A unique value that identifies a user, group, or computer
- **SID Filtering:** A security feature that prevents trust abuse

### Objects

**What are Objects?**

In Active Directory, **everything you care about is an object**. Objects are the fundamental building blocks of AD.

**Types of Objects:**

| Object Type | Description | Examples |
|-------------|-------------|----------|
| **Users** | People who need network access | Employees, contractors, service accounts |
| **Computers** | Machines on the network | Servers, workstations, domain controllers |
| **Groups** | Collections of users or computers | Domain Admins, HR Staff, Developers |
| **Printers** | Network printers | HP LaserJet, Canon multifunction |
| **Shared Folders** | File shares | Department shares, public folders |
| **Group Policy Objects** | Configuration settings | Security policies, software deployment |
| **Contacts** | External people | Vendors, partners |

**Object Attributes:**

Every object has **attributes** (properties) that describe it:

**User Object Attributes:**
- `sAMAccountName` - Login name (e.g., `tstark`)
- `userPrincipalName` - Email-style login (e.g., `tstark@marvel.local`)
- `displayName` - Full name (e.g., `Tony Stark`)
- `memberOf` - Groups the user belongs to
- `lastLogon` - Last time the user logged in
- `pwdLastSet` - When the password was last changed

**Computer Object Attributes:**
- `dNSHostName` - Computer's DNS name
- `operatingSystem` - OS version
- `lastLogon` - Last time the computer authenticated
- `servicePrincipalName` - Services running on the computer

**From a Pentester's Perspective:**

**What Attackers Do with Objects:**
1. **Enumeration** - List objects and their relationships
2. **Misconfiguration Hunting** - Look for:
   - Users in dangerous groups (e.g., regular users in Domain Admins)
   - Computers allowing unconstrained delegation
   - Weak permissions on critical objects
3. **Relationship Leveraging** - Use object relationships to:
   - Move laterally between machines
   - Escalate privileges
   - Maintain persistence

**Common Object Misconfigurations:**
- **Kerberoasting:** Service accounts with weak passwords
- **Unconstrained Delegation:** Computers that can impersonate any user
- **AS-REP Roasting:** Users without pre-authentication required
- **Excessive Privileges:** Users with more rights than needed

**Technical Terms:**
- **Attribute:** A property of an object (e.g., username, email)
- **Distinguished Name (DN):** The full path to an object in AD
- **Object Class:** The type of object (user, computer, group, etc.)
- **Security Descriptor:** Defines permissions on an object

---

## Key Technical Terms Glossary

| Term | Definition |
|------|------------|
| **Active Directory (AD)** | Microsoft's directory service for managing network resources |
| **Authentication** | The process of verifying a user's identity |
| **Authorization** | The process of determining what a user is allowed to do |
| **Kerberos** | Network authentication protocol used by Windows domains |
| **Domain Controller (DC)** | Server that authenticates users and enforces security policies |
| **Domain** | Logical group of network objects sharing a common database |
| **Forest** | Top-level container that includes one or more domain trees |
| **Tree** | Hierarchy of domains sharing a contiguous namespace |
| **Organizational Unit (OU)** | Container in AD for organizing objects |
| **Group Policy** | System for managing configuration settings across Windows computers |
| **Trust** | Relationship that allows authentication between domains |
| **Schema** | Definition of object types and attributes in AD |
| **ntds.dit** | The main database file storing all AD information |
| **LDAP** | Protocol for accessing and managing directory services |
| **RADIUS** | Protocol for network authentication (VPN, Wi-Fi) |
| **Global Catalog** | Searchable catalog of all objects in a forest |
| **SID** | Security Identifier - unique value for users, groups, computers |
| **SPN** | Service Principal Name - identifier for service instances |
| **Delegation** | Assigning administrative control to specific users/groups |
| **GPO** | Group Policy Object - collection of configuration settings |

---

## Summary: The Big Picture

Active Directory is a complex but powerful system that serves as the foundation for Windows network security. Understanding its components and relationships is essential for both administrators and penetration testers.

**Key Takeaways:**

1. **AD is central to Windows security** - it handles authentication and authorization
2. **Physical components** (DCs, ntds.dit) store and serve the data
3. **Logical components** (domains, forests, OUs) organize and structure the data
4. **Trusts** connect different parts of the AD infrastructure
5. **Objects** are the actual entities (users, computers, groups) that you interact with
6. **Misconfigurations** in any component can lead to security vulnerabilities

**For Ethical Hacking:**
- Most internal penetration tests focus on AD abuse
- Understanding AD structure helps identify attack paths
- Many attacks exploit misconfigurations rather than software vulnerabilities
- Compromising a DC or Domain Admin typically means game over