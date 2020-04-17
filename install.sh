#!/bin/bash

if [ -d ~/.dotfiles/includes ]; then
  for file in ~/.dotfiles/includes/.*; do
    . "$file"
  done
fi

#Repos and Basics
hostnamectl set-hostname --static "FedoraBox"
sudo dnf -y update
sudo dnf upgrade --best --allowerasing --refresh -y
sudo dnf install -y fedora-workstation-repositories
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y python-vlc
sudo dnf copr enable bcotton/cherrytree


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
steam \
firefox \
filezilla \
audacity \
keepassxc \
telegram-desktop \
gnome-tweaks \
gnome-tweak-tool \
variety \
qbittorrent \
exfat-utils \
ffmpeg \
git \
nautilus-extensions \
nautilus-image-converter \
nautilus-search-tool \
trash-cli \
libcxx \
remmina \
nautilus-dropbox \
pwgen \
asciinema\
cherrytree

#SoftLinks
rm -rf /home/$USER/.bashrc
ln -s /home/$USER/.dotfiles/.bashrc /home/$USER/.bashrc
rm -rf /home/$USER/.gitconfig
ln -s /home/$USER/.dotfiles/.gitconfig /home/$USER/.gitconfig
rm -rf /home/$USER/.bash_prompt
ln -s /home/$USER/.dotfiles/.bash_prompt /home/$USER/.bash_prompt

source /home/$USER/.bashrc

#TeamViewer
cd /tmp/ && wget -P /tmp/ https://download.teamviewer.com/download/linux/teamviewer.x86_64.rpm && sudo dnf install -y /tmp/teamviewer.x86_64.rpm

#DBeaver
cd /tmp/ && wget -P /tmp/ --trust-server-names https://dbeaver.io/files/dbeaver-ce-latest-stable.x86_64.rpm -O dbeaver-ce-latest-stable.x86_64.rpm && sudo dnf install -y /tmp/dbeaver-ce-latest-stable.x86_64.rpm

#VNC
cd /tmp/ && wget -P /tmp/ https://www.realvnc.com/download/file/viewer.files/VNC-Viewer-6.19.325-Linux-x64.rpm && sudo dnf install -y /tmp/VNC-Viewer-6.19.325-Linux-x64.rpm

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

#Postman
wget -P /tmp/ https://dl.pstmn.io/download/latest/linux64 -O postman-linux-x64.tar.gz
sudo tar xvzf /tmp/postman-linux-x64.tar.gz -C /opt
sudo ln -s /opt/Postman/Postman /usr/bin/postman

cat << EOF > ~/.local/share/applications/postman2.desktop
[Desktop Entry]
Name=Postman
GenericName=API Client
X-GNOME-FullName=Postman API Client
Comment=Make and view REST API calls and responses
Keywords=api;
Exec=/opt/Postman/Postman
Terminal=false
Type=Application
Icon=/opt/Postman/app/resources/app/assets/icon.png
Categories=Development;Utilities;
EOF

#gnome-shell-extension-installer
cd /tmp/ && wget -P /tmp/ -O gnome-shell-extension-installer "https://github.com/brunelli/gnome-shell-extension-installer/raw/master/gnome-shell-extension-installer" && sudo chmod +x /tmp/gnome-shell-extension-installer && sudo mv /tmp/gnome-shell-extension-installer /usr/bin/
gnome-shell-extension-installer 1160 # Dash to Panel by jderose9 
gnome-shell-extension-installer 1112 # Screenshot Tool by oal
gnome-shell-extension-installer 118 # No Topleft Hot Corner by azuri
gnome-shell-extension-installer 1206 # Clock Override by .ext

#Install flat-remix-gtk theme
cd /tmp && sudo rm -rf flat-remix-gtk && git clone https://github.com/daniruiz/flat-remix-gtk && mkdir -p ~/.themes && cp -r flat-remix-gtk/Flat-Remix-GTK* ~/.themes/
cd /tmp && sudo rm -rf flat-remix && git clone https://github.com/daniruiz/flat-remix && mkdir -p ~/.icons && cp -r flat-remix/Flat-Remix* ~/.icons/

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

#Codecs
sudo dnf install gstreamer1-{plugin-crystalhd,ffmpeg,plugins-{good,ugly,bad{,-free,-nonfree,-freeworld,-extras}{,-extras}}} libmpg123 lame-libs --setopt=strict=0 -y

#Telegram to start in tray
sed -i 's/ -- / -startintray --/g' ~/.config/autostart/telegram-desktop.desktop