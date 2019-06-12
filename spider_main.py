#coding:utf-8
from thread_pool import thread_pool
from collect_proxy import GetProxy, chekout_proxy
from spider_dbinfo import spiderDouban
from queue import Queue
import time
from threading import Thread
from minfo_save import csvHandler, mysqlHandler

gQuit = False

def getProxy():
    apiurl = 'http://www.66ip.cn/mo.php?sxb=&tqsl=200&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea='
    starturl ='http://www.66ip.cn'
    proxyhd = GetProxy(url = starturl)
    tpools = thread_pool(20)
    #proxyhd.start()
    proxyhd.getByApi(apiurl)
    ips = proxyhd.getIps()
    print (len(ips))
    for ip in ips:
        tpools.add_task(chekout_proxy, ip)
    tpools.start()
    tpools.join()
    rs = tpools.get_result()
    return rs

def task(*arg, **args):
    year = args['year']
    ipq = args['ipqueue']
    print (year, ipq)
    fcsv = csvHandler('%d.csv'%year)
    new_url = 'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=%s&start=%%s'%year
    spider = spiderDouban(new_url, ipq = ipq, savehd=fcsv)
    spider.start_download()

def startSpider(ipq):
    global gQuit
    tpools = thread_pool(2)
    for year in range(1970, 1972):
        tpools.add_task(task, year = year, ipqueue = ipq)
        
    tpools.start()
    tpools.join()
    gQuit = True

def getProxyFromWeb(ipqueue):
    print (ipqueue)
    ips = getProxy()
    print (len(ips))
    for ip in ips:
        ipqueue.put(ip)
    
if __name__ == '__main__':
    ipqueue = Queue()
    getProxyFromWeb(ipqueue)
    t = Thread(target=  startSpider, args=(ipqueue,))
    t.start()
    
    while gQuit == False:
        print ('gQuit:', gQuit)
        if ipqueue.qsize() < 20:
            getProxyFromWeb(ipqueue)
        time.sleep(2)
    
    
    
    
    
    
    
    
    
    
    
    
    