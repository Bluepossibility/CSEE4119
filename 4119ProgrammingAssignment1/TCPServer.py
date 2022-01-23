from socket import *

Qst1 = "Have you experienced any COVID-19 symptoms in the past 14 days?"
Qst2 = "Have you been in close contact to anyone who has tested positive for COVID-19 in the past 14 days?"
Qst3 = "Have you tested positive for COVID-19 in the past 14 days?"
RedPass = 0

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print("The server is ready to receive")
ConnSocket, addr = serverSocket.accept()


def Question1():
    while True:
        global RedPass
        ConnSocket.send(Qst1.encode())
        answer1 = ConnSocket.recv(1024)
        modifiedAnswer1 = answer1.decode()
        if modifiedAnswer1 in ["Yes", "yes"]:
            RedPass += 1
            break
        elif modifiedAnswer1 in ["No", "no"]:
            RedPass += 0
            break


def Question2():
    while True:
        global RedPass
        ConnSocket.send(Qst2.encode())
        answer2 = ConnSocket.recv(1024)
        modifiedAnswer2 = answer2.decode()
        if modifiedAnswer2 in ["Yes", "yes"]:
            RedPass += 1
            break
        elif modifiedAnswer2 in ["No", "no"]:
            RedPass += 0
            break


def Question3():
    while True:
        global RedPass
        ConnSocket.send(Qst1.encode())
        answer3 = ConnSocket.recv(1024)
        modifiedAnswer3 = answer3.decode()
        if modifiedAnswer3 in ["Yes", "yes"]:
            RedPass += 1
            break
        elif modifiedAnswer3 in ["No", "no"]:
            RedPass += 0
            break


while True:
    Question1()
    Question2()
    Question3()
    if RedPass == 0:
        ConnSocket.send("GreenPass!".encode())
        break
    else:
        ConnSocket.send("RedPass!".encode())
        break

ConnSocket.close()

