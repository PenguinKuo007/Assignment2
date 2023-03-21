import socket
import time

# Global variable
hostname = '142.1.46.51'
filename = 'test1.txt'
y = 80  # packet size
n = 4  # window size
s = n * 2 + 1  # total number of sequence number
seq = 0  # trace the current sequence number
packet_list = [''] * s  # initialize an empty list of for packet
ack_list = list(range(s))  # list for tracking current ack
timeout = 1  # timeout value
data_list = []
create_list = list(range(s))
start_timer = 0  # Time at the point when packet is sent
end_timer = 0  # Time at the point when packet is sent
max_rtt = 0  # Keep updating with the largest RTT
min_rtt = 2**31 -1  # Keep updating with the smallest RTT
rtt_count = 0  # Keep count of every successful packet recieved 
total_rtt = 0  # Sum of all RTT
lost_packets = 0  # Keep count of all timed out packets 
total_packets = 0  # Keep count of all packets sent 
total_bytes = 0  # Keep count of all bytes sent 
effective_bytes = 0  # Keep count of all packets successfully sent
timer_list = list(range(s))  # Keep track of timers for all sent packets to determine RTT 
last_seq = 100
packet_sent = list(range(s))

# Intialize helper lists
for i in range(s):
    ack_list[i] = False
    create_list[i] = False
    packet_sent[i] = False
    timer_list[i] = 0


# helper function to send filename to server
def send_filename():
    try:
        # Send Filename to server & log accordingly 
        packet_list.append(filename)
        sock.sendto(filename.encode('utf-8'), server_address)
        log.write(b'Sender: sent file ' + filename.encode('utf-8') + b'\n')
        log.write(b'Sender: sent PKT0 \n')
        print("Filename successfully sent \n")

        # Receive ACK from server that the filename was sent successfully
        data, server = sock.recvfrom(y)
        log.write(b'Sender: received ACK' + data + b'\n')

    # In case the filename packet times out, we send it again. 
    except Exception as e:
        print("Filename Request Time Out")
        send_filename()

# Helper function to send the packet to server
def send_packet(data_now, seq_base, seq_end, finish, last_seq):
    # Global variables for keeping track of statistics 
    global total_packets, effective_bytes, total_bytes
    current = seq_base
    temp_end = seq_end
    if finish:
        temp_end = last_seq + 1
    while current != temp_end and data_now <= len(data_list) + 1:

        if not create_list[current] and data_now == len(data_list):
            break
        if not create_list[current] and data_now != len(data_list):

            # If the sequence number is one digit long, add a 0 digit to the front
            if current < 10:
                seq_str = b'0' + str(current).encode('utf-8')
            else:
                seq_str = str(current).encode('utf-8')
            # Construct the packet as: sequence number + string data
            packet = seq_str + data_list[data_now]
            packet_list[current] = packet
            create_list[current] = True
            data_now += 1
            if data_now == len(data_list):
                last_seq = current

        if not ack_list[current] and not packet_sent[current]:
            # Send the packet through the socket
            sock.sendto(packet_list[current], server_address)
            packet_sent[current] = True

            log.write(b'Sender: sent PKT' + str(current).encode('utf-8') + b'\n')
            # Keep track of time packet is first sent & other statistics
            timer_list[current] = time.time()
            total_packets = total_packets + 1
            total_bytes = total_bytes + len(packet_list[current])
            effective_bytes = effective_bytes + len(packet_list[current])

        # Wrap around sequence # if it reaches limit, otherwise increment 
        if current == s - 1:
            current = 0
        else:
            current += 1

    if data_now == len(data_list):
        return [True, last_seq, data_now]
    else:
        return [False, last_seq, data_now]


