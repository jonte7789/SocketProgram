# SocketProgram
Socket Programming Assignment

1. Download both server.py and client.py and place them in the same directory.

2. Open 2 terminals and navigate both terminals to this directory that you placed the files in.

3. Run the server by entering the command: python3 server.py [PortNumber]
   - Note Port Number is a number between 1024 and 64000

4. Using the second terminal, run the command python3 client.py localhost [PortNumber] [Name] [Type]

5. Note that Name must have quotation marks around it and is case sensitive, e.g: "Bob". Also Note PortNumber is the same as the server's.

6. Note that Type is either **create** or **read**.
   - Where when you call create, the terminal prompts you to enter a name of the receiver along with a message, no quotation marks are needed here.
   - For a call read, the terminal will read back the messages sent to the name in [Name].

7. To exit the server, you can do Control + C in the terminal. If issues arise in regards to a port being active, you can change to a different port number.
