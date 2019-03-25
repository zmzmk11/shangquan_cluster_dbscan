# -*- coding:gb18030 -*-
import matplotlib.pyplot as plt
import math
import pymysql.cursors
from matplotlib.patches import Ellipse, Circle
from matplotlib.font_manager import FontProperties
from matplotlib.font_manager import FontProperties

font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
f = 0.5
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
    fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

def count_avg_r(x, y):
    lon_all = 0
    lat_all = 0
    for i in range(len(x)):
        lon_all += x[i]
        lat_all += y[i]
    if len(x) > 0:
        lon_avg = lon_all / len(x)
        lat_avg = lat_all / len(y)
        return lon_avg, lat_avg
    else:
        return 0, 0


def count_d(x, y, r_x, r_y):
    dist = 0
    for i in range(len(x)):
        dist += math.pow(math.pow(x[i] - r_x, 2) + math.pow(y[i] - r_y, 2), 0.5)
    if len(x) > 0:
        return dist / len(x)
    else:
        return 0


def count_new_xy(x, y, d):
    _len = len(x)
    lon_un = []
    lat_un = []
    lon_out = []
    lat_out = []
    for i in range(_len):
        count = 0
        lonA = float(x[i])
        latA = float(y[i])
        for j in range(_len):
            if i == j:
                continue
            else:
                lonB = float(x[j])
                latB = float(y[j])
                dist = pow(pow(lonA - lonB, 2) + pow(latA - latB, 2), 0.5)
                # print(dist)
                if dist < d * 1.5:
                    count += 1
        if count > _len * f:
            lon_un.append(float(x[i]))
            lat_un.append(float(y[i]))
        else:
            lon_out.append(float(x[i]))
            lat_out.append(float(y[i]))
    return lon_un, lat_un, lon_out, lat_out


def count_radius(x, y, center_x, center_y):
    radius = 0
    for i in range(len(x)):
        dist = pow(pow(x[i] - center_x, 2) + pow(y[i] - center_y, 2), 0.5)
        if dist > radius:
            radius = dist
    return radius


def Density_calculation(r, len):
    s = math.pi * r * r
    d = len / s * 0.000001
    return d


def connect_mysql(cursor, sql):
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def count_area_center_radius(dis, cursor):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.canvas.mpl_connect('scroll_event', call_back)
    fig.canvas.mpl_connect('button_press_event', call_back)
    sql = "select distinct regionlist from dianping_fuzhou_food where district='" + dis + "'"
    result = connect_mysql(cursor, sql)
    for res1 in result:
        if res1[0] == 'None' or res1[0] == '鼓楼区' or res1[0] == '仓山区' or res1[0] == '五四路商务区':
            continue
        num = 0
        x = []
        y = []
        sql = "select * from dianping_fuzhou_food where regionlist='" + res1[0] + "'"
        res = connect_mysql(cursor, sql)
        for i in res:
            x.append(float(i[8]))
            y.append(float(i[9]))
        sql = "select * from dianping_fuzhou_mall where regionlist='" + res1[0] + "'"
        res = connect_mysql(cursor, sql)
        for i in res:
            if i[7] == '五星商户':
                for j in range(50):
                    x.append(float(i[8]))
                    y.append(float(i[9]))
            elif i[7] == '准五星商户':
                for j in range(40):
                    x.append(float(i[8]))
                    y.append(float(i[9]))
            elif i[7] == '四星商户':
                for j in range(30):
                    x.append(float(i[8]))
                    y.append(float(i[9]))
        sql = "select * from dianping_fuzhou_cinema where regionlist='" + res1[0] + "'"
        res = connect_mysql(cursor, sql)
        for i in res:
            for j in range(30):
                x.append(float(i[8]))
                y.append(float(i[9]))
        lon_avg, lat_avg = count_avg_r(x, y)
        while 1:
            num += 1
            dist = count_d(x, y, lon_avg, lat_avg)
            x, y, x_out, y_out = count_new_xy(x, y, dist)
            radius = count_radius(x, y, lon_avg, lat_avg)
            if len(x) > 0:
                lon_avg, lat_avg = count_avg_r(x, y)
                density = Density_calculation(radius, len(x))
                if num == 1:
                    x_1, y_1, x_out_1, y_out_1 = x, y, x_out, y_out
            else:
                break
            if density > 3 or radius < 0.003:
                break
        if radius * density > 0.015 and len(x) > 50:
            # lon_avg_left = lon_avg * 0.99999
            # cir1 = Circle(xy=(lon_avg, lat_avg), radius=radius, alpha=0.4)  # 第一个参数为圆心坐标，第二个为半径 #第三个为透明度（0-1）
            # plt.annotate(res1[0], xy=(lon_avg_left, lat_avg), fontproperties=font_set)
            # ax.add_patch(cir1)
            # plt.axis('scaled')
            # plt.axis('equal')
            name = str(res1[0]).replace("/", "\\/")
            sql = "insert into shangquan_data_1(name,district,lon,lat,radius) values ('" + name + "','" + dis + "','" + \
                  str(lon_avg) + "','" + str(lat_avg) + \
                  "','" + str(radius * 10000) + "')"
            cursor.execute(sql)
            conn.commit()
    #     plt.scatter(x_1, y_1, s=4, alpha=0.4, c='y')
    #     plt.scatter(x_out_1, y_out_1, s=4, alpha=0.4, c='r')
    # plt.show()


