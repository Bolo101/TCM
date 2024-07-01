	LOOKING AT TEXT FILES:MORE OR LESS
  Less anables to look for a special string by insering '/[pattern_to_find]'. Press 'n' to get next result.Some command as VIM.


Mount:
'df -h' display the disk file system usage on the mounted partitions
'du -sh [file or directory]' display the disk usage of a file or directory

How to mount a device
'sudo fdisk -l' list partitions, unmounted partitions have different output. It is the last one
'mount [location in /dev] [location to mount the device]'. Do not forget to creaty the mounting directory

To formate a USB:
'sudo umount [location in /dev]'
In NTFS:
  'sudo mkfs.ntfs /dev/sdb1'
In FAT:
  'sudo mkfs.vfat /dev/sdb1'

Obtenir IP publique:
curl ifconfig.me

Get disk size:
lsblk -o SIZE /dev/sda

Internet: (network manager cli)
nmcli device wifi list
nmcli device wifi connet SSID

Read the first 10 lines from a file:
$head <file>
$head -n 5 <file>

Read the last 10 lines from a file:
$tail <file>
$tail -5 <file>

Read file being modified with change sync:
$tail -f <file>

Read two files and display where there is a difference:
diff <file1.txt> <file2.txt>

LINKS :
Hard link points to the physical location of the file on storage. Even if the file is deleted or moved we still can access the file while the hard link is not deleted
Create hard link:
$ln <file> < file_hard_link>
We can also create a soft link wich is not going to work if the file is deleted or moved
$ln -s <file_solf> <file>
You cannot link a hard link to a directory but you can with a soft link


Find the files whose name started with 'file' in the directory and subdirectories:
$find . -name 'file*.txt'

Change owner of the file to bolo:
$chown bolo file.txt
or
$chgrp bolo file.txt

Read a file that requires another user privilege
$sudo -u <username>


/etc/passwd 	/etc/group
/etc/shadow

# Redirect input and output
$find / -name "text.txt" > result.txt 2>&1 //redirect error output in the same file as normal output redirection using &1

# Pipes
Used to connect the standard out from one command to the standard in of another command
$ls -l /etc | less
To redirect std err use |&

# Command history
Execute last command 
$!-1
$!!

# Command substitution
Cannot redirect std in input for ls using the following syntax $ ls -l < file.txt. It considers the redirection as an argument
We need to use command substitution
Let's we got a file containing several files names.
$ls -l 'cat register-file.txt' //register-file contains the files' names contained in the directory

# Searching and processing text
## grep
$grep bo wordlist.txt // look for bobo in the texte file wordlist.txt

We can print result that does not contain the letter e
$grep -v e wordlist.txt

Can display the lines before the matching line using -A and the lin after using -B
$grep error -A 3 wordlist.txt

## sort
Used to sort in alphabetical order

Can sort number in decremental order
$sort -nr numbers.txt

## uniq
sort and remove adjacent duplicates

We need to sort first and then pipe with uniq to remove adjacent duplicates

$sort file.txt | uniq 

## wci
print the number of lines, words and bytes in a file
$grep bob wordlist.txt | wc

# Manipulating text
## sedi
Manipulates text as it flows by.

### text substitution
$sed 's/Suite/Ste/' text.txt //substitute the word Suite by Ste in the file file text.txt. Only change the first instance
We need to add a global G to make it recursif
$sed 's/Suite/Ste/g' text.txt

We can also target specific occurence
$sed '$s/Suite/Ste/'

Delete line when pattern is found
$sed 'Suite/d' text.txt

Find mathcing pattern in a line and modify targeted word
$seg '/ee s/Suite/Ste/g' sample.txt    // change Suite to Ste in line where ee is found in a word

$ sign is used to target the end of line and \n to jump a line

## awk
$echo linux bob sally | awk '{print $2}' // prints bob
$echo linux bob sally | awk '{print $3, "likes", $1}'

By default awk use the " " as a delimeter but we can specify a new delimeter using -F
$awk -F ',' 'print{$1}' sample.txt

## tr
Used to change patterns
$cat sample.txt |tr ',' '\t' // change all , into a tab space

$cat sample.txt | tr 'a-z' 'A-Z' //change lowercase to uppercase

# Networking
Perform DNS lookup on a domain name
$dig google.com
$nslookup google.com 

Reverse DNS to obtain domain name based on IP address
$dig -x 8.8.8.8

See all TCP connections
$netstat -at

See listening TCP ports
$netstat -lt // after launching a http server using $ python -m http.server

# File transfert utilities
## scp
$scp file username@ip:/home/bob // if file is a directory add -r for recursivity
username is not necessary to provide if the username is the same as the one sending the files

## rsync 
Better to copy several files on the network
It computes the difference between source file and destination file to only transfer missing files or modified files
$rsync -avzh file.txt 192.168.1.12:/home/bolo 
-a is for archive mode. Ti enables to transfer directories recursively and preserve user permissions and ownership
-z is for compression

# COnverting files
DOS uses  Control Line Feed for line termination
MACOS uses Control for line termination 
Linux uses the normal line termination for Linux which is a line feed

We can see thse details using the file command
When opening a file with vim we can read the linux line termination of linux files using:
In normal mode :
:e ++ff=unix

We can convert files using commands 
## Unix -> Windows format:
cp file1.txt temp.txt
$unix2dos temp.txt
We can use -n to create a new file with the changes 
$unix2dos -n sample.txt newfile.txt

## Unix -> MAC
Can convert to MAC:
$unix2dos -c mac temp.txt

## Dos -> Unix
dos2unix temp.txt 

# Text editors (only vim nano is sh**)
## Searching for letters
/searchCharacter
use lowercase n to go to next match. Uppercase N to go to previous match

# Process management
## Monitor running processes
### ps
$ps -ax | less -S //S enables to chope output wider than the screen size
The previous command displaysthe processes for all users using the BSD syntax

$ps -e | less -S // processes for users using the Unix syntax
$ps aux |less -S // for BSD format
$ps -ef | less -S //for Unix format

First column display the user ID, second is process ID, third column is parent ID
TTY indicates the terminal used to control the process. ? means not associated terminal

## Display process hierarchy:
$pstree | less -S 

## Monitor used ressources linked to running process
$top

