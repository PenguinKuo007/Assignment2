import socket
import random

# Global variables
y = 80  # packet size
n = 4  # window size
s = n * 2 + 1  # total number of sequence number
loss_rate = 4  # Determines the loss rate (3 = 30% packets will be lost)
total_bytes = 0  # To keep track of total bytes received from Client
filename_get = False  # flag to check if filename has successfully receive

seq_base = 0
seq_end = seq_base + n
buffer = list(range(s)) # List to store out of order packets until needed
buf_check = list(range(s))

for i in range(s):
    buf_check[i] = False

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('142.1.46.51', 10000)
sock.bind(server_address)

# Open the log file to be written to
log = open('server_data/server_log', "wb")

# Server will run until the finished packet is received
while True:
    # Receive data packet from client
    data, address = sock.recvfrom(y)
    # Increase total amount of bytes received 
    total_bytes = total_bytes + len(data)

    # This if clause if for getting the filename packet 
    if not filename_get:
        log.write(b'Receiver: received PKT0' b'\n')
        # Randomize the loss integer between 1 and 10 inclusive
        loss = random.randint(1, 10)

        # If the random integer is greater than the loss_rate chosen, then the packet is not lost
        # otherwise the packet is lost and the client will not get an ACK.
        if loss > loss_rate:
            filename = data.decode('utf-8')
            print("Filename successfully received")
            # Open file to be recreated by end of process 
            file = open("server_data/" + filename, "wb")

            ack = str(0).encode('utf-8')

            # Send ack of successfuly filename transfer to client
            sock.sendto(ack, address)
            log.write(b'Receiver: send an ACK0' b'\n')
            print("Receieved: ACK0, Expected: ACK0")
            # The filename is now received, now the server will receive data packets
            filename_get = True
            # Move window
            seq_base += 1
            seq_end += 1
    else:
        try:
            # if the client is done sending packets, then the server will close the socket and the files 
            if data.decode('utf-8') == 'Finished':
                filename_get = False
                file.close()
                log.write(b'Receiver: file transfer completed\n')
                log.write(b'Receiver: number of bytes received: ' + str(total_bytes).encode('utf-8') + b' bytes\n')
                log.close()
                break

            # Receiving Data Packets
            else:
                log.write(b'Receiver: received PKT' + str(int(data[0:2])).encode('utf-8') + b'\n')
                # Randomize the loss integer between 1 and 10 inclusive
                loss = random.randint(1, 10)

                # If the random integer is greater than the loss_rate chosen, then the packet is not lost
                # otherwise the packet is lost and the client will not get an ACK.
                if loss > loss_rate:
                    seq = data[0:2].decode('utf-8')
                    seq = int(seq)
                    seq_str = str(seq)

                    print("Receieved: ACK" + str(seq) + ", Expected: ACK" + str(seq_base))
                    ack = seq_str.encode('utf-8')
                    body = data[2:]

                    # The sequence # is out of order, store in buffer
                    if seq != seq_base:
                        buffer[seq] = body
                        buf_check[seq] = True

                    # The seq # is not out of order:
                    # write to file with new packet and buffered packets
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
                    # Send ACK to client
                    sock.sendto(ack, address)
                    log.write(b'Receiver: sent an ACK' + ack + b'\n')
        except:
            log.write(b'Receiver: received PKT' + str(int(data[0:2])).encode('utf-8') + b'\n')
            # Randomize the loss integer between 1 and 10 inclusive
            loss = random.randint(1, 10)

            # If the random integer is greater than the loss_rate chosen, then the packet is not lost
            # otherwise the packet is lost and the client will not get an ACK.
            if loss > loss_rate:
                seq = data[0:2].decode('utf-8')
                seq = int(seq)
                seq_str = str(seq)

                print("Receieved: ACK" + str(seq) + ", Expected: ACK" + str(seq_base))
                ack = seq_str.encode('utf-8')
                body = data[2:]

                # The sequence # is out of order, store in buffer
                if seq != seq_base:
                    buffer[seq] = body
                    buf_check[seq] = True

                # The seq # is not out of order:
                # write to file with new packet and buffered packets
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
                            
                # Send ACK to client
                sock.sendto(ack, address)
                log.write(b'Receiver: sent an ACK' + ack + b'\n')




