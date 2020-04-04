#!/bin/bash
lpq | grep --quiet "printing"

if [ $? = 0 ]
then
  curl -s 'http://192.168.1.88/cm?cmnd=Power%20On' > /dev/null
  echo "Printing";
fi