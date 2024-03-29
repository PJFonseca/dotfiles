#!/bin/bash

if [ -d ~/.dotfiles/includes ]; then
  for file in ~/.dotfiles/includes/.*; do
    . "$file"
  done
fi

#Repos and Basics
hostnamectl set-hostname --static "zx"
sudo dnf -y update
sudo dnf upgrade --best --allowerasing --refresh -y
sudo dnf install -y fedora-workstation-repositories
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y python-vlc

##Install Software
sudo dnf install \
-y \
steam --enablerepo=rpmfusion-nonfree-steam \
wget \
dnf5 \
numlockx \
yt-dlp \
arc-theme \
vlc \
steam \
keepassxc \
telegram-desktop \
variety \
qbittorrent \
exfat-utils \
ffmpeg \
git \
nautilus-extensions \
nautilus-image-converter \
nautilus-search-tool \
libcxx \
remmina

#SoftLinks
rm -rf /home/$USER/.bashrc
ln -s /home/$USER/.dotfiles/.bashrc /home/$USER/.bashrc
rm -rf /home/$USER/.gitconfig
ln -s /home/$USER/.dotfiles/.gitconfig /home/$USER/.gitconfig
rm -rf /home/$USER/.bash_prompt
ln -s /home/$USER/.dotfiles/.bash_prompt /home/$USER/.bash_prompt

mv ~/Downloads ~/dwnx
mv ~/Videos ~/vids

source /home/$USER/.bashrc

#DBeaver
cd /tmp/ && wget -P /tmp/ --trust-server-names https://dbeaver.io/files/dbeaver-ce-latest-stable.x86_64.rpm -O dbeaver-ce-latest-stable.x86_64.rpm && sudo dnf install -y /tmp/dbeaver-ce-latest-stable.x86_64.rpm

#Skype
cd /tmp/ && wget -P /tmp/ --trust-server-names https://go.skype.com/skypeforlinux-64.rpm && sudo dnf install -y /tmp/skypeforlinux-64.rpm

#Telegram
cd /tmp/ && wget -P /tmp/ --trust-server-names https://telegram.org/dl/desktop/linux | sudo tar xJ -C /opt/
sudo ln -s /opt/Telegram/Telegram /usr/local/bin/telegram-desktop

#VSCode
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
cat <<EOF | sudo tee /etc/yum.repos.d/vscode.repo
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF
sudo dnf install code

#Install flat-remix-gtk theme
sudo dnf install flat-remix-gtk2-theme flat-remix-gtk3-theme

#Cursor
cd /tmp/ && wget -P /tmp/ http://download-ib01.fedoraproject.org/pub/fedora/linux/releases/30/Everything/x86_64/os/Packages/b/breeze-cursor-theme-5.15.4.1-1.fc30.noarch.rpm && sudo dnf install -y /tmp/breeze-cursor-theme-5.15.4.1-1.fc30.noarch.rpm

#Interface
gsettings set org.gnome.desktop.interface gtk-theme 'Flat-Remix-GTK-Blue-Dark'
gsettings set org.gnome.desktop.interface cursor-theme 'Breeze_Snow'
gsettings set org.gnome.desktop.interface icon-theme 'Flat-Remix-Blue-Dark'

#Nautilus
gsettings set org.gnome.nautilus.icon-view default-zoom-level 'standard'
gsettings set org.gnome.nautilus.preferences executable-text-activation 'ask'
gsettings set org.gtk.Settings.FileChooser sort-directories-first true
gsettings set org.gnome.nautilus.list-view use-tree-view true
gsettings set org.gnome.desktop.interface clock-show-seconds true

#Codecs
sudo dnf install gstreamer1-{plugin-crystalhd,ffmpeg,plugins-{good,ugly,bad{,-free,-nonfree,-freeworld,-extras}{,-extras}}} libmpg123 lame-libs --setopt=strict=0 -y