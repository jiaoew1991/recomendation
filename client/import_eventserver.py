"""
Import sample data for similar product engine
"""

import argparse
import random
import os

import predictionio

from data_source import DataSource


SEED = 3


def import_txt_events(client, dir):
    random.seed(SEED)
    count = 0
    print client.get_status()
    print "Importing data..."

    # generate 10 users, with user ids u1,u2,....,u10
    with open(os.path.join(dir, "user.txt"), 'r') as user_file:
        for user_line in user_file:
            user_data = user_line.rstrip().split('\t')
            user_id = user_data[0]
            print "Set user", user_id
            client.create_event(
                event="$set",
                entity_type="user",
                entity_id=user_id
            )
            client.create_event(
                event="$set",
                entity_type="item",
                entity_id=user_id,
                properties={
                    "profiles": map(float, user_data[1:])
                }
            )
            count += 1

    with open(os.path.join(dir, 'like.txt'), 'r') as like_file:
        for like_line in like_file:
            like_data = like_line.rstrip().split('\t')
            user_id = like_data[0]
            item_id = like_data[1]
            print "User", user_id, "like item", item_id
            client.create_event(
                event="like",
                entity_type="user",
                entity_id=user_id,
                target_entity_type="item",
                target_entity_id=item_id
            )
            count += 1

    print "%s events are imported." % count


def import_data_event(client, event_url, data_source):
    assert isinstance(data_source, DataSource)

    users = data_source.list_users()
    for user_id in users:
        print 'set user {}'.format(user_id)
        client.create_event(
            event="$set",
            entity_type="user",
            entity_id=user_id
        )
        client.create_event(
            event="$set",
            entity_type="item",
            entity_id=user_id,
            properties={
                "profiles": map(float, data_source.get_features(user_id))
            }
        )
        likes = data_source.get_likes(user_id)
        [client.create_event(
            event="like",
            entity_type="user",
            entity_id=user_id,
            target_entity_type="item",
            target_entity_id=item_id
        ) for item_id in likes]
        dislikes = data_source.get_dislikes(user_id)
        [client.create_event(
            event="dislike",
            entity_type="user",
            entity_id=user_id,
            target_entity_type="item",
            target_entity_id=item_id
        ) for item_id in dislikes]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Import sample data for similar product engine")
    parser.add_argument('--access_key', default='invald_access_key')
    parser.add_argument('--url', default="http://localhost:7070")
    parser.add_argument('--dir', default="./data")

    args = parser.parse_args()
    print args

    client = predictionio.EventClient(
        access_key=args.access_key,
        url=args.url,
        threads=5,
        qsize=500)
    import_txt_events(client, args.dir)
