import socket as sk
import wave
import pyaudio
from threading import Thread
import errno, time

HOST = '127.0.0.1'
PORT = 5000
ADDR = (HOST, PORT)
CHUNK = 2048
p = pyaudio.PyAudio()
sound_of_silence = wave.open('sound-of-silence.wav', 'rb')
super_mario = wave.open('super-mario.wav', 'rb')
top_gear = wave.open('top-gear.wav', 'rb')
zodiac_opening = wave.open('zodiac-opening.wav','rb')
stream = p.open(format=pyaudio.paInt16,
         		channels = 2,
   	            rate = 44100,
       		    output = True,
       		    frames_per_buffer = CHUNK)


musics = [sound_of_silence, super_mario, top_gear, zodiac_opening]


clients = [[],[],[],[]]

stations = ['1 - sound_of_silence\n', '2 - super_mario\n', '3 - top_gear\n', '4 - zodiac_opening\n']

def wait_for_connections():
	s_sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
	s_sock.bind(ADDR)
	s_sock.listen(5)
	i = 0
	while i<6:
		print('\nwaiting for conections..', i, ' users connected.\n')
		c_sock, c_ADDR = s_sock.accept()
		c_sock.setblocking(False)
		print(c_ADDR, ' connected\n')
		menu_t = Thread(target=handshake, args=(c_sock, c_ADDR, s_sock))
		menu_t.start()
		i = i+1

def handshake(c_sock, c_ADDR, s_sock):
	hello = 0
	U_PORT = 0
	print('waiting hello')
	command = None
	t_U_PORT = None
	
	while command == None:
		try:
			command = c_sock.recv(1024).decode()
		except IOError as e:
			if e.errno == errno.EWOULDBLOCK:
				time.sleep(0.3)
				pass
	if command == '1':
		while t_U_PORT == None:	
			try:
				t_U_PORT = c_sock.recv(1024).decode()
			except IOError as e:
				if e.errno == errno.EWOULDBLOCK:
					time.sleep(0.3)
					pass
			
	print(command)
	if command == '1':
		hello = 1
		U_PORT = int(t_U_PORT)
		print('handshake did, UDP port: ', U_PORT)
		c_sock.send(str.encode('Welcome'))
		menu_response(c_sock, c_ADDR, s_sock, U_PORT)
	else:
		c_sock.send(str.encode('send hello first'))
		handshake(c_sock, c_ADDR, s_sock)

def streamUDP(music, n):
	u_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
	frames = music.readframes(CHUNK)
	stream.write(frames)
	
	while music != b'':
		time.sleep(0.046)
		for i in clients[n]:
			u_sock.sendto(frames, i)
		frames = music.readframes(CHUNK)
	streamUDP(music, n)

def menu_response(c_sock, c_ADDR, s_sock, U_PORT, prev_station = None):
	command = None
	
	print('waiting command..\n')
	while command == None:
		try:
			command = c_sock.recv(1024).decode()
		except IOError as e:
			if e.errno == errno.EWOULDBLOCK:
				time.sleep(0.3)
				pass
	print(command,'\n')
	if command == '1':
		c_sock.send(str.encode("can't say hello again\n"))
		menu_response(c_sock, c_ADDR, s_sock, U_PORT)
	elif command == '2':
		for word in range(len(stations)):
			c_sock.send(str.encode(stations[word]))
		menu_response(c_sock, c_ADDR, s_sock, U_PORT)
	elif command == '3':
		c_sock.send(str.encode("send the station number\n"))
		opt = None
		#receive option from client and handle the clients list.
		
		while opt == None:
			try:
				opt = c_sock.recv(1024).decode()
			except IOError as e:
				if e.errno == errno.EWOULDBLOCK:
					time.sleep(0.3)
					pass
		if int(command) == prev_station:
			c_sock.send(str.encode('aready playing\n'))
			menu_response(c_sock, c_ADDR, s_sock, U_PORT, prev_station)	
			
		if opt == '1':
			clients[int(opt)-1].append((HOST, U_PORT))
			c_sock.send(str.encode('announce\n'))
		elif opt == '2':
			clients[int(opt)-1].append((HOST, U_PORT))
			#prev_station = int(opt)-1
			c_sock.send(str.encode('announce\n'))
		elif opt == '3':
			clients[int(opt)-1].append((HOST, U_PORT))
			#prev_station = int(opt)-1
			c_sock.send(str.encode('announce\n'))
		elif opt == '4':
			clients[int(opt)-1].append((HOST, U_PORT))
			#prev_station = int(opt)-1	
			c_sock.send(str.encode('announce\n'))
		else:
			c_sock.send(str.encode('invalid option, select other radio!\n'))
		if prev_station != None:
			clients[prev_station].remove((HOST, U_PORT))
			prev_station = None
		prev_station = int(opt)-1
		#when while is done, back to menu_response again
		menu_response(c_sock, c_ADDR, s_sock, U_PORT, prev_station)	
		
	elif command == 'q':
		c_sock.send(str.encode('closing..\n'))
		c_sock.close()	
	else:
		c_sock.send(str.encode("invalid command..\n"))
		c_sock.close()
		#menu_response(c_sock, c_ADDR, s_sock, U_PORT)

main_t = Thread(target=wait_for_connections, args=())
main_t.start()

for i in range(4):
	u_t = Thread(target=streamUDP, args=(musics[i], i))
	u_t.start()

