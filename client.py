'''Jonte Auden
Student ID: 76942953

Client Code
NOTE: The server will restart when the client aborts / disconnects the socket.

Keep socket open unless calling a read request or an error occurs. IF an error message is printed then
the server must be re-run as well as the client as the server will notice the socket has disconnected and will
abort / disconnect from the connected port

'''

from sys import exit, argv
from socket import *

''' Create helper functions. For Client as defined in assignment description need to prepare MessageRequest, 
create socket and connect to server, send messagerequest, read request from server and display the information, 
  finally close socket return resources to OS and exit. 
  
  IDEA: create 4 helper functions to handle each of the 4 main steps.
  NOTE: " If any of these steps do not succeed, the client should print an appropriate error message, close the socket (if open),
and exit without attempting the remaining steps. "
  '''


'''prepare_message_request(user_name, receiver_name, message_text, request_type) will create a suitable message request
depending on the type, create or read.
 '''


def prepare_message_request(user_name, receiver_name, message_text, request_type):
    # create byte array to stay request in
    message_request = bytearray(7)  # minimum 7 bytes for the header

    receiver_name_len = len(receiver_name.encode('utf-8'))  # figure out the receiver name length
    user_name_len = len(user_name.encode('utf-8'))  # figure out the username length

    # append 2 bytes for magic number in big ED format 0xAE73
    message_request[0] = (0xAE & 0xFF)
    message_request[1] = (0x73 & 0xFF)

    # append 1 byte for id, 1 for read 2 for request so 0x01 or 0x02
    # as stated earlier only read or create is possible as errors handled earlier

    if request_type == "read":  # request type read, set id equal to 1
        message_request[2] = 0x01  # ID 1 for a read request
        message_request[3] = (user_name_len & 0xFF)  # username length is not needed
        message_request[4] = 0x00  # receiver name length
    else:  # request type create set id equal to 2
        message_request[2] = 0x02  # set ID equal to 2 for a create request
        message_request[3] = (user_name_len & 0xFF)  # sender name length
        message_request[4] = (receiver_name_len & 0xFF)  # receiver name length

    # byte 6 and 7 and end of the fixed header (message length)
    # this will be set to 0 for read request as "" is passed as an argument
    message_text_length = len(message_text.encode('utf-8'))
    message_request[5] = ((message_text_length >> 8) & 0xFF)     # storing in big endian format
    message_request[6] = (message_text_length & 0xFF)  # storing in big endian format
    message_request.extend(user_name.encode('utf-8'))      # add the username (sender) by extending the byte array
    message_request.extend(receiver_name.encode('utf-8'))  # add the receiver name by extending the byte array
    message_request.extend(message_text.encode('utf-8'))  # add the message by extending the byte array

    return message_request     # return message_request, in main function send it to the server


# create socket and connect to the server
def socket_connect(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)  # connect socket to the address
    return sock  # return socket


def send_message_request(sock, message_request):  # attempt to send the message to the server
    amount = sock.send(message_request)
    if amount < len(message_request):
        raise OSError("Unable to send whole message!")  # print error message if cannot send the whole message


''' Helper function which takes a socket and reads back the server's message response '''


def read_request(sock):  # b'\xaes\x03\x01\x00\x00\x02\x00\x00\x05ggaaaaa' format
    # first 0 1 byte magic num, byte 2 id, byte 3 num items, byte 4 0 means no more messages 2 means more messages,
    # byte 5 sender length, byte 6 and 7 message length
    response = sock.recv(66052)  # receive maximum bytes for one response
    if len(response) < 5:  # header is at least 5 bytes so this must be an error
        print("Response is missing information! Response should be at least 5 bytes!")
        close_socket(sock)
    if response[2] != 3:  # if ID is not 3 than there has been an error
        print("ID must equal 3 for a Message Response!")
        close_socket(sock)
    if ((response[0] << 8) + response[1]) != 0xAE73:  # check the magic number
        print("Magic number is not equal to '0xAE73'!")
        close_socket(sock)

    if len(response) > 5:  # decode all the messages and print them out
        j = 5  # start at byte position 5
        for i in range(int(response[3])):  # iterate over the number of items, where response[3] is the number of items

            sender_len = response[j]  # byte position 5 is the sender length
            message_len = ((response[j + 1] << 8) + response[j + 2])  # big endian format for msg len so do a shift
            if sender_len < 1:  # check sender length is at least 1
                print("Sender length must be greater than 0!")
                close_socket(sock)
            if message_len < 1:  # check message length is at least 1
                print("Message length must be greater than 0!")
                close_socket(sock)
            # currently, j is at sender length and next two bytes are message length so shift by 3
            j += 3  # shift j by 3 and start printing the sender along with the message
            #  j is start of sender, where j + sender length is the end position of the sender name
            print("Sender: " + str(response[j:j + sender_len].decode('utf-8')))  # decode the sender
            j += sender_len  # update j to be the starting position of the message
            #  j to j + message length will extract the message from the response
            print("Message: " + str(response[j:j + message_len].decode('utf-8')))  # decode the message
            j += message_len  # update j to be the end of the message
        if response[4] == 1:  # can only deliver 255 messages at a time, this means 255 messages were sent
            print("255 Messages Extracted! To extract more please query a read request again!")  # inform the user
    else:
        print(f"No messages for {argv[3]}.")  # no messages for the receiver


