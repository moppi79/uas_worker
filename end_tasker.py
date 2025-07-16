import socket, sys, time,random

from multiprocessing import shared_memory

#from multiprocessing import Process

'''



'''
def end_task (time_s:int,target:tuple,own_ip:str,share_name:str,message:bytes)->None:	
	print ('start',time_s,share_name,message,target,own_ip)
	
	#exit('end Tasker put out data')
	
	i = int(time_s)
	shm_b = shared_memory.ShareableList(name=share_name)
	while i > 1:
		time.sleep(1)
		i -= 1
		print (i,shm_b[1])
	

	HOST, PORT = target[0], target[1]
	
	# SOCK_DGRAM is the socket type to use for UDP sockets
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print (dir(sock))
	#exit()
	a = True
	while a:
		i = random.randrange(15000,15999)
		#i = 15223
		print (i)
		try: 
			sock.bind((own_ip,i))
		
		except:
			pass
		finally:
			a  = False
			print(own_ip,i)
		

		time.sleep(0.02)
	
	print(dir(sock))		
	# As you can see, there is no connect() call; UDP has no connections.
	# Instead, data is directly sent to the recipient via sendto().
	sock.sendto(message, (HOST, PORT))

	print("Sent:   ",HOST,PORT, message)
	sock.close()
	
	print ('ende')
	#shm_b.shm.unlink()
