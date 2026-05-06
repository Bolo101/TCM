# Cours : Pentest Web - HTTP, serveurs, et configuration ZAP avancée

## Introduction

Cette section couvre :
- **Architecture client-serveur** : Concepts fondamentaux
- **Nginx avec Docker** : Déploiement rapide d'un serveur web
- **Protocole HTTP** : Méthodes, codes de réponse, en-têtes
- **curl** : Manipulation de requêtes HTTP en CLI
- **Configuration avancée ZAP** : Profil navigateur, certificat, contextes, add-ons, filtres

***

## Partie 1 : Architecture client-serveur

### 1.1 Définitions

**Serveur** : Machine et logiciel qui fournissent de l'information aux clients. Les données sont transmises via le protocole HTTP (HyperText Transfer Protocol).

**Client** : Tout logiciel capable d'effectuer des requêtes HTTP.

**Exemples de clients** :
- Navigateurs web (Chrome, Firefox, Brave)
- Outils en ligne de commande (curl, wget)
- Applications mobiles
- Scripts Python (requests)
- Outils de pentest (ZAP, Burp Suite)

**Communication** :
```
Client (curl)  →  Requête HTTP GET /  →  Serveur (Nginx)
Client (curl)  ←  Réponse HTTP 200 OK  ←  Serveur (Nginx)
```

***

## Partie 2 : Déploiement d'un serveur Nginx avec Docker

### 2.1 Pull de l'image Nginx

```bash
# Télécharger l'image officielle Nginx
docker image pull nginx

# Vérifier
docker images | grep nginx
```

### 2.2 Lancer le serveur Nginx

**Commande** :
```bash
docker container run --rm -p 80:80 nginx
```

**Explication des options** :

| Option | Valeur | Signification |
|--------|--------|---------------|
| `--rm` | - | Supprime automatiquement le conteneur après arrêt |
| `-p` | `80:80` | Redirige le trafic HTTP du port 80 (hôte) → port 80 (conteneur) |
| Image | `nginx` | Image Docker officielle Nginx |

**⚠️ Attention** : Le conteneur tourne en mode **non-daemonized** (foreground), occupant le terminal.

**Solution** : Ajouter `-d` pour mode détaché :
```bash
docker container run --rm -d -p 80:80 nginx
```

### 2.3 Tester le serveur

**Méthode 1 : curl**
```bash
# Depuis Kali Linux (client)
curl http://servertcm
# OU avec IP
curl http://192.168.1.100
```

**Réponse attendue** :
```html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

**Méthode 2 : Netcat**
```bash
# Connexion brute au port 80
nc servertcm 80

# Envoyer manuellement une requête HTTP
GET / HTTP/1.1
Host: servertcm

# (Appuyer sur Entrée 2 fois)
```

**Méthode 3 : Navigateur web**
```
http://servertcm
```

### 2.4 Logs Nginx

**Accéder aux logs du conteneur** :
```bash
# Logs en temps réel
docker logs -f <container_id>

# Résultat typique :
# 192.168.1.50 - - [06/May/2026:21:53:00 +0000] "GET / HTTP/1.1" 200 615
```

**Format du log** :
```
IP_client - - [Date] "Méthode URL Protocole" Code_réponse Taille
```

***

## Partie 3 : Protocole HTTP - Fondamentaux

### 3.1 Définition

**HTTP** (HyperText Transfer Protocol) : Protocole qui définit comment le trafic web est structuré et échangé entre clients et serveurs. [api7](https://api7.ai/learning-center/api-101/http-methods-in-apis)

**Caractéristiques** :
- **Sans état** (stateless) : Chaque requête est indépendante
- **Texte clair** : Lisible par l'humain (non chiffré, contrairement à HTTPS)
- **Request/Response** : Modèle question-réponse

### 3.2 Méthodes HTTP (HTTP Verbs)

**Méthodes principales**  : [stackoverflow](https://stackoverflow.com/questions/24886013/http-verbs-when-to-use-get-post-put-delete)

| Méthode | Objectif | Équivalent CRUD | Idempotent | Body |
|---------|----------|-----------------|------------|------|
| **GET** | Demander des informations au serveur | Read | ✅ Oui | Non |
| **POST** | Envoyer des données au serveur | Create | ❌ Non | Oui |
| **PUT** | Remplacer une ressource complète | Update | ✅ Oui | Oui |
| **PATCH** | Modifier partiellement une ressource | Update | ❌ Non | Oui |
| **DELETE** | Supprimer une ressource | Delete | ✅ Oui | Optionnel |
| **HEAD** | Comme GET mais sans le body (métadonnées) | - | ✅ Oui | Non |
| **OPTIONS** | Demander les capacités du serveur | - | ✅ Oui | Non |

#### GET - Récupérer des informations [api7](https://api7.ai/learning-center/api-101/http-methods-in-apis)

**Exemple** :
```bash
curl http://example.com/users/123
```

**Requête HTTP** :
```http
GET /users/123 HTTP/1.1
Host: example.com
```

**Usage** : Afficher une page, télécharger un fichier, lire des données d'API.

#### POST - Créer ou soumettre des données [stackoverflow](https://stackoverflow.com/questions/24886013/http-verbs-when-to-use-get-post-put-delete)

**Exemple** : Connexion à un compte
```bash
curl -X POST http://example.com/login \
  -d "username=admin&password=secret"
