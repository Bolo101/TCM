# Domain Enumeration Tools – Complete Beginner's Guide

## Introduction: What is Domain Enumeration?

**Domain enumeration** is like taking a detailed inventory of an Active Directory environment. Imagine you're exploring a large office building - you'd want to know:
- Who works there (users)
- What departments exist (groups)
- What computers and equipment are available (computers)
- Who has access to what (permissions)
- How everything is organized (structure)

In Active Directory, domain enumeration does exactly this - it gathers information about all the objects, relationships, and configurations in a Windows domain.

**Why Do We Need Domain Enumeration?**

| Purpose | Real-World Analogy |
|---------|-------------------|
| **Security Assessment** | Like a security guard checking all doors and windows |
| **Troubleshooting** | Like a manager understanding the organization chart |
| **Compliance** | Like an auditor checking that rules are followed |
| **Attack Path Discovery** | Like finding which keys open which doors |

---

## Tool 1: ldapdomaindump

### What is ldapdomaindump?

**ldapdomaindump** is a simple tool that extracts information from Active Directory and creates readable reports. Think of it as a **digital camera** that takes snapshots of your Active Directory and saves them as files you can review.

**How It Works:**

```
Your Computer → ldapdomaindump → Domain Controller → Data Files
```

1. **Connection**: ldapdomaindump connects to the Domain Controller using LDAP (Lightweight Directory Access Protocol)
2. **Query**: It asks the Domain Controller for information about users, groups, and computers
3. **Collection**: The Domain Controller sends back the requested data
4. **Export**: ldapdomaindump saves this data in various file formats

### What Does LDAP Mean?

**LDAP** (Lightweight Directory Access Protocol) is the language computers use to talk to Active Directory. It's like a **standardized questionnaire** that all directory services understand.

**Real-World Analogy:**
- LDAP is like a **library catalog system**
- The Domain Controller is the **librarian**
- ldapdomaindump is someone asking the librarian for a list of all books

### How to Use ldapdomaindump

**Step 1: Prepare Your Workspace**

```bash
# Create a folder to store your results
mkdir marvel.local
cd marvel.local
```

**Step 2: Run the Tool**

```bash
sudo ldapdomaindump ldaps://192.168.138.136 -u 'MARVEL\fcastle' -p Password1
```

**Breaking Down the Command:**

| Part | What It Means | Simple Explanation |
|------|---------------|-------------------|
| `sudo` | Run as administrator | Gives the tool permission to run |
| `ldapdomaindump` | The tool name | The program we're using |
| `ldaps://192.168.138.136` | Target address | The Domain Controller's address (secure connection) |
| `-u 'MARVEL\fcastle'` | Username | The account we're using to connect |
| `-p Password1` | Password | The password for that account |

**What is LDAPS?**

**LDAPS** is LDAP over SSL (Secure Sockets Layer). It's like sending your LDAP questions in a **sealed envelope** instead of a postcard - it encrypts the connection so no one can snoop on your data.

### What Files Does ldapdomaindump Create?

After running ldapdomaindump, you'll find several files in your folder:

| File Name | What It Contains | Why It's Useful |
|-----------|------------------|-----------------|
| `domain_users.html` | List of all users in a web page format | Easy to read in a browser |
| `domain_groups.html` | List of all groups in a web page format | See who belongs to what groups |
| `domain_computers.html` | List of all computers in a web page format | Inventory of all machines |
| `domain_users.json` | User data in computer-readable format | For scripts and other tools |
| `domain_groups.json` | Group data in computer-readable format | For automated analysis |
| `domain_computers.json` | Computer data in computer-readable format | For processing by other tools |
| `domain_users.csv` | User data in spreadsheet format | Open in Excel for analysis |
| `domain_groups.csv` | Group data in spreadsheet format | Create reports and charts |
| `domain_computers.csv` | Computer data in spreadsheet format | Track computer inventory |

### When Should You Use ldapdomaindump?

| Situation | Why Use ldapdomaindump |
|-----------|------------------------|
| **Quick overview** | Fast way to see what's in your domain |
| **Documentation** | Create reports for management |
| **Auditing** | Check who has access to what |
| **Troubleshooting** | Find user or computer information |
| **Migration planning** | Understand your AD structure before changes |

