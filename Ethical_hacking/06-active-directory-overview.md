## Active Directory – beginner-friendly fiche

### What Active Directory is

Active Directory (AD) is Microsoft’s identity and directory service for Windows networks.  
You can think of it as a central “phone book + rules engine” that stores who people are, what machines exist, and what they are allowed to do.

Key points:
- Stores information about objects: users, computers, groups, printers, shared folders, etc.  
- Used mainly on internal corporate networks for **authentication** (who are you?) and **authorization** (what are you allowed to do?).  
- It is the most widely used identity system in enterprise Windows environments, so most internal pentests end up focusing on AD abuse rather than classic “remote exploits”.

### How authentication works (high level)

On Windows machines joined to a domain, AD typically uses **Kerberos** for authentication.

Very simplified flow:
1. A user logs into a domain-joined machine with `DOMAIN\username` and a password.  
2. The machine talks to a Domain Controller (DC) and gets a **Kerberos ticket** proving “this user is who they say they are”.  
3. When the user accesses a resource (file share, web app, printer), the ticket is presented to that resource.  
4. The resource trusts the Domain Controller and uses the ticket to decide whether to allow access.

Non-Windows systems (Linux, network devices, Wi‑Fi controllers, VPNs, etc.) can also authenticate against AD via:
- **LDAP/LDAPS** (directory protocol)  
- **RADIUS** (common for VPN and Wi‑Fi)  

As a pentester, many AD attacks are about:
- Stealing or forging Kerberos tickets (Pass-the-Ticket, Golden Ticket, etc.).  
- Abusing misconfigurations in groups, ACLs, and “features” (not zero-days, but design/ops issues).

***

## Physical components

These are the actual servers and files that make AD work.

### Domain Controllers (DCs)

A Domain Controller is a Windows Server that runs the Active Directory Domain Services (AD DS) role.

What a DC does:
- **Hosts a copy of the AD database** (directory store).  
- **Provides authentication and authorization** for domain users and computers.  
- **Replicates changes** (new users, password changes, group updates) to other DCs in the same domain and forest.  
- **Exposes management interfaces** for admins to create users, groups, policies, and manage resources.

For a pentester:
- Compromising a Domain Controller usually means **owning the entire domain**.  
- The DC is where hashes, Kerberos keys, and key configuration live (e.g. `ntds.dit`).

### AD DS data store

This is the actual database and supporting processes.

- The main database file: **`ntds.dit`**.  
- It stores:
  - User and computer accounts.  
  - Password hashes and Kerberos keys.  
  - Group memberships, group policies, and more.

If an attacker extracts `ntds.dit` plus the right system keys, they can offline-crack or directly abuse domain credentials.

***

## Logical components

These are the “conceptual” building blocks that describe how objects are organized and how trust works.

### AD DS Schema

- The **schema** defines all object types and attributes that can exist in AD.  
- Example: it defines that a *user* has attributes like `sAMAccountName`, `userPrincipalName`, `memberOf`, etc.  
- Extensible: installing some applications (e.g. Exchange) can extend the schema with new object types and attributes.

For a beginner: think of the schema like a database schema that defines the tables and columns you are allowed to use.

### Domains

- A **domain** is the core administrative unit in AD.  
- It groups and manages objects (users, computers, groups) under a common **namespace** (e.g. `corp.local`, `example.com`).  
- It is an **administrative boundary**:
  - Policies (GPOs) can be applied at domain level.  
  - Domain Admins have strong power inside that domain.

From a pentest point of view:
- Getting **Domain Admin** in one domain gives you control over that domain’s users and computers.  
- There can be multiple domains in a company (e.g. `corp.local`, `eu.corp.local`, etc.).

### Trees

- A **tree** is a hierarchy of one or more domains in a parent–child structure.  
- Example:
  - Parent: `corp.local`  
  - Child: `europe.corp.local`  
  - Child: `asia.corp.local`  

All domains in a tree share a contiguous namespace.

### Forests

- A **forest** is the top-level security boundary that contains one or more domain trees.  
- All domains in a forest:
  - Share the same **schema**.  
  - Share common configuration data.  
  - Share a **Global Catalog**, which allows users to search for objects across domains.  
  - Have **trusts** that allow authentication between domains inside the forest.  
  - Share high-privilege groups like **Enterprise Admins** and **Schema Admins**.

For security:
- Forest is the **ultimate trust boundary**. If you compromise Enterprise Admins or a forest-level trust, you effectively own everything in the forest.

### Organizational Units (OUs)

- OUs are containers inside a domain used to organize objects (users, groups, computers).  
- Example OUs: `HR`, `IT`, `Servers`, `Workstations`, `Service Accounts`.  
- You can:
  - Delegate administration (e.g. let helpdesk manage only users in `Helpdesk OU`).  
  - Apply **Group Policy Objects (GPOs)** at OU level to configure security settings, software deployment, scripts, etc.

As an attacker:
- OUs and GPOs can be abused:
  - If you can edit a GPO applied to many machines, you can deploy malicious scripts or settings.  
  - Misconfigured delegation on OUs can let low-privileged accounts change high-value settings.

### Trusts

**Trusts** define how authentication and authorization works between domains and forests.

Key ideas:
- **Directional**:
  - Domain A trusts Domain B: users from B can access resources in A (depending on permissions).  
- **Transitive**:
  - Trusts can extend through chains of domains (e.g. trust between forests can allow paths across many domains).

In practice:
- Inside a forest, domains generally have transitive trusts.  
- Between forests, there might be specifically configured forest trusts.

For pentesting:
- Trusts explain how compromising “small” or “peripheral” domains/forests may lead to access in more critical ones.  
- Many AD attack paths are “follow the trust” from low-value domain to high-value domain.

### Objects

In AD, **everything you care about is an object**:
- Users (employees, service accounts).  
- Computers (servers, workstations, domain controllers).  
- Groups (security groups used for access control).  
- Printers, shared folders, group policy objects, etc.

Each object:
- Has attributes (e.g. username, description, group memberships).  
- Is stored in a domain, inside a specific OU or container.

As an attacker, you are often:
- Listing objects and their relationships.  
- Looking for misconfigurations (users in dangerous groups, computers allowing unconstrained delegation, etc.).  
- Leveraging those relationships to move laterally and escalate privileges.
