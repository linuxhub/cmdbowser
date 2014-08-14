# coding=utf-8

import socket
import re

#DOMAIN_NAME = 'meituan.com'
#DOMAIN_NAME = 'www.meituan.com'
DOMAIN_NAME = 'bj.meituan.com'
#DOMAIN_NAME = 'www.google.com'
HOST = socket.gethostbyname(DOMAIN_NAME)
PORT = 80

def parsResponseHeaders(data):
    spl = re.split("\r\n(.+:\ .+)\r\n", data)
    headers = {}
    if spl:
        for val in spl:
            res = re.match("(.+): (.+)", val)
            if res:
                headers[res.groups()[0]] = res.groups()[1]
        headers['Status-Code'] = getStatusCode(spl[0])
        return headers
    return False

def getStatusCode(data):
    res = re.match("^HTTP/1.1\ (\d+)\ ", data)
    if res:
        return res.groups()[0]
    return False

def displayDict(d):
    if d:
        for (key,value) in d.items():
            print '%s: %s' % (key, value)


if __name__=='__main__':
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, e:
         print 'Socket error`` %s' % e

    try:
        soc.connect((HOST, PORT))
    except socket.error, e:
        print 'Connect error %s' % e
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
    headers = parsResponseHeaders(data)
    print headers
    displayDict(headers)
    if not headers:
        print '远程WEB服务器响应格式错误...exit!'
        exit()
    sc = int(headers["Status-Code"])
    if sc >= 300 and sc < 400:
        print "完成请求，需重定向至%s" % headers["Location"]
        exit()

    # Content-Length
    if 'Content-Length' in headers.keys():
        print headers['Content-Length']
        html_idx = data.find('\r\n\r\n', 0, len(data)) + 4
        data_len = long(headers['Content-Length']) + long(len(data[0: html_idx]))
        while True:
            if len(data) >= data_len:
                break
            data += soc.recv(1024)
    elif 'Transfer-Encoding' in headers.keys():
        while True:
            recv = soc.recv(1024)
            if len(recv) == 0:
                break
            data += recv
    print data
    soc.close()