### Pros and Cons

| Advantages | Disadvantages |
|------------|---------------|
| ✅ Very easy to use | ❌ No visual relationship mapping |
| ✅ Creates multiple file formats | ❌ Limited analysis capabilities |
| ✅ No database required | ❌ Doesn't show attack paths |
| ✅ Fast and lightweight | ❌ Less comprehensive than other tools |

---

## Tool 2: BloodHound

### What is BloodHound?

**BloodHound** is a powerful tool that maps relationships in Active Directory and helps you understand how different objects are connected. Think of it as a **GPS navigation system** for Active Directory - it shows you the routes from one place to another.

**The Key Concept: Graph Theory**

BloodHound uses **graph theory**, which is a way of representing relationships as:
- **Nodes** (dots): Objects like users, computers, groups
- **Edges** (lines): Relationships between objects

**Real-World Analogy:**
- Think of a **family tree**
- People are the **nodes**
- Family relationships are the **edges**
- BloodHound helps you trace how you're related to everyone else

### How BloodHound Works

```
Active Directory → Data Collection → BloodHound Database → Visual Analysis
```

1. **Data Collection**: Special tools gather information from Active Directory
2. **Storage**: Data is stored in a graph database (Neo4j)
3. **Analysis**: BloodHound analyzes relationships and finds paths
4. **Visualization**: Shows you the results as interactive graphs

### What is Neo4j?

**Neo4j** is a **graph database** - a special type of database designed to store and query connected data. Unlike traditional databases that store data in tables (like Excel), Neo4j stores data as nodes and relationships.

**Traditional Database vs Graph Database:**

| Traditional Database (Excel) | Graph Database (Neo4j) |
|------------------------------|------------------------|
| Data in rows and columns | Data as nodes and edges |
| Good for lists | Good for relationships |
| Hard to see connections | Easy to trace paths |
| Example: Phone book | Example: Social network |

### Setting Up BloodHound

**Step 1: Install BloodHound**

```bash
sudo pip install bloodhound
```

**Step 2: Install Neo4j (The Database)**

```bash
# Install Neo4j
sudo apt install neo4j

# Start Neo4j
sudo neo4j console
```

**What Happens When You Start Neo4j?**

Neo4j starts a web interface you can access in your browser:
- **URL**: `http://localhost:7474`
- **Default Login**: `neo4j` / `neo4j`
- **First Login**: You'll be asked to create a new password

**Step 3: Launch BloodHound**

```bash
sudo bloodhound
```

This opens the BloodHound application window.

### Collecting Data with BloodHound Ingesters

**What are Ingesters?**

**Ingesters** are like **data collectors** - they go to Active Directory, gather information, and bring it back to BloodHound. Think of them as **research assistants** who collect information for you.

**The New BloodHound Approach:**

Modern versions of BloodHound include built-in ingester tools, making data collection easier than ever.

**How to Collect Data:**

**Step 1: Create a Working Folder**

```bash
mkdir bloodhound
cd bloodhound
```

**Step 2: Run the Ingester**

```bash
sudo bloodhound-python -d MARVEL.local -u fcastle -p Password1 -ns 192.168.138.136 -c all
```

**Breaking Down the Command:**

| Part | What It Means | Simple Explanation |
|------|---------------|-------------------|
| `bloodhound-python` | The ingester tool | The data collection program |
| `-d MARVEL.local` | Domain name | Which domain to collect from |
| `-u fcastle` | Username | Account to use for connection |
| `-p Password1` | Password | Password for the account |
| `-ns 192.168.138.136` | Name server | The Domain Controller's IP address |
| `-c all` | Collection options | Collect everything available |

**What Does "-c all" Mean?**

The `-c` parameter tells the ingester what to collect. Options include:

| Option | What It Collects |
|--------|------------------|
| `all` | Everything (recommended for full analysis) |
| `Session` | Where users are currently logged in |
| `Computer` | Information about computers |
| `Group` | Group memberships |
| `Trusts` | Trust relationships between domains |
| `ACL` | Permissions and access rights |
| `ObjectProps` | Detailed properties of objects |

### What Data Gets Collected?

