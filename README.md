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



and run server:
manage.py runserver
