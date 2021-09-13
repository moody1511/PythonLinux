#!/bin/bash

if [ -z "$1" ]
  then USER=$(whoami)
else
  USER=$1
fi

if [ "$1" == "-h" ] || [ "$1" == "--help" ]
then
 echo "usage: start.sh [-h, --help]"
 exit 1
fi


if [ "$1" == "" ] || [ $AVOID_ARGS == "true" ]
then
  echo $(date +"%m-%d-%y %T") $USER stop >> log/start_stop.txt
  sudo systemctl stop {{ folder }}.service
  echo service {{ folder }} stopped
else
 echo "start.sh: error: the following arguments are required: -h, --help" 
 exit 1
fi 

