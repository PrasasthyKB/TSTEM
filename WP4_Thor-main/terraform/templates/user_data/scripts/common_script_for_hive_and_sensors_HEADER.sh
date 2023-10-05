#!/bin/bash

echo hello there # used for portential debuging by cat /var/log/syslog


sudo apt update
sudo apt -y upgrade
sudo apt install -y git

cd ~
mkdir download
cd download

git clone --depth 1 https://github.com/telekom-security/tpotce
cd tpotce/iso/installer/


cp tpot.conf.dist ${SSH_USER}.tpot.conf


