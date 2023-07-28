import csv
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def max(dt, dtnum, last):
    max = 0
    for j in range(last+1):
        if dt[j][dtnum] > max:
            max = dt[j][dtnum]
    return max

def avg(dt, dtnum, last):
    sum = 0
    for j in range(last+1):
        sum += dt[j][dtnum]
    return round(sum/(last+1),1)

plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)

import koreanize_matplotlib

df = pd.read_csv("C:/DTG_01.txt") # 지정한 경로에서 DTG파일 가져오기
df.shape

ts = df["트립시작일"].unique() #고유한 트립시작일 값을 넣은 trip_start 배열 선언
tlen = len(ts) # 고유한 트립시작일 값의 개수
tt = [[None for i in range(14)] for j in range(tlen)] #비어있는(모든 값이 None값으로 초기화된) trip_table 2차원 배열 선언

for i in range(tlen):
    dt=df[df["트립시작일"]==ts[i]].copy() #data_table, 트립시작일 단위로 분류한 각 트립의 테이블(일회용)
    dt=dt.values #일회용 테이블의 2차원 배열화
    last = len(dt)-1 #위에서 만들어진 2차원 배열의 마지막 인덱스
    
    tt[i][0] = dt[0][2] #출발일시, 트립시작일과 동일한 값 적

    tt[i][1] = dt[last][3] #도착일시, 같은 트립시작일 중 가장 마지막의 정보 발생일

    tt[i][2] = dt[0][22] #운전자명, 운전자 코드 값

    tt[i][3] = dt[0][11] #DTG상태, 기기상태값

    tt[i][4] = int((datetime.strptime(dt[last][3],"%Y-%m-%d %H:%M:%S") - datetime.strptime(dt[0][2],"%Y-%m-%d %H:%M:%S")).total_seconds())
    #운행시간, (도착일시-트립시작일) 계산, 초단위로 변환 후 int 형으로 변환

    tt[i][5] = dt[last][4]-dt[0][4] #운행거리, (도착일시 시점의 누적주행거리 - 트립시작일 시점의 누적주행거리)

    tt[i][6] = max(dt,6,last) #최대속도

    tt[i][7] = avg(dt,6,last) #평균속도

    tt[i][8] = max(dt,7,last) #최대RPM
 
    tt[i][9] = avg(dt,7,last) #평균 RPM

    tt[i][10] = dt[0][14] #최소전압 계산
    for j in range(last+1):
        if dt[j][14]<tt[i][10]:
            tt[i][10] = dt[j][14]

    tt[i][11] = max(dt,14,last) #최대전압 계산

    tt[i][12] = 0 #과속시간, (과속한 후의 정보발생일 - 과속한 정보발생일), 초단위
    for j in range(last+1):
        if dt[j][6]>110:
            tt[i][12] += (datetime.strptime(dt[j+1][3],"%Y-%m-%d %H:%M:%S") - datetime.strptime(dt[j][3],"%Y-%m-%d %H:%M:%S")).total_seconds()
            tt[i][12] = int(tt[i][12]) #int형으로 변환
            
    tt[i][13] = dt[last][4] #해당 트립에서의 최종 누적주행거리값


col_name = ['출발일시', '도착일시', '운전자명', 'DTG 상태', '운행시간', '운행거리', '최고속도', '평균속도', '최고RPM', '평균RPM', '최소전압', '최대전압','과속시간', '누적주행거리']
tt = pd.DataFrame(tt, columns = col_name)
tt.to_csv("dtg_01")

