FROM python:3
COPY ./project_files /matcha
ENV SECRET_KEY='ABSOLUTELY SECRET'
ENV MAIL_SERVER='smtp.googlemail.com'
ENV MAIL_PORT=465
ENV MAIL_USERNAME='evgeny.ocheredko@gmail.com'
ENV MAIL_PASSWORD='36673667'
WORKDIR /matcha
RUN apt-get update; apt install python3-mysqldb; pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