The ingester gathers comprehensive information:

| Data Type | What It Includes | Why It's Important |
|-----------|------------------|-------------------|
| **Users** | All user accounts, their attributes, and properties | Know who has access |
| **Groups** | All groups and who belongs to them | Understand permissions |
| **Computers** | All computers and their configurations | Inventory and attack surface |
| **Sessions** | Where users are currently logged in | Find active targets |
| **Trusts** | Relationships between domains | Identify lateral movement paths |
| **ACLs** | Who has permission to do what | Find privilege escalation opportunities |
| **GPOs** | Group Policy Objects | Understand security settings |
| **SPNs** | Service Principal Names | Find Kerberoasting targets |

### Uploading Data to BloodHound

**Step 1: Open BloodHound**

Launch the BloodHound application (it should open automatically when you run `sudo bloodhound`).

**Step 2: Connect to Neo4j**

1. BloodHound will ask for Neo4j credentials
2. Enter the username and password you created when setting up Neo4j
3. Click "Connect"

**Step 3: Upload Your Data**

1. In BloodHound, click "Upload Data" (usually on the right side)
2. Navigate to your bloodhound folder
3. Select all the JSON files created by the ingester
4. Click "Upload"

**What Happens During Upload?**

BloodHound reads all the data files and:
- Creates nodes for each object (users, computers, groups)
- Creates edges for each relationship (member of, admin on, etc.)
- Builds a complete graph of your Active Directory

### Using BloodHound's Interface

**Main Views in BloodHound:**

| View | What It Shows | When to Use It |
|------|---------------|----------------|
| **Node Info** | Details about a selected object | When you click on something |
| **Graph** | Visual map of relationships | To see connections |
| **Analysis** | Pre-built queries and checks | To find common issues |
| **Queries** | Custom search queries | For specific investigations |

### Understanding BloodHound Analysis

**What is the Analysis Tab?**

The Analysis tab contains **pre-built investigations** that help you find common security issues and attack paths. Think of them as **security checklists** that run automatically.

**Common Analysis Queries:**

| Query Name | What It Finds | Why It's Important |
|------------|---------------|-------------------|
| **Find All Domain Admins** | Lists all users with Domain Admin rights | Know who has the most power |
| **Shortest Path to Domain Admins** | Shows quickest route to become a Domain Admin | Find attack paths |
| **Find Principals with DCSync Rights** | Users who can copy the entire AD database | Critical security risk |
| **Find Unconstrained Delegation** | Computers that can impersonate any user | Serious vulnerability |
| **Find AS-REP Roastable Users** | Users vulnerable to password attacks | Weak configuration |
| **Find Kerberoastable Users** | Service accounts that can be attacked | Common attack vector |

### Example: Finding Attack Paths

**Scenario:** You're a regular user and want to find a path to become a Domain Admin.

**Step 1: Select "Shortest Path to Domain Admins"**

**Step 2: Choose Your Starting User**

Select your user account (e.g., "fcastle")

**Step 3: Review the Path**

BloodHound might show something like this:

```
fcastle (Regular User)
    ↓ MemberOf
IT Staff Group
    ↓ LocalAdminOn
WORKSTATION01
    ↓ HasSession
tstark (Domain Admin)
    ↓ MemberOf
Domain Admins Group
```

**What This Path Means:**

1. **fcastle** is a member of the **IT Staff Group**
2. The **IT Staff Group** has local admin rights on **WORKSTATION01**
3. **tstark** (a Domain Admin) is currently logged into **WORKSTATION01**
4. If you can get admin access to WORKSTATION01, you can steal tstark's credentials
5. With tstark's credentials, you become a Domain Admin

**Real-World Impact:**

This path shows that a regular user can potentially become a Domain Admin by:
1. Exploiting their local admin rights on a workstation
2. Finding where a Domain Admin is logged in
3. Stealing the Domain Admin's credentials
4. Using those credentials to access everything

### Advanced BloodHound Features

**Finding Active Sessions:**

1. Click on a Domain Admin user
2. Look for "HasSession" edges in the graph
3. These show which computers the admin is currently using
4. Target those computers for credential dumping

**What is Credential Dumping?**

