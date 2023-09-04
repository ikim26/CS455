#Author: Isaac Kim G01201648
#CS 455 by Professor Bo Han
#Project 2

import socket
import threading

#server_ip at index 0 is for node A, index 1 is for B, etc...
server_ips = ['127.0.0.1','127.0.0.2','127.0.0.3','127.0.0.4','127.0.0.5']
#keep static port buffer size for simplicity
TCP_PORT = 5005
buffer_size = 1024

class Node:
    neighbors = ['0','0','0','0','0']
    #initializer
    def __init__(self, neighbors, index):
        self.neighbors = neighbors[1:]
        self.name = neighbors[0]
        self.index = index

    #method for server socket
    def receive(self,host_ip,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((host_ip, port))
        sock.listen()
        conn, addr = sock.accept()
        #print(addr)
        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            #implement neighbor update here
            DV_msg = unformat_neighbors(data)

            #determine which one is comparison value for 'shorter' path
            if(DV_msg[0] == 'A'):
                ref = int(self.neighbors[0])

            if(DV_msg[0] == 'B'):
                ref = int(self.neighbors[1])

            if(DV_msg[0] == 'C'):
                ref = int(self.neighbors[2])

            if(DV_msg[0] == 'D'):
                ref = int(self.neighbors[3])

            if(DV_msg[0] == 'E'):
                ref = int(self.neighbors[4])

            print("old " + self.name)
            print(self.neighbors)
            print(DV_msg[0])
            print(DV_msg[1:])
            i = 1
            while(i < len(DV_msg)-1):
                path_len = ref + int(DV_msg[i])
                #if there is no path from sender
                if(DV_msg[i] == '0'):
                    #print("didn't change index " + str(i-1))
                    i += 1
                    continue
                #if there is no path from neighbors
                if(self.neighbors[i-1] == '0'):
                    if(i-1 == self.index):
                        #print("didn't change index " + str(i-1))
                        i += 1
                        continue
                    #print("changed index " + str(i-1) + " to " + str(path_len))
                    self.neighbors[i-1] = str(path_len)  
                #if there is shorter path
                elif(ref + int(DV_msg[i]) < int(self.neighbors[i-1])):
                    #print("changed index " + str(i-1) + " to " + str(path_len))
                    self.neighbors[i-1] = str(path_len)

                i += 1

            print("new " + self.name)
            print(self.neighbors)
            
            conn.send(format_neighbors(self.neighbors))
        conn.close()
    
    #method for client socket
    def send(self,host_ip, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #in case we want to reuse address and socket hasnt closed yet
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((host_ip, port))
        sock.send(message)
        data = sock.recv(buffer_size)
    
        # tell host we are done sending message
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        return data

#network_init() function
#initializes server sockets for nodes
def network_init():
    #get adj matrix data from network.txt
    matrix = read_file("network.txt")

    #matrix[0] = ['A'] + matrix[0]
    #matrix[1] = ['B'] + matrix[1]
    #matrix[2] = ['C'] + matrix[2]
    #matrix[3] = ['D'] + matrix[3]
    #matrix[4] = ['E'] + matrix[4]

    nodeA = Node(['A']+matrix[0], 0)
    nodeB = Node(['B']+matrix[1], 1)
    nodeC = Node(['C']+matrix[2], 2)
    nodeD = Node(['D']+matrix[3], 3)
    nodeE = Node(['E']+matrix[4], 4)
    nodeMatrix = [nodeA, nodeB, nodeC, nodeD, nodeE]

    #start server sockets for nodes
    threading.Thread(target=nodeA.receive,daemon=True, args=(server_ips[0],TCP_PORT,)).start()
    threading.Thread(target=nodeB.receive,daemon=True, args=(server_ips[1],TCP_PORT,)).start()
    threading.Thread(target=nodeC.receive,daemon=True, args=(server_ips[2],TCP_PORT,)).start()
    threading.Thread(target=nodeD.receive,daemon=True, args=(server_ips[3],TCP_PORT,)).start()
    threading.Thread(target=nodeE.receive,daemon=True, args=(server_ips[4],TCP_PORT,)).start()

    

    #matrix[0] is the edge weights of neighbors for node A
    #matrix[1] is the edge weights of neighbors for node B
    #matrix[2] is ... node C
    #etc...

    #count keeps track of which node is sending DV msgs currently
    count = 0
    for node in matrix:
        #neighbor keeps track of which neighbor we are looking at
        neighbor = 0
        currentNode = nodeMatrix[count]
        for edge in node:
            #print("currentEdge:" + edge)
            if(edge != '0'):
                #send DV message
                DV_msg = currentNode.send(server_ips[neighbor], TCP_PORT, format_neighbors([currentNode.name]+node))
                matrix[neighbor] = unformat_neighbors(DV_msg)
                #reopen server socket for future connections
                threading.Thread(target=nodeMatrix[neighbor].receive,daemon=True, args=(server_ips[neighbor],TCP_PORT,)).start()

            neighbor += 1
        count+=1

#method to read in network.txt
def read_file(filename):
    adjacency = [0] * 25
    #reading in adjacency matrix file and formatting
    f = open(filename, "r")
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

    #create matrix
    matrix = [a,b,c,d,e]
    return matrix

#converts array to byte formatted string to send to sockets
def format_neighbors(array):
    neighbor_string = ""
    for i in array:
        neighbor_string += str(i)
        neighbor_string += "."

    return bytes(neighbor_string[:-1], 'utf-8')

#unconverts string byte to array
def unformat_neighbors(data):
    str_version = data.decode('utf-8')
    return (str_version.split('.'))

network_init()