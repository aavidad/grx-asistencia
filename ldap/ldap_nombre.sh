#!/bin/bash
#ldapsearch -QLLL -o ldif-wrap=no -b "dc = grx" "(cn=*$1*)" cn |grep cn | cut -f2 -d":"
ldapsearch -QLLL -o ldif-wrap=no -b "dc = grx" "(cn=*$1*)" cn sAMAccountName

