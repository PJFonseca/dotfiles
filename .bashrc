# .bashrc

# Source global definitions

 if [ -f /etc/bashrc ]; then
	. /etc/bashrc
 fi
# User specific environment
PATH="$HOME/.local/bin:$HOME/bin:$PATH"
export PATH

# User specific aliases and functions
export PATH="$PATH:$HOME/.config/composer/vendor/bin"
export PATH="$PATH:$HOME/.dotfiles/system"

 for DOTFILE in ~/.dotfiles/system/.{alias,functions,functions_install,env}; do
 	[ -f "$DOTFILE" ] && . "$DOTFILE"	
 done;
 unset file;

source ~/.dotfiles/.bash_prompt
