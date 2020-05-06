import socket
import threading
import time
import os
import msvcrt

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 13000)

# Createing Client IP Addresse
hostname = socket.gethostname()
IPaddresse = socket.gethostbyname(hostname)

connection = False
Heartbeat = False
maxpackage = 0
count = 0


def heartBeat(self):
    timer = 0

    while True:
        time.sleep(0.1)
        timer += 0.1
        if timer > 3:
            print("\nSending con-h 0x00 to server")
            sock.sendto(b'con-h 0x00', server_address)
            timer = 0


def sendMsg():
    # Send data
    global count
    time.sleep(1 / int(maxpackage))

    print("Client: Preparing to send data")
    message = input("Client: Write your message here -> ")

    msg = ("C: msg-" + str(count) + "=" + message)
    sock.sendto(msg.encode(), server_address)
    print('Client: Sending {!r}'.format(msg))


def reciveMsg(self):
    # Receive Response

            global count
            print('\nClient: Wating for response')
            sock.setblocking(True)
            data, server = sock.recvfrom(4096)

            if data.decode('ASCII') == 'con-res 0xFE':
                print("\nClient: Recived con-res 0xFE")
                print("Client: Sending con-res 0xFF")
                sent = sock.sendto(b'con-res 0xFF', server_address)
                print("Client: Server closed connection")

                os._exit(0)

            dataanalyse = data.decode('ASCII')

            substring = dataanalyse[dataanalyse.find("-") + len('-'):dataanalyse.find("=")]
            number = substring

            print('\nClient: Recevied {!r}'.format(data.decode()))

            if int(number) - count == 1:
                count += 2
                print("Client: Count updated to: " + str(count))
                print("\n--------------------------------------")
            else:
                print("Count didnt match .. closing con")
                os._exit(0)


f = open("opt.conf", "r")

if f.mode == 'r':
    contents = f.readlines()

    for x in contents:
        resultsFile = contents[0]
        resultsFile2 = contents[1]

        if resultsFile.startswith("KeepALive"):

            if resultsFile.split(":")[1].rstrip("\n") == " True":
                # print("Heartbeat set to True")
                Heartbeat = True

            if resultsFile.split(":")[1].rstrip("\n") == " False":
                # print("Heartbeat set to False")
                Heartbeat = False

            if resultsFile2.startswith("MaxPackage"):
                maxpackage = resultsFile2.split(":")[1]

print("Hearbeat is set to: " + str(Heartbeat))
print("MaxPackage is set to: " + str(maxpackage))

try:

    while not connection:

        print('Client TWH: ByPass connection')

        # Sending SYN
        sock.sendto(b"C: com-0 " + IPaddresse.encode('ASCII'), server_address)

        synData, server = sock.recvfrom(4096)
        print('Client TWH: Recevied {!r}'.format(synData))

        if synData == b"S: com-0 accept 192.168.1.10":
            print("Client TWH: Sending Ack")
            sock.sendto(b"C: com-0 accept 192.168.1.99", server_address)
            break
        else:
            connection = False
        print("Client TWH: Recived data didnt match.. closing connection")
        break

    print("--------------------------------------")


    while connection:

        reciveMsgThread = threading.Thread(target=reciveMsg, args=(1,))
        reciveMsgThread.start()

        sendMsgThread = threading.Thread(target=sendMsg(), args=(2,))
        sendMsgThread.start()










finally:
    print('Client: closing socket')
    sock.close()
