#!/usr/bin/env bash
docker container stop matcha
docker container rm matcha
docker container stop mysql
docker container rm mysql
docker image rm matcha
docker image rm mysql
docker network rm matcha
