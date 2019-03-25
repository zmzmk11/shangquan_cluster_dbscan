# -*- coding:gb18030 -*-
import numpy as np
from sklearn import datasets
import matplotlib.pyplot as plt
import pymysql.cursors
import random
import time
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')
fig = plt.figure()


def call_back(event):
    axtemp = event.inaxes
    x_min, x_max = axtemp.get_xlim()
    y_min, y_max = axtemp.get_ylim()
    fanwei = (x_max - x_min) / 10
    fanwei1 = (y_max - y_min) / 10
    if event.button == 'up':
        axtemp.set(xlim=(x_min + fanwei, x_max - fanwei))
        axtemp.set(ylim=(y_min + fanwei1, y_max - fanwei1))
        print('up')
    elif event.button == 'down':
        axtemp.set(xlim=(x_min - fanwei, x_max + fanwei))
        axtemp.set(ylim=(y_min - fanwei1, y_max + fanwei1))
        print('down')
    fig.canvas.draw_idle()  # ��ͼ����ʵʱ��ӳ��ͼ����


def findNeighbor(j, X, eps):
    N = []
    for p in range(len(X)):  # �ҵ����������ڶ���
        temp = pow(pow(X[p][0] - X[j][0], 2) + pow(X[p][1] - X[j][1], 2), 0.5)
        # temp = np.sqrt(np.sum(np.square(X[p][0] - X[j][0]), np.square(X[p][1] - X[j][1])))  # ŷ�Ͼ���
        if (temp <= eps):
            N.append(p)
    return N


def dbscan(X, eps, min_Pts):
    k = -1
    NeighborPts = []  # array,ĳ�������ڵĶ���
    Ner_NeighborPts = []
    fil = []  # ��ʼʱ�ѷ��ʶ����б�Ϊ��
    gama = [x for x in range(len(X))]  # ��ʼʱ�����е���Ϊδ����
    cluster = [-1 for y in range(len(X))]
    while len(gama) > 0:
        j = random.choice(gama)
        gama.remove(j)  # δ�����б����Ƴ�
        fil.append(j)  # ���������б�
        NeighborPts = findNeighbor(j, X, eps)
        if len(NeighborPts) < min_Pts:
            cluster[j] = -1  # ���Ϊ������
        else:
            k = k + 1
            cluster[j] = k
            for i in NeighborPts:
                if i not in fil:
                    gama.remove(i)
                    fil.append(i)
                    Ner_NeighborPts = findNeighbor(i, X, eps)
                    if len(Ner_NeighborPts) >= min_Pts:
                        for a in Ner_NeighborPts:
                            if a not in NeighborPts:
                                NeighborPts.append(a)
                    if (cluster[i] == -1):
                        cluster[i] = k
    return cluster


city = '��¥��'
conn = pymysql.connect("localhost", "root", "168432", "meituan_data")
cursor = conn.cursor()
sql = "select * from dianping_fuzhou_food where district = '" + city + "'"
# where district = '" + city + "'
cursor.execute(sql)
food = cursor.fetchall()
all = list(food)
a = []
x = []
y = []
CI = []
eps = 0.001
min_Pts = 100
for f in food:
    point = [float(f[8]), float(f[9])]
    a.append(point)
sql = "select * from dianping_fuzhou_mall where district = '" + city + "'"
cursor.execute(sql)
mall = cursor.fetchall()
for m in mall:
    if m[7] == '�����̻�':
        for i in range(50):
            point = [float(m[8]), float(m[9])]
            a.append(point)
            all.append(m)
    elif m[7] == '׼�����̻�':
        for i in range(40):
            point = [float(m[8]), float(m[9])]
            a.append(point)
            all.append(m)
    elif m[7] == '�����̻�':
        for i in range(30):
            point = [float(m[8]), float(m[9])]
            a.append(point)
            all.append(m)
sql = "select * from dianping_fuzhou_cinema where district = '" + city + "'"
cursor.execute(sql)
cinema = cursor.fetchall()
for c in cinema:
    for i in range(30):
        point = [float(c[8]), float(c[9])]
        a.append(point)
        all.append(c)
flag = [False] * len(a)
cluster_id = 1
start = time.time()
C = dbscan(a, eps, min_Pts)
end = time.time()
fig.canvas.mpl_connect('scroll_event', call_back)
fig.canvas.mpl_connect('button_press_event', call_back)
# plt.figure(figsize=(12, 9), dpi=80)
for i in range(len(C)):
    if C[i] != -1:
        x.append(a[i][0])
        y.append(a[i][1])
        CI.append(C[i])
plt.scatter(x, y, c=CI, s=5, alpha=0.5)
# cursor.execute("drop table if exists `dbscan_shangquan`")
sql = """CREATE TABLE IF NOT EXISTS `dbscan_shangquan` (
      `id` int NOT NULL AUTO_INCREMENT,
      `shopid` varchar(10) NOT NULL,
      `shopname` varchar(50) NOT NULL,
      `dishtag` varchar(20),
      `address` varchar(200) NOT NULL,
      `district` varchar(30),
      `regionlist` varchar(30),
      `shoppowertitle` varchar(30),
      `lon` varchar(30),
      `lat` varchar(30),
      `avgprice` varchar(30),
      `defaultpic` varchar(200),
      `clusterid` varchar(30),
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=0"""
cursor.execute(sql)
for s in range(len(all)):
    CompanyAddress = all[s][4].replace("'", "\\'")
    CompanyName = all[s][2].replace("'", "\\'")
    regionlist = all[s][6].replace("/", "\\/")
    sql = "insert into dbscan_shangquan(shopid,shopname,dishtag,address,district,regionlist,shoppowertitle,lon,lat,avgprice,defaultpic,clusterid)" \
          " values(" + all[s][1] + ",'" + CompanyName + "','" + all[s][3] + "','" + \
          CompanyAddress + "','" + all[s][5] + "','" + str(regionlist) + "','" + str(all[s][7]) + "'," \
          + str(all[s][8]) + "," + str(all[s][9]) + "," + str(all[s][10]) + ",'" + str(all[s][11]) + "'," + str(
        C[s]) + ")"
    cursor.execute(sql)
    conn.commit()

print("��ʱ:", end - start)
plt.show()
