from socket import *

Qst1 = "Have you experienced any COVID-19 symptoms in the past 14 days?"
Qst2 = "Have you been in close contact to anyone who has tested positive for COVID-19 in the past 14 days?"
Qst3 = "Have you tested positive for COVID-19 in the past 14 days?"
RedPass = 0

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")

clientAddress = serverSocket.recvfrom(2048)[1]


def Question1():
    while True:
        global RedPass
        serverSocket.sendto(Qst1.encode(), clientAddress)
        answer1 = serverSocket.recvfrom(2048)[0]
        modifiedAnswer1 = answer1.decode()
        if modifiedAnswer1 in ["Yes", "yes"]:
            RedPass += 1
            break
        elif modifiedAnswer1 in ["No", "no"]:
            RedPass += 0
            break


def Question2():
    global RedPass
    while True:
        serverSocket.sendto(Qst2.encode(), clientAddress)
        answer2 = serverSocket.recvfrom(2048)[0]
        modifiedAnswer2 = answer2.decode()
        if modifiedAnswer2 in ["Yes", "yes"]:
            RedPass += 1
            break
        elif modifiedAnswer2 in ["No", "no"]:
            RedPass += 0
            break


def Question3():
    global RedPass
    while True:
        serverSocket.sendto(Qst3.encode(), clientAddress)
        answer3 = serverSocket.recvfrom(2048)[0]
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
        serverSocket.sendto("GreenPass!".encode(), clientAddress)
        break
    else:
        serverSocket.sendto("RedPass!".encode(), clientAddress)
        break