**Credential dumping** is extracting stored passwords or hashes from a computer. It's like finding a hidden key under a doormat.

**Kerberoasting Opportunities:**

1. Run "Find Kerberoastable Users" query
2. BloodHound shows service accounts with SPNs
3. These accounts often have weak passwords
4. You can request Kerberos tickets and crack them offline

**What is Kerberoasting?**

**Kerberoasting** is an attack where you:
1. Request a Kerberos ticket for a service account
2. Extract the encrypted ticket
3. Try to crack the encryption to get the password
4. Use the password to access the service

### When Should You Use BloodHound?

| Situation | Why Use BloodHound |
|-----------|-------------------|
| **Red teaming** | Find attack paths and vulnerabilities |
| **Security assessment** | Understand your AD security posture |
| **Incident response** | Trace how an attacker moved through your network |
| **Privilege audit** | Find excessive permissions |
| **Compliance** | Document who has access to what |

### Pros and Cons

| Advantages | Disadvantages |
|------------|---------------|
| ✅ Visual representation of relationships | ❌ Requires setup (Neo4j) |
| ✅ Finds attack paths automatically | ❌ Steeper learning curve |
| ✅ Powerful analysis capabilities | ❌ Requires more resources |
| ✅ Industry-standard tool | ❌ Can be overwhelming for beginners |

---

## Tool 3: PlumHound

### What is PlumHound?

**PlumHound** is like a **report generator** for BloodHound. While BloodHound shows you the data visually, PlumHound runs automated checks and creates written reports. Think of it as a **security auditor** that reviews your BloodHound data and writes up findings.

**How It Works:**

```
BloodHound Data → PlumHound Analysis → Automated Reports
```

1. **Input**: PlumHound reads data from BloodHound's database
2. **Analysis**: It runs predefined checks and queries
3. **Output**: It generates reports in various formats

### Installing PlumHound

**Step 1: Download PlumHound**

```bash
# Go to the tools directory
cd /opt

# Download PlumHound from GitHub
git clone https://github.com/PlumHound/PlumHound.git

# Go into the PlumHound directory
cd PlumHound
```

**Step 2: Install Required Components**

```bash
# Install Python dependencies
sudo pip3 install -r requirements.txt
```

**What is requirements.txt?**

This file lists all the Python packages PlumHound needs to work. Installing them is like making sure you have all the ingredients before cooking.

### Using PlumHound

**Prerequisites:**

Before running PlumHound, make sure:
- ✅ Neo4j is running
- ✅ BloodHound is running
- ✅ Data has been collected and uploaded to BloodHound

**Method 1: Easy Mode (Recommended for Beginners)**

```bash
sudo python3 PlumHound.py --easy -p neo4j_password
```

**What is Easy Mode?**

Easy mode runs a standard set of security checks and generates a comprehensive report. It's perfect for:
- Quick security assessments
- Regular health checks
- Getting started with PlumHound

**Method 2: Custom Task Mode**

```bash
sudo python3 PlumHound.py -x tasks/default.tasks -p neo4j_password
```

**Breaking Down the Command:**

| Part | What It Means | Simple Explanation |
|------|---------------|-------------------|
| `python3 PlumHound.py` | Run PlumHound | Start the program |
| `-x tasks/default.tasks` | Use specific task file | Which checks to run |
| `-p neo4j_password` | Neo4j password | Database password |

### Understanding Task Files

**What are Task Files?**

Task files are like **checklists** for PlumHound. They tell PlumHound what checks to perform and what questions to ask about your BloodHound data.

**Example Task File:**

```yaml
# tasks/default.tasks

- name: "Find Domain Admins"
  description: "List all users with Domain Admin privileges"
  query: "MATCH (u:User)-[r:MemberOf*]->(g:Group) WHERE g.name CONTAINS 'DOMAIN ADMINS' RETURN u"

- name: "Find Unconstrained Delegation"
  description: "Find computers with unconstrained delegation enabled"
  query: "MATCH (c:Computer {unconstraineddelegation:true}) RETURN c"

- name: "Find Kerberoastable Users"
  description: "Identify service accounts vulnerable to Kerberoasting"
  query: "MATCH (u:User) WHERE u.hasspn=true RETURN u"
```

