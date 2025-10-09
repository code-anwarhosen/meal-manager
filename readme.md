## Meal Manager
A simple project to organize meals and grocery list for single/group of people and keep track of expense.


## Get Started

```bash
git clone https://github.com/code-anwarhosen/meal-manager.git
cd meal-manager

# Activate venv, then
pip install -r requirements.txt

python manage.py makemigrations
python manage.py makemigrations app

python manage.py migrate 
python manage.py migrate app

# Create a .env file with these content variable
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

python manage.py runserver
```

copyright: [(github) code-anwarhosen](https://github.com/code-anwarhosen)
Date: Oct 2025
