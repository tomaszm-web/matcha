sudo apt-get install python3.6-dev libmysqlclient-dev
virtualenv --python python3 venv
source venv/bin/activate
pip install -r requirements.txt
echo 'You can run this app by typing: python3 app.py'
