import time,random

from rtp_engine import *

class sip_handler ():
	'''
	__init__()
	rückgabe ist nichts
	es wird das einkommende packet zerlegt und verwertet. 

	rand_tag()
	erzeutg eine 40 stellige Random ID 

	call_reakt()
	gibt den nächsten step für das Answer/offer aus

	call_setter()
	Es wird gesezt das der Call neu ist und alle start Parameter werden getzt 

	add_sdp()
	ein neu Generites sdp wird in speicher geladen und die Grösse berechnee 

	offer()
	From und To sind nun getauscht und es kann auch die die C-Seq anders sein. 

	answer()
	hier wird mit dem gleichen From und To Werten geantwortet wie auch C-seq
	
	rip_off_tag()
	durch suchd das tail von From und To nach einem Tag 

	rip_off_data()
	Zerlegt die das From oder To 
	name 
	Uri 
	Tail *alle deten nach dem >


	get_sdp()
	gibt den SDP von der Messege aus als Byte wert 

	get_header()
	Gibt inhalt vom Header wieder

	get_tag()
	es gibt den Tag 
	von To oder From wieder

	get_all()
	gibt den kompletten speicher von der klasse aus
	'''


	def rand_tag(self)->str:
		i =0
		ret = ''
		while i <41:
			z = random.randint(0, 2)
			if z == 0:
				ret = ret + chr(random.randint(97, 122))
			elif z == 1:
				ret = ret + chr(random.randint(65, 90))
			else:
				ret = ret + chr(random.randint(48, 57))

			i += 1
		return ret
			

	def __init__(self,packet:str,ip_own:str,ip_sender:str)-> None:
		'''
		in dieser klasse wir der komplette call gehandelt. 

		es wird nach einer matrix vorgangen 
		self.status 

		desweitern in der self.options 
		dort werden die Header für die antworten fest gelegt und können angepassst werden 



		
		runtime infos: 
		rtp_run = start/etablisht/kill #set up RTP and get SDP
		rtp_media = start/running/stop #play media
		sdp_send = offer/answer #selekt to send SDP
		call_status = ini/pre/eta/end/kill 
		ini = nicht beantwortet #first message / not found in ram
		pre = 180/183 # ringing/session proghress
		eta = 200 OK #Call is etablishd
		end = bye #BYE Sendet /watinng for ACK on the BYE 
 		kill = wait of Delete

		answer = see Options
		'''
		
		self.funk_matrix = {
				'INVITE':0,
				'ACK':1,
				'BYE':2,
				'CANCEL':3,
				'OPTIONS':4

		}
		#['send message','rtp_run','rtp_media','new_call_status','end_message']
		self.status = {
			'ini':[['200','start','start','eta','BYE'],['','','','',''],['','','','',''],['','','','',''],['200_o','','','kill','']],
			'pre':[['200','','start','eta','486'],['','','','',''],['','','','',''],['200_o','stop','stop','kill',''],['','','','','']],
			'eta':[['200','','start','eta','BYE'],['','','','',''],['200_o','stop','stop','kill',''],['','','','',''],['','','','','']],
			'end':[['','','','kill',''],['','','','',''],['','','','',''],['','','','',''],['','','','','']],
			'kill':[['','','','',''],['','','','',''],['','','','',''],['','','','',''],['','','','','']],

		}
		self.options = {
			'200':{'value':'OK','sdp':1,'header_ip':0,'list':['From','To','Call-ID','CSeq','Max-Forwards','Content-Length','Supported','Contact','Content-Type','Session-Expires','Session-ID','User-Agent','Record-Route','Via']},
			'100':{'value':'Giving a try','sdp':0,'header_ip':0,'list':['To','From','Record-Route','Via','Call-ID','CSeq','Server','Content-Length','Contact'],'Content-Length':'0'},
			'180':{'value':'Ringing','sdp':0,'header_ip':0,'list':['From','To','CSeq','Allow','Call-ID','Record-Route','Via','Contact','Content-Length'],'Content-Length':'0'},
			'183':{'value':'Session Progress','sdp':1,'header_ip':0,'list':['From','To','Call-ID','CSeq','Max-Forwards','Content-Length','Supported','Contact','Content-Type','Session-Expires','Session-ID','User-Agent','Record-Route','Via']},
			'486':{'value':'Busy Here','sdp':0,'header_ip':0,'list':['To','From','Call-ID','CSeq','Server','Record-Route','Via','Content-Length','Contact'],'Content-Length':'0'},
			'487':{'value':'Request Terminated','sdp':0,'header_ip':0,'list':['To','From','Call-ID','CSeq','Server','Record-Route','Via','Content-Length','Contact'],'Content-Length':'0'},
			'CANCEL':{'value':'','sdp':0,'header_ip':1,'list':['From','To','Call-ID','CSeq','Max-Forwards','Route','Record-Route','Via','Allow','Content-Length','Contact'],'Content-Length':'0'},
			'BYE':{'value':'','sdp':0,'header_ip':1,'list':['From','To','Record-Route','Via','Call-ID','CSeq','Max-Forwards','Content-Length','Reason'],'Content-Length':'0'},
			'ACK':{'value':'','sdp':0,'header_ip':1,'list':['From','To','Record-Route','Via','Call-ID','CSeq','Max-Forwards','Content-Length','Reason'],'Content-Length':'0'},
			'200_o':{'value':'200 OK','header_ip':0,'sdp':0,'list':['From','To','Call-ID','CSeq','Supported','Contact','Content-Type','Session-Expires','Session-ID','User-Agent','Record-Route','Via','Content-Length'],'Content-Length':'0'},
			
		}

		self.data = {}
		self.data['sdp'] = ''
		self.data['ip_own'] = ip_own
		self.data['ip_sender'] = ip_sender
		self.count = {}
		self.count['via'] =  0
		self.count['rr'] = 0
		self.data['detail'] = {}
		self.sdp = {}
		
		try:
			a =packet.decode("utf-8")
		except:
			print (error)
			exit('eroor')
		line = 0
		sdp = 0
		first_sdp = 0
		via = 0
		rr = 0
		for x in a.split('\r\n'):
			set = 0
			if x == '':#wenn eine Leer zeile gefunden wurde, beginnt das SDP 
				sdp = 1
			if line == 0:
				name = ''
				value =''
				jump = 0
				for xi in  x:
					if jump == 0:
						if xi == ' ':
							self.data['typ'] = name 
							self.data['head'] = ''
							jump = 1
						else:
							name = name + xi
					else:
						self.data['head'] = self.data['head'] + xi
			else:		
				if sdp == 0:
					
					i = x.split(': ')

					if i[0] == 'To':
						a = self.rip_off_tag(i[1])
						new_to = a['front'] + ';tag=' +a['tag'] + a['more']
						self.rip_off_data (i[0],new_to)
						self.data[i[0]] = new_to
						set = 1
					if i[0] == 'From':
						self.rip_off_data (i[0],i[1])
						set = 0
					
					if i[0] == 'Max-Forwards':
						self.data[i[0]] = str(int(i[1]) - 1)
						set = 1
					
					if i[0] == 'Contact':
						print ('hier ist contact', '<sip:'+ip_own[0] + ':' + str(ip_own[1]) + '>')
						self.data[i[0]] = '<sip:'+ip_own[0] + ':' + str(ip_own[1]) + '>'
						self.data['header_sip_ip'] = 'sip:'+ip_own[0] 
						self.data['header_sip_ipport'] = 'sip:'+ip_own[0] +':'+ str(ip_own[1])
						set = 1

					if i[0] == 'Via':
						self.data[i[0]+'_'+str(via)] = i[1]
						via += 1
						self.count['via'] += 1 
						set = 1
					
					if i[0] == 'Record-Route':
						self.data[i[0]+'_'+str(rr)] = i[1]
						rr += 1
						self.count['rr'] += 1 
						set = 1
					if set == 0:#alle andern Header 
						self.data[i[0]] = i[1]

				else:#hier wird nur der SDP ausgewertet
					if x != '':
						if first_sdp == 1:
							self.data['sdp'] = self.data['sdp'] + '\r\n'
						self.data['sdp'] = self.data['sdp'] + x
						first_sdp = 1


			line +=1 

		pass
	
	def call_reakt (self,old):
		print ('getter')
		print ('old: ',old,'typ: ',self.data['typ'])
		print(self.status[old][self.funk_matrix[self.data['typ']]])
		ret = self.status[old][self.funk_matrix[self.data['typ']]]
		return ret


	def call_setter (self):
		print ('setter',self.data['typ'])
		print(self.status['ini'][self.funk_matrix[self.data['typ']]])
		ret = self.status['ini'][self.funk_matrix[self.data['typ']]]


		
		'''
		sdp_run = start/etablisht/kill
		sdp_media = start/running/stop
		sdp_send = offer/answer
		call_status = ini/pre/eta/end/kill 
		ini = nicht beantwortet 
		pre = 180/183
		eta = 200 OK
		end = bye
		kill = wait of Delete

		answer = see Options



		'''
		return ret
		#pass

	def add_sdp(self,sdp,target,name):
		if str(type(sdp)) == "<class 'dict'>":
			print ('yaea es ist ein dikt')
			self.sdp[name] = sdp 
			self.options[target]['Content-Length'] = sdp['len']
		else:
			c = sdp.decode('utf8')
			length = 0
			for x in c.split('\n\r'):
				length += len(x)
			
			self.sdp[name] = {'len':length,'sdp':sdp} 
			self.options[target]['Content-Length'] = length

	def offer (self,value:str) -> bytes:

		if value == '200_o':
			ret = 'SIP/2.0'+' '+self.options[value]['value'] +'\r\n'
		else:
			
			if self.options[value]['header_ip'] == 0:
				ret = 'SIP/2.0'+' '+value +' '+self.options[value]['value'] +'\r\n'
			else:
				ret =  value +' sip:'  + self.data['ip_sender'][0] + ':' + str(self.data['ip_sender'][1])  + ' SIP/2.0\r\n'
		add_rn = False
		via = 0
		rr = 0
		for x in  self.options[value]['list']:
			run_standart = True
			if add_rn:
				ret = ret + '\r\n'
				add_rn = False
				
			if x == 'To':
				
				self.data['detail']['To']['tail']
				self.data['detail']['To']['uri']
				s1 = self.data['detail']['To']['uri'].split('@')
				print  (len(s1))
				
				if len(s1) == 1:
					s2 = s1[0].split(';')
					ret = ret + 'From: <sip:'  + self.data['ip_own'][0] + ':' + str(self.data['ip_own'][1]) + '>' + self.data['detail']['To']['tail']
				else: 
					s2 = s1[1].split(';')
					ret = ret + 'From: <sip:' + s1[0] + '@' + self.data['ip_own'][0] + ':' + str(self.data['ip_own'][1]) + '>' + self.data['detail']['To']['tail']
				self.data['ip_own']


				
								
				add_rn = True
				run_standart = False

			if x == 'CSeq':

				if value == 'BYE':
					ret = ret + x + ':  1 BYE'
				elif value == 'CANCEL':
					ret = ret + x + ':  1 CANCEL'
				else:
					ret = ret + x + ': ' + self.data[x]

				add_rn = True
				run_standart = False

			if x == 'From':
				ret = ret + 'To: ' + self.data['From'] 

				add_rn = True
				run_standart = False
				
			
			if self.count['via'] != 0 and x == 'Via':
				ret = ret + 'Via: SIP/2.0/UDP '  + self.data['ip_own'][0] + ':5060;rport \r\n'
				
					#via += 1 

				add_rn = False
				run_standart = False
			
			if self.count['rr'] != 0 and x == 'Record-Route':
				while self.count['rr'] > rr:
					ret = ret + x + ': ' + self.data['Record-Route_'+str(rr)]
					rr += 1 

				add_rn = True
				run_standart = False

			if x in self.data:

				if x == 'Content-Length':
					if x in self.options[value]:
						ret = ret + x + ': '+ str(self.options[value]['Content-Length'])
						add_rn = True
						run_standart = False
				

				if run_standart:
					ret = ret + x + ': ' + self.data[x]
					add_rn = True

			ret2 = ret.encode("utf-8")
			if add_rn:
				ret2 = ret2 + b'\r\n'

			if self.options[value]['sdp'] == 1:
				ret2 = ret2 + b'\r\n' +  self.sdp['answer']['sdp']
		

		ret2 = ret2 + b'Reason: Q.850;cause=16;text="Normal call clearing"\r\n'
		ret2 = ret2 + b'\r\n'
		return ret2


	def answer (self,value:str) -> bytes:
		

		if value == '200_o':
			ret = 'SIP/2.0'+' '+self.options[value]['value'] +'\r\n'
		else:
			
			if self.options[value]['header_ip'] == 0:
				ret = 'SIP/2.0'+' '+value +' '+self.options[value]['value'] +'\r\n'
			else:
				ret = 'SIP/2.0'+' '+value +' '+ self.get_header('header_sip_ip')  +' hier \r\n'
		add_rn = False
		via = 0
		rr = 0
		for x in  self.options[value]['list']:
			run_standart = True
			if add_rn:
				ret = ret + '\r\n'
				add_rn = False
				

			if self.count['via'] != 0 and x == 'Via':
				while self.count['via'] > via:
					ret = ret + x + ': ' + self.data['Via_'+str(via)] + '\r\n'
					via += 1 

				add_rn = False
				run_standart = False
			
			if self.count['rr'] != 0 and x == 'Record-Route':
				while self.count['rr'] > rr:
					ret = ret + x + ': ' + self.data['Record-Route_'+str(rr)] + '\r\n'
					rr += 1 

				add_rn = False
				run_standart = False

			if x in self.data:

				if x == 'Content-Length':
					if x in self.options[value]:
						ret = ret + x + ': '+ str(self.options[value]['Content-Length']) + '\r\n'
						add_rn = False
						run_standart = False

				if run_standart:
					ret = ret + x + ': ' + self.data[x]
					add_rn = True

			ret2 = ret.encode("utf-8")
			if self.options[value]['sdp'] == 1:
				ret2 = ret2 + b'\r\n' +  self.sdp['answer']['sdp']

		return ret2

	def rip_off_tag(self,value:str)-> dict:
		print (value)
		tag = ''
		end = ''
		f = value.split(">")
		for x in f[1].split(';'):
			if x != '':
				n = x.split('=')
				if n[0] == 'tag':
					tag = n[1]
				else:
					end = end + ';'	+ n[0] + '=' + n[1] 
		if tag == '':
			tag = str(self.rand_tag()) 
		
		if end == ';':
			end = ''

		return {'tag':tag,'more':end,'front':f[0]+'>'}


	def rip_off_data(self,name:str,value:str)-> None:
		self.data['detail'][name] = {}
		f = value.split(">")
		self.data['detail'][name]['tail'] = f[1]

		fi = f[0].split('<')
		uri = fi[1][4:]
		self.data['detail'][name]['uri'] = uri

		fii = fi[0].split('\"')

		if len(fii) >2:
			self.data['detail'][name]['name'] = fii[1]

	def get_sdp(self) -> bytes:
		return self.data['sdp']

	def get_header(self,header):
		try:
			ret = self.data[header]
		except:
			return 'error'
		
		return ret
	
	def get_tag(self,target): #From oder To
		i = self.data['detail'][target]['tail'].split(';')

		for x in i:
			xi =  x.split('=')
			if xi[0] == 'tag':
				ret = xi[1]
		
		return ret


	def get_all(self):
		return self.data
