from konfig import *
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

data = client.recv(1024)
print(data.decode('utf-8'))

while True:
    data = client.recv(1024)
    print(data.decode('utf-8'))
    if data.decode('utf-8') != 'You have been disconnected':
        client.send(input('Message: ').encode('utf-8'))
    else:
        break
