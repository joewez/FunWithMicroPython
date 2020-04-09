# Utilities for working with the network
# Author: Joseph G. Wezensky
# License: MIT License (https://opensource.org/licenses/MIT)
import socket
import os

def get(url, filespec, silent=True):

    tempFilename = 'tmp.txt'

    # save text contents
    f = open(tempFilename, 'wb')
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            f.write(data)
        else:
            break
    s.close()
    f.close()

    line_count = 0

    # remove header info
    f = open(tempFilename, 'r')
    o = open(filespec, 'w')
    in_content = False
    for line in f:
        if in_content:
            o.write(line)
            line_count += 1
            if not silent:
                print(line, end='')
        else:
            if line == '\r\n':
                in_content = True
    o.close()
    f.close()

    os.remove(tempFilename)

    if not silent:
        print('{0} lines read.'.format(line_count))