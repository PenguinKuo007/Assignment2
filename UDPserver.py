import socket
import sys
import time
import random


# Global variables
y = 50 # packet size
n = 3 # window size
s = n * 2 + 1 # total number of sequence number
current = 0 # trace the current sequence number


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('142.1.46.51', 10000)

sock.bind(server_address)

while True:

    data, address = sock.recvfrom(y)
    filename = data.decode('utf-8')
    print(filename)
    file = open("server_data/" + filename, "wb")
    file.close
    ack = str(current).encode('utf-8')
    sock.sendto(ack, address)
    