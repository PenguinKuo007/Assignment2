import socket
import sys
import time
import random

# Global variable
y = 50  # packet size
n = 3  # window size
s = n * 2 + 1  # total number of sequence number
seq = 0  # trace the current sequence number
packet_list = list(range(s))  # initialize an empty list of for packet
ack_list = list(range(s))  # list for tracking current ack
timeout = 3  # timeout value
test = 0
data_list = []
create_list = list(range(s))
start_timer = 0
end_timer = 0

for i in range(s):
    create_list[i] = False
for i in range(s):
    ack_list[i] = False


# helper function to send filename to server
def send_filename(test):
    try:
        packet_list.append('test1.txt')
        sock.sendto(b'test1.txt', server_address)
        data, server = sock.recvfrom(y)

        print(data)

    except:
        test += 1
        print("didn't receive")
        send_filename(test)


def send_packet(data_now, seq_base, seq_end):
    current = seq_base

    while current != seq_end:

        if not create_list[current] and data_now != len(data_list):
            if current < 10:
                seq_str = b'0' + str(current).encode('utf-8')
            else:
                seq_str = str(current).encode('utf-8')
            packet = seq_str + data_list[data_now]
            packet_list[current] = packet
            print(packet_list[current])
            create_list[current] = True

            data_now += 1
        if not ack_list[current]:
            sock.sendto(packet_list[current], server_address)

        if current == s - 1:
            current = 0
        else:
            current += 1

    if data_now == len(data_list):
        receive_data(data_now, seq_base, seq_end, True, current - 1)
    else:
        receive_data(data_now, seq_base, seq_end, False, 0)


def receive_data(data_now, seq_base, seq_end, finish, last_seq):
    try:

        data, server = sock.recvfrom(y)

        data = data.decode('utf-8')
        ack = int(data)
        ack_list[ack] = True

        if ack == seq_base:

            while ack_list[seq_base]:

                ack_list[seq_base] = False
                create_list[seq_base] = False

                if seq_base == s - 1:
                    seq_base = 0
                else:
                    seq_base += 1

                if data_now != len(data_list):
                    if seq_end == s - 1:
                        seq_end = 0
                    else:
                        seq_end += 1
        receive_data(data_now, seq_base, seq_end, finish, last_seq)


    except:

        print(finish)
        print(last_seq)
        print(seq_base)
        if seq_base == last_seq and finish:
            print('closing socket')
            sock.close()

        # here is the problem
        if not ack_list[seq_base]:
            send_packet(data_now, seq_base, seq_end)


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('142.1.46.51', 10000)

try:

    file = open('client_data/test1.txt', "rb")
    body = file.read()
    size = len(body)
    data_start = 0
    data_end = y - 2
    data_now = 0

    seq_base = 0
    seq_end = seq_base + n
    packet_amount = 0
    while data_end < size + y - 2:
        data_list.append(body[data_start:data_end])
        data_start = data_end
        data_end = data_end + y - 2
        packet_amount += 1
    sock.settimeout(timeout)
    send_filename(test)
    seq_base += 1
    seq_end += 1
    print(len(data_list))
    data_now = send_packet(data_now, seq_base, seq_end)

    # maybe send_packet call receive_data at the end and receive_data all send_packet for the next packet?

    for i in range(1, n + 1):
        print(ack_list[i])





finally:
    print('closing socket')
    sock.close()
