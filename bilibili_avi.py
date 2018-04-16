import requests
import time
import pymysql
import random
from multiprocessing import Pool


conn = pymysql.connect(host = '127.0.0.1' , port = 3306 , user = 'root' , passwd = '921522' , db = 'practice')
cur = conn.cursor()
result = []
video_list = []

def LoadUserAgent(uafile):
    uas = []
    with open(uafile,'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas

uas = LoadUserAgent("user_agents.txt")

def LoadProxies(uafile):
    ips = []
    with open(uafile,'r') as proxies:
        for ip in proxies.readlines():
            if ip:
                ips.append(ua.strip())
    random.shuffle(ips)
    return ips

ips = LoadProxies("proxies.txt")

def getHtmlInfo(url):
    ua = random.choice(uas)
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'api.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        # 'Referer': 'https://www.bilibili.com/video/' + str(i) + '?spm_id_from=333.338.recommend_report.3',
        'User-Agent': ua
    }
    try:
        response = requests.get(url, headers=headers, timeout=6).json()
        data = response['data']
        video = (
            data['aid'], data['view'], data['danmaku'],
            data['reply'], data['favorite'], data['coin'], data['share'])
        video_list.append(video)
        print(video_list)
        save_db()
        time.sleep(0.4)
        # gevent.sleep(0.1)

    except:
        print("----")
        time.sleep(0.4)
        # gevent.sleep(0.1)
        # print(ip_choice)



def save_db():
    # 将数据保存至本地
    global video_list, cur, conn
    sql = "insert into bili_video values(%s, %s, %s, %s, %s, %s, %s);"
    for row in video_list:
        try:
            # print(row)
            cur.execute(sql, row)
        except:
            conn.rollback()
    conn.commit()
    video_list = []

if __name__ == '__main__':
    pool = Pool()
    for i in range(1,2000):
        elem = (i-1)*10000
        urls = ['https://api.bilibili.com/x/web-interface/archive/stat?aid={}'.format(j) for j in range(elem,elem+10000)]
        #urls = 'https://api.bilibili.com/x/web-interface/archive/stat?aid={}'.format(i)
        pool.map(getHtmlInfo, urls)
        pool.close()
        pool.join()

    conn.close()