```

**Requête HTTP** :
```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=secret
```

**Usage** : Créer un compte, ajouter un commentaire, se connecter.

#### PUT - Remplacer une ressource [api7](https://api7.ai/learning-center/api-101/http-methods-in-apis)

**Exemple** : Mettre à jour un profil utilisateur
```bash
curl -X PUT http://example.com/users/123 \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com"}'
```

**Différence PUT vs PATCH** :
- **PUT** : Remplace **toute** la ressource (tous les champs requis)
- **PATCH** : Met à jour **partiellement** (seulement les champs modifiés)

#### DELETE - Supprimer une ressource [apidog](https://apidog.com/blog/http-methods/)

**Exemple** :
```bash
curl -X DELETE http://example.com/users/123
```

**Requête HTTP** :
```http
DELETE /users/123 HTTP/1.1
Host: example.com
```

#### HEAD - Métadonnées uniquement [api7](https://api7.ai/learning-center/api-101/http-methods-in-apis)

**Exemple** :
```bash
curl -I http://example.com
```

**Utilité** : Vérifier si une ressource existe, obtenir sa taille, dernière modification.

#### OPTIONS - Découvrir les capacités [api7](https://api7.ai/learning-center/api-101/http-methods-in-apis)

**Exemple** :
```bash
curl -X OPTIONS http://example.com/api -v
```

**Réponse typique** :
```http
HTTP/1.1 200 OK
Allow: GET, POST, PUT, DELETE, OPTIONS
```

### 3.3 Codes de réponse HTTP (Status Codes)

**Classification**  : [peterdaugaardrasmussen](https://peterdaugaardrasmussen.com/2020/05/02/list-of-http-status-code-groups-such-as-200-400-and-500/)

| Plage | Catégorie | Signification |
|-------|-----------|---------------|
| **1xx** | Informational | Requête en cours de traitement |
| **2xx** | Success | Succès de la requête |
| **3xx** | Redirection | Ressource déplacée, redirection nécessaire |
| **4xx** | Client Error | Erreur côté client (mauvaise requête) |
| **5xx** | Server Error | Erreur côté serveur |

#### Codes 2xx - Succès [ramotion](https://www.ramotion.com/blog/http-status-codes/)

| Code | Nom | Signification |
|------|-----|---------------|
| **200** | OK | Requête réussie, données retournées |
| **201** | Created | Ressource créée avec succès (POST) |
| **204** | No Content | Succès mais pas de contenu à retourner |

**Exemple** :
```bash
curl -I http://example.com
# HTTP/1.1 200 OK
```

#### Codes 3xx - Redirection [kinsta](https://kinsta.com/blog/http-status-codes/)

| Code | Nom | Signification |
|------|-----|---------------|
| **301** | Moved Permanently | Ressource déplacée définitivement |
| **302** | Found | Redirection temporaire |
| **304** | Not Modified | Ressource non modifiée (cache valide) |

**Exemple** :
```bash
curl http://example.com
# HTTP/1.1 301 Moved Permanently
# Location: https://example.com
```

#### Codes 4xx - Erreur client [peterdaugaardrasmussen](https://peterdaugaardrasmussen.com/2020/05/02/list-of-http-status-code-groups-such-as-200-400-and-500/)

| Code | Nom | Signification |
|------|-----|---------------|
| **400** | Bad Request | Requête malformée |
| **401** | Unauthorized | Authentification requise |
| **403** | Forbidden | Accès refusé (même avec auth) |
| **404** | Not Found | Ressource inexistante |
| **429** | Too Many Requests | Rate limiting dépassé |

**Exemple pentest** :
```bash
curl http://example.com/admin
# HTTP/1.1 403 Forbidden
```

#### Codes 5xx - Erreur serveur [kinsta](https://kinsta.com/blog/http-status-codes/)

| Code | Nom | Signification |
|------|-----|---------------|
| **500** | Internal Server Error | Erreur générique serveur |
| **502** | Bad Gateway | Proxy/Gateway a reçu réponse invalide |
| **503** | Service Unavailable | Serveur surchargé/maintenance |

**Exemple** :
```bash
curl http://example.com/broken-page
# HTTP/1.1 500 Internal Server Error
```

### 3.4 Body de réponse

**Types de contenu courants** :
- **HTML** : Pages web
- **JSON** : APIs REST
- **XML** : APIs SOAP, flux RSS
- **Binaire** : Images, PDF, fichiers

**Exemple JSON** :
```bash
curl https://api.github.com/users/octocat
```

**Réponse** :
```json
{
  "login": "octocat",
  "id": 583231,
  "name": "The Octocat",
  "company": "@github"
}
```

***

## Partie 4 : curl - Manipulation avancée

### 4.1 Option `-v` : Mode verbose

**Cas d'usage** : Afficher tous les détails de la requête/réponse (headers, IP, chiffrement).

```bash
curl -v http://example.com
```

**Sortie typique** :
```
* Trying 93.184.216.34:80...
* Connected to example.com (93.184.216.34) port 80
> GET / HTTP/1.1
> Host: example.com
> User-Agent: curl/7.68.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Content-Type: text/html; charset=UTF-8
< Content-Length: 1256
< 
<!doctype html>
<html>
...
```

**Informations révélées** :
- IP du serveur : `93.184.216.34`
- Headers envoyés (`>`) et reçus (`<`)
- User-Agent par défaut : `curl/7.68.0`

### 4.2 Option `-L` : Suivre les redirections

**Problème sans `-L`** :
```bash
curl http://github.com
# HTTP/1.1 301 Moved Permanently
# Location: https://github.com/
# (Pas de contenu affiché)
```

**Solution avec `-L`** :
```bash
curl -L http://github.com
# Suit la redirection vers https://github.com/
# Affiche le HTML final
```

**Combinaison avec `-v`** :
```bash
curl -L -v http://github.com
# Affiche la redirection 301 ET la réponse finale 200
```

### 4.3 Envoyer une requête POST

**Syntaxe de base** :
```bash
curl -X POST -v https://example.com/api
```

**Avec données** :
```bash
curl -X POST https://example.com/login \
  -d "username=admin&password=secret"
