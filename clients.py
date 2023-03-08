import socket
import threading
import codecs
import sys

HOST = '127.0.0.1'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nickname = input('Enter your nickname: ')

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            print('An error occurred!')
            client.close()
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(to_bytes(message))

def to_bytes(s):
     if type(s) is bytes:
         return s
     elif type(s) is str or (sys.version_info[0] < 3 and type(s) is unicode):
         return codecs.encode(s, 'utf-8')
     else:
         raise TypeError("Expected bytes or string, but got %s." % type(s))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

