    #-*- coding  = utf-8 -*-
#@Time : 19/5/2022 下午11:06
#@Auther : Baiky
#@File : web_weibo_api_spider.py
#@Software : PyCharm
import pprint
import wordcloud
import requests
import re
import time
import json
import datetime
import csv
import random

def get_string(text):
    t = ''
    flag = 1
    for i in text:
        if i == '<':
            flag = 0
        elif i == '>':
            flag = 1
        elif flag == 1:
            t += i
    return t

def random_cookie():
    cookie_list = [#'XSRF-TOKEN=B8S2SuBKvzAuvZZEoGHBkWjc; _s_tentry=weibo.com; Apache=6399160675791.69.1639134710179; SINAGLOBAL=6399160675791.69.1639134710179; ULV=1639134710210:1:1:1:6399160675791.69.1639134710179:; UOR=,,www.baidu.com; SCF=AoSW1wMktBm66L7-_zRCrfLQ3b1CxY8arUyIjhGCjnxIm0zQhrKqTuUw9n05qYx-gIkMWmmEHYnjWOSUP-tRZh0.; wvr=6; SUB=_2A25PiL76DeRhGeBN6FYX8CbLzTuIHXVs_5cyrDV8PUNbmtB-LWegkW9NRGyBh03ZXENipc22YYeG3NOVSpS3I5B5; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF.SaMYF0nAqYa9ZLbdyx785JpX5KzhUgL.Foq0e0BcehnNSoM2dJLoIpjLxKnL1hzL1KqLxKBLB.BLBo5LxKML1K5LBKqt; ALF=1684931114; SSOLoginState=1653395114; WBPSESS=Dt2hbAUaXfkVprjyrAZT_FeQQ-tJbhkr8peFIH6pn4vGFePqaVyZ_w2BXlR6kbNjdQyyJqY6ZMdAue5B75idgjBjKBAeAxGcNyStDCy9APN1w8g50yYwjw-ouHux7wyzOFSbPdAlHTOcipdjY0X4Ze7ylZkOoWcX097MV6eDT0Jw3FD1Koytnu3_0YbctTQMQE2fmevcRICrrNihqMXTFQ==',
                   'XXSRF-TOKEN=B8S2SuBKvzAuvZZEoGHBkWjc; _s_tentry=weibo.com; Apache=6399160675791.69.1639134710179; SINAGLOBAL=6399160675791.69.1639134710179; ULV=1639134710210:1:1:1:6399160675791.69.1639134710179:; UOR=,,www.baidu.com; wvr=6; SSOLoginState=1653399012; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWfM8uxZOJOm8MVeOqHhEfo5JpX5KMhUgL.FoMNSozpe0.p1hM2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNS0qEeKe4eKnN; ALF=1685067902; SCF=AoSW1wMktBm66L7-_zRCrfLQ3b1CxY8arUyIjhGCjnxImUCk0mQmf6h7Yu-gBIO9XGm9tqRRbiscXWus1LUmFZI.; SUB=_2A25PipSvDeRhGeFJ7VAQ8yfNwzuIHXVs4YFnrDV8PUNbmtAKLXj1kW9Nf2Dx2ZxXzTyEMI1jplA3MRGHDnGBotg8; WBPSESS=79qvSwrFymFdgo6BLlTxA5IqO1Fo-QBMdUsLh50LByAAG28G2j1ddq_1DFVzWCWjjcXb7MiXwr2VbRtvRFI23DLKGiSZSysKxXOch8c5QSRzoC3CsU6ZFO_c0eUPFfF5cxO8HbCL_fMerug5IjNarg=='
                   ]
    num = random.randint(0,1)
    return cookie_list[0]



def getPage(url,cookie):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'sec-ch-ua': 'Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('网页访问成功')
            response.encoding = 'utf-8'
            return response.text
        else:
            print('网页访问失败')
    except requests.RequestException:
        return None

def str2json(pageinfo):
    page_json = json.loads(pageinfo)
    #pprint.pprint(page_json)
    return page_json

#微博时间格式
#'Sat May 21 20:05:02 +0800 2022'
def GMT_transfer(dd):
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(dd, GMT_FORMAT)
    create_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return create_time

def getDataFromJson(json_text):
    collective_data = []
    blogs_list = json_text['data']['list']
    try:
        for single_blog in blogs_list:
            #提取全部博文，若有需要展开的博文，则访问全部博文对应的网址
            isLongText = 'true'
            isLongText = single_blog['isLongText']
            # print(isLongText)
            if isLongText == True:
                mblogid = single_blog['mblogid']
                lontTextUrl = 'https://weibo.com/ajax/statuses/longtext?id='+mblogid
                text = getLongText(lontTextUrl)
            else:
                text = get_string(single_blog['text'])
            #提取博客相关信息
            report_count = single_blog['reposts_count']
            comment_count = single_blog['comments_count']
            attitude_count = single_blog['attitudes_count']
            create_time = GMT_transfer(single_blog['created_at'])
            blog = []
            blog.append(text)
            blog.append(report_count)
            blog.append(comment_count)
            blog.append(attitude_count)
            blog.append(create_time)
            collective_data.append(blog)
    except Exception as e:
        print(e)
        pass
    return collective_data



def getLongText(url):
    time.sleep(5)
    web_data  =getPage(url,random_cookie())
    json_data = str2json(web_data)
    longtext = json_data['data']['longTextContent']
    return longtext

def save2Csv(co_data):
    try:
        with open('weibo.csv','a+',encoding='utf-8-sig',newline='')as f:
            writer = csv.writer(f)
            table_header = ['博文','转发','评论','点赞','发表时间']
            #writer.writerow(table_header)
            for line in co_data:
                if line != '':                      #去除空行
                    writer.writerow(line)
        print('数据写入文件成功')
    except Exception as e:
        print(e)

def main():

    page = 1
    while 1:
        try:
            url = 'https://weibo.com/ajax/statuses/mymblog?uid=2803301701&page={}&feature=0'.format(page)
            cookie = random_cookie()
            web = getPage(url,cookie)      #爬取下来的网页源码是str类型的
            page_info = str2json(web)
            co_data = getDataFromJson(page_info)
            save2Csv(co_data)
            print('Page '+str(page)+' finished')
            page=page+1
            time.sleep(15)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
   main()