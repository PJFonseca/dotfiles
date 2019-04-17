#!/bin/bash

#Repos and Basics
hostnamectl set-hostname --static "fedorabox"
sudo dnf -y update
sudo dnf upgrade --best --allowerasing --refresh -y
sudo dnf install -y fedora-workstation-repositories

#VSCode stuff
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'

##Install Software
sudo dnf install \
-y \
steam --enablerepo=rpmfusion-nonfree-steam \
wget \
numlockx 'Enable number lock at startup' \
youtube-dl 'YouTube Downloaded -> https://ytdl-org.github.io/youtube-dl/index.html' \
nano \
arc-theme \
pop-icon-theme \
breeze-cursor-theme \
vlc \
code \
dropbox \
firefox \
filezilla \
audacity \
keepassxc \
telegram-desktop \
qbittorrent \
exfat-utils \
ffmpeg \
git \
nautilus-extensions \
nautilus-image-converter \
nautilus-search-tool 

# Remove un-needed stuff
sudo dnf remove \
-y \
gnome-shell-extension-background-logo \
totem \
chromium \
flowblade

#TeamViewer
wget -P /tmp/ https://download.teamviewer.com/download/linux/teamviewer.x86_64.rpm && sudo dnf install -y /tmp/teamviewer.x86_64.rpm

#VNC
wget -P /tmp/ https://www.realvnc.com/download/file/viewer.files/VNC-Viewer-6.19.325-Linux-x64.rpm && sudo dnf install -y /tmp/VNC-Viewer-6.19.325-Linux-x64.rpm

#Skype
wget -P /tmp/ --trust-server-names https://go.skype.com/skypeforlinux-64.rpm && sudo dnf install -y /tmp/skypeforlinux-64.rpm
#DBeaver
wget -P /tmp/ --trust-server-names https://dbeaver.io/files/dbeaver-ce-latest-stable.x86_64.rpm && sudo dnf install -y /tmp/dbeaver-ce-latest-stable.x86_64.rpm

#Extensions
wget -P /tmp/ -O gnome-shell-extension-installer "https://github.com/brunelli/gnome-shell-extension-installer/raw/master/gnome-shell-extension-installer" && sudo chmod +x /tmp/gnome-shell-extension-installer && sudo mv /tmp/gnome-shell-extension-installer /usr/bin/

#Install
gnome-shell-extension-installer 1160 # Dash to Panel by jderose9 
gnome-shell-extension-installer 1112 # Screenshot Tool by oal

#Install flat-remix-gtk theme
cd /tmp && rm -rf flat-remix-gtk && git clone https://github.com/daniruiz/flat-remix-gtk && mkdir -p ~/.themes && cp -r flat-remix-gtk/Flat-Remix-GTK* ~/.themes/

#Interface
gsettings set org.gnome.desktop.interface gtk-theme 'Flat-Remix-GTK-Dark'
gsettings set org.gnome.desktop.interface cursor-theme 'Breeze_Snow'
gsettings set org.gnome.desktop.interface icon-theme 'Flat-Remix-Blue-Dark'

#Nautilus
gsettings set org.gnome.nautilus.icon-view default-zoom-level 'standard'
gsettings set org.gnome.nautilus.preferences executable-text-activation 'ask'
gsettings set org.gtk.Settings.FileChooser sort-directories-first true
gsettings set org.gnome.nautilus.list-view use-tree-view true

#Codecs
sudo dnf install gstreamer1-{plugin-crystalhd,ffmpeg,plugins-{good,ugly,bad{,-free,-nonfree,-freeworld,-extras}{,-extras}}} libmpg123 lame-libs --setopt=strict=0 -y

#SoftLinks
ln -s ~/.dotfiles/.bashrc ~/.bashrc
ln -s ~/.dotfiles/.gitconfig ~/.gitconfig
ln -s ~/.dotfiles/.bash_prompt ~/.bash_prompt

#Telegram to start in tray
sed -i 's/ -- / -startintray --/g' ~/.config/autostart/telegram-desktop.desktop

#Mounting - FSTab
sudo echo "/dev/disk/by-uuid/80b5f91f-6d05-49f6-bf74-51e7ec9f756f /mnt/Stuff auto nosuid,nodev,nofail,x-gvfs-show 0 0" >> /etc/fstab