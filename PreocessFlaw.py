# -*- coding: utf-8 -*-
"""
Created on Sun Jul 29 13:56:10 2018

@author: ocean
"""

import re
import os
import pandas as pd
from pandas.core.frame import DataFrame,Series
import shutil
import random
print("read flaw excel")
os.chdir("G:\ImageDetect\王朋")
origin_data=pd.read_excel("..\不良问题汇总-全部.xlsx","原始数据")
num_lines=origin_data.shape[0]
print("总行数:",num_lines)

#print(origin_data[origin_data.不良位置=="6*10"])
##  1.分离出同一行有多项的行
index_del=[]
df_add=pd.DataFrame(columns=origin_data.columns)
for indexs in range(num_lines):#([0,4]: #origin_data.index:  num_lines
    flaw_str=origin_data.loc[indexs].values[1]   #第1列为"不良位置"
    #flaw_str.find("*")
    strs=re.split("、|\.",flaw_str)  #strs=re.split("、|\.","3*2、4*7.2*6")
    #print(strs)
    strs_len=len(strs)
    if strs_len>1:    #分离出的"不良位置"不止1个
        dict_temp={"不良位置":strs[0:]}    #比如,["3*2","4*7","2*6"]
        df_now=pd.DataFrame(dict_temp)    #由list构造成DataFrame
        df_now["组件编号"]=origin_data.loc[indexs].values[0] #"组件编号"为同一个
        df_now["不良描述"]=origin_data.loc[indexs].values[2] #"不良描述"为同一个
        df_now["给数据的日期"]=origin_data.loc[indexs].values[3] #"给数据的日期"为同一个
        index_del.append(indexs)                      #原来的这行将来要删除,先做个标记
        df_add=pd.concat([df_add,df_now])            #加入新生成的行
        #print(df_now)

result1=origin_data.drop(index_del)  #删除原来的那些行,比如 "3*2、4*7.2*6"
result2=pd.concat([result1,df_add])  #增加分离出来的那些行,比如增加3行 "3*2" "4*7" "2*6"

##  2.正常表示为类似:1*1,或者1*10, 筛选出长度小于5的行
#pos_str=result2['不良位置']
sels=result2['不良位置'].map(lambda x:len(x)<5)  #删除那些不是形如 x*y的行,比如 5*2*6
result3=result2[sels]
##  3.删除 ”4串"这个不良位置
sels=result3['不良位置'].map(lambda x:x.find("串")==-1) #删除 "4串"这个莫名其妙的行
result4=result3[sels]

##  4.分离出行号和列号,并加入DataFrame里面
rowxcol=result4['不良位置']
#x_pos=rowxcol.map(lambda x:x.find("*"))
line_str=rowxcol.map(lambda x:x[0])
col_str =rowxcol.map(lambda x:x[2:])
result5=pd.concat([result4,pd.DataFrame({"行号":line_str,"列号":col_str})],axis=1)
#result5=pd.concat([result4,line_str,col_str],axis=1)

#result4.insert(0,'行号',line_str)
#result4[['行号']]=line_str
#result4['列号']=col_str

##  5.重新按照组件号从小到大排列
result5=result5.reindex(columns=["组件编号","行号","列号","不良位置","不良描述","给数据的日期"])
result5=result5.sort_values(by=["组件编号","行号","列号","不良位置","给数据的日期"]) 
result5["组件编号"]=result5["组件编号"].map(lambda x:str(x))
#result5.reindex(index=range(len(result5)))
result5=result5.reset_index(drop=True)

#result5.to_excel("..\提取.xlsx","Sheet1")

#index=pd.date_range('2018-07-10',periods=12)
#s=Series(list(range(12)),index)
#d=s.index.map(lambda x:x.day)


rootdir = 'G:\ImageDetect\GPSubs'
dirs = os.listdir(rootdir)
dirs_df=pd.DataFrame({"目录名":dirs})
#dirs_df.to_excel("..\目录.xlsx","Sheet1")

for i in range(0,len(dirs)):
#for i in range(0,3):
    path=os.path.join(rootdir,dirs[i])
    #if os.path.isdir(path):
    if os.path.isfile(path):
        print(path)

#
os.chdir(rootdir)
compenents=result5["组件编号"]
dirs_series=pd.Series(data=dirs)#index="compenent")
#pos_series =pd.Series(data=range(0,len(compenents)))
dir_new="G:\\ImageDetect\\AllBadPics\\"
num_good_sel=2   #选择的好图片的数量
for i in range(0,len(compenents)):
    t=dirs_series.map(lambda x:x.find(compenents[i]))
    pos=t[t>-1].index     #找到的话,下标为0.找不到,下标为-1.取回下标
    pos=pos[0]            #下标虽然只有1个,但也是list
    files_all=os.listdir(dir_now)   #当前文件夹下所有文件
    #复制有问题的小图片
    dir_now=dirs_series[pos]        #找到的文件夹
    files_all=os.listdir(dir_now)   #当前文件夹下所有文件
    row=str(7-int(result5["行号"][i]))
    old_file_name=row+result5["列号"][i]+".jpg"
    #如果这个坏图片的文件不存在,则直接跳过
    if(old_file_name not in files_all):
        continue
    
    old_file=dir_now+"\\"+old_file_name  #有问题的小图片文件
    print(old_file)
    new_file=dir_new+"b-"+compenents[i]+"-"+row+result5["列号"][i]+".jpg"#坏图片文件名前面加"b-"
    shutil.copyfile(old_file,new_file)  
    #另外再复制几个没有问题的小图片
    files_all.remove(old_file_name) #从好图片里面选择时，要去掉刚才的坏图片
    files_num=len(files_all)
    r=list(range(0,files_num))  #产生文件个数的数组,0,1,2.....
    random.shuffle(r)           #打乱序列，然后取前面几个
    for j in range(0,num_good_sel):
        old_file_name=files_all[r[j]] 
        old_file=dir_now+"\\"+old_file_name
        new_file=dir_new+"g-"+compenents[i]+"-"+old_file_name #好图片文件名前面加"g-"
        shutil.copyfile(old_file,new_file)




