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
