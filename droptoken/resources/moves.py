from flask_restful import Resource, reqparse, abort
from droptoken.models.game import GameModel, PlayerModel, MoveModel
from droptoken.logic import GameBoard
from mongoengine.errors import DoesNotExist, ValidationError


move_list_get_parser = reqparse.RequestParser()
move_list_get_parser.add_argument(
    'start', dest='start', default=0,
    type=int, location='args',
    help='Which move number to start with. Error: {error_msg}',
)
move_list_get_parser.add_argument(
    'until', dest='until', default=-1,
    type=int, location='args',
    help='Which move number to end with. Error: {error_msg}',
)

moves_post_parser = reqparse.RequestParser()
moves_post_parser.add_argument(
    'column', dest='column',
    type=int, location='json', required=True,
    help='Number of the column to drop the token into. Error: {error_msg}',
)

def get_next_token(token_list, current_token):
    """
        Given a list if tokens (comparable to each other, unique) and current token,
        find the token for the next turn. This cycles through tokens in ascending order.
    """
    token_list.sort()
    i = token_list.index(current_token)
    next_i = (i + 1) % len(token_list)
    return token_list[next_i]


def get_matching_moves(game, start, until):
    # get the matching moves, filter locally
    moves_tuples_list = [
        (
            m.turn ,  # we will sort by this key
            ({
                'type': m.move_type,
                'player': m.player_name,
                'column': m.column
            } 
            if m.move_type == 'MOVE' 
            else {
                'type': m.move_type,
                'player': m.player_name,
            })
        ) 
        for m in game.moves
        if m.turn >= start and m.turn <= until
    ]

    # display, in order (sort, just in case);
    def compare_key(item):
        return item[0]
    moves_tuples_list.sort(key=compare_key)
    return [ move for _, move in moves_tuples_list]


class Moves(Resource):
    def get(self, game_id, player_id):
        """
            Optional Query parameters: GET /drop_token/{gameId}/moves?start=0&until=1.
                Note: they are zero-indexed
                If the params define a range that is greater than moves available, return the partial/what's available
                404 only if 0 moves were found

            HACK: player_id == 'moves', until we can regex-match the routing
            TODO: move this into a separate resource MovesList once regex routing is supported

            Output:
                {
                "moves": [
                {"type": "MOVE", "player": "player1", "column":1},
                {"type": "QUIT", "player": "player2"}
                ]
                }
            Status codes:
                • 200 - OK. On success
                • 400 - Malformed request
                • 404 - Game/moves not found
        """
        # make sure we respond to /moves only
        if player_id != 'moves':
            abort(404, message=f"URL /drop_token/{game_id}/{player_id} not found.")

        # get the game object
        try:
            g = GameModel.objects(id=game_id).get()
        except (DoesNotExist, ValidationError) :
            abort(404, message=f"Game {game_id} not found.")

        args = move_list_get_parser.parse_args()
        total_moves = g.moves.count()

        # we know this one is impossible
        if args['start'] >= total_moves:
            abort(404, message=f"No moves found for game {game_id}, starting at move {args['start']}.")

        # get the correct boundaries, shift to 1-indexed (because that's how we store them in db at the moment)
        # TODO: maybe rethink the 1-indexing on moves
        start = args['start'] + 1 if args['start'] >=0 else 1
        until = args['until'] + 1 if args['until'] < total_moves and args['until'] > -1 else total_moves

        return get_matching_moves(g, start, until)


    def post(self, game_id, player_id):
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
        args = moves_post_parser.parse_args()
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


    def delete(self, game_id, player_id):
        """
            Status codes:
                • 202 - OK. On success
                • 404 - Game not found or player is not a part of it.
                • 410 - Game is already in DONE state.
        """    
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
        
        # update winning status and save (TODO: assuming 2 players, generalize this )
        remaining = g.players.exclude(name=player_id)
        g.state = 'DONE'
        g.winner = remaining.first().name

        # TODO: possibly use conditional save here, to make sure we're updating the latest tamestamp seen
        g.save()

        return {}
