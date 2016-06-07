#!/bin/bash
mount -v -t cifs //$1/$3 $4 -o username=$6,password=$2,workgroup=$1,uid=$5