**What This Task File Does:**

1. **Find Domain Admins**: Searches for all users who are Domain Admins
2. **Find Unconstrained Delegation**: Looks for computers that can impersonate users
3. **Find Kerberoastable Users**: Finds service accounts that can be attacked

### What Reports Does PlumHound Generate?

PlumHound can create reports in different formats:

| Format | Best For | Example Use |
|--------|----------|-------------|
| **HTML** | Reading in a browser | Share with management |
| **JSON** | Processing by other tools | Import into other systems |
| **CSV** | Opening in Excel | Create charts and graphs |
| **Markdown** | Documentation | Include in technical reports |

### When Should You Use PlumHound?

| Situation | Why Use PlumHound |
|-----------|-------------------|
| **Regular security reviews** | Automated reporting on a schedule |
| **Management reports** | Easy-to-read summaries for non-technical staff |
| **Compliance documentation** | Written evidence of security checks |
| **Large environments** | Process lots of data automatically |
| **Consistency** | Run the same checks every time |

### Pros and Cons

| Advantages | Disadvantages |
|------------|---------------|
| ✅ Automated reporting | ❌ Requires BloodHound and Neo4j |
| ✅ Multiple output formats | ❌ Depends on BloodHound data quality |
| ✅ Customizable tasks | ❌ Less visual than BloodHound |
| ✅ Saves time | ❌ Requires Python knowledge for customization |

---

## Tool 4: PingCastle

### What is PingCastle?

**PingCastle** is a **health check tool** for Active Directory. While BloodHound focuses on attack paths, PingCastle focuses on overall domain health and configuration. Think of it as a **doctor's checkup** for your Active Directory.

**How It Works:**

```
Active Directory → PingCastle Analysis → Health Report with Scores
```

1. **Examination**: PingCastle checks various aspects of your AD
2. **Scoring**: It gives scores for different areas
3. **Recommendations**: It suggests improvements

### Key Difference: PingCastle vs BloodHound

| Aspect | PingCastle | BloodHound |
|--------|------------|------------|
| **Focus** | Health and configuration | Attack paths and relationships |
| **Output** | Scores and recommendations | Visual graphs and maps |
| **Primary Use** | Health checks and compliance | Red teaming and security testing |
| **Ease of Use** | Very easy | Moderate |
| **Target Audience** | Administrators and auditors | Penetration testers and red teams |

**Real-World Analogy:**
- **PingCastle** is like a **car mechanic** checking if your car is safe to drive
- **BloodHound** is like a **GPS navigator** showing you the best route to your destination

### Using PingCastle

**Method 1: Run on a Windows Machine (Recommended)**

PingCastle is designed to run on Windows computers within the domain.

```powershell
# Open PowerShell as Administrator
# Navigate to where PingCastle.exe is located
cd C:\Tools\PingCastle

# Run the health check
.\PingCastle.exe --healthcheck
```

**What Happens:**

1. PingCastle connects to the Domain Controller
2. It runs various health checks
3. It generates an HTML report with scores and recommendations

**Method 2: Run Remotely from Linux**

You can also run PingCastle from Kali Linux:

```bash
pingcastle --healthcheck --server 192.168.138.136 --user MARVEL\\fcastle --password Password1
```

**Breaking Down the Command:**

| Part | What It Means | Simple Explanation |
|------|---------------|-------------------|
| `pingcastle` | The tool name | The program we're running |
| `--healthcheck` | What to do | Run a health check scan |
| `--server 192.168.138.136` | Target server | The Domain Controller IP |
| `--user MARVEL\\fcastle` | Username | Account to use (note the double backslash) |
| `--password Password1` | Password | Password for the account |

### What Does PingCastle Check?

PingCastle examines many aspects of your Active Directory:

| Category | What It Checks | Why It Matters |
|----------|----------------|----------------|
| **Privileged Accounts** | Number of admins, their activity | Too many admins = higher risk |
| **Trust Relationships** | Domain and forest trusts | Trusts can be attack vectors |
| **Password Policies** | Password rules and expiration | Weak passwords = easy to crack |
| **Group Policies** | GPO configurations | Misconfigured GPOs = security issues |
| **Organizational Structure** | OU layout and delegation | Poor organization = management problems |
| **Security Controls** | Enabled security features | Missing controls = vulnerabilities |
| **Compliance** | Alignment with best practices | Compliance = legal and regulatory requirements |

