import socket
import sys
import time
import random

# Global variables
y = 50  # packet size
n = 3  # window size
s = n * 2 + 1  # total number of sequence number

filename_get = False  # flag to check if filename has successfully receive

seq_base = 0
seq_end = seq_base + n
buffer = list(range(s))
buf_check = list(range(s))
for i in range(s):
    buf_check[i] = False

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

            ack = str(0).encode('utf-8')
            sock.sendto(ack, address)
            filename_get = True
            seq_base += 1
            seq_end += 1
    else:
        data, address = sock.recvfrom(y)
        # print(data)
        loss = random.randint(1, 10)
        if loss >= 5:
            seq = data[0:2].decode('utf-8')
            seq = int(seq)
            seq_str = str(seq)

            ack = seq_str.encode('utf-8')

            body = data[2:]
            if seq != seq_base:
                buffer[seq] = body
                buf_check[seq] = True

            else:

                buffer[seq] = body
                temp_end = seq_end
                buf_check[seq] = True
                while (seq_base != temp_end) and buf_check[seq_base]:
                    file.write(buffer[seq_base])
                    buf_check[seq_base] = False
                    if seq_base == s - 1:
                        seq_base = 0
                    else:
                        seq_base += 1
                    if seq_end == s - 1:
                        seq_end = 0
                    else:
                        seq_end += 1

            print(ack)
            sock.sendto(ack, address)

        # else:
        # print('packet lost!')

# TODO: after receiving all the packets, close the file, and set filename_get to false
