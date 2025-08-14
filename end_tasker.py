import socket, sys, time,random

from multiprocessing import shared_memory

#from multiprocessing import Process

'''
Das hier ist der end task 
es wird gestartet wenn der call zustande kommt 

es ist aber nur ein grobes system wurde nicht voll ausgebaut

wie z.b. das er auch bei geht andere nachrichten öndert oder oder oder 


'''
def end_task (time_s:int,target:tuple,own_ip:str,share_name:str,message:bytes)->None:	
	
	#exit('end Tasker put out data')
	
	i = int(time_s)
	shm_b = shared_memory.ShareableList(name=share_name)
	while i > 1:
		time.sleep(1)
		i -= 1
		print (i,shm_b[1]) #das soll nachher prüfen ob der A-TLN  aufgelegt hat und sich selbst terminieren
	

	HOST, PORT = target[0], target[1]
	
	# SOCK_DGRAM is the socket type to use for UDP sockets
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#exit()
	a = True
	while a:
		i = random.randrange(15000,15999)
		#i = 15223

		try: 
			sock.bind((own_ip,i))
		
		except:
			pass
		finally:
			a  = False

		

		time.sleep(0.02)
	

	# As you can see, there is no connect() call; UDP has no connections.
	# Instead, data is directly sent to the recipient via sendto().
	sock.sendto(message, (HOST, PORT))

	sock.close()
