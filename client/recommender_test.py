__author__ = 'jiaoew'

from os import remove

from unittest import TestCase
import unittest

from data_source import MongoDataSource
from recommender import Recommender


SERVER_URL = 'http://omgthree.cloudapp.net:8000'
MONGO_URL = 'mongodb://omgthree.cloudapp.net:27017/simplr'
FEATURE_FILE = 'feature.txt'


class TestRecommender(TestCase):
    def setUp(self):
        super(TestRecommender, self).setUp()
        mongo_source = MongoDataSource(MONGO_URL, FEATURE_FILE)
        mongo_source.save_bounds()
        self.data_source = mongo_source
        # print self.data_source.list_users()
        self.client = Recommender(SERVER_URL, mongo_source)

    def tearDown(self):
        super(TestRecommender, self).tearDown()
        remove(FEATURE_FILE)

    def test_recommend_exist(self):
        print self.client.recommend('54d3365bdb9eb83ba8ff36f3')


if __name__ == '__main__':
    unittest.main()
