from PyQt5.QtCore import QObject, QThread, pyqtSignal
import socket
import sys

# worker class defining methods to be run in server thread
class worker(QObject):
    all_connections = []
    all_address = []
    sentCommand = pyqtSignal(list)
    conn_estabilished = pyqtSignal(str)

    # create a socket 
    def create_socket(self):
        try:
            self.host = ""
            self.port = 9995
            self.s = socket.socket()
        except socket.error as msg:
            print("socket creation error " + str(msg))

    # binding the socket and listening for connections from client
    def bind_socket(self):
        try:
            print("Binding the port " + str(self.port))
            self.s.bind((self.host, self.port)) #tuple format
            self.s.listen(5)
        except socket.error as msg:
            print("socket binding error " + str(msg) + "\n" + "Retrying...")
            self.bind_socket()

    # handling connections from multiple clients and saving to a list
    # closing previous connections when server.py file is restarted
    def accepting_connections(self):
        for c in self.all_connections:
            c.close()
        del self.all_connections[:]
        del self.all_address[:]

        while True:
            try:
                self.conn, self.address = self.s.accept()
                self.all_connections.append(self.conn)
                self.all_address.append(self.address)
                print("Connection has been estabilished: " + self.address[0])
                self.conn_estabilished.emit(str(self.address[0]))
                break
            except:
                print("Error accepting connections")

    # Send commands to clients
    def send_commands(self, cmd):
        print("button was pressed")
        try:
            if cmd == "quit":
                self.conn.close()
                self.s.close()
                sys.exit()
            if len(str.encode(cmd))>0:
                self.conn.send(str.encode(cmd))
                self.client_response = str(self.conn.recv(20480), "utf-8")
                self.sentCommand.emit([cmd, self.address[0], self.client_response])
                print(self.client_response, end="")
        except:
            print("Error sending commands")

    def start_server(self):
        self.create_socket()
        self.bind_socket()
        self.accepting_connections()

    def stop_server(self):
        for c in self.all_connections:
            c.close()
        del self.all_connections[:]
        del self.all_address[:]

