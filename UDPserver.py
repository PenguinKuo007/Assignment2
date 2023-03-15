import socket
import sys
import time
import random

# Global variables
y = 50  # packet size
n = 3  # window size
s = n * 2 + 1  # total number of sequence number
current = 0  # trace the current sequence number
filename_get = False  # flag to check if filename has successfully receive

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('142.1.46.51', 10000)

sock.bind(server_address)

test = 0

while True:

    if not filename_get:

        data, address = sock.recvfrom(y)
        loss = random.randint(1, 10)
        if loss >= 5:
            filename = data.decode('utf-8')
            print(filename)
            file = open("server_data/" + filename, "wb")

            ack = str(current).encode('utf-8')
            sock.sendto(ack, address)
            current += 1
            filename_get = True
    else:
        data, address = sock.recvfrom(y)
        print(data)
        loss = random.randint(1, 10)
        if loss >= 1:
            seq = data[0:2].decode('utf-8')
            seq = int(seq)
            seq = str(seq)

            ack = seq.encode('utf-8')
            body = data[2:]
            file.write(body)
            sock.sendto(ack, address)
        else:
            print('packet lost!')
