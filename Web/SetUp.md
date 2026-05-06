# Cours : Virtualisation - Hyperviseurs et QEMU/KVM
## Introduction
Cette section couvre :
- **Types d'hyperviseurs** : Type 1 (bare metal) vs Type 2 (software)
- **Configuration Hyper-V** (Windows)
- **QEMU/KVM/libvirt** : Virtualisation sur Linux
- **Gestion des VMs avec virsh** : Commandes en ligne
- **Permissions Docker** : Éviter sudo

***
## Partie 1 : Hyperviseurs - Concepts fondamentaux
### 1.1 Qu'est-ce qu'un hyperviseur ?
**Définition** : Un **hyperviseur** est un logiciel qui crée et gère des machines virtuelles (VMs). Il contrôle l'allocation des ressources matérielles (CPU, RAM, stockage, réseau) entre plusieurs VMs. [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)

**Analogie** : L'hyperviseur est comme un chef d'orchestre qui coordonne plusieurs musiciens (VMs) jouant simultanément sur le même instrument (matériel physique).
### 1.2 Type 1 Hypervisor : Bare Metal
**Définition** : L'hyperviseur s'exécute **directement sur le matériel physique**, sans système d'exploitation intermédiaire. [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)

**Architecture**  :
```
┌─────────────────────────────────┐
│   VM 1    │   VM 2    │   VM 3  │  ← Machines virtuelles
├─────────────────────────────────┤
│       Type 1 Hypervisor         │  ← Directement sur le hardware
├─────────────────────────────────┤
│      Physical Hardware          │  ← CPU, RAM, Disque, Réseau
└─────────────────────────────────┘
```

**Caractéristiques**  : [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)
- **Performances élevées** : Accès direct au matériel, pas de couche OS intermédiaire
- **Sécurité renforcée** : Isolation complète entre VMs
- **Stabilité** : Moins de points de défaillance
- **Complexité** : Nécessite des connaissances admin système

**Exemples**  : [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)
- **VMware ESXi** (entreprise)
- **Microsoft Hyper-V** (Windows Server)
- **KVM** (Linux, intégré au noyau)
- **Xen** (open-source)
- **Proxmox VE** (basé sur KVM)

**Cas d'usage**  : [stormagic](https://stormagic.com/company/blog/type-1-vs-type-2-hypervisors/)
- Datacenters et cloud (AWS, Azure, Google Cloud)
- Environnements de production
- Serveurs d'entreprise
- Workloads critiques et gourmands en ressources
### 1.3 Type 2 Hypervisor : Hosted/Embedded
**Définition** : L'hyperviseur s'exécute **comme une application** au-dessus d'un système d'exploitation hôte (Windows, macOS, Linux). [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)

**Architecture**  :
```
┌─────────────────────────────────┐
│   VM 1    │   VM 2    │   VM 3  │  ← Machines virtuelles
├─────────────────────────────────┤
│       Type 2 Hypervisor         │  ← Application
├─────────────────────────────────┤
│        Host OS (Windows/Linux)  │  ← Système d'exploitation hôte
├─────────────────────────────────┤
│      Physical Hardware          │  ← CPU, RAM, Disque, Réseau
└─────────────────────────────────┘
```

