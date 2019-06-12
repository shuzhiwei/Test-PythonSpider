#coding:utf-8
import csv
import pymysql

class csvHandler(object):
    def __init__(self, path):
        print ('path:', path)
        self.f = open(path, 'w', encoding='utf-8')
        self.fw = csv.writer(self.f)
        self.head = False
    def write(self, keys, info):
        rowinfo = [info.get(key, ' ') for key in keys]
        print (rowinfo)
        if self.head:
            self.fw.writerow(rowinfo)
        else:
            self.fw.writerow(keys)
            self.fw.writerow(rowinfo)
            self.head = True
    def close(self):
        self.f.close()


class mysqlHandler(object):
    def __init__(self, host='localhost', user='root', passwd='', dbname='', tbname=''):
        self.dbcon = pymysql.connect(host, user, passwd, dbname, charset='utf8')
        self.cur = self.dbcon.cursor()
        self.tname = tbname
        self.id = 1
    def write(self, keys, info):
        sql = 'insert into %s values'%self.tname
        values = '(%s)'%(('%s,'*(len(keys)+1))[:-1])
        sql += values
        rowinfo = [info.get(key, ' ') for key in keys]
        rowinfo.insert(0, self.id)
        self.id += 1
        self.cur.execute(sql, rowinfo)
        self.dbcon.commit()
    def close(self):
        self.dbcon.close()

if __name__ == '__main__':
    fcsv = csvHandler('test.csv')
    fcsv.write([],[])
    fcsv.close()
    sql = mysqlHandler('localhost', 'root', 'abcd1234', 'test_db1', '')
    sql.write([], [6, 'jiang'])
    sql.close()