installation and start:
clone project.

create virtualenv:
python -m venv myvenv

activate venv:
myvenv/script/activate

install requirements.txt:
pip install -r requirements.txt

makemigration and migrate:

manage.py makemigration
manage.py migrate

you can create superuser if you want:
manage.py createsuperuser



and run server:
manage.py runserver