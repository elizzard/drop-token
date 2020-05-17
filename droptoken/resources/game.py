from flask_restful import Resource, reqparse



# we get input type validation and 400s for free with reqparse
# TODO: add more strict validation on params (# players and # rows/cols)
post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'players', dest='players', action='append',
    location='json', required=True,
    help='Names of the players participating in the game must be a list of strings. Error: {error_msg}',
)
post_parser.add_argument(
    'columns', dest='columns',
    type=int, location='json', required=True,
    help='Number of columns on the game board must be >= 4. Error: {error_msg}',
)
post_parser.add_argument(
    'rows', dest='rows',
    type=int, location='json', required=True,
    help='Number of rows on the game board must be >= 4. Error: {error_msg}',
)


class GameList(Resource):
    """
    Output
        { "games" : ["gameid1", "gameid2"] }
    Status codes
        • 200 - OK. On success
    """
    def get(self):
        return { "games" : ["gameid1", "gameid2"] }
   
    """
    Input:
        { "players": ["player1", "player2"],
        "columns": 4,
        "rows": 4
        }
    Output:
        { "gameId": "some_string_token"}
    Status codes
        • 200 - OK. On success
        • 400 - Malformed request 
    """    
    def post(self):
        args = post_parser.parse_args()
        return { "gameId": f"{str(args)}"}