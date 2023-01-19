from konfig import *
import socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

user1, address1 = server.accept()
print(f'{address1[0]} has been connected as white')
user1.send(f'{address1[0]} has been connected as white'.encode('utf-8'))

user2, address2 = server.accept()
print(f'{address2[0]} has been connected as black')
user2.send(f'{address2[0]} has been connected as black'.encode('utf-8'))

user1.send('Both players connected')
user2.send('Both players connected')

while True:

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
