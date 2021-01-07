# crawl_service
sudo apt-get install libpq-dev python3-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get install npm
sudo npm install -g sass
sudo npm -g install yuglify

#Install uwsgi
sudo apt-get install uwsgi-plugin-python3

# Install .venv
virtualenv -p python3 .venv

# Install lib
.venv/bin/pip3 install -r requirements.txt

# Config .env
cp .env.example .env

# Migrate database
.venv/bin/python3 manage.py migrate

# Create superuser
.venv/bin/python3 manage.py createsuperuser

# install static files
.venv/bin/python3 manage.py collectstatic