### Understanding PingCastle Scores

**Score Interpretation:**

| Score Range | Meaning | Action Required |
|-------------|---------|-----------------|
| **90-100** | Excellent | Maintain current practices |
| **75-89** | Good | Address medium-priority issues |
| **60-74** | Fair | Address high-priority issues |
| **Below 60** | Poor | Immediate action required |

**What Affects Your Score:**

- Security configurations (enabled/disabled features)
- Number of privileged accounts
- Password policies
- Trust relationships
- Organizational structure
- Compliance with best practices

### When Should You Use PingCastle?

| Situation | Why Use PingCastle |
|-----------|-------------------|
| **Regular health checks** | Monitor AD health over time |
| **Before/after changes** | See impact of configuration changes |
| **Compliance audits** | Document security posture |
| **Mergers and acquisitions** | Assess new domains |
| **Management reports** | Easy-to-understand scores |

### Pros and Cons

| Advantages | Disadvantages |
|------------|---------------|
| ✅ Very easy to use | ❌ Less detailed than BloodHound |
| ✅ Clear scoring system | ❌ Doesn't show attack paths |
| ✅ Actionable recommendations | ❌ Windows-focused (though Linux version exists) |
| ✅ Great for management reports | ❌ Limited customization |

---

## Comparison: Which Tool Should You Use?

### Quick Reference Guide

| Tool | Best For | Skill Level | Time Required |
|------|----------|-------------|---------------|
| **ldapdomaindump** | Quick overview and documentation | Beginner | 5-10 minutes |
| **BloodHound** | Deep analysis and attack path discovery | Intermediate | 30-60 minutes |
| **PlumHound** | Automated reporting on BloodHound data | Intermediate | 10-20 minutes |
| **PingCastle** | Health checks and scoring | Beginner | 10-15 minutes |

### Scenario-Based Recommendations

**Scenario 1: Quick Overview of Your Domain**

```
Use: ldapdomaindump
Why: Fast, easy, gives you immediate results
Time: 5-10 minutes
```

**Scenario 2: Understanding Attack Paths**

```
Use: BloodHound
Why: Shows relationships and potential attack routes
Time: 30-60 minutes (including setup)
```

**Scenario 3: Regular Security Reports**

```
Use: PlumHound (after BloodHound)
Why: Automated, consistent, professional reports
Time: 10-20 minutes
```

**Scenario 4: Health Assessment**

```
Use: PingCastle
Why: Quick scoring, clear recommendations
Time: 10-15 minutes
```

**Scenario 5: Comprehensive Security Assessment**

```
Use: All tools in sequence
1. ldapdomaindump (quick overview)
2. BloodHound (deep analysis)
3. PlumHound (automated reporting)
4. PingCastle (health check)

Time: 1-2 hours total
```

---

## Key Technical Terms Glossary

### Basic Terms

| Term | Simple Definition | Real-World Analogy |
|------|-------------------|-------------------|
| **Active Directory** | Microsoft's directory service | A phone book for Windows networks |
| **Domain** | A logical group of network resources | A department in a company |
| **Domain Controller** | Server that manages AD | The manager of the phone book |
| **Enumeration** | Gathering information about a system | Taking inventory |
| **LDAP** | Protocol for accessing directory services | Language for talking to AD |
| **LDAPS** | Secure LDAP | LDAP in a sealed envelope |

### BloodHound-Specific Terms

| Term | Simple Definition | Real-World Analogy |
|------|-------------------|-------------------|
| **Node** | An object in AD (user, computer, group) | A person in a family tree |
| **Edge** | A relationship between objects | A family relationship line |
| **Graph** | Visual representation of nodes and edges | A family tree diagram |
| **Attack Path** | Route from low to high privilege | Path from employee to CEO |
| **Neo4j** | Graph database used by BloodHound | A filing system designed for relationships |
| **Ingesters** | Tools that collect AD data | Research assistants gathering information |

### Security Terms