def receive_data(data_now, seq_base, seq_end, finish, last_seq):
    # Global variables for keeping track of statistics 
    global max_rtt, min_rtt, total_rtt, rtt_count, lost_packets, effective_bytes
    complete = False
    try:
        # Receive ack from server
        data, server = sock.recvfrom(y)
        log.write(b'Sender: received ACK' + data + b'\n')
        data = data.decode('utf-8')
        ack = int(data)
        ack_list[ack] = True
        
        
        # Log and print according to handout
        print("ACK" + str(ack) + " received")
        print("Start Time: " + str(timer_list[ack])[:13] + " sec")
        # Get time of received packet and calculate the RTT
        received = time.time()
        print("End Time: " + str(received)[:13] + " sec")
        rtt = received - timer_list[ack]
        print("RTT: " + str(rtt)[:6] + " sec\n")

        # Configure rtt statistics as needed
        if max_rtt < rtt:
            max_rtt = rtt
        if min_rtt > rtt:
            min_rtt = rtt
        total_rtt = total_rtt + rtt
        rtt_count = rtt_count + 1

        # If last packet is acknowledged then no need to receive data
        if ack == seq_base and finish and seq_base == last_seq:
            pass
        # If there are still packet not acknowledged yet, then keep receiving data
        else:
            # If the ack number is the same as base sequence, then move base sequence and end sequence
            # until the unack sequence
            if ack == seq_base:
                while ack_list[seq_base]:

                    if finish and seq_base == last_seq and ack_list[seq_base]:
                        complete = True
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

    # If a packet times out, we will send it again. 
    except Exception as e:
        print("PKT" + str(seq_base) + " Request Time Out")
        lost_packets = lost_packets + 1
        effective_bytes = effective_bytes - len(packet_list[seq_base])

        # check if the current base sequence if ack or not, if not then resend the packet
        if not ack_list[seq_base]:
            packet_sent[seq_base] = False
            finish = send_packet(data_now, seq_base, seq_end, finish, last_seq)
            receive_data(finish[2], seq_base, seq_end, finish[0], finish[1])
        # If ack, then keep receiving ack from server
        else:
            receive_data(data_now, seq_base, seq_end, finish, last_seq)


# Open the log file to be written to
log = open('client_data/client_log', "wb")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (hostname, 10000)
# Set timeout for the socket
sock.settimeout(timeout)
log.write(b'Sender: starting on host ' + hostname.encode('utf-8') + b'\n')

try:
    # Open and read file to send through socket
    file = open('client_data/' + filename, "rb")
    body = file.read()

    #Initialize variables to keep track of seq # and the window 
    size = len(body)
    data_start = 0
    data_end = y - 2
    data_now = 0
    seq_base = 0
    seq_end = seq_base + n
    packet_amount = 0

    # Assemble file data into a list of each packet to be sent
    while data_end < size + y - 2:
        data_list.append(body[data_start:data_end])
        data_start = data_end
        data_end = data_end + y - 2
        packet_amount += 1
    
    # Sends the file name before the rest of the data packets
    send_filename()
    # Window moves up 1
    seq_base += 1
    seq_end += 1

    finish = send_packet(data_now, seq_base, seq_end, False, last_seq)
    receive_data(finish[2], seq_base, seq_end, finish[0], finish[1])

# There are no more data packets to send, so send the finished packet
finally:
    # Indicates to the server that this is the last packet and close the socket
    sock.sendto(b'Finished', server_address)
    sock.close()

    # Log and output final statistics
    log.write(b'Sender: file transfer completed\n')
    print("Maximum RTT: " + str(max_rtt * 1000)[:4] + " msec")
    print("Minimum RTT: " + str(min_rtt * 1000)[:4] + " msec")
    print("Average RTT: " + str(total_rtt * 1000 / rtt_count)[:4] + " msec")
    print("Packet loss rate: " + str(lost_packets * 100 / total_packets)[:5] + "%")
    log.write(b'Sender: number of effective bytes sent: ' + str(effective_bytes).encode('utf-8') + b' bytes\n')
    log.write(b'Sender: number of packets sent: ' + str(total_packets).encode('utf-8') + b' packets\n')
    log.write(b'Sender: number of bytes sent: ' + str(total_bytes).encode('utf-8') + b' bytes\n')
    log.close()


