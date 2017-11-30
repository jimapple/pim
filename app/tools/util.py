# -*- coding:utf8 -*-
import sys
import math
import requests
import json
from datetime import datetime, date
import decimal
import time
from flask import request

url_host = 'http://47.100.21.125/'

# 时间格式处理
from app.tools import messages


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


# API_Response
def api_result(data=None, status_code=1, message=None):
    result = {"status_code": status_code, "data": data}
    if status_code == 0 and message:
        mes = {"message": message}
        result["data"] = mes
    return json.dumps(result, cls=CJsonEncoder)


# 通过地区或id查询24小时天气
def Weather(city):
    # 请求地址
    url = "http://apis.eolinker.com/common/weather/get24HoursWeatherByArea"
    # 请求参数
    params = {"productKey": "UMBF2sU1684ce1b26033cc1135ea3ebc93c261eeb7d6921", "area": city}
    # 执行请求
    result = requests.post(url=url, data=params)
    ret_code = json.loads(result.text)['result']['ret_code']
    if ret_code != -1:
        hour_weather = json.loads(result.text)['result']['hourList'][0]
        d = date.today()
        times = d.strftime('%Y/%m/%d')
        year, month, days = times.split('/')
        datetimeformat = "{}年{}月{}日".format(year, month, days)
        week = d.isoweekday()
        if week == 1:
            week = '周一'
        elif week == 2:
            week = '周二'
        elif week == 3:
            week = '周三'
        elif week == 4:
            week = '周四'
        elif week == 5:
            week = '周五'
        elif week == 6:
            week = '周六'
        elif week == 7:
            week = '周日'
        weather = hour_weather['weather']
        temperature = hour_weather['temperature']
        result_dict = {'datetime': datetimeformat, 'week': week, 'weather': weather, 'temperature': temperature+'℃'}
        return result_dict
    else:
        return {'message': messages.city_not_found}


# 分页封装
class Pagenator(object):
    """page_index: 页码，
       page_size: 每页条数，
       total_number: 总条数,
       total_page: 总页数,
    """
    def __init__(self, request_data, queryset=None):
        if request_data['page_index'] and request_data['page_size']:
            self.page_index = request_data['page_index']
            self.page_size = request_data['page_size']
        else:
            self.page_index = 1
            self.page_size = 10
        self.queryset = queryset
        self.total_number = len(queryset)
        self.total_page = math.ceil(int(self.total_number) / int(self.page_size))

    def paging(self):
        start = (int(self.page_index) - 1) * int(self.page_size)
        end = start + int(self.page_size)
        if len(self.queryset) < end:
            end = len(self.queryset)
        return self.queryset[start:end]

# flask_sqlalchemy分页器封装
class PagenatorFlaskSqlalchemy(object):
    """
    page_index: 页码，
    page_size: 每页条数，
    total_number: 总条数,
    total_page: 总页数,
    """
    def __init__(self, request_data, queryset=None):
        pageindex = request_data['page_index']
        pagesize = request_data['page_size']
        self.queryset = queryset
        if pageindex == '' and pagesize == '':
            self.pageindex = None
            self.pagesize = None
        else:
            self.pageindex = int(pageindex)
            self.pagesize = int(pagesize)

    def paging(self):
        pagequeryset = self.queryset.paginate(page=self.pageindex, per_page=self.pagesize, error_out=False)
        querysetlist = pagequeryset.items
        page_size = pagequeryset.per_page
        total_number = pagequeryset.total
        total_page = math.ceil(total_number / page_size)
        return querysetlist, total_number, total_page


class DateTimeFormat(object):
    '''
    时间各种格式转换
    '''
    def __init__(self,datetimestr, datetimes=None, datetimestr1=None, datetimestr2=None,today2Ndays=None):
        self.datetimestr = datetimestr
        self.datetimestr1 = datetimestr1
        self.datetimestr2 = datetimestr2
        self.datetimes = datetimes
        self.today2Ndays = today2Ndays

    def date2ymd(self):
        '''2017/11/10, 2017-11-10, 20171120 to year, month, days'''
        if "/" in self.datetimestr:
            year, month, days = self.datetimestr.split("/")
        elif "-" in self.datetimestr:
            year, month, days = self.datetimestr.split("-")
        else:
            new_datetimestr = str(datetime.strptime(self.datetimestr, '%Y%m%d'))
            new_datetimestrfrist = new_datetimestr.split(" ")[0]
            year, month, days = new_datetimestrfrist.split("-")
        return year, month, days


    def date2ymd2datetime(self):
        '''date2ymd to '2017-11-10 00:00:00  2017-11-10 23:59:59'''
        year, month, days = self.date2ymd()
        return "{}-{}-{} 00:00:00".format(year, month, days), "{}-{}-{} 23:59:59".format(year, month, days)


    def date2days(self):
        '''计算两个日期相差天数'''
        year1, month1, days1 = self.date2ymd()
        year2, month2, days2 = self.date2ymd()
        date1 = datetime.date(year1, month1, days1)
        date2 = datetime.date(year2, month2, days2)
        return (date1 - date2).days

    def date2delta(self):
        '''计算两个日期间隔'''
        d1 = datetime.strptime(self.datetimestr1, '%Y-%m-%d %H:%M:%S')
        d2 = datetime.strptime(self.datetimestr2, '%Y-%m-%d %H:%M:%S')
        delta = d1 - d2
        # 日期相差天数
        print (delta.days)
        # 日期间隔
        print (delta)
        return delta

    def str2datetime(self):
        '''将字符串转换为日期 string => datetime'''
        return datetime.strptime(self.datetimestr, '%Y-%m-%d %H:%M:%S')

    def datetime2str(self):
        '''将日期转化为字符串 datetime=> string'''
        if not self.datetimes:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            now = self.datetimes.strftime('%Y-%m-%d %H:%M:%S')
        return now

    def todayNdays(self):
        '''今天的n天后的日期'''
        if not self.datetimestr:
            now = datetime.now()
            delta = datetime.timedelta(days=self.today2Ndays)
            n_days = now + delta
            print (n_days.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            n_days = self.datetimestr + datetime.timedelta(days=self.today2Ndays)
            print(n_days.strftime('%Y-%m-%d %H:%M:%S'))
        return n_days.strftime('%Y-%m-%d %H:%M:%S')