| Term | Simple Definition | Real-World Analogy |
|------|-------------------|-------------------|
| **Domain Admin** | User with full control over domain | Company CEO |
| **Enterprise Admin** | User with control over entire forest | CEO of parent company |
| **DCSync** | Attack that copies AD database | Copying the entire phone book |
| **Kerberoasting** | Attack against service accounts | Picking locks on service doors |
| **Unconstrained Delegation** | Feature allowing impersonation | Giving someone your ID card |
| **AS-REP Roasting** | Attack against weak authentication | Finding doors that don't require keys |
| **SPN** | Service Principal Name | Name tag for a service |
| **ACL** | Access Control List | List of who can do what |
| **GPO** | Group Policy Object | Company policy document |

---

## Summary: Complete Domain Enumeration Workflow

### Step-by-Step Process

**Phase 1: Preparation (5 minutes)**

```bash
# Create workspace
mkdir domain_enum
cd domain_enum

# Create subfolders for each tool
mkdir ldapdomaindump
mkdir bloodhound
mkdir plumhound
mkdir pingcastle
```

**Phase 2: Quick Overview with ldapdomaindump (5-10 minutes)**

```bash
cd ldapdomaindump
sudo ldapdomaindump ldaps://192.168.138.136 -u 'MARVEL\fcastle' -p Password1

# Review the HTML files in your browser
# Get a quick understanding of your domain
```

**Phase 3: Deep Analysis with BloodHound (30-60 minutes)**

```bash
# Start Neo4j (if not already running)
sudo neo4j console

# In another terminal, start BloodHound
sudo bloodhound

# In another terminal, collect data
cd ../bloodhound
sudo bloodhound-python -d MARVEL.local -u fcastle -p Password1 -ns 192.168.138.136 -c all

# Upload data to BloodHound GUI
# Run analysis queries to find attack paths
```

**Phase 4: Automated Reporting with PlumHound (10-20 minutes)**

```bash
cd /opt/PlumHound
sudo python3 PlumHound.py --easy -p neo4j_password

# Review the generated reports
# Share findings with your team
```

**Phase 5: Health Check with PingCastle (10-15 minutes)**

```bash
# On a Windows machine in the domain
.\PingCastle.exe --healthcheck

# Or from Linux
pingcastle --healthcheck --server 192.168.138.136 --user MARVEL\\fcastle --password Password1

# Review scores and recommendations
```

**Phase 6: Analysis and Reporting (30-60 minutes)**

1. **Compile Findings**: Combine results from all tools
2. **Prioritize Issues**: Rank findings by risk level
3. **Create Recommendations**: Develop action plans
4. **Generate Reports**: Create summaries for different audiences
5. **Plan Remediation**: Schedule fixes and improvements

### What You'll Learn

By using all these tools together, you'll understand:

| Aspect | What You'll Know |
|--------|------------------|
| **Users** | Who has access, what they can do |
| **Computers** | What machines exist, their configurations |
| **Groups** | How permissions are organized |
| **Relationships** | How everything connects |
| **Attack Paths** | How someone could compromise your domain |
| **Health Score** | Overall security posture |
| **Risks** | Specific vulnerabilities and issues |
| **Recommendations** | What to fix and how to prioritize |

---

## Important Security Notes

⚠️ **WARNING:** Domain enumeration is a powerful technique that can be used for both good and bad purposes.

**Ethical Guidelines:**

✅ **DO:**
- Only enumerate domains you own or have permission to test
- Use findings to improve security
- Protect collected data appropriately
- Follow responsible disclosure if you find vulnerabilities
- Document everything for legal and compliance purposes

❌ **DON'T:**
- Enumerate domains without authorization
- Use enumeration results for malicious purposes
- Share sensitive information with unauthorized parties
- Exploit vulnerabilities you discover without permission
- Ignore legal and ethical boundaries

**Legal Considerations:**

- Always get written permission before testing
- Understand laws in your jurisdiction
- Follow company policies and procedures
- Consider using contracts or agreements
- Keep records of authorization

---

## Conclusion


- **ldapdomaindump**: Quick and simple overview
- **BloodHound**: Deep analysis and attack path discovery
- **PlumHound**: Automated reporting and documentation
- **PingCastle**: Health checks and scoring
