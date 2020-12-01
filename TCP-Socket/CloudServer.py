import socket
import sys
import threading
from mxnet import nd
from Utils import *

class CloudServer:
    def __init__(self):
        self.parameter = [nd.random_normal(0,1,shape=(128,784))] +\
                    [nd.random_normal(0,1,shape=(128))] +\
                    [nd.random_normal(0,1,shape=(64,128))] +\
                    [nd.random_normal(0,1,shape=(64))] +\
                    [nd.random_normal(0,1,shape=(10,64))] +\
                    [nd.random_normal(0,1,shape=(10))]
        self.buffer = []
        self.cv = threading.Condition()
        self.terminated = False
        self.connections = []
        self.num_edge_servers = 1
        self.num_epochs = 3

    def process(self):
        HOST = socket.gethostname()
        PORT = 9999
        connection_thread = threading.Thread(target=server_handle_connection, args=(HOST, PORT, self, True))
        connection_thread.start()

        with self.cv:
            while len(self.connections) < 1:
                self.cv.wait()

        for i in range(self.num_epochs):
            for conn in self.connections:
                send_message(self.parameter, self.connections[0])
            print('sent parameter to edge servers')

            # wait for response from edge servers
            with self.cv:
                while len(self.buffer) < self.num_edge_servers:
                    self.cv.wait()
            print('received responses from edge servers')

            self.parameter = self.aggregate()

        self.terminated = True

    def aggregate(self):
        return self.buffer.pop()

if __name__ == "__main__":
    cloud_server = CloudServer()
    cloud_server.process()