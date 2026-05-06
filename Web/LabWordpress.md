# Cours : Pentest Web - Docker Compose, WordPress et énumération de login

## Introduction

Cette section couvre :
- **Docker Compose** : Orchestration de conteneurs multiples (WordPress + MySQL)
- **Analyse de fichier YAML** : Comprendre la structure des services
- **Énumération WordPress** : Exploiter les fuites d'information des messages d'erreur
- **Fuzzing de login** : Identifier usernames valides puis brute-force des mots de passe [afundi](https://afundi.im/post/wordpress-username-enumeration)

**⚠️ Important** : N'utilisez ces techniques que sur des environnements autorisés.

***

## Partie 1 : Docker Compose - Orchestration multi-conteneurs

### 1.1 Installation de Docker Compose

**Cas d'usage** : Gérer plusieurs conteneurs liés (application web + base de données) sans configuration manuelle des connexions. [github](https://github.com/docker/awesome-compose/blob/master/official-documentation-samples/wordpress/README.md)

```bash
# Installation du plugin Docker Compose
sudo apt install -y docker-compose-plugin

# Vérifier l'installation
docker compose version
# Résultat : Docker Compose version v2.24.0
```

**Différence avec docker run** :

| Commande | Conteneurs | Configuration | Connexions |
|----------|------------|---------------|------------|
| `docker run` | Un seul | Manuelle (CLI) | Manuelles (--link) |
| `docker compose` | Multiples | Fichier YAML | Automatiques (networks) |

### 1.2 Avantages de Docker Compose

**Sans Docker Compose** (2 conteneurs séparés)  : [shawnmullings](https://www.shawnmullings.com/post/engineering/Setting-up-WordPress-phpMyAdmin-and-MySQL-with-Docker-Compose/)

```bash
# 1. Créer un réseau
docker network create wordpress-network

# 2. Lancer MySQL
docker run -d --name mysql \
  --network wordpress-network \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wppass \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  mysql:latest

# 3. Lancer WordPress
docker run -d --name wordpress \
  --network wordpress-network \
  -p 8080:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wppass \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress:latest
```

**Avec Docker Compose** : Une seule commande !

```bash
docker compose up -d
```

***

## Partie 2 : Analyse du fichier docker-compose.yml (Section 3-4)

### 2.1 Structure YAML de base

**YAML** : Yet Another Markup Language (ou "YAML Ain't Markup Language") - Langage de configuration lisible par l'humain. [gist.github](https://gist.github.com/bradtraversy/faa8de544c62eef3f31de406982f1d42)

**Fichier docker-compose.yml** :

```yaml
version: '3.8'

services:
  db:
    image: mysql:latest
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppassword
    networks:
      - wordpress-network

  wordpress:
    depends_on:
      - db
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppassword
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - ./wp-content:/var/www/html/wp-content
    networks:
      - wordpress-network

volumes:
  db_data:

networks:
  wordpress-network:
```

### 2.2 Explication détaillée du fichier

#### Section `services`

**Définition** : Chaque service = un conteneur (ou groupe de conteneurs). [digitalocean](https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-docker-compose)

**Service `db` (MySQL)** :

```yaml
db:
  image: mysql:latest                    # Image Docker officielle MySQL
  volumes:
    - db_data:/var/lib/mysql            # Persistance des données
  environment:
    MYSQL_ROOT_PASSWORD: rootpassword   # Mot de passe root
    MYSQL_DATABASE: wordpress           # Créer base de données "wordpress"
    MYSQL_USER: wpuser                  # Créer utilisateur "wpuser"
    MYSQL_PASSWORD: wppassword          # Mot de passe de wpuser
  networks:
    - wordpress-network                 # Connecter au réseau
```

**Explication clé** :
- **volumes** : `db_data` est un volume nommé qui persiste les données MySQL
- Sans volume, les données seraient perdues au redémarrage du conteneur
- `/var/lib/mysql` : Répertoire où MySQL stocke ses bases de données [shawnmullings](https://www.shawnmullings.com/post/engineering/Setting-up-WordPress-phpMyAdmin-and-MySQL-with-Docker-Compose/)

**Service `wordpress`** :

```yaml
wordpress:
  depends_on:
    - db                                # Démarre APRÈS le service "db"
  image: wordpress:latest               # Image WordPress officielle
  ports:
    - "8080:80"                         # Port 8080 (host) → 80 (conteneur)
  environment:
    WORDPRESS_DB_HOST: db:3306          # Connexion à MySQL via nom "db"
    WORDPRESS_DB_USER: wpuser
    WORDPRESS_DB_PASSWORD: wppassword
    WORDPRESS_DB_NAME: wordpress
  volumes:
    - ./wp-content:/var/www/html/wp-content  # Synchroniser plugins/themes
  networks:
    - wordpress-network
```

**Explication clé** :
- **depends_on** : WordPress attend que MySQL soit démarré [digitalocean](https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-docker-compose)
- **WORDPRESS_DB_HOST: db:3306** : "db" est le nom du service MySQL (résolution DNS automatique)
- **volumes** : Synchronisation du répertoire local avec le conteneur (développement)

#### Section `volumes`

```yaml
volumes:
  db_data:                              # Volume nommé pour persistance MySQL
```

**Fonctionnement** : Docker crée un volume géré automatiquement. [github](https://github.com/docker/awesome-compose/blob/master/official-documentation-samples/wordpress/README.md)

**Vérification** :
```bash
docker volume ls
# DRIVER    VOLUME NAME
# local     3-4_db_data
```

**Localisation** :
```bash
docker volume inspect 3-4_db_data
# "Mountpoint": "/var/lib/docker/volumes/3-4_db_data/_data"
```

#### Section `networks`

```yaml
networks:
  wordpress-network:                    # Réseau privé pour les conteneurs
```

**Fonctionnement** : Docker crée un réseau virtuel isolé permettant la communication entre conteneurs. [github](https://github.com/docker/awesome-compose/blob/master/official-documentation-samples/wordpress/README.md)

**Avantage** : WordPress peut contacter MySQL via le nom "db" au lieu d'une IP.

### 2.3 Lancer le stack avec Docker Compose

#### Démarrage

```bash
# Aller dans le répertoire contenant docker-compose.yml
cd 3-4

# Lancer les services en arrière-plan
docker compose up -d

# -d : Detached mode (arrière-plan)
```

**Sortie typique** :
```
[+] Running 3/3
 ✔ Network 3-4_wordpress-network    Created
 ✔ Container 3-4-db-1               Started
 ✔ Container 3-4-wordpress-1        Started
```

#### Vérification

```bash
# Lister les conteneurs actifs
docker compose ps

# NAME                IMAGE              STATUS          PORTS
# 3-4-db-1            mysql:latest       Up 2 minutes    3306/tcp
# 3-4-wordpress-1     wordpress:latest   Up 2 minutes    0.0.0.0:8080->80/tcp

# Vérifier les logs
docker compose logs wordpress
docker compose logs db
```

#### Accéder à WordPress

```
http://localhost:8080
```

**Résultat** : Page d'installation WordPress.

#### Arrêt et nettoyage

```bash
# Arrêter les services
docker compose down

# Arrêter ET supprimer les volumes (⚠️ perte de données)
docker compose down -v
```

***

## Partie 3 : Reconnaissance WordPress avec ZAP

### 3.1 Analyse des technologies avec Wappalyzer

**Problème observé** : ZAP peut afficher des informations de version inexactes. [afundi](https://afundi.im/post/wordpress-username-enumeration)

**Solution** : Utiliser **Wappalyzer** (extension navigateur) pour confirmation. [afundi](https://afundi.im/post/wordpress-username-enumeration)

**Installation** :
```
1. Extension Firefox/Chrome : "Wappalyzer"
2. Naviguer sur http://localhost:8080
3. Cliquer sur l'icône Wappalyzer
```

**Informations récupérées** :
- CMS : WordPress 6.x
- Serveur : Apache 2.4.x
- Langage : PHP 8.x
- Base de données : MySQL (déduit)

**Avantage** : Wappalyzer est souvent plus précis que la détection automatique de ZAP.

### 3.2 Configuration du contexte ZAP

```
1. ZAP → Naviguer vers http://localhost:8080 (via proxy)
2. Onglet "Sites" → Clic droit sur "http://localhost:8080"
3. Include in Context → New Context : "WordPress Lab"
4. OK
```

### 3.3 Spider - Découverte automatique

**Lancement** :
```
1. Clic droit sur "http://localhost:8080"
2. Attack → Spider...
3. Start Scan
```

**Pages découvertes** (exemples) :
- `/index.php`
- `/wp-login.php` ← **Page de login trouvée !**
- `/wp-admin/`
- `/wp-content/themes/`
- `/wp-json/wp/v2/users` ← **Énumération utilisateurs (API REST)** [inspectwp](https://inspectwp.com/en/knowledge-base/how-to-prevent-user-enumeration-wordpress)

**Observation clé** : Le Spider a trouvé `wp-login.php` et a même tenté une requête POST automatique avec credentials "ZAP:ZAP".

***

## Partie 4 : Énumération de usernames WordPress

### 4.1 Vulnérabilité des messages d'erreur différenciés

**Problème de sécurité WordPress** : Les messages d'erreur révèlent si un username existe. [invicti](https://www.invicti.com/web-application-vulnerabilities/wordpress-username-enumeration)

#### Test manuel sur wp-login.php

**Tentative 1 : Username invalide**

```
Username : unknownuser
Password : test123
```

**Message d'erreur** :
```
ERROR: The username "unknownuser" is not registered on this site.
```

**Tentative 2 : Username valide, mauvais mot de passe**

```
Username : admin
Password : wrongpassword
```

**Message d'erreur** :
```
ERROR: The password you entered for the username admin is incorrect.
```

**Conclusion** : WordPress **confirme l'existence du username "admin"** ! [invicti](https://www.invicti.com/web-application-vulnerabilities/wordpress-username-enumeration)

**Impact sécurité** :
- Un attaquant peut énumérer tous les usernames valides
- Réduit la complexité d'une attaque brute force (seulement les mots de passe)
- Facilite le phishing ciblé

### 4.2 Autres vecteurs d'énumération WordPress

#### API REST (wp-json) [inspectwp](https://inspectwp.com/en/knowledge-base/how-to-prevent-user-enumeration-wordpress)

```bash
# Lister tous les utilisateurs ayant publié
curl http://localhost:8080/wp-json/wp/v2/users

# Résultat JSON :
[
  {
    "id": 1,
    "name": "admin",
    "slug": "admin",
    "description": "",
    "link": "http://localhost:8080/author/admin/"
  }
]
```

**Exploitation** : Pas d'authentification requise par défaut !

#### Author archives (?author=N) [acunetix](https://www.acunetix.com/vulnerabilities/web/wordpress-username-enumeration/)

```
http://localhost:8080/?author=1

# Redirige vers :
http://localhost:8080/author/admin/
```

**Résultat** : Le username "admin" est révélé dans l'URL.

***

## Partie 5 : Fuzzing de usernames avec ZAP

### 5.1 Intercepter la requête POST de login

**Workflow** :

```
1. ZAP → Activer le proxy
2. Naviguer vers http://localhost:8080/wp-login.php
3. Soumettre : Username = "ZAP" / Password = "test"
4. ZAP intercepte la requête POST
```

**Requête POST capturée** :

```http
POST /wp-login.php HTTP/1.1
Host: localhost:8080
Content-Type: application/x-www-form-urlencoded

log=ZAP&pwd=test&wp-submit=Log+In&testcookie=1
```

**Paramètres importants** :
- `log` : Username
- `pwd` : Password
- `wp-submit` : Bouton de soumission

### 5.2 Configurer le fuzzing de username

#### Étape 1 : Sélectionner la position à fuzzer

```
1. Onglet "History" → Sélectionner la requête POST vers /wp-login.php
2. Onglet "Request" → Localiser : log=ZAP
3. Highlight uniquement "ZAP" (le username)
4. Clic droit → Fuzz...
```

#### Étape 2 : Ajouter des payloads manuels

**Cas d'usage** : Tester des usernames courants WordPress. [hailbytes](https://hailbytes.com/how-to-brute-force-website-login-with-owasp-zap/)

```
1. Fenêtre Fuzzer → Add...
2. Type : Strings
3. Ajouter manuellement :
   - admin
   - administrator
   - user
   - wordpress
   - test
   - root
   - webmaster

4. OK
```

**Alternative : Wordlist** :
```
1. Type : File
2. File : /usr/share/seclists/Usernames/top-usernames-shortlist.txt
3. OK
```

### 5.3 Configurer le Message Processor (Tag Creator)

**Objectif** : Taguer automatiquement les réponses contenant "not registered" pour filtrer les usernames invalides. [zaproxy](https://www.zaproxy.org/blog/2025-04-09-portswigger-labs-broken-brute-force-protection-ip-block/)

#### Étape 3 : Ajouter un Tag Creator

```
1. Fuzzer Options → Message Processors
2. Add → Tag Creator
3. Configuration :
   - Tag name : "not_registered"
   - String to match : "not registered"
   - Case sensitive : Non
   - Apply to : Response body

4. Add
```

**Fonctionnement** : Toutes les réponses contenant "not registered" seront taguées.

### 5.4 Lancer le fuzzing de username

```
1. Vérifier la configuration :
   - Fuzz Location : log=[FUZZ]
   - Payloads : 7 usernames
   - Message Processor : Tag "not_registered"

2. Start Fuzzer
```

### 5.5 Analyser les résultats

#### Trier par tag

```
1. Onglet "Fuzzer" → Results
2. Cliquer sur colonne "Tags" pour trier
3. Observer :
   - "not_registered" : Username inexistant ❌
   - Pas de tag : Username valide ✅
```

**Exemple de résultats** :

| Username | Code | Size | Tags | Interprétation |
|----------|------|------|------|----------------|
| admin | 200 | 5432 | (aucun) | ✅ Username valide ! |
| administrator | 200 | 4987 | not_registered | ❌ Inexistant |
| user | 200 | 4987 | not_registered | ❌ Inexistant |
| wordpress | 200 | 4987 | not_registered | ❌ Inexistant |
| test | 200 | 4987 | not_registered | ❌ Inexistant |

**Conclusion** : Le username **"admin"** existe !

#### Vérification manuelle

```
1. Double-cliquer sur la ligne "admin"
2. Onglet "Response" → Rechercher "incorrect"
3. Confirmer le message : "The password you entered for the username admin is incorrect."
```

***

## Partie 6 : Fuzzing de mots de passe

### 6.1 Préparer la nouvelle attaque

**Objectif** : Maintenant qu'on connaît le username valide ("admin"), fuzzer le mot de passe. [hailbytes](https://hailbytes.com/how-to-brute-force-website-login-with-owasp-zap/)

#### Étape 1 : Sélectionner la requête avec username valide

```
1. Onglet "Fuzzer Results" → Sélectionner la ligne "admin"
2. Clic droit → Open/Resend with Request Editor...
```

**Requête affichée** :

```http
POST /wp-login.php HTTP/1.1
Host: localhost:8080
Content-Type: application/x-www-form-urlencoded

log=admin&pwd=test&wp-submit=Log+In&testcookie=1
```

#### Étape 2 : Fuzzer le mot de passe

```
1. Dans la requête, localiser : pwd=test
2. Highlight uniquement "test" (le mot de passe)
3. Clic droit → Fuzz...
```

#### Étape 3 : Charger une wordlist de mots de passe

```
1. Add...
2. Type : File
3. File : /usr/share/wordlists/rockyou.txt
   OU : /usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt

4. OK
```

### 6.2 Configurer le Message Processor pour les échecs

**Nouveau tag** : Identifier les tentatives échouées.

```
1. Fuzzer Options → Message Processors
2. Add → Tag Creator
3. Configuration :
   - Tag name : "incorrect_password"
   - String to match : "incorrect"
   - Case sensitive : Non

4. Add
```

**Alternative - Grep Match** :

```
1. Fuzzer Options → Message Processors
2. Add → Tag Creator
3. Tag name : "success"
4. String to match : "Dashboard" ou "wp-admin"
   (Texte présent uniquement après connexion réussie)
```

### 6.3 Gérer les limitations (Rate Limiting & Lockout)

**Problème WordPress** : Après X tentatives échouées, le compte peut être bloqué temporairement (si plugin de sécurité installé). [afundi](https://afundi.im/post/wordpress-username-enumeration)

**Solutions** :

#### Option 1 : Ralentir l'attaque

```
1. Fuzzer Options → Advanced
2. Threads per Scan : 1
3. Delay between requests : 500 ms (ou plus)
```

#### Option 2 : Désactiver les plugins de sécurité (environnement de lab)

```bash
# Accéder au conteneur WordPress
docker compose exec wordpress bash

# Renommer le dossier plugins (désactive tous les plugins)
mv /var/www/html/wp-content/plugins /var/www/html/wp-content/plugins.bak

# Relancer l'attaque

# Restaurer après
mv /var/www/html/wp-content/plugins.bak /var/www/html/wp-content/plugins
```

### 6.4 Lancer le fuzzing de mot de passe

```
1. Configuration :
   - Fuzz Location : pwd=[FUZZ]
   - Payloads : rockyou.txt (14M passwords)
   - Tags : "incorrect_password" et "success"
   - Threads : 1
   - Delay : 500ms

2. Start Fuzzer
```

**⚠️ Temps estimé** : Avec rockyou.txt complet (14M) et 500ms de délai, l'attaque prendrait ~80 jours ! Utiliser une wordlist réduite pour les labs.

### 6.5 Analyser les résultats

#### Filtrer les succès

```
1. Onglet "Fuzzer Results"
2. Filtrer :
   - Exclure tag "incorrect_password"
   - OU Afficher seulement tag "success"
   - OU Trier par "Size" (réponse différente si succès)
```

**Exemple de résultat positif** :

| Password | Code | Size | Tags | Interprétation |
|----------|------|------|------|----------------|
| admin123 | 302 | 0 | success | ✅ Mot de passe trouvé ! |
| password | 200 | 4987 | incorrect_password | ❌ Échec |
| 123456 | 200 | 4987 | incorrect_password | ❌ Échec |

**Code 302** : Redirection vers `/wp-admin/` → Connexion réussie !

#### Vérification manuelle

```
1. Navigateur → http://localhost:8080/wp-login.php
2. Username : admin
3. Password : admin123
4. Submit

Résultat : Accès au tableau de bord WordPress ✅
```

***

## Partie 7 : Protection contre l'énumération WordPress

### 7.1 Recommandations de sécurité

#### 1. Messages d'erreur génériques [invicti](https://www.invicti.com/web-application-vulnerabilities/wordpress-username-enumeration)

**Problème actuel** :
```
ERROR: The username "test" is not registered on this site.
ERROR: The password you entered for the username admin is incorrect.
```

**Solution** : Message unique pour tous les cas :
```
ERROR: Invalid username or password.
```

**Implémentation** (functions.php) :
```php
add_filter('login_errors', function() {
    return 'Invalid username or password.';
});
```

#### 2. Désactiver l'API REST users endpoint [inspectwp](https://inspectwp.com/en/knowledge-base/how-to-prevent-user-enumeration-wordpress)

```php
// Bloquer /wp-json/wp/v2/users
add_filter('rest_endpoints', function($endpoints) {
    if (isset($endpoints['/wp/v2/users'])) {
        unset($endpoints['/wp/v2/users']);
    }
    return $endpoints;
});
```

#### 3. Bloquer author enumeration (?author=N) [acunetix](https://www.acunetix.com/vulnerabilities/web/wordpress-username-enumeration/)

**.htaccess** :
```apache
# Bloquer ?author=N
RewriteCond %{QUERY_STRING} ^author=([0-9]*)
RewriteRule ^(.*)$ / [R=301,L]
```

#### 4. Utiliser des plugins de sécurité [afundi](https://afundi.im/post/wordpress-username-enumeration)

**Wordfence** (gratuit) :
- Brute force protection
- Login attempt limiting
- Two-factor authentication
- Firewall

**Installation** :
```
1. WordPress Admin → Plugins → Add New
2. Rechercher "Wordfence"
3. Install → Activate
4. Wordfence → Options → Enable brute force protection
```

#### 5. Utiliser des usernames non-évidents

**Mauvais** : admin, administrator, root, webmaster
**Bon** : j0hn_d03_2024, wp_user_a1b2c3

***

## Partie 8 : Méthodologie complète d'attaque WordPress

### 8.1 Checklist de pentest WordPress

1. ✅ **Reconnaissance passive**
   - Wappalyzer : Technologies utilisées
   - /wp-json/wp/v2/users : Énumération API
   - /?author=1 : Author enumeration
   - View source : Version WordPress dans meta tags

2. ✅ **Spider ZAP**
   - Découvrir wp-login.php, wp-admin, etc.

3. ✅ **Énumération de usernames**
   - Fuzzer wp-login.php avec usernames courants
   - Taguer "not registered" pour filtrer

4. ✅ **Brute force password**
   - Fuzzer avec wordlist (top-1000 → rockyou.txt)
   - Taguer "incorrect" pour filtrer
   - Ralentir si rate limiting

5. ✅ **Post-exploitation**
   - Accès admin → Upload shell PHP
   - Modifier thème → Backdoor
   - Accès base de données → Dump credentials

### 8.2 Optimisation de l'attaque

**Stratégie progressive** :

```
1. Usernames courants (admin, administrator) - 30 secondes
2. Top-100 passwords (password, 123456, admin123) - 1 minute
3. Top-1000 passwords - 10 minutes
4. Rockyou.txt complet (si nécessaire) - Plusieurs heures/jours
```

**Commande pour extraire top passwords** :
```bash
head -1000 /usr/share/wordlists/rockyou.txt > top1000.txt
```

***

## Résumé : Points clés à retenir

1. **Docker Compose** : Orchestre plusieurs conteneurs avec un fichier YAML [digitalocean](https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-docker-compose)
2. **YAML services** : Chaque service = un conteneur (db, wordpress)
3. **volumes** : Persistance des données (`db_data:/var/lib/mysql`)
4. **depends_on** : Ordre de démarrage (WordPress après MySQL)
5. **WordPress username enumeration** : Messages d'erreur différenciés révèlent usernames valides [invicti](https://www.invicti.com/web-application-vulnerabilities/wordpress-username-enumeration)
6. **ZAP Tag Creator** : Filtrer automatiquement les réponses (success/failure)
7. **Fuzzing en 2 étapes** : D'abord usernames, puis passwords
8. **Protection** : Messages génériques, désactiver API REST users, plugins sécurité [inspectwp](https://inspectwp.com/en/knowledge-base/how-to-prevent-user-enumeration-wordpress)
