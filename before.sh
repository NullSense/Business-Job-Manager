#!/bin/sh

# $0 SSH_PRIVATE_KEY
# $1 VPS_PORT
# $2 VPS_IP

# install missing dependencies for running web-app
echo $HOME
pwd
ls
which ssh-agent || ( apk update && apk add openssh-client )
which rsync || ( apk add rsync )
which docker || ( apk add docker )

# set up auth keys for ssh and rsync
mkdir -p $HOME/.ssh
pwd
ls
echo "$0" | tr -d '\r' > $HOME/.ssh/id_rsa # pass the ssh private key
chmod 700 $HOME/.ssh
chmod 600 $HOME/.ssh/id_rsa
eval "$(ssh-agent -s)"
ssh-add $HOME/.ssh/id_rsa
ssh-keyscan -p "$1" -H "$2" >> $HOME/.ssh/known_hosts # pass server port and ip
[[ -f /.dockerenv ]] && echo -e "Host *\n\tStrictHostKeyChecking no\n\n" > $HOME/.ssh/config
