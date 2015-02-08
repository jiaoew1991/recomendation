__author__ = 'jiaoew'

from abc import ABCMeta, abstractmethod
from datetime import date
from time import mktime
import json

from pymongo import MongoClient

__all__ = [
    'DataSource', 'MongoDataSource'
]


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

    @abstractmethod
    def get_bounds(self):
        pass

    @abstractmethod
    def save_bounds(self):
        pass

    @abstractmethod
    def list_users(self):
        pass


class MongoDataSource(DataSource):
    """
    """

    def __init__(self, url, feature_file):
        super(MongoDataSource, self).__init__()
        self.mongo = MongoClient(url)['simplr']
        self._get_constants()
        self.feature_file = feature_file

    def _get_constants(self):
        self.schools = {s['_id']: idx + 1 for idx, s in enumerate(self.mongo['school'].find())}
        self.campus = {c['_id']: idx + 1 for idx, c in enumerate(self.mongo['campus'].find())}
        self.departments = {d['_id']: idx + 1 for idx, d in enumerate(self.mongo['department'].find())}

    def _normalize_features(self, feat_dict):
        bounds = self.get_bounds()
        norm = lambda x, y, z: (z - y) / (x - y) if x > y else 0
        return [
            norm(feat_dict['school'], bounds['school']['down'], bounds['school']['up']),
            norm(feat_dict['campus'], bounds['campus']['down'], bounds['campus']['up']),
            norm(feat_dict['department'], bounds['department']['down'], bounds['department']['up']),
            norm(feat_dict['gender'], bounds['gender']['down'], bounds['gender']['up']),
            norm(feat_dict['grade'], bounds['grade']['down'], bounds['grade']['up']),
            norm(feat_dict['degree'], bounds['degree']['down'], bounds['degree']['up']),
            norm(feat_dict['verify_edu'], bounds['verify_edu']['down'], bounds['verify_edu']['up']),
            norm(feat_dict['verify_real'], bounds['verify_real']['down'], bounds['verify_real']['up']),
            norm(feat_dict['verify_avatar'], bounds['verify_avatar']['down'], bounds['verify_avatar']['up']),
            norm(feat_dict['join_time'], bounds['join_time']['down'], bounds['join_time']['up']),
            norm(feat_dict['birthday'], bounds['birthday']['down'], bounds['birthday']['up']),
            norm(feat_dict['hometown'], bounds['hometown']['down'], bounds['hometown']['up']),
            norm(feat_dict['height'], bounds['height']['down'], bounds['height']['up']),
            norm(feat_dict['weight'], bounds['weight']['down'], bounds['weight']['up']),
            norm(feat_dict['visitor_count'], bounds['visitor_count']['down'], bounds['visitor_count']['up']),
            norm(feat_dict['like_count'], bounds['like_count']['down'], bounds['like_count']['up']),
            norm(feat_dict['follow_count'], bounds['follow_count']['down'], bounds['follow_count']['up']),
            norm(feat_dict['loc_latitude'], bounds['loc_latitude']['down'], bounds['loc_latitude']['up']),
            norm(feat_dict['loc_longitude'], bounds['loc_longitude']['down'], bounds['loc_longitude']['up'])
        ]

    def get_bounds(self):
        json.load(open(self.feature_file))

    def save_bounds(self):
        json.dump({
            'school': {'up': len(self.schools) + 1, 'down': 0},
            'campus': {'up': len(self.campus) + 1, 'down': 0},
            'department': {'up': len(self.departments) + 1, 'down': 0},
            'gender': {'up': 1, 'down': -1},
            'grade': {'up': 5, 'down': 0},
            'degree': {'up': 3, 'down': 0},
            'verify_edu': {'up': 1, 'down': 0},
            'verify_real': {'up': 1, 'down': 0},
            'verify_avatar': {'up': 1, 'down': 0},
            'join_time': {'up': mktime(date(2016, 1, 1)), 'down': mktime(date(2015, 1, 1))},
            'birthday': {'up': mktime(date(2000, 1, 1)), 'down': mktime(date(1990, 1, 1))},
            'hometown': {'up': 1000, 'down': 0},
            'height': {'up': 210, 'down': 150},
            'weight': {'up': 100, 'down': 40},
            'visitor_count': {'up': 1000, 'down': 0},
            'like_count': {'up': 100, 'down': 0},
            'follow_count': {'up': 100, 'down': 0},
            'loc_latitude': {'up': 90, 'down': -90},
            'loc_longitude': {'up': 180, 'down': -180},
        }, open(self.feature_file, 'w'))

    def get_likes(self, user_id):
        return [item['to'] for item in self.mongo['like'].find({'user': user_id})]

    def get_dislikes(self, user_id):
        return [item['blocked_user'] for item in self.mongo['blockeduser'].find({'user': user_id})]

    def get_features(self, user_id):
        origin_user = self.mongo['user'].find_one({'user': user_id})
        join_time = self.mongo['user_base'].find_one(user_id)['join_time']
        profile = self.mongo['profile'].find_one({'user': user_id})
        stat = self.mongo['user_stat'].find_one({'user': user_id})
        features = {
            'school': self.schools[origin_user['school']],
            'campus': self.campus[origin_user['campus']],
            'department': self.departments[origin_user['department']],
            'gender': origin_user['gender'],
            'grade': origin_user['grade'],
            'degree': origin_user['degree'],
            'verify_edu': origin_user['verify']['edu'],
            'verify_real': origin_user['verify']['real'],
            'verify_avatar': origin_user['verify']['avatar'],
            'join_time': join_time,
            'birthday': mktime(date(*profile['birthday'].split('-')).timetuple()),
            'hometown': hash(profile['hometown']) % 1000,
            'height': profile['height'],
            'weight': profile['weight'],
            'visitor_count': stat['visitor_count'],
            'like_count': stat['like_count'],
            'follow_count': stat['follow_count'],
            'loc_latitude': stat['loc'][0] if stat['loc_enabled'] else 0,
            'loc_longitude': stat['loc'][1] if stat['loc_enabled'] else 0
        }
        return self._normalize_features(features)

    def list_users(self):
        return [item['_id'] for item in self.mongo['user_base'].find()]
