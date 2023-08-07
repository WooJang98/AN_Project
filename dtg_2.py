import csv
import pandas as pd
from datetime import datetime

def max(dt, dtnum, last): #최댓값 함수
    max = 0
    for j in range(last+1):
        if dt[j][dtnum] > max:
            max = dt[j][dtnum]
    return max

def min(dt, dtnum, last):
    min = dt[0][dtnum]
    for j in range(last+1):
        if dt[j][dtnum]<min:
            min = dt[j][dtnum]
    return min

def avg(dt, dtnum, last): #평균 함수
    sum = 0
    for j in range(last+1):
        sum += dt[j][dtnum]
    return round(sum/(last+1),1)

def dtg_status(dt, last): #dtg상태 함수, 좌표상태이상(11) or RPM센서이상(13)
    count = 0
    for i in range(last):
        if dt[i][11] == 11 and dt[i+1][11] == 11:
            count += 1
            if count>=450:
                return 11
        else:
            count = 0
            
    for j in range(last):
        if dt[j][7] == 0 and dt[j+1][7] == 0:
            count += 1
            if count >= 300:
                return 13    
        else:
            count = 0

    return 0

df = pd.read_csv("D:/dtg_01.CSV", encoding='cp949') # 지정한 경로에서 DTG파일 가져오기

df.drop(df[df["누적연료사용량"]==0].index, inplace=True) # 누적연료사용량이 0인 에러 데이터 삭제
df.drop(df[(df["기기상태"]==0)&(df["차량위치X"]==0)].index, inplace=True) # 기기상태가 0임에도 차량위치가 0인 에러 데이터 삭제

ts = df["트립시작일"].unique() #고유한 트립시작일 값을 넣은 trip_start 배열 선언
tlen = len(ts) # 고유한 트립시작일 값의 개수
tt = [[None for i in range(14)] for j in range(tlen)] #비어있는(모든 값이 None값으로 초기화된) trip_table 2차원 배열 선언

for i in range(tlen):
    dt=df[df["트립시작일"]==ts[i]].copy() #data_table, 트립시작일 단위로 분류한 각 트립의 테이블(일회용)
    dt=dt.values #일회용 테이블의 2차원 배열화
    last = len(dt)-1 #위에서 만들어진 2차원 배열의 마지막 인덱스
    
    tt[i][0] = "'" + dt[0][2] + "'" #출발일시, 트립시작일과 동일한 값 적

    tt[i][1] = "'" + dt[last][3] + "'" #도착일시, 같은 트립시작일 중 가장 마지막의 정보 발생일

    tt[i][2] = dt[0][22] #운전자명, 운전자 코드 값

    tt[i][3] = dtg_status(dt, last) #DTG상태, 기기상태값

    total_seconds = int((datetime.strptime(dt[last][3],"%Y-%m-%d %H:%M:%S") - datetime.strptime(dt[0][2],"%Y-%m-%d %H:%M:%S")).total_seconds())
    tt[i][4] = "'" + str(int(total_seconds/3600))+":" + str(int((total_seconds%3600)/60)) + ":" + str(total_seconds%60)+"'"
    #운행시간, (도착일시-트립시작일) 계산, 초단위로 변환 후 int 형으로 변환, hh:mm:ss 형식의 문자열로 변환

    tt[i][5] = dt[last][4]-dt[0][4] #운행거리, (도착일시 시점의 누적주행거리 - 트립시작일 시점의 누적주행거리)

    tt[i][6] = max(dt,6,last) #최대속도

    tt[i][7] = avg(dt,6,last) #평균속도

    tt[i][8] = max(dt,7,last) #최대RPM
 
    tt[i][9] = avg(dt,7,last) #평균 RPM

    tt[i][10] = min(dt,14,last) #최소전압
    
    tt[i][11] = max(dt,14,last) #최대전압

    tt[i][12] = 0 #과속시간, (과속한 후의 정보발생일 - 과속한 정보발생일), 초단위
    for j in range(last+1):
        if dt[j][6]>110:
            tt[i][12] += (datetime.strptime(dt[j+1][3],"%Y-%m-%d %H:%M:%S") - datetime.strptime(dt[j][3],"%Y-%m-%d %H:%M:%S")).total_seconds()
            tt[i][12] = int(tt[i][12]) #int형으로 변환
            
    tt[i][13] = dt[last][4] #해당 트립에서의 최종 누적주행거리값

col_name = ['departure_time', 'arrival_time', 'driver_code', 'dtg_status', 'driving_time', 'driving_distance', 'speed_max', 'speed_avg', 'rpm_max', 'rpm_avg', 'volt_min', 'volt_max','overspeed_time', 'accumulated_distance']
tt = pd.DataFrame(tt, columns = col_name)
#tt.to_csv("dtg_01.csv",index=False)

