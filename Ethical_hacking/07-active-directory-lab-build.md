# Ethical Hacking Lab Setup Guide

## Overview
This guide walks you through setting up a complete Windows-based ethical hacking lab environment. You'll create a domain controller, client machines, users, and configure policies to simulate a real corporate network for security testing.

---

## Prerequisites
- Virtualization software (VMware, VirtualBox, or Hyper-V)
- Administrative access to your host machine
- Internet connection for downloading ISOs
- Minimum 16GB RAM on host machine (8GB for DC, 4GB per client recommended)

---

## Part 1: Downloading Necessary ISOs

### Microsoft Evaluation Center
**URL:** https://www.microsoft.com/fr-fr/evalcenter

### Required Downloads
1. **Windows Server** (latest version available)
   - Choose the evaluation edition (typically 180 days)
   - Select the appropriate language and architecture (x64)

2. **Windows Client** (Windows 10 or 11 Enterprise)
   - Download the Enterprise evaluation edition
   - This will serve as your client machines

**Technical Terms:**
- **ISO:** An ISO file is an exact copy of an optical disc (CD/DVD) in digital format. It contains all the files and filesystem structure needed to install an operating system.
- **Evaluation Edition:** A time-limited version of software (usually 180 days) that allows you to test all features before purchasing.

---

## Part 2: Setting Up the Domain Controller

### What is a Domain Controller?
A **Domain Controller (DC)** is a server that responds to security authentication requests within a Windows Server domain. It's the central authority that manages user authentication, security policies, and directory services for all computers in the network.

### Step 1: Create Virtual Machine
1. Create a new VM in your virtualization software
2. **Disk Configuration:**
   - Allocate **60 GB** of disk space
   - Choose to **split the disk into multiple files** (recommended for better performance and easier management)
3. Mount the Windows Server ISO and start the VM

### Step 2: Windows Server Installation
1. Follow the standard installation wizard
2. **Critical Selection:** Choose **"Desktop Experience"** when prompted
   - **Why?** This installs the full graphical interface (GUI). Without it, you'd only have command-line access, which is difficult for beginners.

**Technical Terms:**
- **GUI (Graphical User Interface):** A visual way to interact with the computer using windows, icons, and menus, as opposed to command-line interfaces.

### Step 3: Initial Configuration
1. **Rename the Computer:**
   - Go to **Settings > System > Rename this PC**
   - Choose a descriptive name (e.g., `DC01` or `MARVEL-DC`)
   - **Why?** Clear naming helps identify machines in your network

2. **Set a Static IP Address:**
   - Go to **Settings > Network & Internet > Change adapter options**
   - Right-click your network adapter > Properties
   - Select **Internet Protocol Version 4 (TCP/IPv4)** > Properties
   - Configure:
     - IP Address: `192.168.1.10` (or similar)
     - Subnet Mask: `255.255.255.0`
     - Default Gateway: `192.168.1.1` (your router)
     - Preferred DNS: `192.168.1.10` (the DC itself)

**Technical Terms:**
- **Static IP:** A fixed IP address that doesn't change, essential for servers so clients can always find them.
- **Subnet Mask:** Defines which portion of the IP address identifies the network and which identifies the host.
- **DNS (Domain Name System):** Translates domain names (like `google.com`) to IP addresses.

### Step 4: Install Active Directory Domain Services
1. Open **Server Manager** (should open automatically)
2. Click **Add roles and features**
3. Click **Next** through the wizard until you reach **Server Roles**
4. Select **Active Directory Domain Services (AD DS)**
5. Click **Add Features** when prompted
6. Complete the wizard and click **Install**

**What is Active Directory?**
**Active Directory (AD)** is Microsoft's directory service that stores information about objects on the network (users, computers, printers) and makes this information available to users and administrators. It's the backbone of Windows network authentication and authorization.

### Step 5: Promote Server to Domain Controller
1. After installation completes, click the **Promote this server to a domain controller** flag
2. **Deployment Configuration:**
   - Select **Add a new forest**
   - **Root domain name:** Enter your domain (e.g., `MARVEL.local`)
   - **Why `.local`?** This is a reserved top-level domain for internal networks, preventing conflicts with public internet domains.

3. **Domain Controller Options:**
   - Set a **DSRM (Directory Services Restore Mode) password** - keep this safe!
   - This password is used to recover AD if it becomes corrupted

4. **DNS Options:**
   - DNS should be automatically selected
   - **Why DNS?** AD requires DNS to function - it uses DNS to locate domain controllers and services

