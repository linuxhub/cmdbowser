# coding=utf-8


import sys
import os
import socket
import re


def getStrVal(s):
    return s.replace('\r', '') if s else ''


def showLine():
    print '------------------------------------------------------------'


def parseURL(url):
    req = {}
    pattern = re.compile('^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$')
    res = pattern.match(url)
    if not res:
        return False
    req['SCHEME'] = getStrVal(res.groups()[0])
    req['SLASH']  = getStrVal(res.groups()[1])
    req['HOST']   = getStrVal(res.groups()[2])
    req['PORT']   = int(res.groups()[3]) if res.groups()[3] else 80
    req['PATH']   = '/' + getStrVal(res.groups()[4])
    req['QUERY']  = getStrVal(res.groups()[5])
    req['HASH']   = getStrVal(res.groups()[6])

    try:
        req['IP'] = socket.gethostbyname(req['HOST'])
    except socket.error, e:
        print '传输错误....%s' % e
        exit()

    return req


def parseResponseHeaders(data):
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


def app(req):
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print '成功创建socket... '
    except socket.error, e:
        print '创建socket失败，退出程序... %s' % e
        exit()

    try:
        soc.connect((req['IP'], req['PORT']))
        print '成功连接到远程服务器：http://%s:%d' % (req['IP'], req['PORT'])
    except socket.error, e:
        print '无法连接至远程服务器，退出程序...\nERROR: %s' % e
        soc.close()
        exit()

    print '正在解析响应的头信息数据....'
    try:
        s = 'GET ' + req['PATH'] + ' HTTP/1.1\r\n'
        s += 'Host: ' + req['HOST'] + '\r\n'
        s += 'Connection: keep-alive\r\n\r\n'
        s += 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36\r\n'
        s += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n'
        s += 'Accept-Encoding: gzip,deflate,sdch\r\n'
        s += 'DNT: 1\r\n'
        s += 'Accept-Language: zh-CN,zh;q=0.8,cs;q=0.6,en;q=0.2\r\n'
        s += 'Cache-Control: max-age=0\r\n\r\n'
        s += req['QUERY']
        soc.send(s)
    except socket.error, e:
        print 'Request error ... %s' % e
        soc.close()

    data = soc.recv(1024)
    headers = parseResponseHeaders(data)

    if not headers:
        print '远程WEB服务器响应格式错误...exit!'
        soc.close()
        exit()
    sc = int(headers["Status-Code"])
    if sc >= 300 and sc < 400:
        showLine()
        displayDict(headers)
        showLine()
        print "完成请求，需重定向至%s" % headers["Location"]
        return headers["Location"]

    s = data.find('\r\n\r\n', 0, len(data)) + 4
    # Content-Length
    if 'Content-Length' in headers.keys():
        e = long(headers['Content-Length']) + long(len(data[0: s]))
        while True:
            if len(data) >= e:
                break
            data += soc.recv(1024)
    # Transfer-Encoding
    elif 'Transfer-Encoding' in headers.keys():
        while True:
            recv = soc.recv(1024)
            if len(recv) == 0:
                break
            data += recv
        e = data.find('\r\n0\r\n', 0, len(data))
    html = data[s: e]
    soc.close()

    showLine()
    raw_input('恭喜，操作成功！按Enter键查看头信息...')
    displayDict(headers)
    showLine()
    raw_input('继续按Enter键查看下载的网页数据...')
    print html

    return False


if __name__=='__main__':

    if len(sys.argv) < 2:
        print "无域名，命令Demo：python app.py meituan.com"
        exit()

    os.system('clear')
    showLine()
    # 限制重定向的次数最多为5次
    count = 5
    req = parseURL(sys.argv[1])
    while True:
        reURL = app(req)
        if reURL and count:
            count -= 1
            raw_input('敲Enter键，进行重定向操作...')
            os.system('clear')
            req = parseURL(reURL)
        else:
            break

    showLine()
    raw_input('Done! 完成操作...按Enter键退出程序...')







