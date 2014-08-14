import socket

DOMAIN_NAME = 'bj.meituan.com'
DOMAIN_NAME = 'google.com'
HOST = socket.gethostbyname(DOMAIN_NAME)
PORT = 80

if __name__=='__main__':
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, e:
         print 'socket false %s' % e

    try:
        soc.connect((HOST, PORT))
    except socket.error, e:
        print 'connect error %s' % e
        soc.close()

    try:
        headers = 'GET / HTTP/1.1\r\nHost:' + DOMAIN_NAME
        headers +=  '\r\nConnection:keep-alive\r\n\r\n'
        headers += 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36\r\n'
        headers += 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n'
        headers += 'Accept-Encoding:gzip,deflate,sdch\r\n'
        headers += 'Accept-Language:zh-CN,zh;q=0.8,cs;q=0.6,en;q=0.4,zh-TW;q=0.2\r\n'
        headers += 'Cache-Control:max-age=0\r\n'
        soc.send(headers)
    except socket.error, e:
        print 'Request error ... %s' % e
        soc.close()

    data = soc.recv(1024)
    print data
    # Content-Length
    s = data.find('Content-Length:', 0, len(data))
    e = data.find('Connection', 0, len(data))
    html_idx = data.find('\r\n\r\n', 0, len(data)) + 4
    if s == -1 or e == -1 or s == e or html_idx == 3:
        while True:
            recv = soc.recv(1024)
            if recv == '0' or len(recv) == 0:
                break
            data += recv
        print data
        idx = data.find('\r\n0\r\n', 0, len(data))
        print idx
        exit()

    # Transfer-Encoding
    data_len = long(data[s + 16: e - 2]) + long(len(data[0: html_idx]))
    print data_len
    while True:
        if len(data) >= data_len:
            break
        data += soc.recv(1024)
    print data
    soc.close()









