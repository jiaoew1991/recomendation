__author__ = 'jiaoew'

from os import remove
import unittest
from unittest import TestCase

from data_source import MongoDataSource
from recommender import Recommender


SERVER_URL = 'http://localhost:8000'
MONGO_URL = 'mongodb://localhost:27017/simplr'
FEATURE_FILE = 'feature.txt'


class TestRecommender(TestCase):
    def setUp(self):
        super(TestRecommender, self).setUp()
        mongo_source = MongoDataSource(MONGO_URL, FEATURE_FILE)
        mongo_source.save_bounds()
        self.client = Recommender(SERVER_URL, mongo_source)
        self.data_source = mongo_source

    def tearDown(self):
        super(TestRecommender, self).tearDown()
        remove(FEATURE_FILE)

    def test_recommend_exist(self):
        print self.client.recommend(self.data_source.list_users()[0])

if __name__ == '__main__':
    unittest.main()
