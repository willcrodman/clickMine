# clickMine.org

### good article on proof of work
https://michaelnielsen.org/ddi/how-the-bitcoin-protocol-actually-works/
stopping point: " With the time-ordering now understood, let’s return to think about what happens if a dishonest party tries to double spend."

### launch API server
python3 app.py

### Start and end virtual environment
source venv/bin/activate
exit

### Install third party packages
pip install -r requirements.txt

### Build the docker image
docker build -t clickmine-image .

### Run docker container
docker run -d --name clickmine-container -p 80:80 clickmine-image
