'''Jonte Auden
Student ID: 76942953

Server code.
NOTE: The server will restart when the client aborts / disconnects the socket.

Keep socket open unless calling a read request or an error occurs. IF an error message is printed then
the server must be re-run as well as the client as the server will notice the socket has disconnected and will
abort / disconnect from the connected port
'''

from sys import exit, argv
from socket import *


#  Creates a header and sends back  up to 255 messages for the sender before deleting the sent messages
def MessageResponse(sock, conn, vault, name_to_retrive):
    response = bytearray(5)  # default 5 bytes for header
    response[0] = (0xAE & 0xFF)  # magic number
    response[1] = (0x73 & 0xFF)  # magic number
    response[2] = 0x03  # ID 3
    # number of messages is equal to the length of the list of the vault at the key (sender)
    response[3] = (len(vault.get(name_to_retrive, [])) & 0xFF)

    if len(vault.get(name_to_retrive, [])) > 255:  # if len > 255 then there are over 255 messages thus put 0x01
        response[4] = 0x01  # more messages in the vault
    else:
        response[4] = 0x00  # no more messages in the vault after extracting up to 255

    res = vault.get(name_to_retrive, [])  # get the list using sender as the key

    # iterate over results for name we are getting the messages for
    if len(res) > 0:
        j = min(len(res), 255)  # take the minimum to avoid index error or sending too many messages

        for i in range(j):  # loop up to index j of the list
            sender = res[i][0]  # i index's into the list then [0] corresponds to the tuple position 0 which is sender
            message = res[i][1]  # [1] corresponds to the message stored as a string
            response.append(len(sender) & 0xFF)  # append the length of sender
            response.append((len(message) >> 8) & 0xFF)  # append the length of the message
            response.append(len(message) & 0xFF)  # append the length of the message
            response.extend(sender.encode('utf-8'))  # encode and extend the sender name to response
            response.extend(message.encode('utf-8'))  # encode and extend message to response
        res = vault.get(name_to_retrive, [])
        res = res[j:]  # remove the messages about to be sent
        vault[name_to_retrive] = res

    conn.send(response)  # send the response to the client


''' store the message in a python object when message request of create is used 
the key to the vault will be the receiver name, when read request is called send back all the messages sent to this 
receiver the sender will be stored along with the message 
'''


def storing_message(message, vault):
    name_start = 7  # byte position 7 of the message is the start index of the sender name
    name_end = 7 + message[3]  # byte position 3 is the name length, so start + length is the end index
    receiver_start = name_end  # receiver starts right after sender's name ends
    receiver_end = receiver_start + message[4]  # byte position 4 is the receiver length, so start + length is the end
    message_start = receiver_end   # message starts after receiver's name
    message_end = message_start + ((message[5] << 8) + message[6])  # message end
    sender_name = message[name_start:name_end].decode('utf-8')  # index sender start and end to extract name
    receiver_name = message[receiver_start:receiver_end].decode('utf-8')  # index receiver start and end to extract
    message_data = message[message_start:message_end].decode('utf-8')  # index message start  and end to extract

    if receiver_name not in vault:  # if receiver has not been sent a message then create empty list
        vault[receiver_name] = []
    vault[receiver_name].append((sender_name, message_data))  # append the message sent to receiver

    return vault  # return vault


def main():
    sock = None  # set socket equal to None
    conn = None  # set connection equal to None
    message_vault = {}  # create an empty dictionary which will be used to store messages
    try:
        if len(argv) != 2:  # check if the right number of arguments have been passed
            print(f"Usage:\n\n\tpython(3) {argv[0]} <port>\n")  # default from lecture notes
            exit()  # exit
        for char in argv[1]:  # iterate over port number if it is not a number print error message and exit
            if not char.isdigit():
                print(f"ERROR: Port number {argv[1]} contains invalid characters!")
                exit()

        port = int(argv[1])  # convert the port to an integer
        if port > 64000 or port < 1024:  # The port number should be between 1,024 and 64,000 (inclusive).
            print("ERROR: Port number must be between 1024 and 64000 inclusive.")  # print out error message and exit
            exit()  # socket has not been created so no need to close socket

        sock = socket(AF_INET, SOCK_STREAM)  # create socket
        sock.bind(("0.0.0.0", port))  # bind the socket to the requested port
        sock.listen(5)  # listen for requests
        while True:
            conn, client = sock.accept()  # connect the socket
            print(f"Connected to {port}.")  # print connection message to let user know they are connected to {port}
            message = conn.recv(66052)  # receive the message

            # do some error checks for the message request
            if ((message[0] << 8) + message[1]) != 0xAE73:  # check magic number
                print("Magic number is not equal to '0xAE73'!")
                conn.close()
                exit()
            if len(message) < 7:  # check message length
                print("ERROR: Length of message request is invalid!")
                conn.close()
                exit()

            print(f"Received bytes: {message}.")  # print received bytes

            if message[2] == 1:  # code for read request
                if message[4] != 0:  # check receiver length is equal to 0
                    print("ERROR: Receiver length must be equal to 0 for a read request!")
                    conn.close()
                    exit()

                name_start = 7  # byte 8 position 7 is the start of the name byte
                name_end = 7 + message[3]  # name end index equal to start + length of the sender name

                sender_name = message[name_start:name_end].decode('utf-8')  # extract the sender name from the message
                # use helper function to send back a message response,retrieve the messages stored using key sender_name
                MessageResponse(sock, conn, message_vault, sender_name)
                conn.close()  # close the connection after sending back the message response for a read request

            elif message[2] == 2:  # code for create request
                # use the helper function to store the message in a dictionary
                message_vault = storing_message(message, message_vault)
            else:  # message[2] corresponds to the ID byte if it is not equal to 1 or 2 print an error message and exit
                print("ERROR: Message ID is not equal to 1 or 2!")
                conn.close()
                exit()

    except ValueError as err:  # Value error which slipped past previous checks
        print(f"ERROR: {err}")
        sock.close()
        exit()
    except UnicodeDecodeError:  # message decode
        print("ERROR: Decoding/encoding failure")
    except OSError as err:  # raised by all socket methods
        print(f"ERROR: {err}")  # print the error string
    finally:  # close the sockets
        if sock != None:
            sock.close()
        if conn != None:
            conn.close()
        exit()
main()