# Cours : Pentest Web - OWASP ZAP Lab (Docker, Spider, Fuzzing)

## Introduction

Ce lab couvre l'utilisation d'**OWASP ZAP** (Zed Attack Proxy) pour scanner une application web hébergée dans Docker. Nous allons apprendre à :
- Déployer un serveur web avec Docker
- Configurer un contexte de scan dans ZAP
- Utiliser le **Spider** pour découvrir les pages liées
- Utiliser le **Fuzzer** pour découvrir les pages cachées (non liées) [zaproxy](https://www.zaproxy.org/docs/desktop/addons/spider/)

**⚠️ Important** : N'utilisez ces techniques que sur des applications pour lesquelles vous avez l'autorisation.

***

## Partie 1 : Configuration du lab avec Docker

### 1.1 Analyse du script run.sh

**Cas d'usage** : Déployer rapidement un environnement de test isolé avec Docker. [zaproxy](https://www.zaproxy.org/docs/docker/baseline-scan/)

```bash
# Aller dans le répertoire du lab
cd 2-10zap

# Analyser le script de démarrage
cat run.sh
```

**Contenu typique du script** :
```bash
#!/bin/bash
docker run -d -v $(pwd)/html:/usr/share/nginx/html -p 8080:80 nginx
```

### 1.2 Explication des options Docker

**Décomposition de la commande** :

```bash
docker run -d -v $(pwd)/html:/usr/share/nginx/html -p 8080:80 nginx
```

**Options expliquées** :

| Option | Signification | Explication |
|--------|--------------|-------------|
| `docker run` | Démarrer un conteneur | Crée et lance un nouveau conteneur |
| `-d` | **Daemon mode** | Le processus s'exécute en arrière-plan (détaché du terminal) |
| `-v` | **Volume mount** | Monte un répertoire local dans le conteneur |
| `$(pwd)/html` | Répertoire source (local) | Répertoire actuel/html sur votre machine |
| `:/usr/share/nginx/html` | Répertoire destination (conteneur) | Où Nginx sert les fichiers web par défaut |
| `-p 8080:80` | Port mapping | Redirige le port 8080 de votre machine vers le port 80 du conteneur |
| `nginx` | Image Docker | Utilise l'image officielle Nginx |

**Résultat** :
- Le serveur web Nginx démarre en arrière-plan
- Les fichiers dans `./html/` sont servis par Nginx
- L'application est accessible sur `http://localhost:8080`

### 1.3 Lancer le lab

```bash
# Rendre le script exécutable
chmod +x run.sh

# Lancer le script
./run.sh

# Vérifier que le conteneur est actif
docker ps

# Résultat attendu :
# CONTAINER ID   IMAGE    STATUS         PORTS
# abc123def456   nginx    Up 10 seconds  0.0.0.0:8080->80/tcp
```

### 1.4 Accéder à l'application web

```bash
# Dans un navigateur
http://localhost:8080

# OU si sur une machine distante
http://192.168.1.100:8080
```

**Vérification** : Vous devriez voir le site web hébergé dans le répertoire `html/`.

***

## Partie 2 : Configuration de ZAP - Création d'un contexte

### 2.1 Qu'est-ce qu'un contexte dans ZAP ?

**Définition** : Un **contexte** dans ZAP définit le **périmètre de test** (scope). Il indique à ZAP quelles URLs scanner et lesquelles ignorer. [zippyops](https://www.zippyops.com/za-proxy-run-scan)

**Avantages** :
- **Focus** : Concentrer les scans sur la cible uniquement
- **Sécurité** : En mode "Protected", ZAP n'attaquera que les URLs dans le contexte
- **Organisation** : Gérer plusieurs cibles simultanément

### 2.2 Créer un contexte pour notre cible

#### Étape 1 : Naviguer sur le site web via ZAP

**Prérequis** : ZAP doit être configuré comme proxy (127.0.0.1:8080 + FoxyProxy activé).

```
1. Lancer OWASP ZAP
2. Activer FoxyProxy dans le navigateur (ZAP Proxy)
3. Naviguer vers http://localhost:8080
4. Dans ZAP, vérifier que le site apparaît dans l'onglet "Sites"
```

**Résultat** : L'arborescence du site s'affiche dans le panneau "Sites" à gauche.

#### Étape 2 : Créer le contexte

```
1. Dans l'onglet "Sites", clic droit sur "http://localhost:8080"
2. Include in Context → New Context...
3. Nommer le contexte : "Lab Website"
4. OK
```

**Configuration avancée** (optionnel) :
```
1. Clic droit sur le contexte → Properties
2. Include in Context : http://localhost:8080.*
3. Exclude from Context : .*logout.* (éviter de se déconnecter)
```

#### Étape 3 : Activer le mode Protected

**Cas d'usage** : Empêcher ZAP d'attaquer accidentellement d'autres sites (Google, CDN, etc.). [zippyops](https://www.zippyops.com/za-proxy-run-scan)

```
1. Barre d'outils ZAP → Sélectionner "Protected Mode" (bouclier vert)
2. OU : Menu → View → Mode → Protected Mode
```

**Résultat** : ZAP ne scannera activement que les URLs incluses dans le contexte.

***

## Partie 3 : Spider - Découverte automatique des pages

### 3.1 Qu'est-ce que le Spider ?

**Définition** : Le **Spider** (araignée) explore automatiquement un site web en suivant tous les liens trouvés dans les pages HTML. [zaproxy](https://www.zaproxy.org/getting-started/)

**Fonctionnement** :
1. Commence sur une page de départ (ex: `index.html`)
2. Analyse le HTML pour trouver tous les liens (`<a href="...">`)
3. Visite chaque lien découvert
4. Répète le processus récursivement

**Limitations** :
- Ne trouve que les pages **explicitement liées** dans le HTML
- Ne découvre pas les pages "cachées" ou non liées (ex: `admin.html`, `backup.html`)

### 3.2 Lancer le Spider

#### Méthode 1 : Via le menu contextuel

```
1. Onglet "Sites" → Clic droit sur "http://localhost:8080"
2. Attack → Spider...
3. Starting point : http://localhost:8080
4. Context : Lab Website
5. Start Scan
```

#### Méthode 2 : Via la barre d'outils

```
1. Sélectionner le site dans l'onglet "Sites"
2. Cliquer sur l'icône "Spider" (araignée) dans la barre d'outils
3. Start Scan
```

### 3.3 Analyser les résultats du Spider

**Observer la progression** :

```
1. Onglet "Spider" (en bas de ZAP)
2. Colonnes importantes :
   - Processed : Pages déjà visitées
   - To Process : Pages en attente
   - Status : Running / Complete
```

**Examiner les URLs découvertes** :

```
1. Onglet "Sites" → Développer l'arborescence "http://localhost:8080"
2. Liste complète des pages trouvées :
   - /index.html
   - /about.html
   - /contact.html
   - /products/item1.html
   - /products/item2.html
```

**Problème identifié** : Le Spider ne trouvera **pas** les pages comme :
- `/admin.html` (si non liée dans le HTML)
- `/backup.html`
- `/secret.html`
- `/test.php`

**Solution** : Utiliser le **Fuzzer** pour découvrir ces pages cachées. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/fuzzer/dialogue/)

***

## Partie 4 : Fuzzing - Découverte des pages cachées

### 4.1 Pourquoi fuzzer après le Spider ?

**Raison** : De nombreuses pages existent sur le serveur web mais ne sont **pas liées** dans le HTML. [thehacker](https://www.thehacker.recipes/web/recon/directory-fuzzing)

**Exemples de pages cachées** :
- Panneaux d'administration : `/admin.html`, `/admin.php`
- Fichiers de backup : `/backup.zip`, `/old/`
- Pages de test : `/test.html`, `/dev/`
- Fichiers sensibles : `/config.php`, `/phpinfo.php`

**Objectif du fuzzing** : Tester systématiquement des noms de fichiers/répertoires courants pour découvrir ces pages. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/fuzzer/)

### 4.2 Préparer la requête pour le fuzzing

#### Étape 1 : Identifier une page existante

**Cas d'usage** : Utiliser une page découverte par le Spider comme modèle.

```
1. Onglet "Sites" → Sélectionner une page existante
   Exemple : http://localhost:8080/index.html

2. Onglet "Request" → Observer la requête HTTP :

GET /index.html HTTP/1.1
Host: localhost:8080
User-Agent: Mozilla/5.0
```

#### Étape 2 : Sélectionner la zone à fuzzer

**Principe** : Remplacer le nom du fichier (`index`) par des payloads de fuzzing. [zaproxy](https://www.zaproxy.org/docs/desktop/addons/fuzzer/dialogue/)

```
1. Dans l'onglet "Request", localiser la ligne :
   GET /index.html HTTP/1.1

2. Sélectionner (highlight) uniquement "index" (sans l'extension .html)
   GET /index.html
        ^^^^^

3. Clic droit sur la sélection → Fuzz...
```

**Résultat** : ZAP ouvre la fenêtre de configuration du Fuzzer.

### 4.3 Configurer le Fuzzer avec SecLists

#### Étape 3 : Ajouter un payload depuis SecLists

**SecLists** : Collection de wordlists pour pentest (noms de fichiers, répertoires, mots de passe, etc.). [forum.hackthebox](https://forum.hackthebox.com/t/help-with-question-proxies-zap-fuzzer/257933)

**Installation de SecLists** (si non installé) :
```bash
# Sur Kali Linux
sudo apt install seclists

# Emplacement par défaut
ls /usr/share/seclists/

# OU cloner depuis GitHub
git clone https://github.com/danielmiessler/SecLists.git
```

**Configuration dans ZAP** :

```
1. Fenêtre Fuzzer → Fuzz Locations tab
2. "Add..." → Add Payload
3. Type : File
4. File : Browse...
5. Naviguer vers : /usr/share/seclists/Discovery/Web-Content/common.txt
   OU : /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
6. OK
```

**Wordlists recommandées**  : [thehacker](https://www.thehacker.recipes/web/recon/directory-fuzzing)

| Wordlist | Taille | Cas d'usage |
|----------|--------|-------------|
| `common.txt` | ~4700 entrées | Pages/répertoires courants, rapide |
| `directory-list-2.3-small.txt` | ~87k entrées | Scan moyen, bon compromis |
| `directory-list-2.3-medium.txt` | ~220k entrées | Scan approfondi, plus long |
| `raft-small-files.txt` | ~11k fichiers | Spécifique aux fichiers |
| `raft-small-directories.txt` | ~20k répertoires | Spécifique aux répertoires |

#### Étape 4 : Lancer le fuzzing

```
1. Vérifier la configuration :
   - Fuzz Location : /[FUZZ].html
   - Payload : common.txt (4700 payloads)

2. Options (optionnel) :
   - Concurrent threads : 10 (par défaut, OK pour fuzzing simple)
   - Follow redirects : Activé

3. Start Fuzzer
```

**Résultat** : ZAP va tester :
```
GET /admin.html
GET /backup.html
GET /login.html
GET /test.html
... (4700 requêtes)
```

### 4.4 Analyser les résultats du Fuzzer

#### Étape 5 : Trier par code de réponse HTTP

**Problème** : Avec 4700 requêtes, difficile de trouver les pages existantes.

**Solution** : Trier par code HTTP pour identifier les pages trouvées. [subscription.packtpub](https://subscription.packtpub.com/book/security/9781801817332/2/ch02lvl1sec16/B18829_01.xhtml)

```
1. Onglet "Fuzzer" (en bas de ZAP) → Onglet Results
2. Cliquer sur la colonne "Code" pour trier
3. Observer les codes :
   - 200 OK : Page existe ✅
   - 404 Not Found : Page n'existe pas ❌
   - 403 Forbidden : Page existe mais accès interdit ⚠️
   - 301/302 : Redirection (peut être intéressant) ⚠️
```

**Filtrer les résultats** :

```
1. Clic droit sur l'en-tête de colonne → Filter
2. Afficher uniquement les codes : 200, 301, 302, 403
```

**Exemple de résultats** :

| URL | Code | Size | Interprétation |
|-----|------|------|----------------|
| `/admin.html` | 200 | 5432 | ✅ Page d'admin trouvée ! |
| `/backup.html` | 200 | 1234 | ✅ Page de backup accessible |
| `/config.php` | 403 | 287 | ⚠️ Existe mais accès interdit |
| `/test.html` | 404 | 162 | ❌ N'existe pas |
| `/login.html` | 301 | 0 | ⚠️ Redirige vers /login.php |

#### Étape 6 : Examiner les pages découvertes

```
1. Double-cliquer sur une ligne avec code 200
2. Onglet "Response" → Analyser le contenu HTML
3. Si intéressant, clic droit → Open in browser
```

**Exemple** : Page `/admin.html` trouvée → Tester pour escalade de privilèges.

***

## Partie 5 : Techniques avancées de fuzzing

### 5.1 Fuzzing de répertoires (sans extension)

**Cas d'usage** : Découvrir des répertoires comme `/admin/`, `/backup/`, `/uploads/`.

**Configuration** :

```
1. Requête de base : GET /test/ HTTP/1.1
2. Sélectionner "test" (sans le slash final)
3. Fuzz...
4. Payload : /usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt
5. Start Fuzzer
```

### 5.2 Fuzzing multi-extensions

**Cas d'usage** : Tester plusieurs extensions simultanément (.php, .html, .asp, .jsp).

**Méthode 1 : Wordlist personnalisée**

```bash
# Créer une wordlist avec extensions
cat /usr/share/seclists/Discovery/Web-Content/common.txt | \
while read line; do 
  echo "$line.php"
  echo "$line.html"
  echo "$line.asp"
done > multi-extensions.txt

# Utiliser dans ZAP
Payload : File → multi-extensions.txt
```

**Méthode 2 : Fuzzing imbriqué (avancé)**

```
1. Sélectionner : GET /index.html
2. Highlight "index" → Add Fuzz Location
3. Highlight ".html" → Add Fuzz Location
4. Payload 1 : common.txt (noms de fichiers)
5. Payload 2 : Custom list → .php, .html, .asp, .jsp
```

### 5.3 Fuzzing avec filtres personnalisés

**Cas d'usage** : Ignorer les erreurs 404 pour accélérer l'analyse. [owasp](https://owasp.org/www-project-web-security-testing-guide/latest/6-Appendix/C-Fuzzing)

**Configuration des Message Processors** :

```
1. Fuzzer Options → Message Processors
2. Add → Tag Creator
3. Tag name : "not_found"
4. String to match : "404" ou "Not Found"
5. OK
```

**Filtrer les résultats** :
```
1. Onglet Results → Clic droit sur colonne → Filter
2. Exclure tag "not_found"
```

***

## Partie 6 : Comparaison Spider vs Fuzzer

| Aspect | Spider | Fuzzer |
|--------|--------|--------|
| **Méthode** | Suit les liens HTML | Teste des noms de fichiers |
| **Pages trouvées** | Uniquement liées | Cachées et non liées |
| **Rapidité** | Rapide | Plus lent (milliers de requêtes) |
| **Bruit** | Faible | Élevé (beaucoup de 404) |
| **Détection** | Discret | Très visible (logs serveur) |
| **Utilisation** | Toujours en premier | Après le Spider |

**Workflow recommandé** :
```
1. Spider → Découvrir la structure logique du site
2. Analyse manuelle → Comprendre les fonctionnalités
3. Fuzzer → Trouver les pages cachées
4. Active Scan → Tester les vulnérabilités
```

***

## Partie 7 : Outils alternatifs pour le fuzzing

### 7.1 Gobuster (ligne de commande, très rapide)

```bash
# Installation
sudo apt install gobuster

# Fuzzing de répertoires
gobuster dir -u http://localhost:8080 -w /usr/share/seclists/Discovery/Web-Content/common.txt

# Fuzzing avec extensions
gobuster dir -u http://localhost:8080 -w common.txt -x php,html,txt

# Résultat :
# /admin.html          (Status: 200) [Size: 5432]
# /backup.html         (Status: 200) [Size: 1234]
```

### 7.2 Ffuf (moderne, très flexible)

```bash
# Installation
go install github.com/ffuf/ffuf@latest

# Fuzzing basique
ffuf -u http://localhost:8080/FUZZ.html -w common.txt

# Filtrer par code HTTP (ignorer 404)
ffuf -u http://localhost:8080/FUZZ.html -w common.txt -fc 404

# Fuzzing avec extensions multiples
ffuf -u http://localhost:8080/FUZZ -w common.txt -e .php,.html,.asp
```

### 7.3 Dirb (classique, simple)

```bash
# Installation
sudo apt install dirb

# Fuzzing basique
dirb http://localhost:8080 /usr/share/wordlists/dirb/common.txt

# Avec extensions
dirb http://localhost:8080 common.txt -X .php,.html
```

***

## Partie 8 : Méthodologie complète de scan web

### 8.1 Checklist de reconnaissance web

1. ✅ **Configuration du lab** : Démarrer Docker avec `-d` et `-v`
2. ✅ **Proxy ZAP** : Configurer le navigateur
3. ✅ **Créer un contexte** : Définir le scope de test
4. ✅ **Mode Protected** : Éviter les attaques accidentelles
5. ✅ **Spider** : Découvrir les pages liées (rapide)
6. ✅ **Analyse manuelle** : Explorer les fonctionnalités
7. ✅ **Fuzzer** : Découvrir les pages cachées (lent mais complet)
8. ✅ **Trier les résultats** : Par code HTTP (200, 403, 301)
9. ✅ **Investigation** : Examiner les pages trouvées
10. ✅ **Active Scan** : Tester les vulnérabilités (prochaine étape)

### 8.2 Optimisation des scans

**Stratégie progressive** :

```
1. Spider rapide (1-2 min) → Vue d'ensemble
2. Fuzzing léger (common.txt, ~5 min) → Pages évidentes
3. Analyse manuelle (10-20 min) → Comprendre l'application
4. Fuzzing approfondi (directory-list-medium.txt, ~30 min) → Pages cachées
```

**Éviter la détection** :
- Ralentir le fuzzing : Delay entre requêtes (500ms - 1s)
- Changer le User-Agent : Imiter un navigateur normal
- Limiter les threads : 1-5 threads au lieu de 10-20

***

## Résumé : Points clés à retenir

1. **Docker `-d`** : Daemon mode (arrière-plan), libère le terminal
2. **Docker `-v`** : Monte un volume local dans le conteneur (partage de fichiers)
3. **Contexte ZAP** : Définit le périmètre de scan (scope)
4. **Spider** : Découvre les pages **liées** en suivant les liens HTML
5. **Fuzzer** : Découvre les pages **cachées** en testant des noms courants
6. **SecLists** : Wordlists de référence pour le fuzzing de contenu web
7. **Trier par code HTTP** : 200 = trouvé, 404 = absent, 403 = existe mais interdit
8. **Workflow** : Spider d'abord (rapide), Fuzzer ensuite (complet)

