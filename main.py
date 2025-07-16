import time,socketserver,random, socket, bencodepy, array,json,time,random, sys

from multiprocessing import shared_memory

from multiprocessing import Process

from rtp_engine import *

from sip_handler import *

from end_tasker import *

ip_select  = ['192.0.1.2','8.8.8.8','127.0.0.1']


class MyUDPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		
		data = self.request[0].strip()
		socket = self.request[1]
		print(dir (self.server))
		print (self.server.server_address)
		print(f"{self.client_address} wrote:")
		#exit()
		b = sip_handler(data,self.server.server_address,self.client_address)

		print (b.get_all())
		end_start = ''
		cont = 1
		shared_mem_set = 0
		try:
			mem = shared_memory.ShareableList(name=b.get_tag('To'))
		except:
			new = b.call_setter()
			print ('b')
			if new[1] == 'start':
				'''
				Datenbank werte müssen hier gesezt werden
				end_time = sec
				ansage = '/path/ansage.mp3'
				start_type = 200 / 183  
				'''

				end_time = 10
				ansage = '/path/ansage.mp3'
				start_type = '200'

				if start_type != '200':
					print ('start_type anders als  200 ')
					new[0] = start_type 
					new[3] = 'pre'
					new[4] = 'CANCEL'

				c = rtp_engine(b.get_sdp())
				c.offer(b.get_tag('From'),b.get_header('Call-ID'),b.get_sdp())
				c.answer(b.get_tag('To'),b.get_tag('From'),b.get_header('Call-ID'),b.get_sdp())
				new.append(b.get_sdp())
				new.append(c.sdp_data['offer']['sdp'])
				new.append(c.sdp_data['answer']['sdp'])
				b.add_sdp(c.sdp_data['answer'],new[0],'answer')
				b.add_sdp(c.sdp_data['offer'],new[0],'offer')
				#b.options[new[0]]['Content-Length'] = c.sdp_data['answer']['len']
				#b.sdp_data['answer']  = c.sdp_data['answer']['sdp']
				#b.sdp_data['offer']  = c.sdp_data['offer']['sdp']
				new[1] = 'etablisht'
				print (new)
				print (b.get_all())
			if new[3] != '' and new[3] != 'kill': #when the Status is noz set
				print (new[3])
				mem = shared_memory.ShareableList(new,name=b.get_tag('To'))
				end_start = [end_time ,self.client_address,self.server.server_address[0],b.get_tag('To')]
				shared_mem_set = 1
			else:
				mem = new
			
			cont = 0

		if cont ==  1: #wenn ein call noch am laufen ist
			print ('Call found')
			shared_mem_set = 1
			c = rtp_engine(mem[5])
			cont_i = 0
			while cont_i <= 7:
				print ('mem['+str(cont_i)+']: '+ str(mem[cont_i]))
				cont_i += 1
			new = b.call_reakt(mem[3])
			print ('new: ',new)
			b.add_sdp(mem[7],new[0],'answer')
			b.add_sdp(mem[6],new[0],'offer')
			if mem[2] == 'running':
				if new[2] != 'start':
					mem[2] = new[2] 
			mem[0] = new[0]
			print (b.get_all())
			#if mem[2] != new[2]:
			#	mem[2] = new[2]


		###### UDP packet Send zo SBC #####
		if mem[0] != '':
			ans = b.answer(mem[0])

			#socket.bind(tar_new)
			#socket.sendto(ans, self.client_address) #org
			socket.sendto(ans,self.client_address)
			
			###### UDP packet Send zo SBC #####

		###### RTP ansage Starten/beenden #####
		if mem[2] != '':
			if mem[2] == 'start':
				c.p_m(b.get_tag('From'),b.get_header('Call-ID'))
				c.b_m(b.get_tag('To'),b.get_header('Call-ID'))
				mem[2] == 'running'
			else:
				c.s_m(b.get_tag('From'),b.get_header('Call-ID'))
				mem[2] == 'stop'
		###### RTP ansage Starten/beenden #####
		
		###### End Task Starten #####
		#p = Process(target=end_task, args=([random.randrange(7,9),d]))
		if end_start != '':
			#message_end = b.offer('BYE')
			message_end = b.offer(mem[4])
			print (mem[4])
			
			print (b.offer('BYE'))
			print (b.offer('CANCEL'))
			print (b.offer(mem[4]))

			#exit('ende')
			p = Process(target=end_task, args=(end_start[0],end_start[1],end_start[2],end_start[3],message_end))
			p.start()
			#time.sleep(4)

			#socket.sendto(b.offer('BYE'), self.client_address)
		###### End Task Starten hioer das noch mal versuichen !!!!  #####
		
		


		print ('mem[3]',mem[3], shared_mem_set)
		if shared_mem_set == 1:
			if mem[3] == 'kill':
				mem.shm.close()
				mem.shm.unlink()
				shared_mem_set = 0
		
		
			mem.shm.close()



if __name__ == "__main__":


	#org start
	print(ip_select[int(sys.argv[1])])
	HOST, PORT = ip_select[int(sys.argv[1])], 5060
	with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
		server.serve_forever()

