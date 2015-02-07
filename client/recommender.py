#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from pymongo import MongoClient
import predictionio


class DataSource:
    """
    """

    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_likes(self, user_id):
        """
        """
        pass

    @abstractmethod
    def get_dislikes(self, user_id):
        """
        """
        pass

    @abstractmethod
    def get_features(self, user_id):
        """
        """
        pass


class MongoDataSource(DataSource):
    """
    """

    def __init__(self, url):
        super(MongoDataSource, self).__init__()
        self.mongo = MongoClient(url)

    def get_likes(self, user_id):
        """
        """
        pass

    def get_dislikes(self, user_id):
        pass

    def get_features(self, user_id):
        pass


class Recommender():
    """docstring for Recommander"""

    def __init__(self, url, data_source):
        super(Recommender, self).__init__()
        self.client = predictionio.EngineClient(url)
        self.data_source = data_source

    def recommend(self, user_id, start=0, size=20):
        """
        """
        features = self.data_source.get_features(user_id)
        likes = self.data_source.get_likes(user_id)
        black_list = self.data_source.get_likes(user_id)
        result = self.client.send_query({
            'userId': user_id,
            'profiles': features,
            'likes': likes,
            'start': start,
            'size': size,
            'blackList': black_list
        })
        return result


