#!/bin/bash
##ssarea script
DATE=$(date +%Y-%m-%d-%H:%M:%S)
gnome-screenshot -a -f $HOME/$IMAGES_FOLDER/Screenshot-$DATE.png
gnome-screenshot -a -c $HOME/$IMAGES_FOLDER/Screenshot-$DATE.png