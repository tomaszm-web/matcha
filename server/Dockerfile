FROM python:3
WORKDIR /matcha
COPY requirements.txt /matcha
RUN apt-get update
RUN apt install python3-mysqldb
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
