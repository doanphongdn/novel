# crawl_service
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

