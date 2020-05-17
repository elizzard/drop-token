from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from droptoken.resources.game import GameList

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    "db": "droptokendb",
}
db = MongoEngine(app)
api = Api(app)

api.add_resource(GameList, '/drop-token/')

if __name__ == '__main__':
    app.run(debug=True)