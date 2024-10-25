#!/bin/bash 

RED="\e[31m"
GREEN="\e[32m"

for item in "pedrofonseca.eu" "born2score.pt" "asassociados.pt" "paintugal.pt" "raullen.pt" "multiplus.com.pt" "tecnocosmetica.com" "smclinic.pt" "azores-sea-farming.pt" "azsf.pt" "lynxtacticalgear.com" "pedrofonseca.eu" "logislink-moz.com" "fls-solutions.pt" "madeiraair.pt" "aviationls.pt" "als-solutions.pt" "grupob2s.com" "vipmassagelisbon.com" "laserstore.pt" "poaviation.com" "myownindex.com" "bandodeirmaos.com" "fppaintball.org" "cs-associados.pt";

do
   ip=$(dig @8.8.8.8 +time=1 +tries=1 +short A $item)
   if [ "$ip" != "68.65.121.26" ]; then
    echo -e "${RED}$item A${ENDCOLOR}"
   else
    echo -e "${GREEN}$item A${ENDCOLOR}"
   fi
   ip=$(dig +short MX $item)
   if [ "$ip" != "0 mail.$item." ]; then
    echo  -e "${RED}$item MX $ip${ENDCOLOR}"
   else
    echo  -e "${GREEN}$item MX${ENDCOLOR}"
   fi
done