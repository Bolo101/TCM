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

