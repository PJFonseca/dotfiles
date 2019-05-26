# Repo of my _not-so-fancy-or-techy-_***dotfiles***

## **Intro**
I'm a newbie in the Linux world but this ***dotfiles*** thing it's ***AWESOME***. So, as the law says, one must create a repo of the ***dotfiles*** and share it if he/she does not want to be considered an outlaw.

## **Heads up**

This ***dotfiles*** is to ***help ME*** and are  ***tailored to ME***, and actually it ***works for ME***. 

So don't get **[ put some sort of state of mind and/or spirit in here ]** about this ***dotfiles*** not working 100% on your system. Deal with it, you are more then capable of doing that.

## **Instructions**

I'm so newbie that I don't know what to write in the instructions to install and use my ***dotfiles***. I have one install script ([<code>install.sh</code>](https://github.com/PJFonseca/dotfiles/blob/master/install/install.sh)) but it was never tested and for sure it will ***fail***, so if you try it just remember there will be **Dragons**, not the Daenerys Targaryen ones unfortunately.

## **Install**

**Transfer to machine**

<code>sudo rm -rf ~/.dotfiles && git clone --recurse-submodules https://github.com/PJFonseca/dotfiles ~/.dotfiles</code>

**Instalation**

<code>cd ~/.dotfiles && chmod +x install.sh && sudo ./install.sh</code>

**Activate**

<code>
    rm -rf ~/.bashrc && ln -s ~/.dotfiles/.bashrc ~/.bashrc && rm -rf ~/.gitconfig && ln -s ~/.dotfiles/.gitconfig ~/.gitconfig && rm -rf ~/.bash_prompt && ln -s ~/.dotfiles/.bash_prompt ~/.bash_prompt
</code>

## **Keywords**
**functions**, **aliases**, **alias**, **bash**, **env**, **shell**, petrol, mad max, tina turner, 80, queen... hummmm, this is going the wrong way, let me stop.

## **The end**

Don't have anything else more to write, so:

***There, I hope you enjoyed our time together today. You know, it seems harder and harder to just sit back and enjoy the finer things in life.
Well, till next time.
Ta-ta!***

_by The Offspring on Smash in 1994_


*P.S.: Sorry about my strange english ( I guess ), not my native language.*





