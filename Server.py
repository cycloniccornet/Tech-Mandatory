import socket
import time
import logging

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 13000)
print('Server: starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

count = 1
connection = False
timeout = False
timeoutStop = False
countdown = 0
logging.basicConfig(level=logging.INFO, filename="ServerLog.log")

# Create IP Addresse
hostname = socket.gethostname()

serverIPAddresse = socket.gethostbyname(hostname)


while True:

    if not connection:
        try:

            # Wating to recive syn request
            sock.setblocking(True)
            print("Server TWH: Waiting to recive Syn")
            synData, address = sock.recvfrom(4096)
            clientIp = address[0]
            logging.info(time.asctime() + " | Client with Ip: " + str(address[0]) + " | Port: " + str(address[1]) + " is trying to connect to server")
            print('Server TWH: Recevied {!r}'.format(synData))

            ip = synData[9:21]

            if synData[0:8] == b"C: com-0" and synData[9:21] == ip:
                logging.info(
                    time.asctime() + " | recived Syn from" + "| Client : " + str(address[0]) + " | Port: " + str(
                        address[1]))
                print('Server TWH: Sending Syn-Ack to client')
                logging.info(time.asctime() + " | Server Sending Syn-Ack to " + str(address[0]))
                sent = sock.sendto(b"S: com-0 accept " + serverIPAddresse.encode('ASCII'), address)

                # Waiting for client accept
                ackData, address = sock.recvfrom(4096)
                print('Server TWH: Recevied {!r}'.format(ackData))

                #til hacking
                print("Ip der connectede 1 gang: "+ str(ip) + "\nIp Nr2: " + str(ackData[16:28]))


                if ackData[0:15] == b"C: com-0 accept" and ip == ackData[16:28]:
                    logging.info(
                        time.asctime() + " | recived Ack from " + "| Client : " + str(address[0]) + " | Port: " + str(
                            address[1]))
                    print("Server TWH: TCP socket connection is ESTABLISHED.")
                    connection = True
                    count = 1
                    print("--------------------------------------")
                    logging.info(time.asctime() + " | Server and client Connected")
                else:
                    print("Dont just change your ip....")
                    logging.critical(time.asctime() + " | A Client with diffrent ip tried to loggin bypass three way handshake. " + "Hacker ip: " + str(ackData[16:28]))

            else:
                print("TWH fejlede. Forbindelsen lukkes")
                connection = False
        except BlockingIOError:
            print("BlockingIOError in TWH")

    if connection:

        if countdown < 10:
            # print(countdown)
            time.sleep(0.1)
            countdown += 0.1

        if countdown > 9 and not timeoutStop:
            print("Timeout = True")
            timeout = True
            timeoutStop = True

        try:
            # Sørger for at data server ikke stopper når den skal modtage data

            # Timeout
            if timeout:
                try:
                    print("\nServer: Timeout started, sending timeout to client")
                    timeoutStop = False
                    sent = sock.sendto(b'con-res 0xFE', address)
                    sock.setblocking(True)
                    print("Server: Wating to recive timeout acknowledge form client")
                    data, address = sock.recvfrom(4096)
                    logging.info(
                        time.asctime() + " | Disconnected from  " + "| Client : " + str(address[0]) + " | Port: " + str(
                            address[1]))
                    if data.decode('ASCII') == 'con-res 0xFF':
                        print("Server: Resetting timeoutstopper.")
                        timeoutStop = False
                        print("Server: Client acknowledge Recived. \nServer: Connection set to False")
                        connection = False
                        timeout = False
                        countdown = 0
                        print("\n--------------------------------------")
                except BlockingIOError:
                    print("fejl kom")

            sock.setblocking(False)

            data, address = sock.recvfrom(4096)

            countdown = 0

            print('Server: received {} bytes from {}'.format(len(data.decode()), address))
            print('Server: Message From Client = ' + data.decode())

            dataanalyse = data.decode("ASCII")
            substring = dataanalyse[dataanalyse.find("-") + len('-'):dataanalyse.find("=")]
            number = substring

            if dataanalyse == 'con-h 0x00':
                print('Server: Heartbeat recived from client')
                print('Server: resetting countdown')
                print("\n--------------------------------------")
                countdown = 0

            # Internet Protekoller
            dataBreakdown = dataanalyse.split("=")

            if data.decode('ASCII').startswith('C: msg-'):
                print("\nServer: Preparing response")
                if int(number) + 1 == count:

                    if dataBreakdown[1] == "hej":
                        message = b"Hej tilbage"

                        msg = (b"S: res-" + str(count).encode("ASCII") + b"=" + message)
                        print('Server: Sending {!r}'.format(msg))

                        sent = sock.sendto(msg, address)

                    elif dataBreakdown[1] == "test":
                        message = b"TESTER"

                        msg = (b"S: res-" + str(count).encode("ASCII") + b"=" + message)
                        print('Server: Sending {!r}'.format(msg))

                        sent = sock.sendto(msg, address)
                        print("Test loop færdigt.")
                    else:
                        message = dataBreakdown[1].encode("ASCII")
                        msg = (b"S: res-" + str(count).encode("ASCII") + b"=" + message)

                        print('Server: Sending {!r}'.format(msg))
                        sent = sock.sendto(msg, address)

                    count += 2
                    print("Server: Count updated to: " + str(count))
                    print("\n--------------------------------------")
                    # print('ClientCount : ' + str(number) + ' ' + 'ServerCount ' + str(count))
                else:
                    print("Server: Number didnt match")
                    print('ClientCount : ' + str(number) + ' ' + 'ServerCount ' + str(count))
        except:
            continue
