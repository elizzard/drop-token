from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from droptoken.resources.game import GameList, GameDetail
from droptoken.resources.moves import Moves, MoveDetail


app = Flask(__name__)
# this mongodb is running locally in a docker container
app.config['MONGODB_SETTINGS'] = {
    "db": "droptokendb",
}
db = MongoEngine(app)
api = Api(app) # TODO: use prefix='drop-token' to clean up the routes below

# NOTE: This snippet is useful for debugging routing issues
### Begin Diagnosing routing issues

# from flask_restful import Resource
# class SiteMap(Resource):
#     def get(self):
#         return {
#             'rules': [str(rule) for rule in app.url_map.iter_rules()],  # rule.__dict__
#             'converters': [ {k : str(v)} for k,v in app.url_map.converters.items()]
#         }
# api.add_resource(SiteMap, '/site-map')

### End Diagnosing routing issues


# NOTE: Repeat routes with and without '/' at the end for resources handling POST.
# This is just in case: Flask should redirect automatically, however, 
# Flask Debug-mode informed me that forwarding may lose the payload in some cases.
# I am choosing to heed that warning.
api.add_resource(GameList, '/drop-token', '/drop-token/')
api.add_resource(GameDetail, '/drop-token/<string:game_id>')
api.add_resource(Moves, '/drop-token/<string:game_id>/<string:player_id>', 
    '/drop-token/<string:game_id>/<string:player_id>/')
api.add_resource(MoveDetail, '/drop-token/<string:game_id>/moves/<int:move_id>')

# TODO: this route '/drop_token/<string:game_id>/moves' is currently in conflict with 
#   '/drop-token/<string:game_id>/<string:player_id>', because player_id a string 
#   and Flask cannot distinguish between is and 'moves' string literal.
#   I am merging the two, for now. However, there is a way to make regex matching happen: 
#   see https://gist.github.com/ekayxu/5743138 
# api.add_resource(MovesList, '/drop_token/<string:game_id>/moves')


# api.init_app(app) # TODO: flask is working without this??

if __name__ == '__main__':
    app.run(debug=True)