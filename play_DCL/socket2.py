# Echo client program
import socket

def test1():
    HOST = '127.0.0.1'    # The remote host
    PORT = 50000              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    for i in range(0, 10):       
        s.sendall('Hello, world' + str(i))
        data = s.recv(1024)
        print 'Received', repr(data)
    
    s.close()
    
def test2():
    HOST = '127.0.0.1'    # The remote host
    PORT = 50001              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    for i in range(0, 10):       
        s.send('Hello, world' + str(i))
        data = s.recv(1024)
        print 'Received', repr(data)
    
    s.close()
    

def test3():
    HOST = '127.0.0.1'    # The remote host
    PORT = 50001              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    s.send('eval:sgfs/test.sgf')
    data = s.recv(1024)
    print 'Received', repr(data)
    
    s.close()
    


if __name__=="__main__":    
    test3()
    
    