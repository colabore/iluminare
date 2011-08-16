#!/bin/bash

USUARIO=$1
SENHA=$2
BASE=$3

mysqldump -u $USUARIO -p$SENHA $BASE > /media/Arquivo/backup-mysql/backup-`date +%F`.sql
