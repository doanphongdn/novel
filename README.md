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

# Install static files
.venv/bin/python3 manage.py collectstatic

# Install memcached
sudo apt-get install memcached

# Install Redis Server (using default)
sudo apt-get install redis-server

# Install Selenium
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add 

echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list

sudo apt-get update 

sudo apt-get install google-chrome-stable

google-chrome-stable -version

sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4

wget https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip

unzip chromedriver_linux64.zip

sudo mv chromedriver /usr/bin/chromedriver

sudo chown root:root /usr/bin/chromedriver

sudo chmod +x /usr/bin/chromedriver

chromedriver -v

.venv/bin/pip install webdriver_manager

.venv/bin/pip install selenium

# Install django-backblaze-b2

.venv/bin/pip install django-backblaze-b2
> or .venv/bin/pip install -r requirements.txt

## Setting backblaze in .evn

BACKBLAZE_KEY_ID = ''

BACKBLAZE_KEY = ''

BACKBLAZE_MAX_RETRY = 5

CAMPAIGNS_THREAD_NUM = 2


### Setting in CDNServer and CDN novel files from Admin page
### Settings cron to run_cdn_files.py


# TRANSLATION
 sudo apt-get install gettext
 
 mkdir locale
 
 .venv/bin/django-admin makemessages -l vi
 
 .venv/bin/django-admin compilemessages