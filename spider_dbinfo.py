# coding:utf-8
from urllib import request
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent
import json

from minfo_save import csvHandler, mysqlHandler

#base_url = 'https://movie.douban.com/tag/2010'
new_url = 'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=2010&start=%s'

class spiderDouban(object):
    def __init__(self, url=None, ipq=None, savehd=None):
        self.starturl = url
        self.infohd = savehd
        self.ua = FakeUserAgent()
        self.ipqueue = ipq
        self.ips = []
        self.opener = None
        self.reqnum = 0
        self.iterips = None
        self.curip = None
    
    def getipfrom_ips(self):
        if self.ipqueue:
                while len(self.ips) < 10:
                    try:
                        ip = self.ipqueue.get(timeout=1)
                        self.ips.append(ip)
                    except:
                        print ('no proxy ip')
                        break
    
    def start_download(self):
        for a in range(0,1000,20):
            url = self.starturl
            self.getipfrom_ips()
                
            if url:
                url = url%a
                print('pageurl:', url)
                self.load_page(url)
        for ip in self.ips:
            self.ipqueue.put(ip)
                
    
    def get_proxyip(self):
        if self.iterips == None:
            self.iterips = iter(self.ips)
        try:
            ip = next(self.iterips)
            return ip
        except:
            if self.ips:
                self.getipfrom_ips()
                self.iterips = iter(self.ips)
                ip = next(self.iterips)
                return ip
            
    def change_proxy(self):
        ip = self.get_proxyip()
        if ip:
            proxyhd = request.ProxyHandler(ip)
            self.opener = request.build_opener(proxyhd)
            self.curip = ip
            return True
        return False

    def req_page(self, url):
        req = None
        if self.reqnum % 10 == 0:
            self.change_proxy()
        while True:
            try:
                headinfo = {'User-Agent':self.ua.random}
                reqhd = request.Request(url, headers=headinfo)
                #time.sleep(2)
                req = self.opener.open(reqhd)
                self.reqnum += 1
                break
            except Exception as e:
                print('catch e:', e)
                self.ips.remove(self.curip)
                self.curip = None
                if not self.change_proxy():
                    return None
        

        if req.code != 200:
            return
        pageinfo = req.read().decode('utf-8')
        return pageinfo

    def parse_text(self, minfo):
        # listt = minfo.split('\n')
        print(minfo)
        listt = [item.strip() for item in minfo.split('\n') if item.strip(' ')]
        listt = [item.split(':', 1) for item in listt]
        listt = [items for items in listt if len(items) == 2 and items[0].strip() and items[1].strip()]
        print(listt)
        dinfo = dict(listt)

        return dinfo

    def parse_minfo(self, url, mname):
        pinfo = self.req_page(url)
        if not pinfo:
            return
        obj = BeautifulSoup(pinfo, 'html5lib')
        minfo = obj.find('div', id='info')
        tinfo = minfo.get_text()
        dinfo = self.parse_text(tinfo)
        mscore = obj.find('div', class_='rating_self clearfix')
        score = mscore.find(property="v:average").get_text()
        votes = mscore.find(property="v:votes").get_text()
        dinfo['score'] = score
        dinfo['votes'] = votes
        dinfo['name'] = mname
        print(dinfo.keys())
        for item in dinfo.items():
            print(item)
        return dinfo


    def load_page(self, url):
        pinfo = self.req_page(url)
        if not pinfo:
            return
        
        print (self.curip)
        
        jsonStr = json.loads(pinfo) 
        for i in jsonStr['data']:
            murl = i['url']
            mname = i['title']
            print (murl, mname)
            minfo = self.parse_minfo(murl, mname)
            if minfo and self.infohd:
                keys = ['name', '导演', '主演', '类型', '制片国家/地区',
                        '语言', '上映日期', '片长', '又名',
                        'score', 'votes']
                self.infohd.write(keys, minfo)
            #break
        


    def load_img(self, info):
        imgreq = request.urlopen(info[1])
        img_c = imgreq.read()
        imgf = open('E:\\test\\' + info[0] + '.jpg', 'wb')
        imgf.write(img_c)
        imgf.close()


# fcsv = csvHandler('minfo.csv')
#sql = mysqlHandler('localhost', 'root', 'abcd1234', 'test_db1', 'mvinfo')
if __name__ == '__main__':
    spider = spiderDouban(new_url, ipq=None, savehd=None)
    spider.start_download()
# fcsv.close()









