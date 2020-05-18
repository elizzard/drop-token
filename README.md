# drop-token
REST API that enables 2 users to play connect-four. 98point6 homework.

## Setup
Disclaimer: Apologies for having to do setup. I wanted to dockerise this, but ran into some routing bugs and ran out of time. 
Any questions? - feel free to reach out at liza.kadochnikova@gmail.com


### Prerequisites
You will need 
* Docker (to run MongoDB with)
* python3
* pipenv package, see https://pipenv-fork.readthedocs.io/en/latest/
* clone this repo


### Environment
From project root:

Load dependencies 
```
pipenv shell
```

Make sure flask is happy:
```
export FLASK_APP=app.py
```

### Run

First, pull dowm and start MongoDB image
```
docker pull mongo
docker run -p 27017:27017 --name drop-token-mongo -d mongo
```
The db should run without any secrets by default.

Then start the flask app, from app directory:
```
cd droptoken
flask run
```

You should be able to query the API on default port `localhost:5000`.

### Tests
Unit Tests:
```
pytest
```

API was tested manually via Postman. Unit tests TBD.


### Troubleshooting

Useful things to know to inspect state of the DB: 
```
docker logs drop-token-mongo
docker exec -it drop-token-mongo bash
```
https://www.thepolyglotdeveloper.com/2019/01/getting-started-mongodb-docker-container-deployment/
https://docs.mongodb.com/manual/reference/mongo-shell/


To enable flask debug mode, add this to out environment.
(I left debug=True in the app initialization, but it won't actually happen unless this variabnle is set)
```
export FLASK_ENV=development
```


## Project Structure
```
├── Pipfile                 # dependency management files for pipenv
├── Pipfile.lock
├── README.md
└── droptoken               
    ├── app.py              # FlaskApp setup, routing and settings
    ├── logic.py            # Main business logic for the game 
    ├── models              # ODM definitions live here
    │   └── game.py
    ├── resources           # API endpoint controllers live here
    │   ├── game.py
    │   └── moves.py
    └── tests
        └── test_logic.py   # This one is a bit scarce - only board game logic tested.
```
