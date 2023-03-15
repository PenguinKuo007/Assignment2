import socket
import sys
import time
import random

# Global variable
y = 50  # packet size
n = 3  # window size
s = n * 2 + 1  # total number of sequence number
seq = 0  # trace the current sequence number
packet_list = []  # initialize an empty list of for packet
ack_list = list(range(s))  # list for tracking current ack
timeout = 3  # timeout value
test = 0
packet_list = []
start_timer = 0
end_timer = 0

for i in range(s):
    ack_list[i] = False


# helper function to send filename to server
def send_filename(test):
    sock.settimeout(timeout)
    try:

        sock.sendto(b'test1.txt', server_address)
        data, server = sock.recvfrom(y)

        print(data)
        print(test)
    except:
        test += 1
        print("didn't receive")
        send_filename(test)


def send_packet(packet):
    sock.settimeout(timeout)
    try:
        sock.sendto(packet, server_address)
        data, server = sock.recvfrom(y)
        return data
    except:
        print("packet didn't receive")
        send_packet(packet)


def send_packet_test(packet):
    sock.sendto(packet, server_address)


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('142.1.46.51', 10000)

try:

    file = open('client_data/test1.txt', "rb")
    body = file.read()
    size = len(body)

    send_filename(test)

    data_start = 0
    data_end = y - 2

    seq += 1

    # testing the timeout
    for i in range(n):
        if seq < 10:
            seq_str = b'0' + str(seq).encode('utf-8')
        else:
            seq_str = str(seq).encode('utf-8')
        packet = seq_str + body[data_start:data_end]
        packet_list.append(packet)
        print(packet_list[i])
        data_start = data_end
        data_end = data_end + y - 2
        if seq == s:
            seq = 0
        else:
            seq += 1
        size += 2
        if (ack_list[i] == False):
            send_packet_test(packet)
            if i == 0:
                end_timer = time.time()
            else:

                for x in range(i):
                    timer = time.time()
                    timer_list[i - 1] = timer_list[i - 1] + end_timer - start_timer
                start_timer = time.time()

    sock.settimeout(timeout)
    while True:
        try:
            data, server = sock.recvfrom(y)
            end_timer = time.time()
            for i in range(n + 1):
                timer_list[i] = timer_list + end_timer - start_timer
            data = data.decode('utf-8')
            ack = int(data)
            ack_list[ack] = True
        except:
            print('bruh')
            break

    for i in range(n + 1):
        print(ack_list[i])

    for i in range(n + 1):
        print(timer_list[i])

    while data_end <= size:
        if seq < 10:
            seq_str = b'0' + str(seq).encode('utf-8')
        else:
            seq_str = str(seq).encode('utf-8')
        packet = seq_str + body[data_start:data_end]
        data_start = data_end
        data_end = data_end + y - 2
        if seq == s:
            seq = 0
        else:
            seq += 1
        size += 2
        ack = send_packet(packet)

        print(ack)

















finally:
    print('closing socket')
    sock.close()
