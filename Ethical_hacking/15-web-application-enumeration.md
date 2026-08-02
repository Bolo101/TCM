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