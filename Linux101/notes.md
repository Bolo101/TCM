# Guide d'Introduction à Linux pour Ethical Hacking

## Introduction

Linux est l'environnement de prédilection pour le hacking éthique. La maîtrise de la ligne de commande est essentielle pour automatiser des tâches, analyser des fichiers de logs, manipuler du texte, et gérer les systèmes lors d'un pentest. [linuxfrombeginning.wordpress](https://linuxfrombeginning.wordpress.com/2008/09/19/linux/)

***

## Partie 1 : Visualisation de fichiers texte

### 1.1 Less et More - Lecture page par page

**Cas d'usage** : Lire de longs fichiers (logs, résultats de scans) sans surcharger le terminal. [hostafrica](https://www.hostafrica.com/blog/linux/linux-basics-head-tail-cat-and-more-or-less/)

#### Less (recommandé)

```bash
# Ouvrir un fichier avec less
less /var/log/syslog

# Navigation :
# Espace      : Page suivante
# b           : Page précédente  
# g           : Début du fichier
# G           : Fin du fichier
# q           : Quitter

# Recherche dans less
# /pattern    : Chercher "pattern"
# n           : Résultat suivant
# N           : Résultat précédent

# Exemple : chercher "error" dans un log
less /var/log/apache2/error.log
# Puis taper : /error
# Puis : n (next) pour passer aux occurrences suivantes
```

**Fonctionnalités avancées** : Less utilise les mêmes commandes que Vim pour la navigation et la recherche. [linuxfrombeginning.wordpress](https://linuxfrombeginning.wordpress.com/2008/09/19/linux/)

#### More (ancien, moins de fonctionnalités)

```bash
# Ouvrir avec more
more fichier.txt

# Navigation limitée :
# Espace : Page suivante uniquement
# q      : Quitter
```

**Différence clé** : `less` permet de naviguer en avant ET en arrière, `more` seulement en avant. [dev](https://dev.to/amandaigwe/day-19-30-days-of-linux-mastery-file-viewing-commands-cat-less-more-head-tail-4385)

### 1.2 Head - Premières lignes

**Cas d'usage** : Voir rapidement l'en-tête d'un fichier (logs, CSV, résultats). [linuxfoundation](https://www.linuxfoundation.org/blog/blog/classic-sysadmin-14-tail-and-head-commands-in-linux-unix)

```bash
# 10 premières lignes (par défaut)
head fichier.txt

# 5 premières lignes
head -n 5 fichier.txt
# OU
head -5 fichier.txt

# Exemple : voir l'en-tête d'un scan nmap
head -20 scan_results.txt
```

### 1.3 Tail - Dernières lignes

**Cas d'usage** : Analyser les dernières entrées de logs, surveiller des fichiers en temps réel. [devhankering.hashnode](https://devhankering.hashnode.dev/cat-more-less-head-tail-in-linux-operating-system)

```bash
# 10 dernières lignes (par défaut)
tail fichier.txt

# 5 dernières lignes
tail -5 fichier.txt

# Suivre un fichier en temps réel (crucial pour logs)
tail -f /var/log/apache2/access.log

# Résultat : chaque nouvelle ligne ajoutée s'affiche automatiquement
# Ctrl+C pour arrêter
```

**Exemple pentest** : Surveiller les connexions SSH lors d'une attaque par brute force :
```bash
tail -f /var/log/auth.log
# Affiche en temps réel chaque tentative de connexion
```

### 1.4 Diff - Comparaison de fichiers

**Cas d'usage** : Détecter des changements dans des fichiers de configuration, comparer des versions de scripts. [dev](https://dev.to/amandaigwe/day-19-30-days-of-linux-mastery-file-viewing-commands-cat-less-more-head-tail-4385)

```bash
# Comparer deux fichiers
diff fichier1.txt fichier2.txt

# Résultat typique :
# 3c3
# < Cette ligne a changé (version 1)
# ---
# > Cette ligne a changé (version 2)

# Format côte à côte
diff -y fichier1.txt fichier2.txt

# Ignorer les différences de casse
diff -i fichier1.txt fichier2.txt
```

***

## Partie 2 : Gestion des disques et montages

### 2.1 Affichage de l'espace disque

```bash
# Afficher l'espace utilisé sur les partitions montées
df -h

# -h : Human-readable (Go, Mo au lieu d'octets)

# Résultat typique :
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1        50G   20G   28G  42% /
# /dev/sdb1       500G  100G  400G  20% /mnt/data

# Afficher l'espace utilisé par un fichier/dossier
du -sh /home/user/Documents

# -s : Summary (total seulement)
# -h : Human-readable
```

### 2.2 Monter un périphérique (USB, disque externe)

**Cas d'usage** : Accéder à une clé USB contenant des outils de pentest, exfiltrer des données. [ubuntumint](https://www.ubuntumint.com/mount-filesystems-linux/)

#### Étape 1 : Identifier le périphérique

```bash
# Lister toutes les partitions
sudo fdisk -l

# Résultat typique :
# /dev/sda1   *     2048  104857599  ext4   /
# /dev/sdb1        2048   15728639   vfat   (USB non monté)

# Alternative : lsblk
lsblk

# Résultat :
# NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
# sda      8:0    0    50G  0 disk
# └─sda1   8:1    0    50G  0 part /
# sdb      8:16   1   7.5G  0 disk
# └─sdb1   8:17   1   7.5G  0 part
```

#### Étape 2 : Créer un point de montage

```bash
# Créer un répertoire pour monter le périphérique
sudo mkdir /mnt/usb
```

#### Étape 3 : Monter le périphérique

```bash
# Monter /dev/sdb1 vers /mnt/usb
sudo mount /dev/sdb1 /mnt/usb

# Vérifier le montage
df -h | grep usb
# OU
mount | grep usb

# Accéder aux fichiers
cd /mnt/usb
ls -la
```

#### Étape 4 : Démonter

```bash
# Démonter le périphérique
sudo umount /mnt/usb

# ⚠️ Attention : toujours démonter avant de retirer la clé USB
```

### 2.3 Formater une clé USB

**Cas d'usage** : Préparer une clé USB bootable, effacer des traces. [ubuntumint](https://www.ubuntumint.com/mount-filesystems-linux/)

```bash
# 1. Démonter d'abord
sudo umount /dev/sdb1

# 2. Formater en NTFS (compatible Windows)
sudo mkfs.ntfs /dev/sdb1

# 3. Formater en FAT32 (compatible multi-OS)
sudo mkfs.vfat /dev/sdb1

# 4. Formater en ext4 (Linux uniquement)
sudo mkfs.ext4 /dev/sdb1

# ⚠️ Attention : le formatage EFFACE toutes les données
```

### 2.4 Obtenir la taille d'un disque

```bash
# Afficher la taille d'un disque spécifique
lsblk -o SIZE /dev/sda

# Résultat : 50G
```

***

## Partie 3 : Réseau et connectivité

### 3.1 Obtenir son IP publique

```bash
# Via curl
curl ifconfig.me

# Résultat : 203.0.113.45

# Alternatives
curl icanhazip.com
curl ipinfo.io/ip
wget -qO- ifconfig.me
```

**Cas d'usage** : Vérifier votre IP avant de lancer un reverse shell, configurer un serveur C2.

### 3.2 Se connecter à un WiFi (nmcli)

```bash
# Lister les réseaux WiFi disponibles
nmcli device wifi list

# Se connecter à un réseau
nmcli device wifi connect "NomDuSSID" password "MotDePasse"

# Vérifier la connexion
nmcli connection show
```

***

## Partie 4 : Liens (Hard et Soft)

### 4.1 Hard Link (lien physique)

**Concept** : Un hard link pointe directement vers les données physiques sur le disque. Même si le fichier original est supprimé, le hard link permet toujours d'accéder aux données. [ubuntumint](https://www.ubuntumint.com/mount-filesystems-linux/)

```bash
# Créer un hard link
ln fichier.txt fichier_hard_link.txt

# Vérifier avec ls -li
ls -li fichier.txt fichier_hard_link.txt

# Résultat : même inode number (identique physiquement)
# 12345678 -rw-r--r-- 2 user user 1024 May 6 21:00 fichier.txt
# 12345678 -rw-r--r-- 2 user user 1024 May 6 21:00 fichier_hard_link.txt

# Supprimer le fichier original
rm fichier.txt

# Le hard link fonctionne toujours !
cat fichier_hard_link.txt
```

**Limitation** : Impossible de créer un hard link vers un répertoire.

### 4.2 Soft Link / Symlink (lien symbolique)

**Concept** : Un soft link est un raccourci vers le fichier original. Si le fichier original est supprimé, le lien ne fonctionne plus.

```bash
# Créer un soft link
ln -s fichier.txt fichier_soft_link.txt

# Vérifier
ls -l fichier_soft_link.txt

# Résultat : l indique un link
# lrwxrwxrwx 1 user user 11 May 6 21:00 fichier_soft_link.txt -> fichier.txt

# Supprimer le fichier original
rm fichier.txt

# Le soft link est cassé (broken link)
cat fichier_soft_link.txt
# Erreur : No such file or directory
```

**Avantage** : On peut créer des soft links vers des répertoires.

```bash
# Lien vers un répertoire
ln -s /var/log logs_symlink
cd logs_symlink  # Accès direct à /var/log
```

***

## Partie 5 : Recherche de fichiers

### 5.1 Find - Recherche puissante

```bash
# Chercher tous les fichiers commençant par "file" dans le répertoire courant
find . -name 'file*.txt'

# Chercher dans tout le système
find / -name 'passwd' 2>/dev/null

# Chercher par type
find /home -type f -name '*.sh'  # Fichiers
find /home -type d -name 'backup*'  # Répertoires

# Chercher par permission
find / -perm 4000 2>/dev/null  # Fichiers SUID (escalade de privilèges)

# Chercher par taille
find /var/log -size +100M  # Fichiers > 100 Mo

# Chercher et exécuter une commande
find . -name '*.log' -exec rm {} \;  # Supprimer tous les .log
```

**Cas d'usage pentest** : Trouver des fichiers SUID pour escalade de privilèges.

***

## Partie 6 : Permissions et propriétaires

### 6.1 Changer le propriétaire (chown)

```bash
# Changer le propriétaire d'un fichier
sudo chown bob fichier.txt

# Vérifier
ls -l fichier.txt
# -rw-r--r-- 1 bob user 1024 May 6 21:00 fichier.txt

# Changer propriétaire et groupe
sudo chown bob:staff fichier.txt
```

### 6.2 Changer le groupe (chgrp)

```bash
# Changer le groupe
sudo chgrp staff fichier.txt

# Vérifier
ls -l fichier.txt
# -rw-r--r-- 1 bob staff 1024 May 6 21:00 fichier.txt
```

### 6.3 Lire un fichier avec les privilèges d'un autre utilisateur

```bash
# Exécuter une commande en tant qu'un autre utilisateur
sudo -u bob cat /home/bob/private.txt

# Cas d'usage : tester les permissions après une escalade de privilèges
```

### 6.4 Fichiers système importants

```bash
# Utilisateurs et groupes
/etc/passwd   # Liste des utilisateurs
/etc/group    # Liste des groupes
/etc/shadow   # Mots de passe hashés (nécessite root)

# Lire /etc/passwd
cat /etc/passwd

# Format : username:x:UID:GID:comment:home:shell
# root:x:0:0:root:/root:/bin/bash
```

***

## Partie 7 : Redirection et Pipes

### 7.1 Redirection de sortie

```bash
# Rediriger stdout vers un fichier
find / -name "test.txt" > resultats.txt

# Rediriger stderr vers le même fichier
find / -name "test.txt" > resultats.txt 2>&1

# Explication :
# > : Redirige stdout
# 2>&1 : Redirige stderr (2) vers stdout (1)

# Ajouter à un fichier existant (append)
echo "Nouvelle ligne" >> resultats.txt
```

### 7.2 Pipes (|)

**Concept** : Connecter la sortie standard d'une commande à l'entrée standard d'une autre. [news.ycombinator](https://news.ycombinator.com/item?id=34280281)

```bash
# Lister /etc et paginer avec less
ls -l /etc | less

# Rediriger stderr aussi avec |&
find / -name "*.conf" |& less

# Exemples composés
cat /var/log/auth.log | grep "Failed" | wc -l  # Compter échecs SSH
ps aux | grep apache | awk '{print $2}'  # PIDs des processus Apache
```

***

## Partie 8 : Historique de commandes

### 8.1 Réexécuter des commandes

```bash
# Dernière commande
!!
# OU
!-1

# Avant-dernière commande
!-2

# Dernière commande commençant par "ssh"
!ssh

# Afficher l'historique
history

# Exécuter la commande numéro 42 de l'historique
!42
```

***

## Partie 9 : Substitution de commande

**Cas d'usage** : Passer la sortie d'une commande comme argument d'une autre. [docs.vultr](https://docs.vultr.com/how-to-process-text-with-bash-using-grep-sed-and-awk-commands)

```bash
# Problème : ls ne peut pas lire depuis stdin
ls -l < fichiers.txt  # ❌ Ne fonctionne pas

# Solution : Substitution de commande avec backticks
ls -l `cat fichiers.txt`

# OU avec $()
ls -l $(cat fichiers.txt)

# Exemple : Lister les détails de fichiers listés dans register-file.txt
cat register-file.txt
# fichier1.txt
# fichier2.txt
# fichier3.txt

ls -l $(cat register-file.txt)
# -rw-r--r-- 1 user user 1024 May 6 fichier1.txt
# -rw-r--r-- 1 user user 2048 May 6 fichier2.txt
```

***

## Partie 10 : Manipulation de texte

### 10.1 Grep - Recherche de patterns

```bash
# Chercher "bob" dans un fichier
grep bob wordlist.txt

# Inverser la recherche (lignes ne contenant PAS "e")
grep -v e wordlist.txt

# Afficher 3 lignes après le match (-A = After)
grep error -A 3 /var/log/syslog

# Afficher 3 lignes avant le match (-B = Before)
grep error -B 3 /var/log/syslog

# Recherche insensible à la casse
grep -i ERROR log.txt

# Recherche récursive dans tous les fichiers
grep -r "password" /home/user/

# Compter les occurrences
grep -c "Failed" /var/log/auth.log
```

**Cas d'usage pentest**  : [news.ycombinator](https://news.ycombinator.com/item?id=34280281)
```bash
# Trouver des mots de passe hardcodés
grep -r "password" /var/www/html/

# Analyser les tentatives SSH échouées
grep "Failed password" /var/log/auth.log | wc -l
```

### 10.2 Sort - Tri

```bash
# Trier alphabétiquement
sort fichier.txt

# Trier numériquement
sort -n nombres.txt

# Trier en ordre décroissant
sort -r fichier.txt

# Trier numériquement en décroissant
sort -nr nombres.txt
```

### 10.3 Uniq - Supprimer les doublons

**Important** : `uniq` ne supprime que les doublons **adjacents**. Toujours trier d'abord !

```bash
# Supprimer les doublons adjacents
sort fichier.txt | uniq

# Compter les occurrences
sort fichier.txt | uniq -c

# Afficher uniquement les doublons
sort fichier.txt | uniq -d
```

**Exemple pentest** :
```bash
# Compter les IPs les plus fréquentes dans un log
cat access.log | awk '{print $1}' | sort | uniq -c | sort -nr | head -10
```

### 10.4 Wc - Compter lignes, mots, bytes

```bash
# Compter lignes, mots, bytes
wc fichier.txt

# Résultat : 42 256 1024 fichier.txt
# 42 lignes, 256 mots, 1024 bytes

# Seulement les lignes
wc -l fichier.txt

# Exemple : Compter les résultats d'une recherche
grep bob wordlist.txt | wc -l
```

### 10.5 Sed - Éditeur de flux

#### Substitution de texte

```bash
# Remplacer la première occurrence de "Suite" par "Ste"
sed 's/Suite/Ste/' texte.txt

# Remplacer toutes les occurrences (global)
sed 's/Suite/Ste/g' texte.txt

# Remplacer uniquement sur la dernière ligne
sed '$s/Suite/Ste/' texte.txt

# Sauvegarder dans un nouveau fichier
sed 's/Suite/Ste/g' texte.txt > nouveau.txt

# Modifier le fichier en place
sed -i 's/Suite/Ste/g' texte.txt
```

#### Suppression de lignes

```bash
# Supprimer les lignes contenant "Suite"
sed '/Suite/d' texte.txt

# Supprimer les lignes vides
sed '/^$/d' texte.txt
```

#### Substitution conditionnelle

```bash
# Remplacer "Suite" par "Ste" uniquement dans les lignes contenant "ee"
sed '/ee/s/Suite/Ste/g' sample.txt
```

**Cas d'usage pentest**  : [docs.vultr](https://docs.vultr.com/how-to-process-text-with-bash-using-grep-sed-and-awk-commands)
```bash
# Nettoyer les résultats de nmap
sed -n '/open/p' scan.txt  # Garder seulement les ports ouverts

# Extraire les IPs d'un log
sed -n 's/.*from \([0-9.]*\).*/\1/p' auth.log
```

### 10.6 Awk - Traitement de colonnes

```bash
# Afficher la 2ème colonne
echo "linux bob sally" | awk '{print $2}'
# Résultat : bob

# Réarranger les colonnes
echo "linux bob sally" | awk '{print $3, "likes", $1}'
# Résultat : sally likes linux

# Changer le délimiteur (par défaut : espace)
awk -F ',' '{print $1}' sample.txt

# Exemple : Extraire le premier champ d'un CSV
cat users.csv
# bob,30,admin
# alice,25,user

awk -F ',' '{print $1}' users.csv
# bob
# alice
```

**Cas d'usage pentest**  : [news.ycombinator](https://news.ycombinator.com/item?id=34280281)
```bash
# Extraire les IPs des connexions SSH réussies
grep "Accepted" /var/log/auth.log | awk '{print $11}'

# Calculer l'espace disque total utilisé
df -h | awk '{sum += $3} END {print sum}'
```

### 10.7 Tr - Transformer des caractères

```bash
# Remplacer les virgules par des tabulations
cat sample.txt | tr ',' '\t'

# Minuscules en majuscules
cat sample.txt | tr 'a-z' 'A-Z'

# Supprimer les deux-points
echo "192.168.1.1:" | tr -d ':'
# Résultat : 192.168.1.1

# Supprimer plusieurs caractères
echo "hello123" | tr -d '0-9'
# Résultat : hello
```

***

## Partie 11 : Commandes réseau avancées

### 11.1 Dig - Requêtes DNS

```bash
# Lookup DNS basique
dig google.com

# Lookup DNS concis
dig google.com +short

# Reverse DNS (IP → Nom de domaine)
dig -x 8.8.8.8

# Spécifier un serveur DNS
dig @8.8.8.8 google.com
```

### 11.2 Nslookup - Alternative à dig

```bash
# Lookup basique
nslookup google.com

# Reverse DNS
nslookup 8.8.8.8
```

### 11.3 Netstat - Connexions réseau

```bash
# Afficher toutes les connexions TCP
netstat -at

# Afficher les ports TCP en écoute
netstat -lt

# Afficher avec les PIDs
netstat -tlnp

# Exemple : Vérifier qu'Apache écoute sur le port 80
python3 -m http.server 8000 &
netstat -lt | grep 8000
```

***

## Partie 12 : Transfert de fichiers

### 12.1 SCP - Secure Copy

```bash
# Copier un fichier vers une machine distante
scp fichier.txt bob@192.168.1.10:/home/bob/

# Si même username, pas besoin de le spécifier
scp fichier.txt 192.168.1.10:/home/user/

# Copier un répertoire (récursif)
scp -r dossier/ bob@192.168.1.10:/home/bob/

# Copier depuis une machine distante
scp bob@192.168.1.10:/home/bob/fichier.txt ./
```

### 12.2 Rsync - Synchronisation intelligente

**Avantage** : Rsync ne transfère que les différences, pas le fichier complet. [ubuntumint](https://www.ubuntumint.com/mount-filesystems-linux/)

```bash
# Synchroniser un fichier
rsync -avzh fichier.txt bob@192.168.1.12:/home/bob/

# Options :
# -a : Archive mode (récursif, préserve permissions)
# -v : Verbose
# -z : Compression
# -h : Human-readable

# Synchroniser un répertoire
rsync -avzh /var/www/ bob@192.168.1.12:/var/www/

# Dry-run (tester sans exécuter)
rsync -avzhn /var/www/ bob@192.168.1.12:/var/www/

# Exclure des fichiers
rsync -avzh --exclude='*.log' /var/www/ bob@192.168.1.12:/var/www/
```

***

## Partie 13 : Conversion de fichiers (DOS ↔ Unix)

**Contexte** : Les fins de ligne diffèrent entre OS :
- **DOS/Windows** : `\r\n` (Carriage Return + Line Feed)
- **Unix/Linux** : `\n` (Line Feed)
- **Mac (ancien)** : `\r` (Carriage Return)

### 13.1 Vérifier le format

```bash
# Voir le format d'un fichier
file fichier.txt

# Résultat :
# fichier.txt: ASCII text
# OU
# fichier.txt: ASCII text, with CRLF line terminators (DOS)

# Dans Vim, forcer le format Unix
vim fichier.txt
# En mode normal :
:e ++ff=unix
```

### 13.2 Conversion Unix → DOS

```bash
# Convertir en place
unix2dos fichier.txt

# Créer un nouveau fichier converti
unix2dos -n source.txt destination.txt
```

### 13.3 Conversion DOS → Unix

```bash
# Convertir en place
dos2unix fichier.txt

# Créer un nouveau fichier
dos2unix -n source.txt destination.txt
```

### 13.4 Conversion Unix → Mac

```bash
unix2dos -c mac fichier.txt
```

***

## Partie 14 : Éditeur Vim (bases)

### 14.1 Recherche dans Vim

```bash
# Ouvrir un fichier
vim fichier.txt

# En mode Normal, rechercher "error"
/error

# Navigation :
# n : Match suivant
# N : Match précédent

# Recherche inverse
?error
```

### 14.2 Autres commandes utiles

```bash
# Quitter sans sauvegarder
:q!

# Sauvegarder et quitter
:wq

# Aller à la ligne 42
:42
```

***

## Partie 15 : Gestion des processus

### 15.1 Ps - Lister les processus

```bash
# Tous les processus (BSD syntax)
ps -ax | less -S

# -S : Chop lines (ne pas couper les lignes larges)

# Tous les processus (Unix syntax)
ps -e | less -S

# Format complet BSD
ps aux | less -S

# Format complet Unix
ps -ef | less -S

# Colonnes importantes :
# USER : Utilisateur propriétaire
# PID  : Process ID
# PPID : Parent Process ID
# TTY  : Terminal (? = pas de terminal)
# CMD  : Commande exécutée
```

### 15.2 Pstree - Hiérarchie des processus

```bash
# Afficher l'arborescence des processus
pstree | less -S

# Avec PIDs
pstree -p | less -S
```

### 15.3 Top - Monitoring en temps réel

```bash
# Lancer top
top

# Navigation :
# q : Quitter
# k : Kill un processus (entrer PID)
# M : Trier par mémoire
# P : Trier par CPU
# 1 : Afficher tous les CPUs
```

***

## Partie 16 : Foreground et Background

### 16.1 Suspendre et reprendre

```bash
# Lancer un processus
sleep 100

# Suspendre avec Ctrl+Z
# Résultat :  [linuxfrombeginning.wordpress](https://linuxfrombeginning.wordpress.com/2008/09/19/linux/)+ Stopped    sleep 100

# Voir les jobs
jobs

# Résultat :
#  [linuxfrombeginning.wordpress](https://linuxfrombeginning.wordpress.com/2008/09/19/linux/)+ Stopped    sleep 100

# Reprendre en arrière-plan
bg

# Reprendre en premier plan
fg

# Si plusieurs jobs, spécifier le numéro
fg %2
bg %1
```

### 16.2 Lancer directement en background

```bash
# Ajouter & à la fin
sleep 100 &

# Résultat :  [linuxfrombeginning.wordpress](https://linuxfrombeginning.wordpress.com/2008/09/19/linux/) 12345 (job number et PID)
```

***

## Partie 17 : Tuer des processus

### 17.1 Kill - Envoyer des signaux

```bash
# Lister tous les signaux
kill -l

# Signaux importants :
# 1  SIGHUP  : Reload config
# 9  SIGKILL : Tuer immédiatement (force)
# 15 SIGTERM : Terminer proprement (défaut)

# Tuer un processus par PID
kill 12345

# Forcer la terminaison
kill -9 12345

# Envoyer SIGHUP (reload)
kill -1 12345
```

### 17.2 Pkill - Tuer par nom

```bash
# Tuer tous les processus "firefox"
pkill firefox

# Forcer
pkill -9 firefox

# Avec pattern
pkill -f "python.*server"
```

### 17.3 Sleep - Pause

```bash
# Pause de 5 secondes
sleep 5

# Pause de 2 minutes
sleep 2m

# Pause d'1 heure
sleep 1h
```

***

## Partie 18 : Planification avec Cron

### 18.1 Crontab système (/etc)

**Cas d'usage** : Tâches de maintenance système, exécutées par root. [ubuntumint](https://www.ubuntumint.com/mount-filesystems-linux/)

```bash
# Crontab système
cat /etc/crontab

# Répertoires de planification
ls /etc/cron.daily    # Scripts quotidiens
ls /etc/cron.weekly   # Scripts hebdomadaires
ls /etc/cron.monthly  # Scripts mensuels
```

### 18.2 Crontab utilisateur

**Syntaxe** : `minute heure jour mois jour_semaine commande`

```bash
# Éditer le crontab de l'utilisateur courant
crontab -e

# Exemple : Exécuter à 1h05 le 2 de chaque mois
5 1 2 * * touch /home/bob/cron/crontab-ran.txt

# Exemple : Toutes les 5 minutes
*/5 * * * * /home/bob/script.sh

# Exemple : Tous les jours à minuit
0 0 * * * /home/bob/backup.sh

# Exemple : Chaque lundi à 8h
0 8 * * 1 /home/bob/weekly.sh

# Lister les tâches planifiées
crontab -l

# Supprimer toutes les tâches
crontab -r
```

**Syntaxe des champs** :
```
* * * * * commande
│ │ │ │ │
│ │ │ │ └─ Jour de la semaine (0-7, 0 et 7 = dimanche)
│ │ │ └─── Mois (1-12)
│ │ └───── Jour du mois (1-31)
│ └─────── Heure (0-23)
└───────── Minute (0-59)
```

### 18.3 Init.d - Démarrage au boot

**Cas d'usage** : Lancer des services au démarrage du système.

```bash
# Lister les runlevels
ls -d /etc/rc*.d

# rc5.d : Graphical login (desktop)
# rc3.d : Multi-user, network (servers)

# Contenu de rc5.d
ls /etc/rc5.d

# Résultat :
# S01apache2  : S = Start, 01 = Ordre de démarrage
# K02mysql    : K = Kill/Stop
```

***

## Partie 19 : Scripts Bash

### 19.1 Shebang et variables

```bash
#!/bin/bash

# Stocker le résultat d'une commande dans une variable
user=$(whoami)

# Afficher la variable
echo "Utilisateur actuel : $user"

# Alternative avec backticks (ancien)
user=`whoami`
```

### 19.2 Script complet exemple

```bash
#!/bin/bash

# Script de backup automatique
user=$(whoami)
date=$(date +%Y-%m-%d)
backup_dir="/home/$user/backups"

echo "Backup lancé par $user le $date"

# Créer le répertoire si inexistant
mkdir -p $backup_dir

# Copier les fichiers
cp -r /home/$user/Documents $backup_dir/docs_$date

echo "Backup terminé dans $backup_dir"
```

**Exécution** :
```bash
chmod +x backup.sh
./backup.sh
```