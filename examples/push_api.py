############################
### Not Functioning Code ###
############################

# This example exposes a push endpoint
import json
from datetime import timedelta, datetime, timezone
import socket

from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutput
from bytewax.inputs import PartitionedInput, StatefulSource

from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

class PushInput(PartitionedInput):

    def __init__(self, endpoint:str, port: int = 8000, host: str = "0.0.0.0"):
        self.endpoint = endpoint
        # Define socket host and port
        self.host = host
        self.port = port

    def list_parts(self):
        return {"single-part"}

    def build_part(self, for_key, resume_state):
        assert for_key == "single-part"
        assert resume_state is None
        return _PushSource(self.endpoint, self.host, self.port)
    
class _PushSource(StatefulSource):
    
    def __init__(self, endpoint, host, port):
        # Create connection
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        print('Listening on port %s ...' % port)

    def next(self):
        # Wait for client connections
        client_connection, client_address = self.server_socket.accept()

        # Get the client request
        request = client_connection.recv(1024)
        request = HTTPRequest(request)
        content_len = int(request.headers['Content-Length'])
        print(content_len)
        post_body = request.rfile.read(content_len)
        data = json.loads(post_body)

        # Send HTTP response
        response = 'HTTP/1.0 200 OK'
        client_connection.sendall(response.encode())
        client_connection.close()

        return data
    
    def snapshot(self):
        pass

    def close(self):
        pass

# Define the dataflow object and input.
flow = Dataflow()
flow.input(
    "push-input",
    PushInput("hey")
)
flow.inspect(print)

def key_on_user_id(payload):
    return (payload['anonymousId'], payload)

flow.map(key_on_user_id)

class Event:
    def __init__(self):
        self.events = {}

    def update(self, new_event):
        self.events[new_event['name']] = new_event['timestamp']
        return (self, self.events)
        

flow.stateful_map('calc', Event, Event.update)

flow.output("out", StdOutput())
