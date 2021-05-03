echo "Enter a few values before running the script, MAKE SURE there is no space character."
echo "App name:"
read APP
echo "User:"
read USER
if id "$USER" &>/dev/null; then
else
    echo 'User not found'
    exit
fi
echo "Postgres user:"
read POSTGRES_USER
echo "Postgres password:"
read POSTGRES_PASSWORD

sudo mkdir -p /var/log/nginx/$APP /var/log/uwsgi/$APP /var/log/$APP /run/uwsgi/$APP
sudo chown $USER. -R /var/log/nginx/$APP /var/log/uwsgi/$APP /var/log/$APP /run/uwsgi/$APP

sudo apt update
sudo apt-get update

sudo apt-get -y install git
sudo apt-get -y install systemd
sudo apt-get -y install redis-server

# Install pip3
sudo apt install -y python3-pip

# Install library
sudo apt-get -y install libpq-dev python3-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get -y install npm
sudo npm install -g sass
sudo npm -g install yuglify

# Clone config
sudo cp -a deploy/etc/. /etc

# Install Nginx
sudo apt-get -y install nginx
sudo mkdir -p /var/www/$APP/static /var/www/$APP/media
sudo mv /etc/nginx/sites-available/nginx.example.conf /etc/nginx/sites-available/$APP.conf
sudo ln -s /etc/nginx/sites-available/$APP.ini /etc/nginx/sites-enabled/

# Install uwsgi
sudo apt-get -y install uwsgi-plugin-python3
sudo mv /etc/uwsgi/apps-available/uwsgi.example.ini /etc/uwsgi/apps-available/$APP.ini
sudo ln -s /etc/uwsgi/apps-available/$APP.ini /etc/uwsgi/apps-enabled/
sudo chmod +x /etc/systemd/system/uwsgi.service

sed -i "s/<APP>/$APP/g" /etc/nginx/sites-available/$APP.conf
sed -i "s/<APP>/$APP/g" /etc/uwsgi/apps-available/$APP.ini
sed -i "s/<USER>/$USER/g" /etc/uwsgi/apps-available/$APP.ini
sed -i "s/<USER>/$USER/g" /etc/systemd/system/uwsgi.service

sudo systemctl enable uwsgi.service
sudo systemctl daemon-reload

# Install postgres
sudo apt-get -y install postgresql
sudo -i -u postgres psql -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
sudo -i -u postgres psql -c "CREATE DATABASE $APP;"
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $APP TO $POSTGRES_USER;"

# Install virtualenv
sudo pip3 install virtualenv

# Install .venv
virtualenv -p python3 .venv
