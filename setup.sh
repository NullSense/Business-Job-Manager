#!/bin/sh

# $0 VPS_PORT
# $1 VPS_USER
# $2 VPS_IP

# rsync built files to the docker build stage
rsync -ave "ssh -p $0" frontend/build backend "$1"@"$2":/home/"$1"/docker/
# run docker-compose with nginx
ssh -p "$0" "$1"@"$2" "cd docker/ && docker-compose down && docker-compose up --build -d"
