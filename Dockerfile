FROM python:3
COPY requirements.txt config_environment.sh /matcha/
WORKDIR /matcha
RUN apt-get update
RUN apt install python3-mysqldb
RUN pip install -r requirements.txt
RUN eval $(sh config_environment.sh)
ENTRYPOINT ["python3"]
CMD ["app.py"]
