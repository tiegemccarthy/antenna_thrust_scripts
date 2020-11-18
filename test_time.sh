#!/bin/bash

currenttime=$(date +%s)
test=$(date -d 2020-11-18T22:43:40+11:00 +%s)

if [ $currenttime -ge $(date -d 2020-11-18T22:43:40+11:00 +%s) ]
then
    echo "oi"
fi


