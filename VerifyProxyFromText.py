from urllib import request
import fake_useragent
import re
from thread_pool import thread_pool

file = open('valid_proxy.txt', 'r')
con = file.read()
listip = con.split('\n')

print (listip)

def verifyIP(ip):    
    ip = {'https': ip}
    proxy = request.ProxyHandler(ip)
    opener = request.build_opener(proxy)
    url = 'https://ip.cn/'
    ua = fake_useragent.FakeUserAgent()
    headerinfo = {'User-Agent':ua.random}
    reqhd = request.Request(url, headers=headerinfo)
    try:
        req = opener.open(reqhd, timeout=5)
        #req = request.urlopen(reqhd)
        con = req.read().decode('utf-8')
        result = re.findall('<div class="well"><p>您现在的 IP：<code>(.*?)</code>',con)
        print ('valid ip:', "".join(result))
    except Exception as e:
        print ('invalid ip:', e, ip)

#多线程验证ip的可用性
# tpools = thread_pool(5)
# for ip in listip:
#     tpools.add_task(verifyIP, ip)
# tpools.start()   
# tpools.join()

for ip in listip:
    verifyIP(ip)
        

