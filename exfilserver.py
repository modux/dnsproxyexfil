from scapy.all import DNS, DNSQR, DNSRR, dnsqtypes
from socket import AF_INET, SOCK_DGRAM, socket
from traceback import print_exc
import base64
import json
from threading import Thread, Timer
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('0.0.0.0', 53))
config={"filename":" " , "receiving": 0, "writing": False, "domain":"notsetyet"}

buf = {}
f=None



def writebuffertofile():


        with open(config['filename'], 'wb') as file:

                for key, value in buf.iteritems():
                        value=base64.b32decode(value.upper())
                        file.write(value)
                file.close()
        print 'closing file'
        config['receiving'] = 0
        config['writing'] = False


def processrequest(request, addr, buf):

    try:
        dns = DNS(request)
        assert dns.opcode == 0

        ptype=''
        ip='1.1.1.1'
        if dns[DNSQR].qtype == 1:
                ptype = 'A'
        elif dns[DNSQR].qtype == 28:
                ptype='AAAA'
                ip='2a00:1450:4009:80f::200e'
        else:
                assert 1==2

        query = dns[DNSQR].qname.decode('ascii')  # test.1.2.3.4.example.com.

        response = DNS(
            id=dns[DNS].id,
            aa=1, #we are authoritative
            qr=1, #it's a response
            rd=dns[DNS].rd, # copy recursion-desired
            qdcount=dns[DNS].qdcount, # copy question-count
            qd=dns[DNS].qd, # copy question itself
            ancount=1, #we provide a single answer
            an=DNSRR(rrname=dns[DNS].qd.qname, type=ptype, ttl=1, rdata=str(ip) ))
        sock.sendto(bytes(response), addr)

        
        if 'startoffile' in query:
                head, config["domain"] = query.split('.2e0o2e.',1)
                ran = head.split('.', 1)[0]

                print "receiving file to subdomain" + config["domain"]
                
                if config['receiving'] != 0:
                        return
                config['receiving'] = ran
                ran, count, config['filename'] = head.split('.',2) # drop leading "prefix." part
                print 'creating file ' + config['filename']


                buf = {}
                
        assert config["domain"] in query
        
        head = query.rsplit(config["domain"], 1)[0]

        ran = head.split('.', 1)[0]
        head = head.split('.', 1)[-1] #remove random bytes
        count = head.split('.', 1)[0]
        head = head.split('.', 1)[-1] # remove random leading bytes
        head=head.replace('.','')
        # remove random leading bits

        if 'endoffile' in query:

                if config['receiving'] != ran:

                        return
                if config['writing'] == True:
                        return
                print 'attempting to write file'

                config['writing'] = True
                print "waiting 20 seconds to collect lost dns queries"

                r = Timer(20.0, writebuffertofile)
                r.start()
        
        if config['receiving'] == ran:


                head=head.replace('-', '=')
                buf[int(count)]=head

#       print head

    except Exception as e:
        print e
        print('')
        print_exc()
#        print('garbage from {!r}? data {!r}'.format(addr, request))


while True:
    request, addr = sock.recvfrom(4096)
    t= Thread(target=processrequest, args=(request, addr, buf))
    t.start()
