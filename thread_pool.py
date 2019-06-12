import threading
from threading import Thread
from queue import Queue


class thread_pool(object):
    def __init__(self, num=5):
        self.qtask = Queue()
        self.qresult = Queue()
        self.tnum = num
        self.tlist = []
    def task(self):
        while True:
            try:
                func, args, kwargs = self.qtask.get(timeout=1)
                result = func(*args, **kwargs)
                if result:
                    self.qresult.put(result)
            except:
                print ('no task in poll')
                break
    def start(self):
        for i in range(self.tnum):
            t = Thread(target=self.task)
            self.tlist.append(t)
            t.start()

    def add_task(self, func, *args, **kwargs):
        self.qtask.put((func, args, kwargs))
    def join(self):
        for t in self.tlist:
            t.join()
    def get_result(self):
        rlist = []
        for i in range(self.qresult.qsize()):
            r = self.qresult.get()
            rlist.append(r)
        return rlist

def testfunc(num, **kwargs):
    print ('call test func', num, kwargs)
    return str(num)

if __name__ == '__main__':
    tpool = thread_pool(4)
    for i in range(40):
        tpool.add_task(testfunc, i)
    tpool.start()
    tpool.join()
    rs = tpool.get_result()
    for r in rs:
        print (r)


