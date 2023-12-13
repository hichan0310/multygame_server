import pygame
from pygame.math import Vector2
import socket
import threading

clock = pygame.time.Clock()
MPS = 45
bufferSize = 1024


class client_manager:
    def __init__(self):
        self.clients = [
            client('p1', Vector2(200, 0), self, ('127.0.0.1', 10001)),
            client('p2', Vector2(-200, 0), self, ('127.0.0.1', 10002))
        ]

    def send_all(self, message: str):
        message = message.encode()
        for c in self.clients:
            c.sock.sendto(message, c.send)

    def status_send(self):
        for i in range(len(self.clients)):
            for j in range(len(self.clients)):
                if i != j:
                    c = self.clients[j]
                    s = self.clients[i]
                    s.sock.sendto(f'status {c.name} {c.position.x} {c.position.y} {c.hp}'.encode(), s.send)


class client:
    def __init__(self, name, location: Vector2, manager: client_manager, send: tuple[str, int]):
        self.send = send
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.name = name
        self.hp = 100
        self.position = location
        self.manager = manager

    def sushin(self, message: str):
        message = message.split()
        if message[0] == 'shot':
            x, y = message[1], message[2]
            self.manager.send_all(f'shot {self.name} {x} {y}')
        elif message[0] == 'status':
            x, y = message[1], message[2]
            self.position = Vector2(float(x), float(y))
            self.hp = int(message[3])
        elif message[0] == 'gun':
            self.manager.send_all(f'gun {self.name} {message[1]} {message[2]}')


def udp_listen(manager: client_manager):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 10000))
    print("UDP server up and listening")
    while (True):
        bytesAddressPair = sock.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        message = message.decode()
        manager.clients[int(message[0]) - 1].sushin(message[1:])


c_manager = client_manager()

def status_send():
    while True:
        c_manager.status_send()
        clock.tick(MPS)



threading.Thread(target=udp_listen, args=(c_manager,)).start()
threading.Thread(target=status_send).start()

while True:
    command=input().split()

