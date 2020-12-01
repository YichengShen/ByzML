#Socket client example in python

import socket	#for sockets
from mxnet import nd
from Utils import *

class Worker:

    def __init__(self):
        self.gradient = None

    def process(self):
        gradient = [nd.random_normal(0,1,shape=(128,784))] +\
                    [nd.random_normal(0,1,shape=(128))] +\
                    [nd.random_normal(0,1,shape=(64,128))] +\
                    [nd.random_normal(0,1,shape=(64))] +\
                    [nd.random_normal(0,1,shape=(10,64))] +\
                    [nd.random_normal(0,1,shape=(10))]

        # Build connection with edge server
        host = socket.gethostname()
        port = 6666
        
        while True:
            edge_server_conn = client_build_connection(host, port)
            print('connection established')

            parameter = wait_for_message(edge_server_conn)
            print('received gradient')
            try:
                send_message(gradient, edge_server_conn)
            except:
                break
            print('gradient sent to edge server')

            # Wait for a confirmation message from edge server
            wait_for_message(edge_server_conn)
            print('confirmation received. Closing.')
            edge_server_conn.close()

    def compute(self, parameter):
        # TODO: replace this
        return parameter

if __name__ == "__main__":
    worker = Worker()
    worker.process()