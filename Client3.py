import socket as sk
import pyaudio
from threading import Thread
import wave, time, os, sys

CHUNK = 8192
HOST = '127.0.0.1'
PORT = 5000
ADDR = (HOST, PORT)
alive = True

p = pyaudio.PyAudio()
u_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
u_sock.bind(('127.0.0.1', int(sys.argv[1])))
stream = p.open(format=pyaudio.paInt16,
         		channels = 2,
   	            rate = 44100,
       		    output = True,
       		    frames_per_buffer = CHUNK)
		
def make_connection():
	c_sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
	c_sock.connect(ADDR)
	menu(c_sock)
	
def menu(c_sock, handshake = False):
	print('\n---------choose an option: --------\n')
	print('Option 1: send hello\n')
	print('Option 2: list stations\n')
	print('Option 3: choose a station\n')
	print('Option q: quit\n')
	command = input()
	c_sock.send(str.encode(command))
	time.sleep(0.5)	
	if command == '1' and not handshake:
		c_sock.send(str.encode(sys.argv[1]))
		handshake = True
	
	msg = c_sock.recv(1024).decode()
	print(msg)
	
	if command == '3' and handshake:
		udp_menu(c_sock)	
	if command == 'q':
		print('ending...\n')
		alive = False
		c_sock.close()
		stream.close()
		u_sock.close()
		
	else: 
		menu(c_sock, handshake)

def udp_menu(c_sock):
	sel = input()
	c_sock.send(str.encode(sel))
	msg = c_sock.recv(1024).decode()
	print(msg)
	
def play(u_sock):
	ms = u_sock.recv(CHUNK)
	while True and alive:
		stream.write(ms)	
		ms = u_sock.recv(CHUNK)
	stream.close()
	u_sock.close()

mt = Thread(target=make_connection, args=())
mt.start()
udp_t = Thread(target=play, args=(u_sock,))
udp_t.start()
