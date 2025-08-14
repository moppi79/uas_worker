import time,socketserver,random, socket, bencodepy, array,json,time,random, sys

from multiprocessing import shared_memory

from multiprocessing import Process

from rtp_engine import *

from sip_handler import *

from end_tasker import *


ip_select  = ['10.0.0.1','192.168.0.1','127.0.0.1']

'''



für den ersten betrieb muss bencodepy installiert werde
pip install bencode.py --break-system-package  

ansonsten läuft alles aus dem standart vorhanden Python strukturen 


desweitern die offenen dateien muss stark erhöht werden
ulimit -n 4096 <-- maximal offene dateien

'''


class MyUDPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		'''
		Standart IP Handle
		hier wir jede neues Packt was rein kommt gestartet
		
		'''
		
		data = self.request[0].strip()
		socket = self.request[1]
		b = sip_handler(data,self.server.server_address,self.client_address)

		end_start = ''
		cont = 1
		shared_mem_set = 0
		try:
			'''
			Hier wird versucht ein Datenstz im speicher zu finden. 
			wenn es noch keinen call gibt, erzeugt es einen fehler und wird im Except abgefangen
			dort wird dann der Datensatz angelegt
			Sharedmemory beschreibung
			[0] start_type, 200 OK oder 183 
			[1] Status RTP Engine  start/etablisht/kill
			[2] Status von RTP Playback start/running/stop
			[3] zustand vom Call ini/pre/eta/end/kill
			[4] nächster schritt typ für den End_tasker (BYE,Cancel etc)
			[5] SDP vom Initalen Invite
			[6] SDP answer
			[7] SDP offer
			'''
			mem = shared_memory.ShareableList(name=b.get_tag('To'))
		except:
			new = b.call_setter()
			if new[1] == 'start':
				'''
				Datenbank werte könnten hier abgefragt werden
				end_time = sec
				ansage = '/path/ansage.mp3'
				start_type = 200 / 183  
				'''

				end_time = 10
				ansage = '/path/ansage.mp3'
				start_type = '200'

				if start_type != '200': #wenn start type nicht 200 OK ist.
					new[0] = start_type 
					new[3] = 'pre'
					new[4] = 'CANCEL'

				c = rtp_engine(b.get_sdp()) #RTP initalisieren
				c.offer(b.get_tag('From'),b.get_header('Call-ID'),b.get_sdp())
				c.answer(b.get_tag('To'),b.get_tag('From'),b.get_header('Call-ID'),b.get_sdp())
				new.append(b.get_sdp())
				new.append(c.sdp_data['offer']['sdp'])
				new.append(c.sdp_data['answer']['sdp'])
				b.add_sdp(c.sdp_data['answer'],new[0],'answer')
				b.add_sdp(c.sdp_data['offer'],new[0],'offer')
				new[1] = 'etablisht'

			if new[3] != '' and new[3] != 'kill': #when the Status is not set
				'''
				wenn der call kein call ist, es wird auch kein memory 
				'''
				mem = shared_memory.ShareableList(new,name=b.get_tag('To'))
				end_start = [end_time ,self.client_address,self.server.server_address[0],b.get_tag('To')]
				shared_mem_set = 1
			else:
				mem = new
			
			cont = 0

		if cont ==  1:
			'''
			wemnn der call schon am laufen ist, 
			es wurde der tag schon gefunden. 
			'''
			print ('Call found')
			shared_mem_set = 1
			c = rtp_engine(mem[5])
			cont_i = 0
			while cont_i <= 7: #dieser part ist nur für die anzeige des speichers
				print ('mem['+str(cont_i)+']: '+ str(mem[cont_i]))
				cont_i += 1
			new = b.call_reakt(mem[3]) # prüfen was er nun auf die nachrichten machen soll
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
		'''
		antworten senden
		'''
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
			'''
			Hier wird der End Task vorbereiet
			es werden alle wichtigen daten mitgeteilt 
			'''
			#message_end = b.offer('BYE')
			message_end = b.offer(mem[4])

			p = Process(target=end_task, args=(end_start[0],end_start[1],end_start[2],end_start[3],message_end))
			p.start()
			#time.sleep(4)

			#socket.sendto(b.offer('BYE'), self.client_address)
		###### End Task Starten hioer das noch mal versuichen !!!!  #####
		
		


		print ('mem[3]',mem[3], shared_mem_set)
		if shared_mem_set == 1: #end task und löschen aller call daten
			if mem[3] == 'kill':
				mem.shm.close()
				mem.shm.unlink()
				shared_mem_set = 0
		
		
			mem.shm.close()





if __name__ == "__main__": 

	'''
	Start von dem script 

	im ip_select müssen die Eigenen IPs stehtn
	es könnte noch ein temporärer umgebeung gebaut werden, 
	um dann eine Generelle laufzeit steuerung zu bauen,.
	also Script beendigung oder steuerung	
	'''


	#org start
	print(ip_select[int(sys.argv[1])])
	HOST, PORT = ip_select[int(sys.argv[1])], 5060
	with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
		server.serve_forever()
