#!/usr/bin/python
# coding utf8
import sqlite3
import base64
import cPickle
import cv2
import sys
import urllib2
import warnings
warnings.filterwarnings("ignore")

pm = lambda x: cPickle.loads(base64.b64decode(x))
pm2 = lambda x: x[:, :, 0] * 0.2 + x[:, :, 1] * 0.2 + x[:, :, 2] * 0.2
pm3 = lambda x: x.reshape((440,))
procRGB2Data = lambda x: pm3(pm2(pm(x)))

def getimg(num):
    url = 'https://ebank.sdb.com.cn/corporbank/VerifyImage'
    for idx in range(num):
        a = urllib2.urlopen(url)
        pic_file = '%08d.jpg' % idx
        f = open(pic_file, 'w')
        f.write(a.read())
        f.close()


def splitimg(img):
    nimg = cv2.imread(img)
    pic1 = nimg[:, 0:20, :]
    pic2 = nimg[:, 20:40, :]
    pic3 = nimg[:, 40:60, :]
    pic4 = nimg[:, 60:80, :]
    return pic1, pic2, pic3, pic4


def insert2db(filename):
    data = splitimg(filename)
    for idx in data:
        conn = sqlite3.connect('picdata')
        bimgs = base64.b64encode(cPickle.dumps(idx))
        sql = '''insert into pic_table (file_name,pic_data) values('%s','%s')''' % (filename, bimgs)
        conn.execute(sql)
        conn.commit()
        conn.close()


def labelpic(idx):
    conn = sqlite3.connect('picdata')
    sql = '''select pic_data from pic_table where id = %d''' % idx
    cur = conn.cursor()
    cur.execute(sql)
    pic_data = cur.fetchall()[0][0]
    img = cPickle.loads(base64.b64decode(pic_data))
    cv2.namedWindow(str(id), 0)
    cv2.resizeWindow(str(id), 400, 400)
    cv2.moveWindow(str(id), 400, 200)
    cv2.imshow(str(id), img)
    inputi = cv2.waitKey(0)
    cv2.destroyAllWindows()
    inputi = chr(inputi).upper()
    if ord(inputi) >= 65:
        label2 = str(ord(inputi) - 55)
    else:
        label2 = inputi
    sql = '''update pic_table set label1='%s',label2 ='%s'  where id =%d ''' % (inputi, label2, idx)
    print(sql)
    conn.execute(sql)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        x, y = int(sys.argv[1]), int(sys.argv[2])
    else:
        x, y = 100, 101
    for i in range(x, y):
        labelpic(i)
