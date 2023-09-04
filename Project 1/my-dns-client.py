#Isaac Kim 
#CS 455 
#Project 1

import socket
import binascii
import sys
import time

#usage: python my-dns-client.py gmu.edu
def send_dns_query(url):
	#make our query message
	message = make_dns_request(url)

	#use google dns server
	serverName = "8.8.8.8"
	#dns query is usually port 53
	serverPort = 53
	print("Contacting DNS server...")
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#send dns query
	print("Sending DNS query...")
	response = ""
	count = 0
	#timeout function
	while(response == ""):
		clientSocket.sendto(binascii.unhexlify(message.encode()),(serverName, serverPort))
		response, serverAddress = clientSocket.recvfrom(2048)
		#if response is empty
		if(response == ""):
			time.sleep(5)
		count += 1
		#if more than 3 tries, quit
		if(count >= 3):
			print("Error: Destination server timed out after 3 attempts! Please try again")
			return


	#response from server
	print("DNS response received (attempt " + str(count) + " of 3)")
	print("Processing DNS response...")
	#close connection
	clientSocket.close()

	print("------------------------------------------------")
	process_dns_response(binascii.hexlify(response).decode(), url)

def make_dns_request(url):
	print("Preparing DNS query...")
	#since our type is always going to be A
	msg_type = "A"

	ID = 43981  # ID for us is "ABCD"

	#our question field
	#Given to us in project spec
	#Note: unknown fields set to 0 by default (change if needed)
	'''
	0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                      ID                       |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                    QDCOUNT                    |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                    ANCOUNT                    |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                    NSCOUNT                    |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                    ARCOUNT                    |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	'''

	#create our dns header
	#start with ID
	header = "{:04x}".format(ID)	#convert our ID to hex

	QR = "0"     # Query: 0, Response: 1
	OPCODE = "0000"  # Standard query = 0
	AA = "0"      
	TC = "0"     
	RD = "1"		# set to 1 in project spec
	RA = "0"    
	Z = "000"  
	RCODE = "0000"

	#insert our query message part we built previously after our ID field
	#query (above) is always going to be int 4 = 0b0100
	header += "0100"	

	#Given in project spec
	header += "0001" #QDCOUNT
	header += "0000" #ANCOUNT
	header += "0000" #NSCOUNT
	header += "0000" #ARCOUNT

	#header is complete now
	print("DNS query header = " + header)

	#Create question section now
	'''
	0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                                               |
	/                     QNAME                     /
	/                                               /
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                     QTYPE                     |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	|                     QCLASS                    |
	+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
	'''
	question = ""
	#at this point, we now need to create our QNAME field
	qname_labels = str(url).split(".")		#example: gmu.edu -> ["gmu", "edu"]

	for i in qname_labels:
		len_label = "{:02x}".format(len(i))		#convert length of first label to hex value
		question += len_label						#add to header

		#hexlify requires byte parameter, so we encode i, what encoding is not important since we decode right after
		label_chars = binascii.hexlify(i.encode())	#Example: encode "gmu" into utf-8 to use binascii hexlify
		question += label_chars.decode()			#add decoded hex to header

	question += "00" #null label of the root for QNAME

	#Given to us in project spec
	#QTYPE = 1 A type
	question += "0001"

	#Given to us in project spec
	#QCLASS = 1 for internet
	question += "0001"

	#print our completed question section
	print("DNS query question section = " + question)
	
	print("Complete DNS query = " + header + question + "\n")

	#returns as hex string
	return header + question

#method to print different parts of header and question
def process_dns_response(message, url):
	#print(message)
	#header section
	print("header components:")
	print("header.ID = " + message[0:4])
	print("header.QR = 1")				#1
	print("header.OPCODE = 0000")		#1000 0
	print("header.AA = 0")				#1000 00
	print("header.TC = 0")				#1000 000
	print("header.RD = 1")				#1000 0001
	print("header.RA = 1")				#1000 0001 1
	print("header.Z = 000")			#1000 0001 1000
	print("header.RCODE = 0000")		#1000 0001 1000 0000 = 8180
	print("header.QDCOUNT = " + message[8:12])
	print("header.ANCOUNT = " + message[12:16])
	print("header.NSCOUNT = " + message[16:20])
	print("header.ARCOUNT = " + message[20:24])

	#question section
	#since QNAME is the exact same as in the query, we can use the same code with the url
	print("\nquestion components:")
	question = ""
	qname_labels = str(url).split(".")		#example: gmu.edu -> ["gmu", "edu"]
	count = 2
	for i in qname_labels:
		len_label = "{:02x}".format(len(i))		#convert length of first label to hex value
		question += len_label						#add to header
		count += 2

		#hexlify requires byte parameter, so we encode i, what encoding is not important since we decode right after
		label_chars = binascii.hexlify(i.encode())	#Example: encode "gmu" into utf-8 to use binascii hexlify
		question += label_chars.decode()			#add decoded hex to header
		count += len(label_chars.decode())

	question += "00" #null label of the root for QNAME
	print("question.QNAME = " + question)
	print("question.QTYPE = " + message[24+count:24+count+4])
	print("question.QCLASS = " + message[24+count+4:24+count+8])

	#answer section
	print("\nanswer components:")
	answer_start_index = 24+count+8
	count_answers = int(message[12:16],16)
	count = 0
	num = 1
	for i in range(count_answers):
		print("answer number "+ str(num) + ":")
		print("answer.NAME = " + message[answer_start_index+count:answer_start_index+4+count])			
		print("answer.TYPE = " + message[answer_start_index+4+count:answer_start_index+8+count])
		print("answer.CLASS = " + message[answer_start_index+8+count:answer_start_index+12+count])
		print("answer.TTL = " + message[answer_start_index+16+count:answer_start_index+20+count])
		print("answer.RDLENGTH = " + message[answer_start_index+20+count:answer_start_index+24+count])
		
		rd_num = int(message[answer_start_index+20+count:answer_start_index+24+count],16)
		rd_data = message[answer_start_index+24+count:answer_start_index+24+count+(2*rd_num)]
		print("answer.RDATA = " + rd_data)

		IP = ""
		#if CNAME type
		if(message[answer_start_index+7+count] == "5"):
			x = 0
			while(x < len(rd_data)/2):
				n = int(rd_data[0+(2*x):2+(2*x)],16)
				if(n < 45 or n > 122):
					IP += "."
				else:
					IP += chr(n)
				x += 1

			print("Resolved IP address: " + IP[1:])

		else:
			#resolve ip address
			x = 0
			while(x < len(rd_data)/2):
				n = int(rd_data[0+(2*x):2+(2*x)],16)
				x += 1
				IP += str(n) + "."

			print("Resolved IP address: " + IP[:-1])

		num += 1
		print("\n")
		count += 24+(2*rd_num)

def main():
	if len(sys.argv) <= 1:
		print("Usage: 'python my-dns-client.py [url (example: google.com)]")
	else:
		send_dns_query(sys.argv[1])

if __name__ == "__main__":
    main()