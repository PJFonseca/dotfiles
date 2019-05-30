#!/bin/bash

#Repos and Basics
hostnamectl set-hostname --static "FedoraBox"
sudo dnf -y update
sudo dnf upgrade --best --allowerasing --refresh -y
sudo dnf install -y fedora-workstation-repositories
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y python-vlc npapi-vlc 

##Install Software
sudo dnf install \
-y \
steam --enablerepo=rpmfusion-nonfree-steam \
wget \
numlockx \
youtube-dl \
nano \
arc-theme \
vlc \
code \
firefox \
filezilla \
audacity \
keepassxc \
telegram-desktop \
gnome-tweak-tool \
qbittorrent \
exfat-utils \
ffmpeg \
git \
nautilus-extensions \
nautilus-image-converter \
nautilus-search-tool \
trash-cli \
libcxx \
pwgen

#SoftLinks
rm -rf ~/.bashrc
ln -s ~/.dotfiles/.bashrc ~/.bashrc
rm -rf ~/.gitconfig
ln -s ~/.dotfiles/.gitconfig ~/.gitconfig
rm -rf ~/.bash_prompt
ln -s ~/.dotfiles/.bash_prompt ~/.bash_prompt

source ~/.bashrc

#TeamViewer
install_teamviewer
#DBeaver
install_dbeaver
#VNC
install_vnc
#Skype
install_skype
#Postman
install_postman
#gnome-shell-extension-installer
install_gsei
#Install flat-remix-gtk theme
install_theme
#Cursor
install_breeze_cursor

#Interface
gsettings set org.gnome.desktop.interface gtk-theme 'Flat-Remix-GTK-Blue-Dark'
gsettings set org.gnome.desktop.interface cursor-theme 'Breeze_Snow'
gsettings set org.gnome.desktop.interface icon-theme 'Flat-Remix-Blue-Dark'

#Nautilus
gsettings set org.gnome.nautilus.icon-view default-zoom-level 'standard'
gsettings set org.gnome.nautilus.preferences executable-text-activation 'ask'
gsettings set org.gtk.Settings.FileChooser sort-directories-first true
gsettings set org.gnome.nautilus.list-view use-tree-view true

#Codecs
install_codecs


#Telegram to start in tray
sed -i 's/ -- / -startintray --/g' ~/.config/autostart/telegram-desktop.desktop

# Remove un-needed stuff
sudo dnf remove \
-y \
gnome-shell-extension-background-logo \
totem \
chromium \
flowblade