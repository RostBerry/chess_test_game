from konfig import *
import socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

while True:
    user, address = server.accept()
    print(f'{address[0]} has been connected')
    user.send('Connected successfully'.encode('utf-8'))
    while True:
        msg = user.recv(1024)
        if msg.decode('utf-8') != 'quit':
            print(f"{address[0]}: {msg.decode('utf-8')}")
            user.send(input('Message: ').encode('utf-8'))
        else:
            user.send('You have been disconnected'.encode('utf-8'))
            break
    print(f'{address[0]} has been disconnected')