```

**Avec JSON** :
```bash
curl -X POST https://example.com/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}'
```

### 4.4 Headers personnalisés : `-H`

**Changer le User-Agent** :
```bash
curl -X POST https://example.com \
  -H "User-Agent: PWST"
```

**Requête complète** :
```http
POST / HTTP/1.1
Host: example.com
User-Agent: PWST      ← Personnalisé
Accept: */*
```

**Autres headers utiles** :
```bash
# Authentification
curl -H "Authorization: Bearer TOKEN123" https://api.example.com

# Cookie
curl -H "Cookie: sessionid=abc123" https://example.com

# Referrer (contourner protections)
curl -H "Referer: https://example.com/admin" https://example.com/api
```

***

## Partie 5 : Configuration avancée de ZAP

### 5.1 Configuration du navigateur (Brave)

#### Étape 1 : Créer un profil navigateur dédié

**Raison** : Isoler le trafic de pentest du trafic personnel.

**Brave** :
```
1. Paramètres → Gérer les profils
2. Créer un nouveau profil : "Pentest"
3. Lancer Brave avec ce profil
```

#### Étape 2 : Installer Proxy SwitchyOmega

**Extension** : Proxy SwitchyOmega (Chrome Web Store)

```
1. Chrome Web Store → Rechercher "Proxy SwitchyOmega"
2. Ajouter à Brave
3. Icône apparaît dans la barre d'outils
```

#### Étape 3 : Installer Wappalyzer

**Extension** : Wappalyzer (détection de technologies)

```
1. Chrome Web Store → Rechercher "Wappalyzer"
2. Ajouter à Brave
```

### 5.2 Configuration de Proxy SwitchyOmega

#### Renommer le profil "proxy" en "ZAP"

```
1. Cliquer sur l'icône Proxy SwitchyOmega
2. Options
3. Profiles → "proxy" → Renommer en "ZAP"
```

#### Configurer le proxy ZAP [zaproxy](https://www.zaproxy.org/docs/desktop/start/proxies/)

```
1. Profile : ZAP
2. Protocol : HTTP
3. Server : localhost
4. Port : 8080
5. Apply changes
```

**⚠️ Important** : ZAP utilise par défaut `localhost:8080`. [zaproxy](https://www.zaproxy.org/docs/desktop/start/proxies/)

#### Activer le profil ZAP

```
1. Cliquer sur l'icône Proxy SwitchyOmega
2. Sélectionner "ZAP"
3. Le trafic passe maintenant par ZAP
```

### 5.3 Installation du certificat SSL de ZAP [security.my.salesforce-sites](https://security.my.salesforce-sites.com/security/tools/webapp/zapbrowsersetup)

**Problème** : Sans certificat, les sites HTTPS affichent des erreurs de certificat. [gabriel.urdhr](https://www.gabriel.urdhr.fr/2022/03/24/zap-no-certificate-validation/)

#### Étape 1 : Générer/Sauvegarder le certificat ZAP [security.my.salesforce-sites](https://security.my.salesforce-sites.com/security/tools/webapp/zapbrowsersetup)

```
1. ZAP → Options (icône engrenage ⚙️)
2. Network → Server Certificates
   OU
   Dynamic SSL Certificates
3. Save (bouton en bas)
4. Enregistrer : zap_root_ca.cer
```

#### Étape 2 : Importer le certificat dans Brave [security.my.salesforce-sites](https://security.my.salesforce-sites.com/security/tools/webapp/zapbrowsersetup)

```
1. Brave → Paramètres
2. Confidentialité et sécurité
3. Sécurité → Gérer les certificats
4. Autorités → Importer
5. Sélectionner zap_root_ca.cer
6. ✅ Cocher "Faire confiance à ce certificat pour identifier des sites web"
7. OK
```

**Vérification** :
```
1. Naviguer vers https://google.com
2. Aucun avertissement de certificat = succès ✅
```

### 5.4 Utilisation basique - Spider et contextes

#### Lancer une attaque Spider

```
1. Dans ZAP, naviguer vers le site cible via Brave
2. Onglet "Sites" → Clic droit sur l'URL
3. Attack → Spider...
4. Start Scan
```

**Résultat** : ZAP explore automatiquement tous les liens du site.

#### Créer un contexte

**Cas d'usage** : Définir le périmètre du test (scope). [zaproxy](https://www.zaproxy.org/docs/desktop/start/proxies/)

```
1. Onglet "Sites" → Clic droit sur l'URL cible
2. Include in Context → New Context
3. Nom : "Site Cible"
4. OK
```

**Avantage** : ZAP ne scanera que les URLs dans le contexte (évite d'attaquer des sites tiers).

#### Analyser les requêtes et réponses

```
1. Sélectionner une requête dans l'onglet "History"
2. Onglet "Request" : Voir la requête HTTP complète
3. Onglet "Response" : Voir la réponse serveur
```

### 5.5 Installation d'add-ons (Marketplace)

**Accès au Marketplace** :
```
1. ZAP → Lancer
2. Fenêtre "Add-ons" s'ouvre automatiquement
   OU
   Menu Manage Add-ons (icônes rouge/bleu/vert)
```

**Mettre à jour tous les add-ons** :
```
1. Cliquer sur "Update All" en bas
2. ⚠️ Redimensionner la fenêtre si nécessaire
3. Attendre la fin des téléchargements
```

**Add-ons recommandés** :
- **Active Scanner Rules** : Détection de vulnérabilités
- **FuzzDB** : Wordlists pour fuzzing
- **Advanced SQL Injection** : Tests SQL avancés
- **XSS Scanner** : Détection XSS
- **AJAX Spider** : Crawler pour sites JavaScript

### 5.6 Configuration : Exclure Brave des scans

**Problème** : ZAP scanne les connexions de Brave (mises à jour, telemetry).

**Solution** : Ajouter Brave à la liste d'exclusion.

```
1. Options (⚙️) → Global Exclude URL
2. Add...
3. Pattern (regex) : ^https?://.*\.brave\.com.*$
4. Description : Brave telemetry
5. OK
```

**Syntaxe regex expliquée** :
- `^` : Début de l'URL
- `https?` : HTTP ou HTTPS
- `://` : Séparateur protocole
- `.*\.brave\.com` : Sous-domaines de brave.com
- `.*$` : Fin de l'URL

**Autres exclusions courantes** :
```
^https?://.*\.google\.com.*$      # Google services
^https?://.*\.gstatic\.com.*$     # Google CDN
^https?://.*\.mozilla\.org.*$     # Firefox updates
```

### 5.7 Désactiver le HUD (Heads-Up Display)

**HUD** : Interface overlay dans le navigateur (utile pour démos, moins pour travail réel).

**Désactivation** :
```
1. Options (⚙️) → HUD
2. ✅ Décocher "Enable when using the ZAP Desktop"
3. OK
```

### 5.8 Filtres d'alertes globaux

**Cas d'usage** : Réduire le bruit en désactivant les alertes de faible criticité. [zaproxy](https://www.zaproxy.org/docs/desktop/start/proxies/)

```
1. Options (⚙️) → Global Alert Filters
2. Add...
3. Configuration :
   - Alert : Anti-clickjacking Header
   - Risk : Low
   - Action : False Positive
4. OK
```

**Résultat** : Les alertes "X-Frame-Options" manquantes ne seront plus remontées comme vulnérabilités.

**Autres filtres courants** :
- **Cookie Without SameSite Attribute** (Low) → False Positive si non critique
- **Cookie Without Secure Flag** (Low) → Garder si HTTP seulement
- **X-Content-Type-Options Header Missing** (Low) → False Positive selon contexte

***

## Partie 6 : Workflow complet de pentest avec ZAP

### 6.1 Checklist de configuration

1. ✅ **Profil navigateur dédié** : Isolation du trafic
2. ✅ **Proxy SwitchyOmega** : Basculer facilement entre ZAP et navigation normale
3. ✅ **Certificat SSL ZAP** : Intercepter HTTPS sans erreurs
4. ✅ **Contexte** : Définir le scope (URLs à tester)
5. ✅ **Exclusions globales** : Brave, Google, Mozilla
6. ✅ **Add-ons à jour** : Dernières règles de scan
7. ✅ **Filtres d'alertes** : Réduire le bruit

### 6.2 Workflow d'analyse

```
1. Naviguer manuellement sur le site (exploration)
2. Spider automatique (découvrir les liens)
3. Fuzzing (trouver pages cachées)
4. Active Scan (tester les vulnérabilités)
5. Analyse manuelle des alertes
6. Exploitation des vulnérabilités trouvées
7. Génération du rapport
```

***

## Résumé : Points clés à retenir

1. **Client/Serveur** : Client = requêtes HTTP, Serveur = réponses
2. **Nginx Docker** : `docker run --rm -p 80:80 nginx`
3. **HTTP GET** : Récupérer des données [developer.mozilla](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
4. **HTTP POST** : Créer/soumettre des données [stackoverflow](https://stackoverflow.com/questions/24886013/http-verbs-when-to-use-get-post-put-delete)
5. **HTTP PUT/PATCH** : Mettre à jour (complet/partiel) [api7](https://api7.ai/learning-center/api-101/http-methods-in-apis)
6. **HTTP DELETE** : Supprimer une ressource [apidog](https://apidog.com/blog/http-methods/)
7. **Codes 2xx** : Succès (200 OK) [ramotion](https://www.ramotion.com/blog/http-status-codes/)
8. **Codes 3xx** : Redirection (301, 302) [peterdaugaardrasmussen](https://peterdaugaardrasmussen.com/2020/05/02/list-of-http-status-code-groups-such-as-200-400-and-500/)
9. **Codes 4xx** : Erreur client (403, 404) [ramotion](https://www.ramotion.com/blog/http-status-codes/)
10. **Codes 5xx** : Erreur serveur (500) [kinsta](https://kinsta.com/blog/http-status-codes/)
11. **curl -v** : Mode verbose (détails complets)
12. **curl -L** : Suivre les redirections
13. **curl -H** : Headers personnalisés
14. **ZAP certificat** : Importer dans Navigateur > Sécurité > Autorités [security.my.salesforce-sites](https://security.my.salesforce-sites.com/security/tools/webapp/zapbrowsersetup)
15. **ZAP exclusions** : Regex pour éviter scans hors scope
16. **ZAP filtres** : Réduire alertes Low Risk selon contexte
