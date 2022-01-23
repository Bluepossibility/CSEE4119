from _ast import While
from socket import *

serverName = 'localhost'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

while True:

    modifiedMessage = clientSocket.recv(1024)
    print(modifiedMessage.decode())
    if modifiedMessage.decode() in ["RedPass!", "GreenPass!"]:
        break
    message = input('Response:')  # raw_input no longer exists in Python!
    clientSocket.send(message.encode())

clientSocket.close()




