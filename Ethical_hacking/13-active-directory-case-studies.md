## AD Case Study 1

Cannot use MITM as IPv6 is disables, password are uncrackable.
But we can relay passwords, dump hashes, find password reuse, relay again
Try connecting using hash, on smbexec.py for example

## AD Case Study 2

No relaying, no MITm6, no cracking
Look for active services and browse the web for default credentials
Get access, ry getting administrative password if avaailable in clear, then crackmapexec on it
Try Wdigest on older version of Windows < Windows 8 & Windows 2012

## AD Case Study 3

Intercept hashes circulating on the network, try to crack them.
Account got an access to a public share, cotnaining a procedure to a Macbook set up, containing hardcoded credentials
try connecting using smb and the provided credentials an you got an admin access, then secretsdump
