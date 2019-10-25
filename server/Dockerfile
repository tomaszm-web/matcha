FROM python:3
COPY requirements.txt /matcha/
WORKDIR /matcha
ENV MYSQL_HOST=""
ENV MYSQL_USER=""
ENV MYSQL_DB=""
ENV MYSQL_PASSWORD=""
ENV GMAIL_USERNAME=""
ENV GMAIL_PASSWORD=""
ENV SECRET_KEY=""
RUN apt-get update
RUN apt install python3-mysqldb
RUN pip install -r requirements.txt
RUN eval $(sh config_environment.sh)
ENTRYPOINT ["python3"]
CMD ["app.py"]
