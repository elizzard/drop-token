from flask_restful import Resource, reqparse, abort
from droptoken.models.game import GameModel, PlayerModel, MoveModel
from droptoken.logic import GameBoard
from mongoengine.errors import DoesNotExist, ValidationError


post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'column', dest='column',
    type=int, location='json', required=True,
    help='Number of the column to drop the token into. Error: {error_msg}',
)

def get_next_token(token_list, current_token):
    token_list.sort()
    i = token_list.index(current_token)
    next_i = (i + 1) % len(token_list)
    return token_list[next_i]

class Moves(Resource):
    """
        Input:
            {
            "column" : 2
            }
        Output:
            {
            "move": "{gameId}/moves/{move_number}"
            }
        Status codes:
            • 200 - OK. On success
            • 400 - Malformed input. Illegal move
            • 404 - Game not found or player is not a part of it.
            • 409 - Player tried to post when it’s not their turn.
            • 410 - Game is already in DONE state. (additional requirement, noticed while testing)
    """
    def post(self, game_id, player_id):
        args = post_parser.parse_args()
        request_column = args['column']

        # get the game object
        try:
            g = GameModel.objects(id=game_id).get()
        except (DoesNotExist, ValidationError) :
            abort(404, message=f"Game {game_id} not found.") 

        # check if player is part of the game
        try:
            p = g.players.get(name=player_id)
        except DoesNotExist:
            abort(404, message=f"Player {player_id} does not belong to game {game_id}.") 

        # check if game is already DONE
        if g.state == 'DONE':
            abort(410, message=f"The game is already DONE.")

        # check if it's player's turn
        if g.current_token != p.token:
            abort(409, message=f"Player {player_id} tried to post when it’s not their turn.")
        
        # build GameBoard
        gb = GameBoard(g.num_cols, g.num_rows)
        players_to_token_map = { p.name: p.token for p in g.players }
        moves = [ { 'token': players_to_token_map[m.player_name], 'column': m.column } for m in g.moves if m.move_type == 'MOVE']
        gb.apply_moves(moves)

        # test if next move is legal
        if not gb.can_drop(request_column):
            abort(400, message=f"Illegal move. Unable to drop token in column {request_column}")

        # apply move and check winning condition
        row = gb.drop_token(request_column, p.token)

        if gb.check_win(request_column, row):
            g.state = 'DONE'
            g.winner = p.name

        move_number = len(moves) + 1
        g.moves.create(turn=move_number, move_type='MOVE', player_name=p.name, column=request_column)

        token_list = list(players_to_token_map.values())
        g.current_token = get_next_token(token_list, p.token)
        
        # TODO: possibly use conditional save here, to make sure we're updating the latest tamestamp seen
        g.save()
        
        # success
        return { "move": f"{game_id}/moves/{move_number}" }   # TODO: use @marshal_with, fields.Url('endpoint_resource')

    """
        Status codes:
            • 202 - OK. On success
            • 404 - Game not found or player is not a part of it.
            • 410 - Game is already in DONE state.
    """    
    def delete(self, game_id, player_id):
        # get the game object
        try:
            g = GameModel.objects(id=game_id).get()
        except (DoesNotExist, ValidationError) :
            abort(404, message=f"Game {game_id} not found.") 

        # check if player is part of the game
        try:
            p = g.players.get(name=player_id)
        except DoesNotExist:
            abort(404, message=f"Player {player_id} does not belong to game {game_id}.") 

        # check if game is already DONE
        if g.state == 'DONE':
            abort(410, message=f"The game is already DONE.")

        # add a move
        move_number = g.moves.count() + 1
        g.moves.create(turn=move_number, move_type='QUIT', player_name=p.name)
        
        # update winning status and save (assuming 2 players)
        remaining = g.players.exclude(name=player_id)
        g.state = 'DONE'
        g.winner = remaining.first().name

        # TODO: possibly use conditional save here, to make sure we're updating the latest tamestamp seen
        g.save()

        return
