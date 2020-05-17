from flask_mongoengine import Document
import mongoengine as me

class GameModel(Document):
    players = me.ListField(me.StringField(max_length=50), required=True)
    num_rows = me.IntField(required=True)
    num_cols = me.IntField(required=True)
    