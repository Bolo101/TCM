# Cours : Applications client-side et défis de sécurité

## Introduction

Cette section couvre :
- **Client-Side Applications** : Applications qui utilisent les ressources du client pour le rendu [tateeda](https://tateeda.com/blog/client-side-rendering-vs-server-side-rendering-for-web-application-development)
- **Principe fondamental** : Rien côté client ne peut être secret
- **JavaScript et rendu HTML** : Défis pour les scanners de sécurité [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
- **ZAP et applications modernes** : Limitations et solutions [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

***

## Partie 1 : Client-Side Applications - Concepts

### 1.1 Définition

**Client-Side Application** : Application web qui utilise les **ressources du client** (navigateur, CPU, RAM) pour **rendre le contenu** au lieu de faire porter tout le fardeau sur le serveur web. [technologies.insign](https://technologies.insign.fr/articles/client-side-rendering-csr)

**Synonymes** :
- Client-Side Rendering (CSR)
- Single Page Application (SPA)
- JavaScript-heavy apps
- Modern web apps [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

### 1.2 Différence Client-Side vs Server-Side Rendering

#### Server-Side Rendering (SSR) - Traditionnel

**Fonctionnement** :
```
1. Client (navigateur) → Requête HTTP → Serveur
2. Serveur exécute PHP/Python/Ruby
3. Serveur génère HTML complet
4. Serveur envoie HTML prêt à afficher
5. Client affiche immédiatement
```

**Exemple de réponse serveur (SSR)** :
```html
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>User Profile</title></head>
<body>
  <h1>Welcome, John Doe</h1>
  <p>Email: john@example.com</p>
  <p>Member since: 2020</p>
</body>
</html>
```

**Caractéristiques**  : [web](https://web.dev/articles/rendering-on-the-web)
- ✅ HTML complet immédiatement disponible
- ✅ Bon pour SEO (moteurs de recherche)
- ✅ Temps de chargement initial rapide
- ❌ Chaque interaction = nouvelle requête serveur
- ❌ Rechargement complet de la page

#### Client-Side Rendering (CSR) - Moderne

**Fonctionnement**  : [web](https://web.dev/articles/client-side-rendering-of-html-and-interactivity)
```
1. Client → Requête HTTP → Serveur
2. Serveur envoie HTML minimal + JavaScript
3. Client télécharge JavaScript
4. JavaScript s'exécute dans le navigateur
5. JavaScript fait des requêtes API (JSON)
6. JavaScript génère et affiche le HTML
```

**Exemple de réponse serveur (CSR)** :
```html
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>App</title></head>
<body>
  <div id="app"></div>  <!-- Vide ! -->
  <script src="bundle.js"></script>  <!-- Tout le rendu ici -->
</body>
</html>
```

**JavaScript (bundle.js) génère ensuite** :
```javascript
// JavaScript exécuté côté client
fetch('/api/user/123')
  .then(response => response.json())
  .then(data => {
    document.getElementById('app').innerHTML = `
      <h1>Welcome, ${data.name}</h1>
      <p>Email: ${data.email}</p>
      <p>Member since: ${data.joinDate}</p>
    `;
  });
```

**Caractéristiques**  : [technologies.insign](https://technologies.insign.fr/articles/client-side-rendering-csr)
- ✅ Expérience utilisateur fluide (pas de rechargement)
- ✅ Interactions rapides après chargement initial
- ✅ Décharge le serveur (envoie juste du JSON)
- ❌ Temps de chargement initial long (téléchargement JS)
- ❌ Problèmes SEO (HTML vide au départ)
- ❌ Nécessite JavaScript activé

### 1.3 Comparaison visuelle

**Server-Side Rendering** :
```
[Client]  →  Requête: GET /profile  →  [Serveur]
          ←  HTML complet prêt     ←
          
Charge serveur: ████████████ (100%)
Charge client:  ██ (10%)
```

**Client-Side Rendering**  : [technologies.insign](https://technologies.insign.fr/articles/client-side-rendering-csr)
```
[Client]  →  Requête: GET /         →  [Serveur]
          ←  HTML vide + JS        ←
          
[Client exécute JS]
          →  API: GET /api/profile →  [Serveur]
          ←  JSON: {name, email}   ←
          
[Client génère HTML avec JS]

Charge serveur: ███ (30%)
Charge client:  ████████████ (100%)
```

### 1.4 Exemples de frameworks Client-Side

**Frameworks populaires** :
- **React** (Facebook/Meta)
- **Vue.js**
- **Angular** (Google)
- **Svelte**
- **Next.js** (React avec SSR hybride)

**Exemple React** :
```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data));
  }, [userId]);
  
  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <p>Email: {user?.email}</p>
    </div>
  );
}
```

***

## Partie 2 : Principe fondamental - Rien côté client ne peut être secret

### 2.1 Le client est un environnement hostile

**Règle d'or** : **Tout ce qui est envoyé au client peut être vu, modifié, et rejoué**.

**Raison** : Le client (navigateur) est **contrôlé par l'utilisateur**, pas par l'application.

### 2.2 Exemples de "secrets" exposés côté client

#### a) Clés API dans le code JavaScript

**Mauvais** :
```javascript
// Code JavaScript public
const API_KEY = "sk_live_51N3xH2KtHnKpYZgM3xH2KtHnKpYZgM";
fetch('https://api.payment.com/charge', {
  headers: { 'Authorization': `Bearer ${API_KEY}` }
});
```

**Problème** : N'importe qui peut ouvrir DevTools et voir la clé. [web](https://web.dev/articles/client-side-rendering-of-html-and-interactivity)

**Solution** : Ne JAMAIS mettre de clés sensibles côté client. Utiliser un backend proxy.

```javascript
// Bon : Appeler un backend qui possède la clé
fetch('/api/payment/charge', {
  method: 'POST',
  body: JSON.stringify({ amount: 100 })
});
```

#### b) Logique métier sensible

**Mauvais** :
```javascript
// Calculer le prix côté client
function calculatePrice(quantity) {
  return quantity * 10; // Prix unitaire exposé !
}

// Envoyer au serveur
fetch('/api/checkout', {
  method: 'POST',
  body: JSON.stringify({ total: calculatePrice(5) })
});
```

**Exploitation** :
```javascript
// Attaquant modifie le prix dans DevTools Console
fetch('/api/checkout', {
  method: 'POST',
  body: JSON.stringify({ total: 0.01 }) // Prix modifié !
});
```

**Solution** : Calculer le prix côté **serveur**.

```javascript
// Client envoie seulement la quantité
fetch('/api/checkout', {
  method: 'POST',
  body: JSON.stringify({ quantity: 5 })
});

// Serveur calcule et valide
// POST /api/checkout
// { quantity: 5 }
// → Serveur calcule: 5 * 10 = 50
```

#### c) Validation côté client uniquement

**Mauvais** :
```javascript
// Formulaire validé uniquement en JavaScript
function submitForm() {
  const email = document.getElementById('email').value;
  
  if (!email.includes('@')) {
    alert('Email invalide');
    return; // Empêche la soumission
  }
  
  // Envoyer au serveur
  fetch('/api/register', {
    method: 'POST',
    body: JSON.stringify({ email })
  });
}
```

**Exploitation** : Bypass avec curl ou Burp Suite
```bash
# Contourner la validation JavaScript
curl -X POST https://example.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"invalidemail"}'
```

**Solution** : **Toujours** valider côté serveur également.

```php
<?php
// Backend validation
$email = $_POST['email'];
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    die("Email invalide");
}
// Continuer...
?>
```

#### d) Données sensibles dans le localStorage/sessionStorage

**Mauvais** :
```javascript
// Stocker le mot de passe dans le localStorage
localStorage.setItem('password', 'MySecretP@ss123');
```

**Problème** : localStorage est accessible par **n'importe quel JavaScript sur le même domaine** (XSS). [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Vérification** :
```javascript
// Console DevTools
console.log(localStorage.getItem('password'));
// → "MySecretP@ss123"
```

**Solution** : Ne jamais stocker de données sensibles côté client. Utiliser des cookies HttpOnly ou des sessions serveur.

### 2.3 Outils pour inspecter le client

**DevTools du navigateur** :
```
1. F12 ou Clic droit → Inspecter
2. Console : Exécuter du JavaScript arbitraire
3. Network : Voir toutes les requêtes/réponses
4. Application : localStorage, sessionStorage, cookies
5. Sources : Code JavaScript déobfusqué
```

**Exemple pratique** :
```javascript
// Dans la console
console.log(window); // Voir toutes les variables globales
console.log(localStorage); // Voir le stockage local
document.cookie; // Voir les cookies
```

***

## Partie 3 : JavaScript et rendu HTML - Défis pour les scanners

### 3.1 Pourquoi les applications JavaScript sont difficiles à scanner

**Problème 1 : HTML vide au départ** [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Application traditionnelle (SSR)** :
```html
<!-- Code source initial = code source final -->
<a href="/profile">Mon Profil</a>
<a href="/settings">Paramètres</a>
<a href="/logout">Déconnexion</a>
```

**Scanners traditionnels** : Peuvent facilement trouver ces liens.

**Application moderne (CSR)** :
```html
<!-- Code source initial -->
<div id="root"></div>
<script src="app.js"></script>
```

**Code source après exécution JavaScript** :
```html
<!-- DOM généré dynamiquement -->
<div id="root">
  <a href="#/profile">Mon Profil</a>
  <a href="#/settings">Paramètres</a>
  <a href="#/logout">Déconnexion</a>
</div>
```

**Problème** : Les scanners qui analysent seulement le HTML initial ne voient **aucun lien**. [debugbear](https://www.debugbear.com/docs/client-side-rendering)

**Problème 2 : Fragments d'URL non envoyés au serveur** [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**URL moderne** :
```
https://example.com/app#/profile/settings
                        ^^^^^^^^^^^^^^^^^^
                        Fragment (hash)
```

**Communication réseau** :
```
Client → Serveur : GET /app
                   (Le fragment #/profile/settings n'est PAS envoyé)
```

**Conséquence** : Les proxies (comme ZAP) ne voient **pas** les fragments. [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Problème 3 : Routes gérées par JavaScript** [technologies.insign](https://technologies.insign.fr/articles/client-side-rendering-csr)

**Exemple React Router** :
```javascript
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/profile" element={<Profile />} />
  <Route path="/admin" element={<Admin />} />
</Routes>
```

**Navigation** :
```
1. Utilisateur clique sur "Profile"
2. JavaScript change l'URL : / → /profile
3. JavaScript affiche le composant <Profile />
4. AUCUNE requête HTTP envoyée au serveur !
```

**Problème** : ZAP ne voit **aucune requête** pour `/profile`. [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Problème 4 : Contenu chargé dynamiquement (AJAX)** [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Flux typique** :
```javascript
// Cliquer sur "Charger plus"
button.addEventListener('click', () => {
  fetch('/api/posts?page=2')
    .then(res => res.json())
    .then(data => renderPosts(data));
});
```

**Problème** : Le scanner ne sait pas qu'il faut cliquer sur ce bouton pour découvrir `/api/posts?page=2`.

### 3.2 Limitations des scanners traditionnels

**Scanners passifs (Proxy)**  : [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
- ✅ Voient les requêtes HTTP/HTTPS
- ❌ Ne voient **pas** les fragments (#)
- ❌ Ne voient **pas** le contenu généré par JavaScript
- ❌ Ne voient **pas** les routes client-side

**Spider classique** :
- ✅ Suit les liens `<a href="...">`
- ❌ Ne peut pas cliquer sur les boutons
- ❌ Ne peut pas remplir les formulaires dynamiques
- ❌ Ne peut pas exécuter JavaScript

**Conséquence** : Couverture incomplète des applications modernes. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

***

## Partie 4 : ZAP et applications modernes - Solutions

### 4.1 AJAX Spider de ZAP

**AJAX Spider** : Spider qui lance un navigateur réel (Firefox/Chrome) pour exécuter JavaScript. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Avantages**  : [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
- ✅ Exécute JavaScript
- ✅ Voit le DOM généré dynamiquement
- ✅ Peut cliquer sur les boutons
- ✅ Explore les routes client-side

**Lancement** :
```
1. ZAP → Tools → AJAX Spider
2. Ou clic droit sur URL → Attack → AJAX Spider
3. Browser : Firefox Headless (par défaut)
4. Start Scan
```

**Différence avec Spider classique** :

| Spider Classique | AJAX Spider |
|------------------|-------------|
| Analyse HTML statique | Lance un navigateur réel |
| Rapide | Plus lent |
| Ne voit pas le JavaScript | Exécute le JavaScript |
| Liens `<a href>` seulement | Clique sur boutons, remplit formulaires |

### 4.2 Client Side Integration Add-on

**Add-on** : Client Side Integration (nouveau en 2023) [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Installation** :
```
1. ZAP → Manage Add-ons (icônes colorées)
2. Marketplace
3. Rechercher "Client Side Integration"
4. Install
5. Redémarrer ZAP
```

**Fonctionnalités**  : [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

#### a) Client Map

**Description** : Arborescence des sites visités, **incluant les fragments d'URL**. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Différence avec Sites Tree** :

**Sites Tree (traditionnel)** :
```
https://example.com
  └─ /app
```

**Client Map**  : [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
```
https://example.com
  └─ /app
      ├─ #/profile           ← Fragments visibles !
      ├─ #/settings
      ├─ #/admin
      └─ Storage
          ├─ Cookies
          ├─ localStorage
          └─ sessionStorage  ← Contenu du storage visible !
```

**Avantage** : Compréhension complète de la structure client-side. [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Indication visuelle** :
- URLs visitées : Icône normale
- URLs trouvées mais non visitées : ❌ (petit signe rouge moins) [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Accès** :
```
1. ZAP avec Client Side Integration installé
2. Nouveau tab : "Client Map"
3. Navigation via proxy
4. Voir les URLs avec fragments apparaître
```

#### b) Client Details

**Description** : Détails sur les nœuds du Client Map. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Informations affichées**  : [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)
- **Buttons** : Boutons détectés dans le DOM
- **Cookies** : Cookies définis dans le navigateur
- **FORM** : Formulaires détectés
- **Input** : Éléments `<input>` détectés
- **Link** : Liens détectés
- **Local Storage** : Données du localStorage
- **Session Storage** : Données du sessionStorage

**Cas d'usage** :
```
1. Sélectionner un nœud dans Client Map
2. Onglet "Client Details" affiche automatiquement les détails
3. Voir les formulaires cachés, inputs, storage
```

**Exemple** :
```
URL: https://example.com/app#/profile

Client Details :
  Forms: 1
    - action: /api/updateProfile
    - method: POST
    - fields: name, email, bio
  
  Local Storage:
    - authToken: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    - userId: 12345
  
  Links: 3
    - #/settings
    - #/logout
    - #/admin
```

#### c) Client History

**Description** : Historique de **tous les événements client-side** envoyés du navigateur à ZAP. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Types d'événements**  : [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
- **DOM Mutation** : Modification du DOM (MutationObserver)
- **Node Added** : Nœud DOM ajouté à une URL
- **Page Load** : Événement `load` du navigateur
- **Page Unload** : Événement `unload`
- **Button** : Boutons détectés
- **Form** : Formulaires détectés
- **Link** : Liens détectés
- **Storage** : Modifications localStorage/sessionStorage

**Utilité** : Traçabilité complète des événements client-side pour analyse. [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Exemple** :
```
Timestamp       Event           URL                      Details
21:45:00        Page Load       /app#/home               -
21:45:02        Link            /app#/profile            href="#/profile"
21:45:05        DOM Mutation    /app#/profile            <div id="user">...</div> added
21:45:05        Local Storage   /app#/profile            Set: authToken=abc123
21:45:10        Form            /app#/settings           <form action="/api/update">
```

#### d) Browser Extensions automatiques

**Fonctionnement** : ZAP installe automatiquement une extension dans Firefox/Chrome quand ils sont lancés depuis ZAP. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Rôle de l'extension**  : [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
- Surveiller les événements du navigateur
- Capturer les fragments d'URL
- Détecter les modifications du DOM
- Envoyer toutes les données à ZAP en temps réel

**Activation** :
```
1. ZAP → Tools → Options → Selenium
2. Cocher "Enable WebDriver Provider"
3. Lancer un navigateur depuis ZAP
4. Extension ZAP automatiquement installée
```

### 4.3 Client Spider (amélioré)

**Fonctionnalité** : Si le Client Side Integration détecte des URLs dans le DOM non visitées par l'AJAX Spider, il les **requête directement**. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Exemple** :
```
1. AJAX Spider trouve #/profile, #/settings
2. Dans le DOM, JavaScript référence aussi #/admin
3. Client Spider détecte #/admin non visité
4. Client Spider requête directement #/admin
5. Meilleure couverture !
```

### 4.4 Passive Scanning client-side

**Fonctionnalité** : Scan passif de **toutes les données reçues du navigateur**. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)

**Exemples de vulnérabilités détectées** :
- Clés API dans le code JavaScript
- Credentials dans localStorage
- Tokens JWT non chiffrés
- Données sensibles dans sessionStorage

**Activation** :
```
Automatique avec Client Side Integration add-on installé
```

### 4.5 Fonctionnalités futures prévues

**Roadmap**  : [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
- ✅ Client-side passive scanning (disponible)
- 🔜 Client-side active scanning
- 🔜 Stockage des données client dans la session ZAP
- 🔜 Recording de scripts client-side pour authentification

***

## Partie 5 : Bonnes pratiques pour tester les applications client-side

### 5.1 Approche manuelle recommandée

**Étape 1 : Explorer manuellement** [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
```
1. Naviguer normalement sur l'application via ZAP proxy
2. Cliquer sur tous les boutons
3. Remplir tous les formulaires
4. Tester toutes les fonctionnalités
5. ZAP capture tout le trafic
```

**Étape 2 : AJAX Spider**
```
1. Lancer AJAX Spider sur la page d'accueil
2. Laisser explorer automatiquement
3. Combiner avec exploration manuelle
```

**Étape 3 : Client Side Integration**
```
1. Installer l'add-on
2. Analyser le Client Map pour URLs manquées
3. Vérifier Client Details pour forms/storage cachés
4. Consulter Client History pour événements
```

**Étape 4 : Analyse des résultats**
```
1. Sites Tree : Requêtes HTTP classiques
2. Client Map : Structure client-side complète
3. Comparer les deux pour identifier les écarts
```

### 5.2 Savoir ce qu'on cherche

**Problème** : JavaScript peut cacher beaucoup de choses. [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)

**Solution** : Avoir des **objectifs de test clairs**.

**Checklist client-side** :

1. ✅ **Fragments d'URL** : Vérifier routes cachées (#/admin)
2. ✅ **localStorage/sessionStorage** : Chercher tokens, credentials
3. ✅ **Clés API** : Rechercher dans le code JavaScript
4. ✅ **Formulaires cachés** : Vérifier Client Details
5. ✅ **Boutons dynamiques** : Cliquer manuellement pour découvrir endpoints
6. ✅ **WebSockets** : Intercepter avec ZAP
7. ✅ **Requêtes AJAX** : Analyser Network tab pour endpoints non documentés

**Outils complémentaires** :

**DevTools du navigateur** :
```
1. F12 → Console
2. Taper "localStorage" pour voir le stockage
3. Network → Filtrer XHR pour voir les requêtes AJAX
4. Sources → Déobfusquer le JavaScript
```

**Wappalyzer** :
```
Identifier le framework (React, Vue, Angular)
→ Adapter la stratégie de test selon le framework
```

### 5.3 Automatisation avec scripts

**Exemple script ZAP** (Python) :
```python
from zapv2 import ZAPv2

zap = ZAPv2(apikey='your-api-key')

# Lancer AJAX Spider
target = 'https://example.com'
zap.ajaxSpider.scan(target)

# Attendre la fin
while zap.ajaxSpider.status != 'stopped':
    time.sleep(5)

# Lancer Active Scan
zap.ascan.scan(target)

# Récupérer les alertes
alerts = zap.core.alerts()
for alert in alerts:
    print(f"{alert['risk']} - {alert['name']}")
```

***

## Résumé : Points clés à retenir

1. **Client-Side Apps** : Utilisent les ressources du client pour rendre le contenu [tateeda](https://tateeda.com/blog/client-side-rendering-vs-server-side-rendering-for-web-application-development)
2. **CSR vs SSR** : CSR = HTML généré par JavaScript, SSR = HTML généré par serveur [web](https://web.dev/articles/rendering-on-the-web)
3. **Rien n'est secret côté client** : Tout peut être vu, modifié, rejoué
4. **Validation client ≠ Sécurité** : Toujours valider côté serveur également
5. **localStorage exposé** : Ne jamais stocker de credentials/tokens sensibles [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)
6. **JavaScript rend le scanning difficile** : HTML vide au départ, routes dynamiques [debugbear](https://www.debugbear.com/docs/client-side-rendering)
7. **Fragments (#) invisibles** : Proxies ne les voient pas [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)
8. **AJAX Spider** : Lance un navigateur réel pour exécuter JavaScript [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)
9. **Client Side Integration** : Add-on ZAP pour voir fragments, DOM, storage [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
10. **Client Map** : Arborescence incluant fragments et storage [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)
11. **Client Details** : Détails sur forms, inputs, links, storage [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
12. **Client History** : Événements client-side (load, mutation, storage) [zaproxy](https://www.zaproxy.org/blog/2023-11-03-handling-modern-web-apps-better-part1/)
13. **Browser Extensions** : ZAP installe automatiquement dans Firefox/Chrome [zaproxy](https://www.zaproxy.org/docs/desktop/addons/client-side-integration/)
14. **Approche hybride** : Explorer manuellement + AJAX Spider + Client Integration
15. **Objectifs clairs** : Savoir quoi chercher (fragments, storage, API keys)
