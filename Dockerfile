FROM python:3
COPY ./project_files /matcha
ENV SECRET_KEY='ABSOLUTELY SECRET'
ENV MAIL_SERVER='smtp.googlemail.com'
ENV MAIL_PORT=465
ENV MAIL_USERNAME='unit.matcha42@gmail.com'
ENV MAIL_PASSWORD='A1b2c3d4@'
WORKDIR /matcha
RUN apt-get update; apt install python3-mysqldb; pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
