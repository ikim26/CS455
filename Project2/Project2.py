# Author: Isaac Kim
# CS 455 Project 2

import socket
import threading
 
server_ips = ['127.0.0.1','127.0.0.2','127.0.0.3','127.0.0.4','127.0.0.5']
TCP_PORT = 5005
BUFFER_SIZE = 1024


def create_server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server_ips[0], port))
    s.listen()
    print("listening")
    
    conn, addr = s.accept()
    print('Connection address:', addr)
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        print("server received data:", data)
        conn.send(data)  # echo
    conn.close()


def network_init():
    adjacency = [0] * 25

    #reading in adjacency matrix file and formatting
    f = open("network.txt", "r")
    inputStr = f.read()
    inputStr = inputStr.replace(" ","")
    inputStr = inputStr.replace("\n","")
    count = 0
    for i in inputStr:
        adjacency[count] = i
        count += 1

    #vars for node path lengths
    a = adjacency[0:5]
    b = adjacency[5:10]
    c = adjacency[10:15]
    d = adjacency[15:20]
    e = adjacency[20:25] 

    ta = threading.Thread(target=create_server(), args=(5005,))
    tb = threading.Thread(target=create_server(), args=(5006,))
    tc = threading.Thread(target=create_server(), args=(5007,))
    td = threading.Thread(target=create_server(), args=(5008,))
    te = threading.Thread(target=create_server(), args=(5009,))
 
if __name__ =="__main__":
    # creating thread
    #t1 = threading.Thread(target=print_square, args=(10,))
    #t2 = threading.Thread(target=print_cube, args=(10,))
 
    # starting thread 1
    #t1.start()
    # starting thread 2
    #t2.start()
 
    # wait until thread 1 is completely executed
    #t1.join()
    # wait until thread 2 is completely executed
    #t2.join()
 
    # both threads completely executed
    #print("Done!")
    ta = threading.Thread(target=create_server(5005), daemon=True).start()
    print("created thread successfully")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ips[0], TCP_PORT))
    s.send("test1")
    data = s.recv(1024)
    s.close()
    
    
    print("client received data:", data)
       