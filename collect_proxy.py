#coding:utf-8
from urllib import request
from fake_useragent import FakeUserAgent
from bs4 import BeautifulSoup
import re
import time
from thread_pool import thread_pool

def chekout_proxy(ip):
    ip = {'http': ip}
    proxy = request.ProxyHandler(ip)
    opener = request.build_opener(proxy)
    ua = FakeUserAgent()
    url = 'http://www.baidu.com'
    headinfo = {'User-Agent': ua.random}
    reqhd = request.Request(url, headers=headinfo)
    try:
        req = opener.open(reqhd, timeout=5)
    except Exception as e:
        print ('invalid ip:', ip, e)
        return
    if req.code == 200:
        return ip

class GetProxy(object):
    def __init__(self, url = ''):
        self.baseurl = url
        self.ua = FakeUserAgent()
        self.pools = []
    def getIps(self):
        return self.pools
    def getByApi(self, url):
        content = self.reqPage(url)
        if content:
            obj = BeautifulSoup(content, 'html5lib')
            listip = [item for item in obj.stripped_strings if re.match(r'\d', item)]
            self.pools.extend(listip)


    def getCharset(self, content):
        scon = str(content)
        meta = re.search(r'<meta(.*?)content-type(.*?)>', scon, re.I)
        if meta:
            s = meta.group()
            m = re.search(r'charset=(.*?)[\"\' /]', s, re.I)
            if m:
                charset = m.groups()[0]
                return charset
        return 'utf-8'

    def reqPage(self, url):
        time.sleep(2)
        headinfo = {'UserAgent': self.ua.random}
        reqhd = request.Request(url, headers=headinfo)
        try:
            req = request.urlopen(reqhd)
        except Exception as e:
            print ('Error:', e)
        if req.code != 200:
            return
        con = req.read()
        charset = self.getCharset(con)
        print (charset)
        try:
            con = con.decode(charset)
        except Exception as e:
            print ('decode Error:', e)
            return
        return con

    def parsePage(self, url):
        con = self.reqPage(url)
        obj = BeautifulSoup(con, 'html5lib')
        div = obj.find('div', class_="containerbox boxindex")
        tbody = div.find('tbody')
        listtr = tbody.find_all('tr')
        for tr in listtr[1:]:
            tds = list(tr.stripped_strings)
            ip = ':'.join(tds[:2])
            print (ip)
            self.pools.append(ip)

    def parseArea(self, url):
        print (url)
        con = self.reqPage(url)
        obj = BeautifulSoup(con, 'html5lib')
        listpage = obj.find('div', id="PageList")
        lista = listpage.find_all('a')
        for a in lista[:6]:
            step = a.get('href')
            if step.endswith('/index'):
                step = step.replace('/index', '/1.html')
            self.parsePage(self.baseurl+step)


    def start(self):
        con = self.reqPage(self.baseurl)
        obj = BeautifulSoup(con, 'html5lib')
        areas = obj.find('ul', class_="textlarge22")
        if areas:
            lista = areas.find_all('a')
            if lista:
                lista = lista[1:]
                for a in lista:
                    step = a.get('href')
                    if step:
                        self.parseArea(self.baseurl + step)

if __name__ == '__main__':
    apiurl = 'http://www.66ip.cn/mo.php?sxb=&tqsl=2000&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea='
    starturl ='http://www.66ip.cn'
    proxyhd = GetProxy(url = starturl)
    tpools = thread_pool(50)
    #proxyhd.start()
    proxyhd.getByApi(apiurl)
    ips = proxyhd.getIps()
    print (len(ips))
    validips = []
    for ip in ips:
        tpools.add_task(chekout_proxy, ip)
    stime = time.time()
    tpools.start()
    tpools.join()
    etime = time.time()
    rs = tpools.get_result()
    print ('valid ips:',len(rs))
    for ip in rs:
        print (ip)
    print (stime, etime)

