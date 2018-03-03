#coding=utf-8

from gevent import monkey; monkey.patch_os()
from gevent.server import StreamServer
from multiprocessing import Process

def eat_cpu():
    for i in xrange(10000): pass

def cb(socket, address):
    eat_cpu()
    socket.recv(1024)
    socket.sendall('HTTP/1.1 200 OK\n\nHello World!!')
    socket.close()

server = StreamServer(('',1080), cb, backlog=100000)
server.init_socket()

def serve_forever():
    server.start_accepting()
    # server._stop_event.wait()

process_count = 4

for i in range(process_count - 1):
    Process(target=serve_forever, args=tuple()).start()

serve_forever()