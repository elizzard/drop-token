from flask_restful import Resource, reqparse
from droptoken.models.game import GameModel, PlayerModel


# we get input type validation and 400s for free with reqparse
# TODO: add more strict validation on params (player names unique, #players == 2 and #rows/cols == 4)
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
    def get(self):
        """
            Output
                { "games" : ["gameid1", "gameid2"] }
            Status codes
                • 200 - OK. On success
        """
        res = [str(r.id) for r in GameModel.objects]
        return { "games": res}
   
    def post(self):
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
        args = post_parser.parse_args()
        
        player_list = [
            PlayerModel(
                token=i,
                name=name
            )
            for i, name in enumerate(args['players'], start=1)
        ]

        g = GameModel(
            players=player_list,
            num_cols=args['columns'],
            num_rows=args['rows']
        )
        g.save()
        return { "gameId": f"{g.id}"}
