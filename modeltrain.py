
from sklearn.metrics import  confusion_matrix
from sklearn import metrics
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import sys,os
import sqlite3
import base64
import cPickle
import cv2
import warnings
warnings.filterwarnings("ignore")

pm  = lambda x: cPickle.loads(base64.b64decode(x))
pm2 = lambda x: x[:, :, 0] * 0.2 + x[:, :, 1] * 0.2 + x[:, :, 2] * 0.2
pm3 = lambda x: x.reshape((440,))
procRGB2Data = lambda x : pm3(pm2(pm(x)))
model = None

def getDataByID(id):
    conn = sqlite3.connect('picdata')
    sql = '''select pic_data,label1 from pic_table where id =%d''' % (id)
    print sql
    cur = conn.cursor();
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    return data[0]


def showPredicPic(id,model):
    pic_data, label1 = getDataByID(id)
    print "id:%s label1====>%s" % (id,label1)
    img = pm(pic_data)
    xi = pm3(pm2(img))
    yi = model.predict(xi)
    if int(yi) >= 10:
        yi = chr(yi + 55)
    print "id:%s pridict===>%s" %(id ,yi)
    cv2.namedWindow(str(yi), 0)
    cv2.resizeWindow(str(yi), 400, 400)
    cv2.moveWindow(str(yi), 400, 200)
    cv2.imshow(str(yi), img)
    cv2.waitKey(1500)
    cv2.destroyAllWindows()


def trainModel():
    conn = sqlite3.connect('picdata')
    sql = '''select pic_data,label2 from pic_table where label2 is not null'''
    cur = conn.cursor()
    cur.execute(sql)
    pic_data = cur.fetchall()
    conn.close()
    d = [];
    t = []
    for k, v in pic_data:
        d.append(k)
        t.append(v)
    d = map(procRGB2Data, d)
    t = map(lambda x: int(x), t)
    rf_model = RandomForestClassifier(n_estimators=100)
    rf_model.fit(d, t)
    svc_model = SVC(C=3)
    svc_model.fit(d, t)
    model = rf_model
    ty = model.predict(d)
    con_matrix = confusion_matrix(t, ty)
    classify_report = metrics.classification_report(t, ty)
    conn = sqlite3.connect('picdata')
    for i in range(len(ty)):
        if ty[i] >= 10:
            label3 = chr(55 + ty[i])
        else:
            label3 = str(ty[i])
        sql = '''update pic_table set label3 ='%s' where id = %d''' % (label3, i + 1)
        conn.execute(sql)
    conn.commit()
    conn.close()
    return model



if  __name__=='__main__':
    if len(sys.argv)>2:
        x,y = int(sys.argv[1]),int(sys.argv[2])
    else:
        x,y = 100,110
    if os.path.exists('model.data'):
        model = cPickle.load(open('model.data','r'))
    else:
        model = trainModel()
        cPickle.dump(model,open('model.data','w'))
    for i in range(x,y):
        showPredicPic(i,model)
