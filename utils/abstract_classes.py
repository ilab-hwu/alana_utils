# import abc
from flask_restful import Resource
import json
from utils.dict_query import DictQuery


class Bot(Resource):

    def __init__(self, bot_name, bot_version=None):
        self.response = Response({'bot_name': bot_name, 'bot_version': bot_version})


class Response(object):
    def __init__(self, json_data=None):
        self.result = None
        self.bot_name = None
        self.bot_version = None
        self.lock_requested = False
        self.bot_params = {}
        self.user_attributes = {}

        if json_data:
            self.__dict__.update(json_data)

    def toJSON(self):
        # Placeholder to add more preprocessing here if we need to
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    # class BotAttributes:
    #     """
    #     Deserialize bot_attributes json
    #     TODO: Not yet implemented
    #     """
    #     def __init__(self, json_data):
    #         self.__dict__ = json.loads(json_data)
    #
    #     def toJSON(self):
    #         return self.__dict__
    #
    #     def __str__(self):
    #         return str(self.__dict__)



class UserAttributes(object):
    def __init__(self, json_data=None):
        if not json_data:
            self.user_id = None
            self.user_name = None
            self.preferences = []
            self.dislikes = []
            self.last_sessionID = None
        else:
            self.__dict__ = json_data

    def toJSON(self):
        # Placeholder to add more preprocessing here if we need to
        return self.__dict__


class SelectionStrategy(object):
    def select_response(self, bucket, current_state):
        raise NotImplementedError