**Caractéristiques**  : [biztechmagazine](https://biztechmagazine.com/article/2024/08/type-1-vs-type-2-hypervisors-whats-difference-perfcon)
- **Facile à installer** : Installation comme n'importe quelle application
- **Performances réduites** : Overhead de l'OS hôte
- **Flexibilité** : Peut coexister avec applications natives
- **Portabilité** : VMs facilement transférables

**Exemples**  : [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)
- **Oracle VirtualBox** (gratuit, open-source)
- **VMware Workstation** (Windows/Linux)
- **VMware Fusion** (macOS)
- **Microsoft Virtual PC** (Windows)
- **Parallels Desktop** (macOS)

**Cas d'usage**  : [stormagic](https://stormagic.com/company/blog/type-1-vs-type-2-hypervisors/)
- Développement et tests
- Environnements de lab (pentest, formation)
- Postes de travail (desktop virtualization)
- Démonstrations et POCs
### 1.4 Comparaison Type 1 vs Type 2
| Critère | Type 1 (Bare Metal) | Type 2 (Hosted) |
|---------|---------------------|-----------------|
| **Installation** | Sur hardware nu | Sur OS hôte |
| **Performances** | Excellentes (accès direct) | Bonnes (overhead OS) |
| **Sécurité** | Très élevée | Dépend de l'OS hôte |
| **Complexité** | Élevée (admin système) | Faible (utilisateur standard) |
| **Coût** | Souvent payant (ESXi, Hyper-V Server gratuit) | Gratuit (VirtualBox) ou payant |
| **Cas d'usage** | Production, datacenter | Dev, test, desktop |
| **Exemples** | ESXi, Hyper-V, KVM, Xen | VirtualBox, VMware Workstation |

***
## Partie 2 : Configuration Hyper-V (Windows)
### 2.1 Activation de Hyper-V
**Prérequis**  : [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)
- Windows 10/11 Pro, Enterprise ou Education (pas Home)
- Processeur avec virtualisation matérielle (Intel VT-x ou AMD-V)
- Minimum 4 Go RAM

**Étapes d'installation** :

#### Méthode 1 : Interface graphique

```
1. Panneau de configuration
2. Programmes et fonctionnalités
3. Activer ou désactiver des fonctionnalités Windows
4. ✅ Cocher "Hyper-V" (toutes les sous-options)
5. OK
6. Redémarrer l'ordinateur
```

#### Méthode 2 : PowerShell (admin)

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

**Vérification** :
```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
```
### 2.2 Lancer Hyper-V Manager
```
1. Menu Démarrer → Rechercher "Hyper-V Manager"
2. OU : Win+R → virtmgmt.msc
```
### 2.3 Créer une VM dans Hyper-V
```
1. Hyper-V Manager → Action → New → Virtual Machine
2. Wizard :
   - Name : Ubuntu-Server
   - Generation : 2 (UEFI)
   - Memory : 4096 MB
   - Networking : Default Switch
   - Hard Disk : 20 GB (VHD dynamique)
   - Installation Options : ISO → Parcourir ubuntu-server.iso
3. Finish
```

***
## Partie 3 : QEMU/KVM/libvirt sur Linux
### 3.1 Architecture de la stack de virtualisation
**Composants**  : [bdrshield](https://www.bdrshield.com/blog/qemu-kvm-and-libvirt-installation-and-configuration/)
- **KVM** (Kernel-based Virtual Machine) : Module du noyau Linux, hypervisor Type 1
- **QEMU** : Émulateur de machine, fournit les périphériques virtuels
- **libvirt** : API de gestion de VMs
- **virt-manager** : Interface graphique
- **virsh** : Outil en ligne de commande

**Schéma** :
```
┌──────────────────────────────────┐
│  virt-manager (GUI) / virsh (CLI) │  ← Interface utilisateur
├──────────────────────────────────┤
│          libvirt API             │  ← Couche d'abstraction
├──────────────────────────────────┤
│     QEMU (périphériques)         │  ← Émulation
├──────────────────────────────────┤
│     KVM (noyau Linux)            │  ← Hypervisor Type 1
├──────────────────────────────────┤
│      Hardware (CPU avec VT-x)    │  ← Matériel physique
└──────────────────────────────────┘
```
### 3.2 Installation de QEMU/KVM/libvirt
**Commande complète**  : [bdrshield](https://www.bdrshield.com/blog/qemu-kvm-and-libvirt-installation-and-configuration/)

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer la stack complète
sudo apt install -y \
  qemu-kvm \
  libvirt-daemon \
  libvirt-daemon-system \
  libvirt-clients \
  bridge-utils \
  virt-manager \
  virt-viewer \
  virtinst

# Vérifier l'installation
qemu-system-x86_64 --version
virsh --version
```

**Explication des paquets** :

| Paquet | Rôle |
|--------|------|
| `qemu-kvm` | QEMU avec support KVM (accélération matérielle) |
| `libvirt-daemon` | Démon de gestion des VMs |
| `libvirt-daemon-system` | Configuration système de libvirt |
| `libvirt-clients` | Outils clients (virsh, virt-install) |
| `bridge-utils` | Outils pour créer des ponts réseau |
| `virt-manager` | Interface graphique de gestion |
| `virt-viewer` | Viewer pour la console des VMs |
| `virtinst` | Outils d'installation de VMs |
### 3.3 Configuration post-installation
#### Ajouter l'utilisateur aux groupes libvirt et kvm [oneuptime](https://oneuptime.com/blog/post/2026-01-15-setup-kvm-qemu-virtualization-ubuntu/view)

**Raison** : Permettre à l'utilisateur de gérer les VMs sans sudo.

```bash
# Ajouter l'utilisateur actuel aux groupes
sudo usermod -aG libvirt $(whoami)
sudo usermod -aG kvm $(whoami)

# Vérifier l'appartenance
groups

# Résultat attendu :
# user adm cdrom sudo dip plugdev libvirt kvm
```

**⚠️ Important** : Se déconnecter et se reconnecter pour que les changements prennent effet.

#### Démarrer et activer libvirtd [bdrshield](https://www.bdrshield.com/blog/qemu-kvm-and-libvirt-installation-and-configuration/)

```bash
# Démarrer le service libvirt
sudo systemctl start libvirtd

# Activer au démarrage
sudo systemctl enable libvirtd

# Vérifier le statut
sudo systemctl status libvirtd

# Résultat attendu :
# ● libvirtd.service - Virtualization daemon
#    Active: active (running)
```

***
## Partie 4 : Création de VM avec QEMU (ligne de commande)
### 4.1 Préparation
**Créer un répertoire pour la VM** :

```bash
# Créer le répertoire
mkdir -p ~/Ubuntu-VM
cd ~/Ubuntu-VM

# Déplacer l'ISO Ubuntu
sudo mv /path/to/ubuntu-22.04-server-amd64.iso ./ubuntu.iso
# OU télécharger directement
wget https://releases.ubuntu.com/22.04/ubuntu-22.04-live-server-amd64.iso -O ubuntu.iso
```
### 4.2 Créer l'image disque virtuelle
**Syntaxe** :
```bash
qemu-img create -f <format> <filename> <size>
```

**Commande** :
```bash
# Créer une image qcow2 de 20 Go
qemu-img create -f qcow2 Image.img 20G
```

**Explication** :
- `qemu-img create` : Créer une image disque
- `-f qcow2` : Format QCOW2 (QEMU Copy-On-Write version 2)
- `Image.img` : Nom du fichier image
- `20G` : Taille (20 gigaoctets)

**Avantages QCOW2** :
- **Copy-on-write** : Économie d'espace (allocation dynamique)
- **Snapshots** : Possibilité de sauvegarder l'état de la VM
- **Compression** : Réduction de taille
- **Chiffrement** : Sécurité des données
### 4.3 Lancer la VM avec QEMU
**Commande complète** :

```bash
qemu-system-x86_64 \
  -enable-kvm \
  -cdrom ubuntu.iso \
  -boot menu=on \
  -drive file=Image.img \
  -m 4G \
  -cpu host \
  -vga virtio \
  -display sdl,gl=on
```

**Explication des options** :

| Option | Valeur | Signification |
|--------|--------|---------------|
| `-enable-kvm` | - | Activer l'accélération matérielle KVM |
| `-cdrom` | `ubuntu.iso` | Monter l'ISO comme CD-ROM |
| `-boot` | `menu=on` | Afficher le menu de boot |
| `-drive` | `file=Image.img` | Disque dur virtuel |
| `-m` | `4G` | Mémoire RAM allouée (4 Go) |
| `-cpu` | `host` | Utiliser les capacités CPU de l'hôte |
| `-vga` | `virtio` | Carte graphique virtuelle (VirtIO = performances) |
| `-display` | `sdl,gl=on` | Affichage SDL avec accélération OpenGL |

**Résultat** : Une fenêtre s'ouvre avec l'installateur Ubuntu.
### 4.4 Options supplémentaires utiles
**Réseau (NAT par défaut)** :
```bash
-net nic -net user
```

**Réseau (bridge)** :
```bash
-netdev bridge,id=net0,br=virbr0 -device virtio-net-pci,netdev=net0
```

**Nombre de CPUs** :
```bash
-smp 2  # 2 vCPUs
```

**Snapshot (mode read-only, pas de modification du disque)** :
```bash
-snapshot
```

***
## Partie 5 : Gestion des VMs avec virt-manager (GUI)
### 5.1 Lancer virt-manager
```bash
# Lancer l'interface graphique
virt-manager
```

**OU depuis le menu** :
```
Applications → Système → Virtual Machine Manager
```
### 5.2 Configurer le réseau automatique
**Problème observé** : Le réseau virtuel peut ne pas démarrer automatiquement au boot de la VM. [download.libvirt](https://download.libvirt.org/virshcmdref/html/sect-net-autostart.html)

**Vérification** :

```bash
# Lister tous les réseaux virtuels
sudo virsh net-list --all

# Résultat typique :
# Name      State    Autostart   Persistent
# default   active   no          yes      ← Autostart désactivé !
```

**Solution** : Activer l'autostart  : [docs.redhat](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/sect-managing_guest_virtual_machines_with_virsh-managing_virtual_networks)

```bash
# Activer l'autostart pour le réseau "default"
sudo virsh net-autostart default

# Résultat :
# Network default marked as autostarted

# Vérifier
sudo virsh net-list --all
# Name      State    Autostart   Persistent
# default   active   yes         yes      ← Autostart activé ✅
```

**Pour un réseau personnalisé** :
```bash
# Activer pour un réseau nommé "my-network"
sudo virsh net-autostart my-network

# Désactiver l'autostart
sudo virsh net-autostart my-network --disable
```

***
## Partie 6 : Gestion des VMs avec virsh (CLI)
### 6.1 Commandes essentielles
#### Lister les VMs

```bash
# Lister les VMs en cours d'exécution
sudo virsh list

# Lister toutes les VMs (actives et inactives)
sudo virsh list --all

# Résultat typique :
# Id   Name          State
# 1    ubuntu-vm     running
# -    debian-vm     shut off
```

#### Démarrer une VM [oneuptime](https://oneuptime.com/blog/post/2026-01-15-setup-kvm-qemu-virtualization-ubuntu/view)

```bash
# Démarrer la VM "ubuntu-vm"
sudo virsh start ubuntu-vm

# Résultat :
# Domain ubuntu-vm started
```

#### Vérifier l'état d'une VM [oneuptime](https://oneuptime.com/blog/post/2026-01-15-setup-kvm-qemu-virtualization-ubuntu/view)

```bash
# Vérifier l'état de "ubuntu-vm"
sudo virsh domstate ubuntu-vm

# Résultat possible :
# running
# shut off
# paused
```

#### Arrêter une VM [oneuptime](https://oneuptime.com/blog/post/2026-01-15-setup-kvm-qemu-virtualization-ubuntu/view)

```bash
# Arrêt propre (envoie signal ACPI)
sudo virsh shutdown ubuntu-vm

# Arrêt forcé (équivalent à couper le courant)
sudo virsh destroy ubuntu-vm

# ⚠️ "destroy" ne supprime pas la VM, juste l'arrête brutalement
```

#### Autres commandes utiles

```bash
# Redémarrer une VM
sudo virsh reboot ubuntu-vm

# Suspendre une VM (pause)
sudo virsh suspend ubuntu-vm

# Reprendre une VM suspendue
sudo virsh resume ubuntu-vm

# Supprimer une VM (⚠️ supprime la définition, pas le disque)
sudo virsh undefine ubuntu-vm

# Supprimer avec le disque
sudo virsh undefine ubuntu-vm --remove-all-storage
```
### 6.2 Autostart des VMs
**Activer le démarrage automatique**  : [forum.endeavouros](https://forum.endeavouros.com/t/libvirt-qemu-autostart-vm-with-bridge-network/67865)

```bash
# Marquer "ubuntu-vm" pour démarrage automatique
sudo virsh autostart ubuntu-vm

# Vérifier
sudo virsh list --all
# Id   Name          State      Autostart
# -    ubuntu-vm     shut off   yes       ← Autostart activé
```

**Désactiver l'autostart** :
```bash
sudo virsh autostart ubuntu-vm --disable
```
### 6.3 Accéder à la console d'une VM
```bash
# Console texte (VMs sans GUI)
sudo virsh console ubuntu-vm

# Sortir de la console : Ctrl+]

# Viewer graphique
virt-viewer ubuntu-vm
```
### 6.4 Informations sur une VM
```bash
# Afficher toutes les infos (RAM, CPU, disque, réseau)
sudo virsh dominfo ubuntu-vm

# Configuration XML de la VM
sudo virsh dumpxml ubuntu-vm

# Liste des disques
sudo virsh domblklist ubuntu-vm

# Liste des interfaces réseau
sudo virsh domiflist ubuntu-vm
```

***
## Partie 7 : Permissions Docker (éviter sudo)
### 7.1 Problème
**Symptôme** : Devoir taper `sudo` avant chaque commande Docker.

```bash
# Sans permissions
docker ps
# permission denied while trying to connect to the Docker daemon socket

# Avec sudo (fastidieux)
sudo docker ps
```
### 7.2 Solution : Ajouter l'utilisateur au groupe docker
```bash
# Ajouter l'utilisateur actuel au groupe docker
sudo usermod -aG docker $(whoami)

# Vérifier l'appartenance au groupe
groups

# Résultat attendu :
# user adm cdrom sudo dip plugdev docker
```
### 7.3 Appliquer les changements
**Option 1 : Se déconnecter et se reconnecter**
```bash
# Fermer la session et rouvrir
```

**Option 2 : Nouvelle session dans le terminal**
```bash
# Forcer le rechargement des groupes
newgrp docker

# Tester
docker ps
# Fonctionne sans sudo ✅
```
### 7.4 Vérification
```bash
# Tester une commande Docker sans sudo
docker run hello-world

# Résultat attendu :
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
```

***
## Partie 8 : Workflow complet de virtualisation
### 8.1 Checklist pour un environnement de pentest
1. ✅ **Choisir l'hyperviseur**
   - Type 1 (KVM/Hyper-V) pour performances
   - Type 2 (VirtualBox) pour simplicité

2. ✅ **Installer les outils**
   - QEMU/KVM + libvirt sur Linux
   - Hyper-V sur Windows Pro+
   - VirtualBox sur n'importe quel OS

3. ✅ **Configurer les permissions**
   - Groupes libvirt, kvm, docker
   - Éviter sudo pour productivité

4. ✅ **Créer des VMs de lab**
   - Kali Linux (attaquant)
   - Metasploitable / DVWA (cible)
   - Windows Server (tests AD)
   - Ubuntu Server (web apps)

5. ✅ **Configurer le réseau**
   - NAT pour accès Internet
   - Host-only pour isolation
   - Bridged pour réseau réel
   - Autostart des réseaux

6. ✅ **Snapshots et backups**
   - Snapshot avant chaque test destructif
   - Export des VMs importantes
### 8.2 Commandes récapitulatives
**Virtualisation (virsh)** :
```bash
sudo virsh list --all              # Lister VMs
sudo virsh start <vm>              # Démarrer
sudo virsh domstate <vm>           # État
sudo virsh shutdown <vm>           # Arrêter
sudo virsh autostart <vm>          # Autostart VM
sudo virsh net-autostart default   # Autostart réseau
```

**Docker** :
```bash
sudo usermod -aG docker $(whoami)  # Permissions
docker ps                          # Lister conteneurs
docker compose up -d               # Lancer stack
```

**QEMU direct** :
```bash
qemu-img create -f qcow2 disk.img 20G
qemu-system-x86_64 -enable-kvm -cdrom ubuntu.iso -drive file=disk.img -m 4G
```

***
## Résumé : Points clés à retenir
1. **Type 1 Hypervisor** : Bare metal, sur hardware nu, performances max (ESXi, Hyper-V, KVM) [aws.amazon](https://aws.amazon.com/compare/the-difference-between-type-1-and-type-2-hypervisors/)
2. **Type 2 Hypervisor** : Hosted, sur OS hôte, facile (VirtualBox, VMware Workstation) [biztechmagazine](https://biztechmagazine.com/article/2024/08/type-1-vs-type-2-hypervisors-whats-difference-perfcon)
3. **QEMU** : Émulateur de machine, fournit périphériques virtuels [bdrshield](https://www.bdrshield.com/blog/qemu-kvm-and-libvirt-installation-and-configuration/)
4. **KVM** : Module noyau Linux, hypervisor Type 1 [oneuptime](https://oneuptime.com/blog/post/2026-01-15-setup-kvm-qemu-virtualization-ubuntu/view)
5. **libvirt** : API pour gérer VMs, compatible multi-hyperviseurs [bdrshield](https://www.bdrshield.com/blog/qemu-kvm-and-libvirt-installation-and-configuration/)
6. **virsh** : CLI pour gérer VMs (start, shutdown, domstate) [download.libvirt](https://download.libvirt.org/virshcmdref/html/sect-net-autostart.html)
7. **net-autostart** : Activer démarrage auto réseau virtuel [docs.redhat](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/sect-managing_guest_virtual_machines_with_virsh-managing_virtual_networks)
8. **usermod -aG** : Ajouter utilisateur aux groupes (libvirt, kvm, docker) [oneuptime](https://oneuptime.com/blog/post/2026-01-15-setup-kvm-qemu-virtualization-ubuntu/view)

