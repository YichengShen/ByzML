import socket	#for sockets
import sys	#for exit
import threading
from Utils import *

class EdgeServer:
    def __init__(self):
        self.model = 0
        self.gradient = 0
        self.buffer = []
        self.cv = threading.Condition()
        self.terminated = False
        self.connections = []
        self.num_epochs = 3
        self.num_of_workers = 3

    def process(self):
        HOST = socket.gethostname()
        WORKER_PORT = 6666
        CLOUD_SERVER_PORT = 9999
        threading.Thread(target=server_handle_connection, args=(HOST, WORKER_PORT, self, False)).start()

        # build_connection with cloud server
        central_server_conn = client_build_connection(HOST, CLOUD_SERVER_PORT)

        for i in range(self.num_epochs):
            # wait for at least num_of_workers workers to join
            with self.cv:
                while len(self.connections) < self.num_of_workers:
                    self.cv.wait()

            parameter = wait_for_message(central_server_conn)
            print('received parameter from central server')

            # send parameters to all connected workers
            for conn in self.connections:
                send_message(parameter, conn)
            print('sent messages to workers')
            
            # wait for gradients from workers
            with self.cv:
                while len(self.buffer) < self.num_of_workers:
                    self.cv.wait()
            print('received responses from workers')

            reduced_gradient = self.reduce()
            aggregated_gradient = self.aggregate(reduced_gradient)

            # send aggregated result to server
            send_message(aggregated_gradient, central_server_conn)
            print('sent aggregated result to central server')

            # Edge server has to close the connections with workers every time
            for conn in self.connections:
                send_message(b'1', conn)
                conn.close()
            self.connections = []

        
        central_server_conn.close()
        self.terminated = True

    def reduce(self):
        # TODO: replace this
        with self.cv:
            return self.buffer.pop()

    def aggregate(self, data):
        # TODO: replace this
        return data

if __name__ == "__main__":
    edge_server = EdgeServer()
    edge_server.process()