"""
Send sample query to prediction engine
"""

import predictionio
engine_client = predictionio.EngineClient(url="http://localhost:8000")
event_client = predictionio.EventClient(access_key='Zwybqp8kKTdTApM0S53HEB31Ti6bgiaDFGNMZ8TlCyfhJjDhouUtNC3bCgYcTdiX', url="http://localhost:7070", threads=5, qsize=500)
print engine_client.send_query({'userId': 20,"items": ['100', '101'], "num": 10})
#event_client.create_event(
        #event="like",
        #entity_type="user",
        #entity_id='20',
        #target_entity_type="item",
        #target_entity_id='25'
        #)