def close_socket(sock):  # helper function to close a socket and exit
    sock.close()
    exit()


'''main is where the error handling mostly occurs. Query user for receiver and message if type create
Create a socket and connect to server where it can receive messages and send back response
'''
def main():
    sock = None  # Define sock in case error occurs before it is created

    try:
        if len(argv) != 5:  # check number of command line arguments, argv[0] is name of file
            print(f"Usage:\n\ntpython(3) {argv[0]} <hostname> <port> <user_name> <request_type>\n")
            exit()

        port = int(argv[2])  # attempt to cast port as an integer, if it fails an exception will run at bottom of main
        if port < 1024 or port > 64000:  # port must be within this range
            print(f"Invalid port number {port}. Port number must be between 1,024 and 64,000")
            exit()

        services = getaddrinfo(argv[1], port, AF_INET, SOCK_STREAM)  # retrieve services
        family, type_req, proto, name, address = services[0]  # retrieve address as stated in assignment description
        sock = socket_connect(address)  # connect the socket to the address

        name = argv[3]  # argv[3] is equal to the sender's name
        if len(name) < 1 or len(name.encode('utf-8')) > 255:  # check if the sender's name is valid
            print("Username must be between 1 character and 255 bytes!")
            close_socket(sock)
        #  assuming names with numbers are acceptable, just checking it doesn't start with a space
        if name.startswith(" "):  # if name starts with space then print error message and exit
            print(f"Invalid name {name}.")
            close_socket(sock)

        request_type = argv[4]  # Request type should be argv[4], check later on if it is valid

        '''The name of the receiver: This must be at least 1 character and less than 255 bytes. If it is not, then the
        client prints an appropriate error message and prompts again until a valid receiver name is provided.
         The message contents: The message must be at least 1 character and less than 65,535 bytes. If it is not,
        then the client prints an appropriate error message and prompts again until a valid message is provided.'''
        if request_type == "create":  # prepare message request of type create

            receiver_name = input("Enter receiver's name: ")  # Ask user for receiver's name
            # convert to bytes and keep requesting while wrong size and print out error message
            while len(receiver_name) < 1 or len(receiver_name.encode('utf-8')) >= 255:
                print(f"ERROR: Invalid receiver name size! receiver name must be between 1 character and 255 bytes!")
                receiver_name = input("Enter receiver's name: ")

            message_text = input("Please enter a message to send: ")  # Ask user for the message they want to send
            # convert to bytes and keep requesting while wrong size and print out message
            while len(message_text) < 1 or len(message_text.encode('utf-8')) >= 65535:
                print(f"ERROR: Invalid message size! Message must be between 1 character and 65,535 bytes!")
                message_text = input("Please enter a message to send: ")

            # Call the helper function to prepare the header and message request of type create
            message_request = prepare_message_request(name, receiver_name, message_text, request_type)
            send_message_request(sock, message_request)  # send the message to the server

        elif request_type == "read":  # prepare read request
            #  pass in empty string as receiver name and message as this is not needed for the request
            message_request = prepare_message_request(name, "", "", request_type)  # call helper function
            send_message_request(sock, message_request)  # send the message request to the socket
            read_request(sock)  # read the message respond sent from the server
            close_socket(sock)  # close sock and exit

        else:
            #  if request type is not read or create then print error message and exit the socket, case-sensitive
            print(f"ERROR: Invalid request type '{type_req}'! Request type must be 'create' or 'read'")
            close_socket(sock)

    except ValueError:  # this value error occurs when trying to cast port number as an integer if it is not an integer
        print(f"Invalid port number. Port number must be a valid integer between 1024 and 64000.")
        close_socket(sock)

    except UnicodeDecodeError:
        print("ERROR: Response decoding failure")

    except gaierror:
        print(f"ERROR: Host '{argv[1]}' does not exist")

    except OSError as err:
        print(f"ERROR: {err}")

    finally:
        if sock != None:  # close socket and return resources to OS
            close_socket(sock)


# call main() and run the client
main()


