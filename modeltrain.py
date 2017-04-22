
from sklearn.metrics import  confusion_matrix
from sklearn import metrics
from sklearn.svm import SVC
import sqlite3
import base64
import cPickle
import cv2
import warnings
warnings.filterwarnings("ignore")

pm = lambda x: cPickle.loads(base64.b64decode(x))
pm2 = lambda x: x[:, :, 0] * 0.2 + x[:, :, 1] * 0.2 + x[:, :, 2] * 0.2
pm3 = lambda x: x.reshape((440,))


procRGB2Data = lambda x : pm3(pm2(pm(x)))

def getDataByID(id):
    conn = sqlite3.connect('picdata')
    sql = '''select pic_data,label1 from pic_table where id =%d''' % (id)
    print sql
    cur = conn.cursor();
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    return data[0]


def showPredicPic(id):
    pic_data, label1 = getDataByID(id)
    print "label1====>%s" % (label1)
    img = pm(pic_data)
    xi = pm3(pm2(img))
    yi = model.predict(xi)
    print "pridict===>%s" % (yi)
    if int(yi) >= 10:
        yi = chr(yi + 55)
    print "pridict===>%s" % (yi)
    cv2.namedWindow(str(yi), 0);
    cv2.resizeWindow("a", 400, 400)
    cv2.imshow(str(yi), img);
    input = cv2.waitKey(2000);
    cv2.destroyAllWindows();


conn = sqlite3.connect('picdata')
sql = '''select pic_data,label2 from pic_table where label2 is not null'''
cur= conn.cursor()
cur.execute(sql)
pic_data = cur.fetchall()
conn.close()
d=[];t=[]
for k,v in pic_data:
    d.append(k)
    t.append(v)
d = map(procRGB2Data,d)
t = map(lambda x:int(x), t)

model = SVC()
model.fit(d,t)
ty = model.predict(d)
con_matrix=confusion_matrix(t,ty)
classify_report = metrics.classification_report(t,ty)

conn = sqlite3.connect('picdata')
for i in range(len(ty)):
    if ty[i]>=10:
        label3 = chr(55+ty[i])
    else:
        label3 = str(ty[i])
    sql = '''update pic_table set label3 ='%s' where id = %d''' %(label3,i+1)
    print sql
    conn.execute(sql)
conn.commit()
conn.close()

for id in range(400,500):
    showPredicPic(id)
