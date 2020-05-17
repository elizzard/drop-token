from flask import Flask
from flask_restful import Api
from droptoken.resources.game import GameList

app = Flask(__name__)
api = Api(app)

api.add_resource(GameList, '/drop-token/')

if __name__ == '__main__':
    app.run(debug=True)