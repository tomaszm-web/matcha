#!/usr/bin/env bash

MYSQL_HOST=""
MYSQL_USER=""
MYSQL_DB=""
MYSQL_PASSWORD=""
GMAIL_USERNAME=""
GMAIL_PASSWORD=""
SECRET_KEY=""

echo "export MYSQL_HOST='${MYSQL_HOST}'"
echo "export MYSQL_USER='${MYSQL_USER}'"
echo "export MYSQL_DB='${MYSQL_DB}'"
echo "export MYSQL_PASSWORD='${MYSQL_PASSWORD}'"
echo "export MAIL_USERNAME='${GMAIL_USERNAME}'"
echo "export MAIL_PASSWORD='${GMAIL_PASSWORD}'"
echo "export SECRET_KEY='${SECRET_KEY}'"

echo "# Environment variables were successfully set!"
