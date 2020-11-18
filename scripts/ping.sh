 #!/bin/bash 
if [ -z  "$1"  ] ;then
    echo  "Passe um IP" 
    exit 1;
fi
 
ping -c1 $1  >  /dev/null
 
if [ $? -ne 0 ]; then
        echo  "OFF" 
else
        echo  "ON" 
fi
