from konfig import *
import socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

while True:
    user1, address1 = server.accept()
    print(f'{address1[0]} has been connected')
    user1.send('Waiting for opponent'.encode('utf-8'))
    user2, address2 = server.accept()
    print(f'{address2[0]} has been connected')
    user2.send('Waiting for opponent'.encode('utf-8'))
    user1.send('Connected successfully'.encode('utf-8'))
    user2.send('Connected successfully'.encode('utf-8'))
    while True:
        msg = user1.recv(1024)
        if msg.decode('utf-8') != 'quit':
            print(f"{address1[0]}: {msg.decode('utf-8')}")
            user1.send(input('Message: ').encode('utf-8'))
        else:
            user1.send('You have been disconnected'.encode('utf-8'))
            break
    print(f'{address1[0]} has been disconnected')
