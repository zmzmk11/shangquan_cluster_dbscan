# -*- coding:gb18030 -*-
import matplotlib.pyplot as plt
import math

r = 1500
f = 0.5
f1 = open("log.txt", "a", encoding='gb18030')
for line in open("companyposition(1).txt", "r"):
    outlier = []
    lat_list = []
    lon_list = []
    lat_out_list = []
    lon_out_list = []
    line = line[:-1]
    linelist = line.split("|")
    companycode = linelist[0]
    lonlat_list = linelist[1].split("#")
    if len(lonlat_list) < 10:
        print("商家编号（" + companycode + "）的数据不足十条。", file=f1)
    else:
        for i in range(len(lonlat_list)):
            count = 0
            # print("第" + str(i) + "点")
            lonlat_1 = lonlat_list[i].split("&")
            lat_1 = float(lonlat_1[0])
            lon_1 = float(lonlat_1[1])
            for j in range(len(lonlat_list)):
                if i == j:
                    continue
                else:
                    # print("第" + str(j) + "点")
                    lonlat_2 = lonlat_list[j].split("&")
                    lat_2 = float(lonlat_2[0])
                    lon_2 = float(lonlat_2[1])
                    
                    lat_sub = lat_1 * 1000000 - lat_2 * 1000000
                    lon_sub = lon_1 * 1000000 - lon_2 * 1000000
                    dist = pow(pow(lat_sub, 2) + pow(lon_sub, 2), 0.5)
                    if dist < r:
                        count += 1
            if count < f * len(lonlat_list):
                outlier.append(i)
                # print("outlier:" + str(lat_1) + "," + str(lon_1))
                lat_out_list.append(lat_1)
                lon_out_list.append(lon_1)
            else:
                # print("latlon:" + str(lat_1) + "," + str(lon_1))
                lat_list.append(lat_1)
                lon_list.append(lon_1)
        # for x in range(len(lat_list)):
        #     print(lat_list[x])
        #     print(lon_list[x])
        if len(lon_list) >= 10:
            plt.scatter(lon_list, lat_list, s=10, c='b')
            plt.scatter(lon_out_list, lat_out_list, s=10, c='r')
            file = 'picture/code_' + str(companycode) + '.png'
            plt.savefig(file)
            print("生成商家编号（" + companycode + ")的散点图,文件位置："+file, file=f1)
            plt.close()
        else:
            print("商家编号（" + companycode + ")的非离群点数不足十个", file=f1)
        # print("商家编号("+companycode+")的离群点为:"+outliter)
