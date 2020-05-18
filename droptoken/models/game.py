from datetime import datetime
from flask_mongoengine import Document
import mongoengine as me

STATE_CHOICES = ['IN_PROGRESS', 'DONE']
MOVE_CHOICES = ['MOVE', 'QUIT']

class PlayerModel(me.EmbeddedDocument):
    token = me.IntField(required=True)
    name = me.StringField(max_length=50, required=True)
    # has_quit = me.BooleanField(choices=[True])  # possibly useful if more than 2 players


class MoveModel(me.EmbeddedDocument):
    turn = me.IntField(required=True)
    move_type = me.StringField(max_length=4, required=True, choices=MOVE_CHOICES, default='MOVE')
    player_name = me.StringField(max_length=50, required=True)
    column = me.IntField()


class GameModel(Document):
    players = me.EmbeddedDocumentListField(PlayerModel, required=True)
    num_rows = me.IntField(required=True)
    num_cols = me.IntField(required=True)
    state = me.StringField(max_length=11, required=True, choices=STATE_CHOICES, default='IN_PROGRESS')
    winner = me.StringField(max_length=50)
    current_token = me.IntField(required=True, default=1)
    moves = me.EmbeddedDocumentListField(MoveModel, default=[])
     # can possibly use this with save_condition: http://docs.mongoengine.org/apireference.html#mongoengine.Document.save
    last_modified = me.DateTimeField(required=True, default=datetime.utcnow) 
