import socket
import sys
import time
import random

# Global variable
hostname = '142.1.46.51'
filename = 'test2.jpg'
y = 80  # packet size
n = 4  # window size
s = n * 2 + 1  # total number of sequence number
seq = 0  # trace the current sequence number
packet_list = [''] * s  # initialize an empty list of for packet
ack_list = list(range(s))  # list for tracking current ack
timeout = 1  # timeout value
data_list = []
create_list = list(range(s))
start_timer = 0
end_timer = 0
max_rtt = 0
min_rtt = 2 ** 31 - 1
rtt_count = 0
total_rtt = 0
lost_packets = 0
total_packets = 0
total_bytes = 0
effective_bytes = 0
timer_list = list(range(s))
last_seq = 100
packet_sent = list(range(s))
for i in range(s):
    ack_list[i] = False
    create_list[i] = False
    packet_sent[i] = False
    timer_list[i] = 0


# helper function to send filename to server
def send_filename():
    try:
        packet_list.append(filename)
        sock.sendto(filename.encode('utf-8'), server_address)
        log.write(b'Sender: sent file ' + filename.encode('utf-8') + b'\n')
        log.write(b'Sender: sent PKT0 \n')
        print("Filename successfully sent \n")

        data, server = sock.recvfrom(y)
        recieved = time.time()
        log.write(b'Sender: received ACK' + data + b'\n')

    except Exception as e:
        print(e)
        print("didn't receive")
        send_filename()


def send_packet(data_now, seq_base, seq_end, finish, last_seq):
    global total_packets, effective_bytes, total_bytes
    current = seq_base
    temp_end = seq_end
    if finish:
        temp_end = last_seq + 1
    while current != temp_end and data_now <= len(data_list) + 1:

        if not create_list[current] and data_now == len(data_list):
            break
        if not create_list[current] and data_now != len(data_list):
            if current < 10:
                seq_str = b'0' + str(current).encode('utf-8')
            else:
                seq_str = str(current).encode('utf-8')
            packet = seq_str + data_list[data_now]
            packet_list[current] = packet
            # print(packet_list[current])
            create_list[current] = True

            data_now += 1
            if data_now == len(data_list):
                print('here')
                last_seq = current

        if not ack_list[current] and not packet_sent[current]:
            sock.sendto(packet_list[current], server_address)
            packet_sent[current] = True
            log.write(b'Sender: sent PKT' + str(current).encode('utf-8') + b'\n')
            timer_list[current] = time.time()
            total_packets = total_packets + 1
            total_bytes = total_bytes + len(packet_list[current])
            effective_bytes = effective_bytes + len(packet_list[current])

        if current == s - 1:
            current = 0
        else:
            current += 1

    if data_now == len(data_list):
        return [True, last_seq, data_now]
    else:
        return [False, last_seq, data_now]


def receive_data(data_now, seq_base, seq_end, finish, last_seq):
    global max_rtt, min_rtt, total_rtt, rtt_count, lost_packets, effective_bytes
    complete = False
    try:
        data, server = sock.recvfrom(y)
        log.write(b'Sender: received ACK' + data + b'\n')
        data = data.decode('utf-8')
        ack = int(data)
        ack_list[ack] = True

        print("ACK" + str(ack) + " received")
        print("Start Time: " + str(timer_list[ack])[:13] + " sec")
        received = time.time()
        print("End Time: " + str(received)[:13] + " sec")
        rtt = received - timer_list[ack]
        print("RTT: " + str(rtt)[:6] + " sec\n")

        if max_rtt < rtt:
            max_rtt = rtt
        if min_rtt > rtt:
            min_rtt = rtt
        total_rtt = total_rtt + rtt
        rtt_count = rtt_count + 1

        if ack == seq_base and finish and seq_base == last_seq:

            # print(seq_end)
            pass
        else:
            if ack == seq_base:

                while ack_list[seq_base]:

                    if finish and seq_base == last_seq and ack_list[seq_base]:
                        complete = True
                        # print(seq_end)
                        break
                    ack_list[seq_base] = False
                    create_list[seq_base] = False
                    packet_sent[seq_base] = False

                    if seq_base == s - 1:
                        seq_base = 0
                    else:
                        seq_base += 1

                    if not finish:
                        if seq_end == s - 1:
                            seq_end = 0
                        else:
                            seq_end += 1
                if complete:
                    pass
                else:

                    finish = send_packet(data_now, seq_base, seq_end, False, last_seq)
                    receive_data(finish[2], seq_base, seq_end, finish[0], finish[1])
            else:
                receive_data(data_now, seq_base, seq_end, finish, last_seq)


    except Exception as e:
        print(e)
        # print("test" + str(packet_list))
        print("PKT" + str(seq_base) + " Request Time Out")
        lost_packets = lost_packets + 1
        effective_bytes = effective_bytes - len(packet_list[seq_base])
        if not ack_list[seq_base]:
            packet_sent[seq_base] = False
            finish = send_packet(data_now, seq_base, seq_end, finish, last_seq)
            receive_data(finish[2], seq_base, seq_end, finish[0], finish[1])
        else:
            receive_data(data_now, seq_base, seq_end, finish, last_seq)


log = open('client_data/client_log', "wb")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (hostname, 10000)
log.write(b'Sender: starting on host ' + hostname.encode('utf-8') + b'\n')

try:
    file = open('client_data/' + filename, "rb")
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
    send_filename()
    seq_base += 1
    seq_end += 1
    # print(len(data_list))
    finish = send_packet(data_now, seq_base, seq_end, False, last_seq)
    receive_data(finish[2], seq_base, seq_end, finish[0], finish[1])




finally:
    sock.sendto(b'Finished', server_address)
    sock.close()
    log.write(b'Sender: file transfer completed\n')
    print("Maximum RTT: " + str(max_rtt * 1000)[:4] + " msec")
    print("Minimum RTT: " + str(min_rtt * 1000)[:4] + " msec")
    print("Average RTT: " + str(total_rtt * 1000 / rtt_count)[:4] + " msec")
    # print(lost_packets, total_packets)
    print("Packet loss rate: " + str(lost_packets * 100 / total_packets)[:5] + "%")
    log.write(b'Sender: number of effective bytes sent: ' + str(effective_bytes).encode('utf-8') + b' bytes\n')
    log.write(b'Sender: number of packets sent: ' + str(total_packets).encode('utf-8') + b' packets\n')
    log.write(b'Sender: number of bytes sent: ' + str(total_bytes).encode('utf-8') + b' bytes\n')
    log.close()


