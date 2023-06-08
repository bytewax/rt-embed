############################
### Not Functioning Code ###
############################

# This example exposes a push endpoint
import json
import logging
import socket

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import PartitionedInput, StatefulSource
from http.server import BaseHTTPRequestHandler
from io import BytesIO

logging.basicConfig(level=logging.INFO)


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
    def __init__(self, endpoint: str, port: int = 8000, host: str = "0.0.0.0"):
        self.endpoint = endpoint
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        logging.info("Listening on port %s ...", port)

    def next(self):
        client_connection, client_address = self.server_socket.accept()
        try:
            request = client_connection.recv(1024)
            request = HTTPRequest(request)
            content_len = int(request.headers["Content-Length"])
            post_body = request.rfile.read(content_len)
            data = json.loads(post_body)
        except Exception as e:
            logging.error(f"Failed to process request: {e}")
            return None
        finally:
            response = "HTTP/1.0 200 OK"
            client_connection.sendall(response.encode())
            client_connection.close()
        return data

    def snapshot(self):
        pass

    def close(self):
        self.server_socket.close()
        logging.info("Server socket closed.")


flow = Dataflow()
flow.input("push-input", PushInput("hey"))
flow.output("out", StdOutput())
