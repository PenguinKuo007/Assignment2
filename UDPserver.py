import socket
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
total_bytes = 0
for i in range(s):
    buf_check[i] = False

test = 0
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('142.1.46.51', 10000)

sock.bind(server_address)

log = open('server_data/server_log', "wb")

test = 0

while True:

    data, address = sock.recvfrom(y)
    total_bytes = total_bytes + len(data)

    if not filename_get:

        log.write(b'Receiver: received PKT0' b'\n')
        loss = random.randint(1, 10)

        # if loss >= 3:
        if loss >= 5:
            filename = data.decode('utf-8')
            print("Filename successfully received")
            file = open("server_data/" + filename, "wb")

            ack = str(0).encode('utf-8')
            sock.sendto(ack, address)
            log.write(b'Receiver: send an ACK0' b'\n')
            print("Receieved: ACK0, Expected: ACK0")
            filename_get = True
            seq_base += 1
            seq_end += 1
    else:

        if data.decode('utf-8') == 'Finished':
            filename_get = False
            file.close()
            log.write(b'Receiver: file transfer completed\n')
            log.write(b'Receiver: number of bytes received: ' + str(total_bytes).encode('utf-8') + b' bytes\n')
            log.close()
            break
        else:

            log.write(b'Receiver: received PKT' + str(int(data[0:2])).encode('utf-8') + b'\n')
            loss = random.randint(1, 10)

            if loss >= 5:
                if True:
                    test += 1
                    seq = data[0:2].decode('utf-8')
                    seq = int(seq)
                    seq_str = str(seq)

                    print("Receieved: ACK" + str(seq) + ", Expected: ACK" + str(seq_base))
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

                    sock.sendto(ack, address)
                    log.write(b'Receiver: sent an ACK' + ack + b'\n')