5. **Additional Options:**
   - **NetBIOS domain name:** Automatically generated (e.g., `MARVEL`)
   - **NetBIOS** is an older naming system still used for backward compatibility

6. **Paths:** Accept defaults or customize if needed
7. **Review Options:** Verify your settings
8. **Prerequisites Check:** Ensure all checks pass
9. **Install:** The server will restart automatically

**Technical Terms:**
- **Forest:** The highest level of organization in AD. A forest contains one or more domains.
- **Domain:** A logical group of network objects (computers, users, devices) that share the same AD database.
- **NetBIOS:** A legacy naming service that allows computers to identify each other on a local network.

### Step 6: Install Additional Roles
1. **File and Storage Services:**
   - Open **Server Manager > Add roles and features**
   - Select **File and Storage Services** (may already be installed)
   - This allows the DC to act as a file server

2. **Active Directory Certificate Services (AD CS):**
   - **Manage > Add Roles and Features**
   - Select **Active Directory Certificate Services**
   - **Role Services:** Select all options
   - **Create a new private key** if none exists
   - **What is this?** AD CS issues and manages digital certificates used for encryption, authentication, and secure communication.

---

## Part 3: Setting Up User Machines (Clients)

### What are Client Machines?
**Client machines** are regular computers that users work on. They connect to the domain controller for authentication, access to resources, and to receive security policies.

### Step 1: Create Virtual Machine
1. Create a new VM for each client
2. **Recommended Specs:**
   - Disk: 40 GB (can be split into files)
   - RAM: 4 GB minimum
3. Mount the Windows Client ISO

### Step 2: Windows Installation
1. Follow standard installation steps
2. When prompted for edition, choose **Windows Enterprise** (if available)

### Step 3: Initial Configuration
1. **Rename the Computer:**
   - **Settings > System > Rename this PC**
   - Use descriptive names (e.g., `CLIENT01`, `CLIENT02`)

2. **Set Static IP Address:**
   - Follow the same process as the DC
   - Use IPs in the same range (e.g., `192.168.1.20`, `192.168.1.21`)
   - **Critical:** Set the DNS server to the DC's IP (`192.168.1.10`)
   - **Why?** Clients need to know where the DC is to join the domain

---

## Part 4: Setting Up Users, Groups, and Policies

### Understanding Organizational Units (OUs)
An **Organizational Unit (OU)** is a container within Active Directory that can hold users, groups, computers, and other OUs. OUs allow you to organize objects logically and apply Group Policies to specific sets of objects.

### Step 1: Organize Active Directory Structure
1. On the DC, open **Server Manager > Tools > Active Directory Users and Computers**
2. Expand your domain (e.g., `MARVEL.local`)
3. You'll see default containers:
   - **Built-in:** Default groups
   - **Computers:** Domain-joined computers
   - **Domain Controllers:** Your DC(s)
   - **Users:** Default users and groups

### Step 2: Create Custom OUs
1. Right-click on your domain name > **New > Organizational Unit**
2. Name it `Groups` (or any logical name)
3. Click **OK**
4. Move all groups from the `Users` container to your new `Groups` OU
   - **Exception:** Keep `Guest` and `Administrator` in the default location
   - **Why?** Better organization and easier management

### Step 3: Create Users
1. Right-click on your domain or an OU > **New > User**
2. Fill in user details:
   - **First name, Last name, User logon name**
   - Example: `Tony Stark` with username `tstark`
3. Set a password (make it complex for realism)
4. Choose password options:
   - **User must change password at next logon** (recommended for real environments)
   - **Password never expires** (convenient for labs)
5. Create additional users as needed

### Step 4: Create Groups
1. Right-click on your `Groups` OU > **New > Group**
2. **Group name:** e.g., `IT Admins`, `Developers`, `Regular Users`
3. **Group scope:** Global (for most cases)
4. **Group type:** Security
5. Add users to groups by double-clicking the group > **Members > Add**

**Technical Terms:**
- **Security Group:** Used to assign permissions and rights to resources.
- **Distribution Group:** Used only for email distribution (not relevant for our lab).

### Step 5: Create a Network Share
1. On the DC, open **Server Manager > File and Storage Services > Shares**
2. Click **Tasks > New Share**
3. Select **SMB Share - Quick**
4. **Share location:** Choose a folder or type a path
5. **Share name:** `hackme` (or any name)
6. **Configure share settings:**
   - Enable **Allow caching of share** (for offline access)
7. Set permissions as needed

**What is SMB?**
**SMB (Server Message Block)** is a protocol that allows applications to read and write to files and request services from server programs in a computer network. It's the standard file sharing protocol in Windows.

