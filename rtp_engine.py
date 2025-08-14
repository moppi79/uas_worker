import random, socket, bencodepy

class rtp_engine ():
	
	'''
	Diese klasse ist für die Kommunikation für die RTP Engine zuständig
	es muss bencodpy installiert werden. 

	pip install bencode.py --break-system-package  

	was noch ganz wichtig ist, hier müsste alles noch stark dynamisiert werden
	da hier doe IP/port noch fest drin ist
	damit man auch mehrere rtp-Eninges verwenden kann, wie auch andere dateien wiedergeben

	__init__
	es wird die Orginal SDP gespeichert, sie ist auch zwingend notwendigf 
	desweiteren wird ermittelt welche interfaces auf den rpt-engines verwenmdet werden

	get_sdp()
	gibt alle Daten aus dem eigeben speicher wieder 

	get_orgin()
	zum ermittelen des zum verwendenen  Interface auf der rtp-Engine

	get_sdp_from_engine()
	das ist zum verarbeiten der rückgabe von der RTP-Engine
	es gibt ein Dikt länge von dem SDP und das SDP selbst als Bytees

	cookie_c()
	rendet einen zuf#lligen cooki für die übertragung 

	ping()
	Sendet ein Ping an den RTP server 

	offer()
	Holt sich die Offer SDP daten von der rtp-engine
	
	answer()
	Holt sich die answer SDP daten von der rtp-engine

	delete()
	Beendet die Session auf der rtp-enine

	p_m()
	Starte Play media auf der rtp-engine

	s_m()
	stopt media playback auf der rtp-engine

	b_m()
	Block media, stopt weiterleitung des rtp-streams

	'''


	def __init__(self,sdp_org):
		self.av_ranges = {
			'10':'internal',
			'rest':'external'

		}
		self.sdp_data = {}
		self.sdp_data['org'] = sdp_org
		self.sdp_data['interface'] = ''
		self.get_orgin()

	def get_sdp (self):
		return self.sdp_data

	def get_orgin (self):

		if self.sdp_data['org'].find('\n\r') == -1:
			str_search = '\r\n'
		else:
			str_search = '\n\r'

		for x in self.sdp_data['org'].split(str_search):
			if x[0] == 'o':

				i = x.split('IP4 ')

				for u in self.av_ranges:


					if u == i[1][0:len(u)]:
						self.sdp_data['interface'] = self.av_ranges[u]
			
			if self.sdp_data['interface'] == '':
				self.sdp_data['interface'] = self.av_ranges['rest']
		

	def get_sdp_from_engine (self,data):

		i = bencodepy.decode(data.decode("utf-8").split(' ',1)[1].encode('utf8'))
		c = i[b'sdp'].decode("utf-8")
		length = 0
		for x in c.split('\n\r'):
			length += len(x)
		
		return {'len':length,'sdp':i[b'sdp']}
		

		#print (bencodepy.decode(data.decode("utf-8").split(' ',1)))

	def cookie_c (self):
		ret = ''
		i1 = str(random.randint(1, 999))
		i2 = str(random.randint(1, 999))
		i3 = str(random.randint(1, 999))
		return i1 +'_' + i2 + '_' + i3 + ' '

	def ping (self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
		message = bencodepy.encode({'command':'ping'})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(1000)
		sock.close()

	def offer (self,fr,call_id,sdp):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
		message = bencodepy.encode({'command':'offer','call-id':call_id,'from-tag':fr,'sdp':sdp, "direction": [ self.sdp_data['interface'], self.sdp_data['interface'] ]})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		self.sdp_data['offer'] = self.get_sdp_from_engine(data)
		sock.close()

	def answer (self,to,fr,call_id,sdp):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
		message = bencodepy.encode({'command':'answer','call-id':call_id,'from-tag':fr,'to-tag':to,'sdp':sdp,  "direction": [ self.sdp_data['interface'], self.sdp_data['interface'] ]})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		self.sdp_data['answer'] = self.get_sdp_from_engine(data)
		sock.close()

	def delete (self,fr,call_id):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
				
		message = bencodepy.encode({'command':'delete','call-id':call_id,'from-tag':fr})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		sock.close()
	
	
	def p_m (self,fr,call_id): #play media
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
				
		message = bencodepy.encode({'command':'play media','file':'/net/audio/ansagea.wav','call-id':call_id,'from-tag':fr})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		sock.close()


	def s_m (self,fr,call_id): #stop media
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
				
		message = bencodepy.encode({'command':'stop media','file':'/net/audio/ansagea.wav','call-id':call_id,'from-tag':fr})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		sock.close()

	def b_m (self,fr,call_id): #block media
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('10.0.0.4', 2223)
				
		message = bencodepy.encode({'command':'block media','call-id':call_id,'from-tag':fr})
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		sock.close()
