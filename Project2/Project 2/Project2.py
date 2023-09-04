#Author: Isaac Kim G01201648
#CS 455 by Professor Bo Han
#Project 2

import socket
import threading
import copy

#server_ip at index 0 is for node A, index 1 is for B, etc...
server_ips = ['127.0.0.1','127.0.0.2','127.0.0.3','127.0.0.4','127.0.0.5']
#keep static port buffer size for simplicity
TCP_PORT = 5005
buffer_size = 1024

#global vars
round = 1
last_round = 0
change = [0,0,0,0,0]

#Node class for nodes in graph
#has receive and send method for server and client sockets
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
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((host_ip, port))
        sock.listen()
        conn, addr = sock.accept()

        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            #implement neighbor update here
            #-----------------------------------------------------------------------------------------
            DV_msg = unformat_neighbors(data)

            #output stuff
       	    print("Node " + self.name + " received DV from " + DV_msg[0])

            #determine which node sent for comparison value for 'shorter' path
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

            #save old neighbors to see if there was an update or not later
            temp = copy.deepcopy(self.neighbors)
            
            #bellman ford
            i = 1
            while(i < 6):
            	#path length to consider for replacement
                path_len = ref + int(DV_msg[i])

                #if there is no path from sender
                if(DV_msg[i] == '0'):
                    i += 1
                    continue

                #if there is no path from neighbors
                elif(self.neighbors[i-1] == '0'):
                	#if we are at sender neighbor
                    if(i-1 == self.index):
                        i += 1
                        continue
                    self.neighbors[i-1] = str(path_len)  

                #if there is shorter path
                if(ref + int(DV_msg[i]) < int(self.neighbors[i-1])):
                    self.neighbors[i-1] = str(path_len)
                
                i += 1

            #see if there was an update or not
            if(temp == self.neighbors):
            	#outputstuff
            	print("No change at node " + self.name)
            else:
            	#output stuff
                print("Updating DV at node " + self.name)
                print("Old DV at node " + self.name + ":" + str(temp))
                print("New DV at node " + self.name + " = " + str(self.neighbors))
            print("")

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
    #--------------------------------------------------------------------------------------------------------------------
    #if filename is not network.txt, replace network.txt with filename
    matrix = read_file("network.txt")

    #--------------------------------------------------------------------------------------------------------------------
    temp = copy.deepcopy(matrix)
    last = copy.deepcopy(matrix)

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

    global change
    global last_round
    global round

    while(change != [1,1,1,1,1]):
    	#count keeps track of which node is sending DV msgs currently
    	count = 0
    	name = ['A','B','C','D','E']
    	for node in temp:
    		#output stuff--------------------------------------------------------------
    	    print("Round " + str(round) + ":" + name[count])
    	    round += 1
    	    print("Current DV = " + str(matrix[count]))
    	    print("last DV = " + str(last[count]))
    	    
    	    updated = ""
    	    if(last[count] == matrix[count]):
    	    	updated = "No update"
    	    	change[count] = 1

    	    else:
    	    	updated = "Updated"
    	    	last_round = round - 1
    	    
    	    last[count] = matrix[count]
    	    print("Updated from the last DV or the same? "+updated)
    	    print("")
    	    #--------------------------------------------------------------------------

    	    #check for no change
    	    if(change == [1,1,1,1,1]):
    	    		break
    	    
    	    #neighbor keeps track of which neighbor we are looking at
    	    neighbor = 0
    	    #currentNode keeps track of which node we are sending dv's from
    	    currentNode = nodeMatrix[count]
    	    for edge in node:
    	        if(edge != '0'):
    	            #output stuff
    	            print("Sending DV to node "+ name[neighbor])

    	            #send DV message
    	            DV_msg = currentNode.send(server_ips[neighbor], TCP_PORT, format_neighbors([currentNode.name]+matrix[count]))

    	            #update matrix with recalculated DV's
    	            matrix[neighbor] = unformat_neighbors(DV_msg)
    	            
    	            #reopen server socket for future connections
    	            threading.Thread(target=nodeMatrix[neighbor].receive,daemon=True, args=(server_ips[neighbor],TCP_PORT,)).start()
	
    	        neighbor += 1
    	    count+=1

    #output stuff
    print("Final output:")
    for j in range(0,5):
        print("Node " + name[j] +" DV = " + str(matrix[j]))

    print("The number of rounds till convergence(Round # when one of the nodes last updated its DV) = " + str(last_round))

#method to read in network.txt
def read_file(filename):
    adjacency = [0] * 25
    #reading in adjacency matrix file and formatting
    f = open(filename, "r")
    inputStr = f.read()
    inputStr = inputStr.replace(" ",".")
    inputStr = inputStr.replace("\n",".")
    inputStr = inputStr.split(".")

    count = 0
    for i in inputStr[:-1]:
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