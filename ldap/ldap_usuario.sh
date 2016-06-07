#!/bin/bash
 ldapsearch -QLLL -o ldif-wrap=no -b "dc = grx" "(samAccountName=*$1*)" sAMAccountName |grep sAMAccountName | cut -f2 -d":"

