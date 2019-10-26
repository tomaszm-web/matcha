#!/usr/bin/env bash
docker network create matcha
docker build -t mysql mysql/
docker build -t matcha server/
docker run -d --net matcha -p 3306:3306 --name mysql mysql
#status="1"
#while [[ ${status} -ne 0 ]]; do
#docker run -d --net matcha -v $(pwd):/matcha -p 80:80 --name matcha matcha
#status=$?
#done
docker run -d --net matcha --restart on-failure -v $(pwd):/matcha -p 80:80 --name matcha matcha