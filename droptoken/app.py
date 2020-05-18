from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from droptoken.resources.game import GameList
from droptoken.resources.moves import Moves


app = Flask(__name__)
# this mongodb is running locally in a docker container
app.config['MONGODB_SETTINGS'] = {
    "db": "droptokendb",
}
db = MongoEngine(app)
api = Api(app)

api.add_resource(GameList, '/drop-token')
api.add_resource(Moves, '/drop-token/<string:game_id>/<string:player_id>')

if __name__ == '__main__':
    app.run(debug=True)