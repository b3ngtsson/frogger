import socket
import threading
import random
import time
import codecs
import sys 
import pandas as pd 

HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

timer: int = 0
question_answered : bool = False
clients = []
nicknames = []
count_thread : threading
canceled = threading.Event()


def broadcastWithoutSender(message, sender):
    for client in clients:
        if(client != sender):
            client.send(to_bytes(message))

def broadcast(message):
    for client in clients:
        client.send(to_bytes(message))
def to_bytes(s):
    if type(s) is bytes:
       return s
    elif type(s) is str or (sys.version_info[0] < 3 and type(s) is unicode):
        return codecs.encode(s, 'utf-8')
    else:
        raise TypeError("Expected bytes or string, but got %s." % type(s))

def handle(client):
    global timer
    global question_answered

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('NICK'):
                nickname = message.split(' ')[1]
                nicknames.append(nickname)
                clients.append(client)
                broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
            # here we can filter the message to not be racist
            broadcastWithoutSender(message, client)
            print(message)
            command =  message.split(':')[1].lstrip()
            if command.lower() == 'start':
                print('question time')
                ask_chatbot_question()

            if(command.lower() == chatbot_answer.lower()):
                question_answered = True
                index = clients.index(client)
                nickname = nicknames[index]
                broadcast(f'Thats correct, good job {nickname}, you got it after {timer} seconds!')
        except:
            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8', errors='ignore')
        nicknames.append(nickname)
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        client.send('Connected to the server!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def count_to_15():
    global canceled
    global question_answered
    global timer
    global chatbot_answer

    end = 16
    while not canceled.is_set():
        timer = 0
        for i in range(1, end):
                if question_answered:
                    broadcast('you are correct!')
                    canceled.set()
                    return
                if(timer == end-2):
                    broadcast(f'Out of time, the correct answer was: {chatbot_answer}')
                time.sleep(1)
                timer += 1
        ask_chatbot_question()
        return
    return

def thread_stop():
    global count_thread
    global canceled

    canceled.set()
    start_chatbot()

def ask_chatbot_question():
    global chatbot_busy
    global chatbot_answer
    global count_thread
    global question_answered
    global timer

    timer = 0
        
    questions = [
        {'question': 'What is the capital city of Norway?', 'answer': 'Oslo'},
        {'question': 'What is the tallest mountain in the world?', 'answer': 'Everest'},
        {'question': 'What is the smallest country in the world?', 'answer': 'Vatican'},
        {'question': 'What is the largest ocean in the world?', 'answer': 'Pacific'},
        {'question': 'What is the largest country in the world?', 'answer': 'Russia'}
    ]


    # ask a question
    question = random.choice(questions)
    chatbot_answer = question['answer']
    chatbot_busy = True
    broadcast(f'Chatbot: {question["question"]}. You have 15 seconds to answer.'.encode('utf-8'))


    
    question_answered = False
    
    thread_stop()
    canceled.clear()
    count_thread.start()


def chatbot_handler():
    global chatbot_busy
    global chatbot_answer
    global chatbot_time_left

    while True:
        if not chatbot_busy:
            time.sleep(5) # Wait for 5 seconds before asking another question
            broadcast('CHATBOT_QUESTION'.encode('utf-8'))
        else:
            if chatbot_time_left == 0:
                chatbot_busy = False
                broadcast(f'Chatbot: The correct answer was {chatbot_answer}.'.encode('utf-8'))

def start_chatbot():
    global chatbot_busy
    global count_thread
    
    count_thread = threading.Thread(target=count_to_15)

chatbot_answer = "-^/&1235"
chatbot_busy = False
timer = 0
question_answered = False
print("server is listening...")
start_chatbot()
receive()
