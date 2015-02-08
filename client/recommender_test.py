__author__ = 'jiaoew'

from os import remove
from unittest import TestCase

from data_source import MongoDataSource
from recommender import Recommender


SERVER_URL = 'omgthree.cloudapp.net:8000'
MONGO_URL = 'mongo://@omgthree.cloudapp.net:27017'
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
        print self.client.recommend(self.data_source.list_users()[0]['_id'])
