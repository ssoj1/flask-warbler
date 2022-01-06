# flask-warbler

Twitter clone built with Python, Flask, SQLAlchemy, PostgreSQL, and uses template-rendering via Jinja.

**To create your Python Virtual Environment:**  
$ python3 -m venv venv  
$ source venv/bin/activate  
(venv) $ pip install -r requirements.txt  

**To setup a database:**  
(venv) $ psql  
=# CREATE DATABASE warbler;  
=# (control-d)  
(venv) $ python seed.py  

**To start the server:**  
flask run  

**To run tests:**  
python3 -m unittest test_message_model.py
FLASK_ENV=production python -m unittest test_message_views.py
python3 -m unittest test_user_model.py
FLASK_ENV=production python -m unittest test_user_views.py

