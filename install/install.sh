#!/bin/bash

#Repos and Basics
sudo dnf install fedora-workstation-repositories
sudo dnf install -y steam --enablerepo=rpmfusion-nonfree-steam
sudo dnf install -y wget

# YouTube Downloaded -> https://ytdl-org.github.io/youtube-dl/index.html
sudo dnf install -y youtube-dl

#Enable number lock at startup
sudo dnf install -y numlockx

##Install Software
sudo dnf install -y nano 
sudo dnf install -y vlc
sudo dnf install -y visual-studio-code
sudo dnf install -y dropbox
sudo dnf install -y firefox
sudo dnf install -y filezilla
sudo dnf install -y audacity
sudo dnf install -y keepassxc
sudo dnf install -y telegram-desktop
sudo dnf install -y qbittorrent

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

#Codecs
sudo dnf install gstreamer1-{plugin-crystalhd,ffmpeg,plugins-{good,ugly,bad{,-free,-nonfree,-freeworld,-extras}{,-extras}}} libmpg123 lame-libs --setopt=strict=0 -y

#SoftLinks
ln -s ~/.dotfiles/.bashrc ~/.bashrc
ln -s ~/.dotfiles/.gitconfig ~/.gitconfig
ln -s ~/.dotfiles/.bash_prompt ~/.bash_prompt

#Configs

#Telegram to start in tray
sed -i 's/ -- / -startintray --/g' ~/.config/autostart/telegram-desktop.desktop

#Mounting - FSTab
sudo echo "/dev/disk/by-uuid/80b5f91f-6d05-49f6-bf74-51e7ec9f756f /mnt/Stuff auto nosuid,nodev,nofail,x-gvfs-show 0 0" >> /etc/fstab