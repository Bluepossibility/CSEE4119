from socket import *

serverName = 'localhost'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

conn_message = "Client is connected"
clientSocket.sendto(conn_message.encode(), (serverName, serverPort))

while True:
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    print(modifiedMessage.decode())
    if modifiedMessage.decode() in ["RedPass!", "GreenPass!"]:
        break
    message = input('Response:')  # raw_input no longer exists in Python!
    clientSocket.sendto(message.encode(), (serverName, serverPort))

clientSocket.close()


