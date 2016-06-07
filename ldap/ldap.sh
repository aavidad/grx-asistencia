#!/bin/bash
ldapsearch -QLLL -o ldif-wrap=no -b "dc = grx" "(samAccountName=$1)" 2>&1