### Step 6: Configure Service Principal Names (SPNs)
1. Open **Command Prompt** as Administrator
2. Run the following command:
   ```
   setspn -a DC_NAME/SQLService.DOMAIN_NAME.local:60111 DOMAIN\SQLService
   ```
   - Replace `DC_NAME` with your DC's name
   - Replace `DOMAIN_NAME` with your domain name
   - Example: `setspn -a MARVEL-DC/SQLService.MARVEL.local:60111 MARVEL\SQLService`

**What is an SPN?**
A **Service Principal Name (SPN)** is a unique identifier for a service instance. SPNs are used by Kerberos authentication to associate a service instance with a service login account. This is crucial for certain hacking techniques like Kerberoasting.

### Step 7: Create and Apply Group Policies

#### What is Group Policy?
**Group Policy** is a feature of Windows that allows you to control the working environment of user and computer accounts. It provides centralized management and configuration of operating systems, applications, and user settings.

#### Create a Group Policy Object (GPO)
1. Open **Group Policy Management** (Server Manager > Tools)
2. Expand your domain > Right-click on it > **Create a GPO in this domain, and Link it here**
3. Name it: `Disable Windows Defender`
4. Click **OK**

#### Configure the GPO
1. Right-click on your new GPO > **Edit**
2. Navigate to: **Computer Configuration > Policies > Administrative Templates > Windows Components > Microsoft Defender Antivirus**
3. Find **Turn off Microsoft Defender Antivirus**
4. Double-click it > Select **Enabled** > Click **Apply** > **OK**
5. Close the Group Policy Management Editor

#### Enforce the GPO
1. In Group Policy Management, right-click your GPO
2. Select **Enforced** (check the box)
3. **Why?** This ensures the policy applies even if other GPOs conflict

**Why disable Windows Defender in a lab?**
In an ethical hacking lab, you want to simulate a vulnerable environment. Disabling antivirus allows you to test malware, exploits, and attack techniques without interference. **Never do this in production!**

---

## Part 5: Joining Machines to the Domain

### What is Domain Joining?
**Domain joining** is the process of connecting a computer to a Windows domain. Once joined, the computer authenticates users against the domain controller and receives domain policies.

### Step 1: Prepare Client Network Settings
Ensure each client has:
- IP address in the same range as the DC (e.g., `192.168.1.20`)
- Subnet mask: `255.255.255.0`
- DNS server set to the DC's IP (`192.168.1.10`)

### Step 2: Join the Domain
1. On the client machine, open **Settings**
2. Go to **Accounts > Access work or school**
3. Click **Connect**
4. Select **Join this device to a local Active Directory domain**
5. Enter your domain name (e.g., `MARVEL.local`)
6. Enter domain administrator credentials when prompted
7. The computer will restart

### Step 3: Verify Domain Join
1. On the DC, open **Active Directory Users and Computers**
2. Expand your domain > Click on the **Computers** container
3. You should see your client machine listed there

### Step 4: Configure Local Administrator
1. On the client, open **Computer Management** (right-click Start > Computer Management)
2. Navigate to **Local Users and Groups > Users**
3. Right-click **Administrator** > **Set Password**
4. Set a strong password
5. Right-click **Administrator** > **Properties**
6. Check **Account is disabled** > **OK**
7. **Why?** Disabling the local admin forces users to use domain accounts, which is more secure and realistic.

### Step 5: Add Domain Administrators to Local Admin Group
1. Still in **Computer Management**, go to **Groups**
2. Double-click **Administrators**
3. Click **Add**
4. Type your domain admin group name (e.g., `Domain Admins`)
5. Click **Check Names** > **OK**
6. This allows domain admins to have local admin rights on all machines

### Step 6: Map Network Drives (Manual Method)
1. On the client, open **File Explorer**
2. Click **This PC** > **Map network drive**
3. Choose a drive letter (e.g., `Z:`)
4. Folder: `\\DC_NAME\hackme` (replace with your DC name and share name)
5. Check **Reconnect at sign-in**
6. Click **Finish**

This manual method works fine for small labs, but for larger environments or more consistency, use Group Policy instead (see below).

---

## Part 6: Map Network Drives via Group Policy (Alternative Method)

You can automatically map network drives for all users using Group Policy. This is more efficient for large networks and ensures consistency across all machines.

### What is Group Policy Drive Mapping?

**Group Policy Drive Mapping** allows administrators to automatically assign network drive letters to users or computers. When users log in, the drives are automatically mapped without any manual intervention.

