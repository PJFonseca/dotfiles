# .bashrc

# Source global definitions

 if [ -f /etc/bashrc ]; then
	. /etc/bashrc
 fi
# User specific environment
PATH="$HOME/.local/bin:$HOME/bin:$PATH"
export HISTSIZE=
export HISTFILESIZE=
export PATH

# User specific aliases and functions
export PATH="$PATH:$HOME/.config/composer/vendor/bin"
export PATH="$PATH:$HOME/.dotfiles/system"

 for DOTFILE in ~/.dotfiles/system/.{alias,functions,housekeeping,env}; do
 	[ -f "$DOTFILE" ] && . "$DOTFILE"	
 done;

 for UTILS in ~/.dotfiles/includes/.{utils,install,podcasts,pass.config}; do
 	[ -f "$UTILS" ] && . "$UTILS"	
 done;
 unset file;

source ~/.dotfiles/.bash_prompt
