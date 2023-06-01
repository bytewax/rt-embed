import json
import logging
import queue
import threading

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import StatelessSource, DynamicInput
from flask import Flask, request

app = Flask(__name__)
data_queue = queue.Queue()

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    data_queue.put(data)
    return json.dumps({"success": True}), 200

class _PushSource(StatelessSource):
    def next(self):
        if not data_queue.empty():
            return data_queue.get()
        else:
            return None

class PushInput(DynamicInput):
    def build(self, worker_count, worker_index):
        assert worker_count == 1
        return _PushSource()

def start_flask_app():
    app.run(host='0.0.0.0', port=8000)

# Start the Flask app in a separate thread
flask_thread = threading.Thread(target=start_flask_app)
flask_thread.start()

flow = Dataflow()
flow.input("flask-input", PushInput())
flow.inspect(print)
flow.output("out", StdOutput())