### Step 1: Open Group Policy Management
1. On the Domain Controller, open **Group Policy Management**
2. Navigate to your domain (e.g., `MARVEL.local`)

### Step 2: Create or Edit a GPO
1. Right-click on your domain > **Create a GPO in this domain, and Link it here**
2. Name it: `Map Network Drives`
3. Click **OK**

### Step 3: Configure Drive Mapping
1. Right-click on your new GPO > **Edit**
2. Navigate to: **User Configuration > Preferences > Windows Settings > Drive Maps**
3. Right-click in the right panel > **New > Mapped Drive**

### Step 4: Configure the Drive
In the **New Drive Properties** window:

1. **Action:** Select **Create** (creates new mapping) or **Replace** (replaces existing)
2. **Location:** Type the UNC path to your share
   - Example: `\\MARVEL-DC\hackme`
   - **UNC Path:** A Universal Naming Convention path identifies network resources. Format: `\\ServerName\ShareName`
3. **Drive Letter:** Choose a letter (e.g., `Z:`)
4. **Label:** Give it a friendly name (e.g., `Hacking Lab Share`)
5. **Reconnect:** Check **Reconnect** (this ensures the drive persists after logoff)
6. **Hide/Show this drive:** Choose whether users can see the drive
7. **Drive Letter First:** If you have multiple drives, this determines the order

### Step 5: Set Permissions (Optional)
1. Click the **Common** tab
2. **Item-level targeting:** Click **Targeting...** to specify which users get this drive
   - Example: Only members of "IT Admins" group get the Z: drive
   - This allows different users to have different drive mappings
3. Click **OK** when done

### Step 6: Apply and Test
1. Click **Apply** > **OK** to close the drive properties
2. Close the Group Policy Management Editor
3. In Group Policy Management, right-click your GPO and select **Enforced**
4. On a client machine, run `gpupdate /force` in Command Prompt (as Administrator)
5. Log off and log back on
6. Open **File Explorer** - you should see the mapped drive automatically!

### Advantages of GPO Drive Mapping
- **Centralized Management:** Change one GPO, affects all users
- **Consistency:** Everyone gets the same drives
- **Targeting:** Different drives for different users/groups
- **Automatic:** No user intervention required
- **Scalable:** Works for 10 users or 10,000 users

### Troubleshooting GPO Drive Mapping
- **Drive not appearing?** Run `gpupdate /force` and log off/on again
- **Access denied?** Check share permissions and NTFS permissions on the DC
- **Wrong drive letter?** Another GPO might be conflicting - use Group Policy Results to check
- **Only some users get it?** Check Item-level targeting settings

### Technical Terms

| Term | Definition |
|------|------------|
| **UNC Path** | Universal Naming Convention - a standard way to identify network resources |
| **Item-level Targeting** | A feature that allows you to apply GPO settings only to specific users, groups, or computers |
| **gpupdate /force** | Command that forces the computer to immediately apply all Group Policy settings |

---

## Summary of Your Lab Environment

After completing this guide, you'll have:

| Component | Purpose | Example Name |
|-----------|---------|--------------|
| Domain Controller | Central authentication server | MARVEL-DC |
| Domain | Network identity | MARVEL.local |
| Client Machines | User workstations | CLIENT01, CLIENT02 |
| Users | Domain user accounts | tstark, nbanner |
| Groups | Organized user collections | IT Admins, Developers |
| Network Share | Shared file storage | \\MARVEL-DC\hackme |
| Group Policies | Centralized configuration | Disable Windows Defender, Map Network Drives |

---

## Key Technical Terms Glossary

| Term | Definition |
|------|------------|
| **Active Directory (AD)** | Microsoft's directory service for managing network resources |
| **Domain Controller (DC)** | Server that authenticates users and enforces security policies |
| **Organizational Unit (OU)** | Container in AD for organizing objects |
| **Group Policy** | System for managing configuration settings across Windows computers |
| **DNS** | System that translates domain names to IP addresses |
| **SMB** | Protocol for file and printer sharing in Windows |
| **SPN** | Unique identifier for service instances in Kerberos authentication |
| **Static IP** | Fixed IP address that doesn't change |
| **ISO** | Digital copy of an optical disc for software installation |
| **GUI** | Graphical User Interface - visual way to interact with computers |
| **NetBIOS** | Legacy naming system for network identification |
| **Forest** | Highest level container in AD, can contain multiple domains |
| **Kerberos** | Network authentication protocol used by Windows domains |
| **UNC Path** | Universal Naming Convention - standard way to identify network resources |
| **Item-level Targeting** | Feature to apply GPO settings to specific users/groups/computers |
