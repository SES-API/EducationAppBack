installation and start:
clone project.

create virtualenv:
python -m venv myvenv

activate venv:
myvenv/Scripts/activate

install requirements.txt:
pip install -r requirements.txt

makemigration and migrate:

manage.py makemigrations
manage.py migrate

you can create superuser if you want:
manage.py createsuperuser

dont forget create a .env file from .env-sample and fill it

and run server:
manage.py runserver
