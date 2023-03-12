import socket
import sys

# Global variable
y = 50 # packet size
n = 3 # window size
s = n * 2 + 1 # total number of sequence number
current = 0 # trace the current sequence number
packet = list(range(s)) # initialize a list of size s for packet

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('142.1.46.51', 10000)
message = b'This is the message.  It will be repeated.'

try:

    file = open('client_data/test1.txt' , "rb")
    body = file.read()
    size = len(body)
    
    

    sent = sock.sendto(b'test1.txt', server_address)
    data,server = sock.recvfrom(y)
    print(data)






finally:
    print('closing socket')
    sock.close()