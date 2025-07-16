import random, socket, bencodepy

class rtp_engine ():

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
				print (x)
				i = x.split('IP4 ')
				print(i)
				for u in self.av_ranges:
					print ()

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
		server_address = ('192.168.1.3', 2223)
		
		message = bencodepy.encode({'command':'ping'})
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		#i = '876_123_2 '.encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(1000)
		print (data, server)
		sock.close()

	def offer (self,fr,call_id,sdp):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('192.168.1.3', 2223)
		
		#message = bencodepy.encode({'command':'offer','call-id':call_id,'from-tag':fr,'sdp':sdp,"from-interface": "external" ,"to-interface":"external" })
		#message = bencodepy.encode({'command':'offer','call-id':call_id,'from-tag':fr,'sdp':sdp, "direction": [ "external", "external" ]})
		message = bencodepy.encode({'command':'offer','call-id':call_id,'from-tag':fr,'sdp':sdp, "direction": [ self.sdp_data['interface'], self.sdp_data['interface'] ]})
		#message = json.dumps(arr).encode('utf8')
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		#i = '876_123_1 '.encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		print (data, server)
		self.sdp_data['offer'] = self.get_sdp_from_engine(data)
		sock.close()

	def answer (self,to,fr,call_id,sdp):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('192.168.1.3', 2223)
		#message = bencodepy.encode({'command':'answer','call-id':call_id,'from-tag':fr,'to-tag':to,'sdp':sdp,  "direction": [ "external", "external" ]})
		message = bencodepy.encode({'command':'answer','call-id':call_id,'from-tag':fr,'to-tag':to,'sdp':sdp,  "direction": [ self.sdp_data['interface'], self.sdp_data['interface'] ]})
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		print (data, server)
		self.sdp_data['answer'] = self.get_sdp_from_engine(data)
		sock.close()

	def delete (self,fr,call_id):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('192.168.1.3', 2223)
				
		message = bencodepy.encode({'command':'delete','call-id':call_id,'from-tag':fr})
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		print (data, server)
		sock.close()
	
	
	def p_m (self,fr,call_id): #play media
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('192.168.1.3', 2223)
				
		message = bencodepy.encode({'command':'play media','file':'/net/audio/ansagea.wav','call-id':call_id,'from-tag':fr})
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		print (data, server)
		sock.close()


	def s_m (self,fr,call_id): #stop media
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('192.168.1.3', 2223)
				
		message = bencodepy.encode({'command':'stop media','file':'/net/audio/ansagea.wav','call-id':call_id,'from-tag':fr})
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		print (data, server)
		sock.close()

	def b_m (self,fr,call_id): #block media
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('192.168.1.3', 2223)
				
		message = bencodepy.encode({'command':'block media','call-id':call_id,'from-tag':fr})
		#message = json.dumps(arr).encode('utf8')
		i = self.cookie_c().encode('utf8')
		sent = sock.sendto(i+message, server_address)
		data, server = sock.recvfrom(5000)
		print (data, server)
		sock.close()
