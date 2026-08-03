## Assetfinder

From tomnomnom

Follow install from Github page

Use :
assetfinder tesla.com // can also detect subdomain related to Tesla or owned by Tesla but not containing tesla.com

Subdomain only :
assetfinder --subs-only tesla.com // but better to get all results then remove unrelated domains

```bash
#!/bin/bash

url=$1

if [ ! -d "$url" ];then
    mkdir $url
fi

if [ ! -d "$url/recon"];then
    mkdir $url/recon
fi

echo "Harvesting using assetfinder..."
assetfinder $url >> $url/recon/assets.txt
cat $url/recon/assets.txt | grep $1 >> $url.recon/final.txt
rm $url/recon/assets.txt
```

## Amass

Follow install instructions from Github page to set up Go

amass enum -d tesla.com

```bash
#!/bin/bash

url=$1

if [ ! -d "$url" ];then
    mkdir $url
fi

if [ ! -d "$url/recon"];then
    mkdir $url/recon
fi

echo "Harvesting subdomains using assetfinder..."
assetfinder $url >> $url/recon/assets.txt
cat $url/recon/assets.txt | grep $1 >> $url.recon/final.txt
rm $url/recon/assets.txt

echo "Harvesting subdomains with Amass
amass enum -d $url >> ûrl/recon/f.txt
sort -u $url/recon.f.txt >> $url/recon.final.txt
rm $url/recon/f.txt
```

## Finding Alive Domains with Httprobe

httprobe from Tomnomnom on Github
Ensure if the host returned from assetfinder or amass are alive

cat tesla.com/recon/final.txt | httprobe -s -p https:443 | sed 's/https\?:\/\///' | tr -d ':443'
-s : remove all default ports
-p : specify port

```bash
#!/bin/bash

url=$1

if [ ! -d "$url" ];then
    mkdir $url
fi

if [ ! -d "$url/recon"];then
    mkdir $url/recon
fi

echo "Harvesting subdomains using assetfinder..."
assetfinder $url >> $url/recon/assets.txt
cat $url/recon/assets.txt | grep $1 >> $url.recon/final.txt
rm $url/recon/assets.txt

echo "Harvesting subdomains with Amass
amass enum -d $url >> ûrl/recon/f.txt
sort -u $url/recon.f.txt >> $url/recon.final.txt
rm $url/recon/f.txt

echo "Probing for alive domains"
cat $url/recon/final.txt | httprobe -s -p https:443 | sed 's/https\?:\/\///' | tr -d ':443' >> $url/recon/alive.txt
```

## Gowitness

Follow instal from Sensepost Github repo

First :
go get -u gorm.io/gorm
Follow rest of instructions

gowitness single https://tesla.com //screenshots folder appears in running directory