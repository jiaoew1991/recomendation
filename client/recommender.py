#!/usr/bin/env python
# -*- coding: utf-8 -*-

from data_source import DataSource
import predictionio


class Recommender():
    """docstring for Recommander"""

    def __init__(self, url, data_source):
        assert isinstance(data_source, DataSource)

        self.client = predictionio.EngineClient(url)
        self.data_source = data_source

    def recommend(self, user_id, start=0, size=20):
        """
        """
        user_id = str(user_id)
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
        print result
        return result


