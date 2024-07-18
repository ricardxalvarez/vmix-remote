echo "# vmix-remote"

Start virtual enviroment

python -m venv ./env 
source env/bin/activate 
pip install -r requirements.txt
python3 main.py


run app
gunicorn main:app