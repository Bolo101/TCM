# Cours : Reconnaissance en Ethical Hacking

## Introduction à la phase de reconnaissance

La reconnaissance est la première et l'une des plus importantes phases en ethical hacking. Elle consiste à collecter un maximum d'informations sur la cible avant toute action intrusive. Cette phase se divise en deux catégories : la reconnaissance **passive** (sans interaction directe avec la cible) et la reconnaissance **active** (interaction directe mais limitée). [guardia](https://guardia.school/boite-a-outils/top-meilleurs-logiciels-hack-pentesting.html)

**Règle d'or** : Toujours valider votre cible pour éviter d'attaquer la mauvaise entité. Pour pratiquer légalement, utilisez des plateformes comme [bugcrowd.com](https://www.bugcrowd.com) qui listent des programmes de bug bounty où les entreprises autorisent explicitement les tests de sécurité.

***

## Partie 1 : Reconnaissance Passive (OSINT)

La reconnaissance passive utilise des sources publiques sans jamais interagir directement avec la cible. L'objectif est de rester invisible.

### 1.1 Collecte d'informations sur les personnes

**OSINT (Open Source Intelligence)** : Recherche d'informations publiques sur les réseaux sociaux, sites web, bases de données publiques.

**Ce qu'on cherche** :
- Noms et prénoms des employés
- Titres de poste et organigramme
- Photos et métadonnées
- Relations professionnelles
- Habitudes et comportements en ligne

**Outils recommandés** :
- **theHarvester** (open-source, alternative à hunter.io)
- **Maltego** (version Community gratuite)
- **Recon-ng** (framework OSINT)

### 1.2 Découverte d'adresses email

**Cas d'usage** : Identifier les emails pour du phishing éthique, tester la sensibilisation des employés, ou vérifier les fuites de données.

**Outils** :

**Hunter.io** (freemium, limité en version gratuite)
```
# Via navigateur web : hunter.io
# Recherche : @entreprise.com
```

**theHarvester** (open-source, recommandé) [lemondeinformatique](https://www.lemondeinformatique.fr/actualites/lire-10-outils-de-pen-test-pour-hackers-ethiques-75526.html)
```bash
# Installation
sudo apt install theharvester

# Recherche d'emails pour un domaine
theHarvester -d entreprise.com -b all

# Recherche ciblée sur Google uniquement
theHarvester -d entreprise.com -b google -l 500
```

**Autres outils** :
- phonebook.cz (base de données publique)
- tools.verifyemailaddress.io (vérification de validité)

### 1.3 Recherche de credentials compromis

**Cas d'usage** : Vérifier si les employés de la cible ont des mots de passe exposés dans des fuites de données (data breaches).

**DeHashed** (service payant, environ 2€/semaine)
```
# Via interface web : dehashed.com
# Recherche par : email, IP, username, adresse, téléphone
# Retourne : mots de passe hashés
```

**Workflow recommandé** :
1. Récupérer le hash du mot de passe sur DeHashed
2. Identifier le type de hash (MD5, SHA-1, bcrypt, etc.)
3. Chercher le hash sur hashes.org ou utiliser **hashcat** (open-source)

**Hashcat** (alternative open-source pour cracker les hashs) [jedha](https://www.jedha.co/formation-cybersecurite/10-meilleurs-logiciels-de-hacking-open-source)
```bash
# Installation
sudo apt install hashcat

# Exemple : cracker un hash MD5
hashcat -m 0 -a 0 hash.txt rockyou.txt

# -m 0 : mode MD5
# -a 0 : attaque par dictionnaire
# rockyou.txt : dictionnaire de mots de passe
```

### 1.4 Découverte de sous-domaines

**Cas d'usage** : Identifier tous les sous-domaines d'une organisation pour trouver des points d'entrée oubliés ou mal sécurisés (ex: dev.entreprise.com, admin.entreprise.com).

**Sublist3r** (open-source) [lemondeinformatique](https://www.lemondeinformatique.fr/actualites/lire-10-outils-de-pen-test-pour-hackers-ethiques-75526.html)
```bash
# Installation
git clone https://github.com/aboul3la/Sublist3r.git
cd Sublist3r
pip install -r requirements.txt

# Utilisation basique
python sublist3r.py -d entreprise.com

# Avec énumération de ports
python sublist3r.py -d entreprise.com -p 80,443,8080
```
*Note : Problème possible avec l'API VirusTotal. Alternative : utiliser sans cette source ou créer une clé API gratuite.*

**crt.sh** (navigateur web)
```
# Via navigateur : https://crt.sh
# Recherche : %.entreprise.com
# Retourne : tous les certificats SSL émis (révèle les sous-domaines)
```

**OWASP Amass** (très puissant, open-source) [lemondeinformatique](https://www.lemondeinformatique.fr/actualites/lire-10-outils-de-pen-test-pour-hackers-ethiques-75526.html)
```bash
# Installation
sudo apt install amass

# Énumération passive
amass enum -d entreprise.com

# Énumération active (+ DNS brute force)
amass enum -active -d entreprise.com -o resultats.txt

# Avec résolution DNS et vérification
amass enum -d entreprise.com -ip -brute
```

**httprobe** (par tomnomnom, open-source)
```bash
# Installation
go install github.com/tomnomnom/httprobe@latest

# Utilisation : vérifier quels sous-domaines sont actifs
cat subdomains.txt | httprobe

# Résultat : http://subdomain.com:80 ou https://subdomain.com:443
```

### 1.5 Identification des technologies web

**Cas d'usage** : Connaître les technologies utilisées (CMS, frameworks, serveurs) pour identifier des vulnérabilités connues.

**BuiltWith** (via navigateur web)
```
# Site : builtwith.com
# Entre l'URL cible
# Retourne : CMS, analytics, serveurs, CDN, frameworks
```

**Wappalyzer** (extension navigateur, gratuite)
```
# Installation : addon Firefox/Chrome
# Utilisation : icône dans la barre d'outils
# Affiche automatiquement les technologies du site visité
```

**WhatWeb** (open-source, ligne de commande) [lemondeinformatique](https://www.lemondeinformatique.fr/actualites/lire-10-outils-de-pen-test-pour-hackers-ethiques-75526.html)
```bash
# Installation
sudo apt install whatweb

# Scan basique
whatweb https://entreprise.com

# Scan agressif avec plus de détails
whatweb -a 3 https://entreprise.com

# Scan multiple avec export
whatweb -i urls.txt -o resultats.json --log-json
```

### 1.6 Google Dorking (recherche avancée)

**Cas d'usage** : Trouver des informations sensibles indexées par Google (fichiers confidentiels, pages admin, erreurs exposées).

**Syntaxe et exemples** :
```
# Rechercher uniquement sur un site
site:entreprise.com

# Exclure des résultats
site:entreprise.com -www -blog

# Rechercher un type de fichier
site:entreprise.com filetype:pdf
site:entreprise.com filetype:xlsx

# Combinaisons puissantes
site:entreprise.com inurl:admin
site:entreprise.com intitle:"index of"
site:entreprise.com filetype:sql "password"
```

**Google Hacking Database (GHDB)** : Base de données de requêtes Google pour trouver des vulnérabilités.

### 1.7 Reconnaissance sur les réseaux sociaux

**Cas d'usage** : Profiler les employés, identifier les relations, comprendre l'organigramme, préparer des attaques de social engineering.

**Plateformes à explorer** :
- LinkedIn (organigramme, compétences techniques)
- Twitter/X (opinions, événements)
- Facebook (informations personnelles)
- GitHub (code source, credentials exposés)

**Outils open-source** :
- **Sherlock** (trouver des comptes sur plusieurs plateformes)
```bash
# Installation
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock
pip install -r requirements.txt

# Recherche d'un username sur toutes les plateformes
python sherlock.py nom_utilisateur
```

- **Social-Analyzer** (analyse de profils sociaux)
```bash
pip install social-analyzer
social-analyzer --username "john_doe" --websites "youtube facebook twitter"
```

***

## Partie 2 : Reconnaissance Active (limitée)

La reconnaissance active implique une interaction directe mais non intrusive avec la cible. **Attention** : certaines activités peuvent être détectées ou considérées comme illégales sans autorisation.

### 2.1 Interception de trafic avec Burp Suite

**Burp Suite** est un proxy HTTP qui intercepte et modifie le trafic entre votre navigateur et le serveur web. [subrosacyber](https://subrosacyber.com/fr/blog/ethical-hacking-tools)

**Cas d'usage** : Analyser les requêtes HTTP/HTTPS, identifier les paramètres, détecter les failles (XSS, SQLi, CSRF).

**Installation et configuration** :

```bash
# Téléchargement (version Community gratuite)
# Site : portswigger.net/burp/communitydownload

# Lancement
java -jar burpsuit_community.jar
```

**Configuration du proxy** :
1. Dans Burp Suite : aller dans **Proxy → Options**
2. Vérifier que le proxy écoute sur `127.0.0.1:8080`
3. Installer **FoxyProxy** (extension Firefox/Chrome)
4. Configurer FoxyProxy : `127.0.0.1` port `8080`

**Installation du certificat SSL** :
1. Activer le proxy FoxyProxy
2. Naviguer vers : `http://burp`
3. Télécharger le certificat CA
4. Dans Firefox : Paramètres → Vie privée et sécurité → Certificats → Importer
5. Cocher "Faire confiance à cette autorité pour identifier des sites web"

**Utilisation basique** :
1. Activer "Intercept is on" dans l'onglet **Proxy**
2. Naviguer vers un site web
3. Les requêtes apparaissent dans Burp → analyser/modifier → Forward

**Alternative open-source** : **OWASP ZAP** (Zed Attack Proxy) [lemondeinformatique](https://www.lemondeinformatique.fr/actualites/lire-10-outils-de-pen-test-pour-hackers-ethiques-75526.html)
```bash
# Installation
sudo apt install zaproxy

# Lancement
zaproxy

# Configuration similaire : proxy sur 127.0.0.1:8080
```

***

## Outils complémentaires recommandés

**Recon-ng** (framework de reconnaissance) [lemondeinformatique](https://www.lemondeinformatique.fr/actualites/lire-10-outils-de-pen-test-pour-hackers-ethiques-75526.html)
```bash
# Installation
sudo apt install recon-ng

# Lancement et utilisation
recon-ng
[recon-ng][default] > marketplace install all
[recon-ng][default] > modules search
[recon-ng][default] > use recon/domains-hosts/google_site_web
```

**Shodan** (moteur de recherche pour appareils connectés)
```bash
# Installation CLI
pip install shodan

# Utilisation (nécessite clé API gratuite)
shodan init VOTRE_CLE_API
shodan search "apache country:FR"
```

**SpiderFoot** (automatisation OSINT)
```bash
# Installation
git clone https://github.com/smicallef/spiderfoot.git
cd spiderfoot
pip install -r requirements.txt

# Lancement interface web
python sf.py -l 127.0.0.1:5001
```

***

## Méthodologie de reconnaissance (checklist)

1. ✅ **Validation de la cible** : Vérifier que vous avez l'autorisation
2. ✅ **OSINT passive** : Emails, personnes, réseaux sociaux
3. ✅ **Sous-domaines** : Sublist3r, Amass, crt.sh
4. ✅ **Technologies** : WhatWeb, Wappalyzer
5. ✅ **Google Dorking** : Fichiers sensibles, pages cachées
6. ✅ **Credentials** : DeHashed, haveibeenpwned
7. ✅ **Proxy analysis** : Burp Suite ou ZAP
8. ✅ **Documentation** : Tout noter pour les phases suivantes
