############################
### Not Functioning Code ###
############################

import json
from datetime import datetime, timedelta, timezone

from bytewax.dataflow import Dataflow
from bytewax.window import EventClockConfig, SessionWindow


from embed.sources.streaming import KafkaInput
from embed.stores.sqlite import RedisVectorOuput
from embed.embedding.temporal import sequence_embed

model = "my fancy model"

flow = Dataflow()
flow.input("events", KafkaInput("my_topic"))
# output: {"user_id": 1, "event_type": "click", "entity": "product1", "timestamp":2023-05-31 13:19:07.830219}
flow.map(json.loads)

# Build a session window of events
window_config = SessionWindow(gap=timedelta(minutes=30))
clock_config = EventClockConfig(
                lambda e: e["time"], wait_for_system_duration=timedelta(seconds=0)
                )

flow.collect_window("collect", clock_config, window_config)
# output: [{"user_id": 1, "event_type": "click", "entity": "product1", "timestamp":2023-05-31 13:19:07.830219}, {"user_id": 1, "event_type": "click", "entity": "product2", "timestamp":2023-05-31 13:19:10.80456}]

flow.map(lambda x: sequence_embed(x, model))
# output: <class UserEvents>
# class UserEvents:
#     user_id: str
#     window_id: str # hashed time window
#     events: Optional[list]
#     embedding: Optional[list]

flow.output("out", RedisVectorOuput())