def update_radius(xy_radius):
    xy_radius_list = []
    for i in range(len(xy_radius)):
        xy_radius_list.append(list(xy_radius[i]))
    for i in range(len(xy_radius_list)):
        x = float(xy_radius_list[i][3])
        y = float(xy_radius_list[i][4])
        radius = float(xy_radius_list[i][5])
        for j in range(len(xy_radius_list)):
            if i == j:
                continue
            _x = float(xy_radius_list[j][3])
            _y = float(xy_radius_list[j][4])
            _radius = float(xy_radius_list[j][5])
            D = radius + _radius
            print(str(xy_radius_list[i][1]) + "," + str(xy_radius_list[j][1]) + "(D):" + str(D))
            dist = pow(pow(x - _x, 2) + pow(y - _y, 2), 0.5) * 10000
            print(str(xy_radius_list[i][1]) + "," + str(xy_radius_list[j][1])+ "(dist):" + str(dist))
            if dist < D:
                xy_radius_list[i][5] = radius - (D - dist) * radius / D
                xy_radius_list[j][5] = _radius - (D - dist) * _radius / D
    ax = fig.add_subplot(111)
    fig.canvas.mpl_connect('scroll_event', call_back)
    fig.canvas.mpl_connect('button_press_event', call_back)
    for i in xy_radius_list:
        lon = float(i[3])
        lat = float(i[4])
        radius = float(i[5])/10000
        sql = "insert into shangquan_center_radius1(name,district,lon,lat,radius) values ('" + i[1] + "','" + i[2] + "','" + \
              str(lon) + "','" + str(lat) + \
              "','" + str(radius * 10000) + "')"
        cursor.execute(sql)
        conn.commit()
    #     cir1 = Circle(xy=(lon, lat), radius=radius, alpha=0.4)  # 第一个参数为圆心坐标，第二个为半径 #第三个为透明度（0-1）
    #     plt.annotate(i[1], xy=(lon, lat), fontproperties=font_set)
    #     ax.add_patch(cir1)
    #     plt.axis('scaled')
    #     plt.axis('equal')
    # plt.show()


def creat_table(cursor):
    cursor.execute("drop table if exists shangquan_data_1")
    sql = """CREATE TABLE IF NOT EXISTS `shangquan_data_1` (
          `id`int NOT NULL AUTO_INCREMENT,
          `name` varchar(50) NOT NULL,
          `district` varchar(20) NOT NULL,
          `lon` varchar(20) NOT NULL,
          `lat` varchar(20) NOT NULL,
          `radius` varchar(30) NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=0"""
    cursor.execute(sql)
    return 0





if __name__ == '__main__':
    conn = pymysql.connect("localhost", "root", "168432", "meituan_data")
    cursor = conn.cursor()
    # creat_table(cursor)
    sql = "select distinct district from dianping_fuzhou_food"
    district = connect_mysql(cursor, sql)
    # for dis in district:
    #     count_area_center_radius(dis[0], cursor)
    sql = "select * from shangquan_data_1"
    xy_radius = connect_mysql(cursor, sql)
    update_radius(xy_radius)
