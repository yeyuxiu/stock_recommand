# 大盘日k分析
import requests
import re, time, random, json
from urllib.parse import urlencode
from typing import List, Any, Tuple
import logging.config

class _K_lines_test(object):
    # klt参数从 101 开始 {101:日k} {102:周k} {103:月k} {5:5分k} {15:15分k} {30:30分k}

    # 默认开启最近模式
    def __init__(self,week_now_or_lately='lately'):
        self.week_now_or_lately = week_now_or_lately
        super().__init__()

    # 获取网页函数
    def resp_url(self,klt: int) -> str:
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        }
        base_K_url = "http://push2his.eastmoney.com/api/qt/stock/kline/get?"  # 原始网址
        # 两个时间截
        tm1 = str(int(time.time())) + str(random.randint(500, 900))
        tm2 = str(int(time.time())) + str(random.randint(500, 800))
        # path数据
        data = {
            'cb': 'jQuery1124016114332960306132_' + tm1,
            'secid': '1.000001',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
            'klt': str(klt),
            'fqt': '0',
            'beg': '19900101',
            'end': '20220101',
            '_': tm2,
        }
        url = base_K_url + urlencode(data)
        resp = requests.get(url=url, headers=headers)
        if resp.status_code == 200:
            # 返回1990-2022 所有股市数据
            return resp.text
        else:
            return "访问页面失败"

    # 处理返回数据得出需要的列表
    def back_data(self,lately_data: List) -> Tuple:
        quantity_list = []  # 装载量
        price_list = []  # 价格装载 涨为+ 负为跌
        up_over_list = []  # 装载上引线
        down_over_list = []  # 装载下引线

        def testtest(price_over_up,price_over_down):
            if price_over_up:
                up_over_list.append(round(price_over_up,2))
            else:
                up_over_list.append(0)
            if price_over_down:
                down_over_list.append(round(price_over_down,2))
            else:
                down_over_list.append(0)

        for each_week_data in lately_data:
            s_data = each_week_data.split(',')
            # 获取量 return : list(*int)
            quantity_list.append(int(s_data[-3]))
            #  时间         开盘    收盘     最高    最低     成交量    成交额           振幅
            # 获取(收-开) + 涨 - 跌 return:list(*float)
            price = float(s_data[2]) - float(s_data[1])
            price_list.append(round(price,2))

            if price > 0 :
                # 获取上影线(最高-收盘) +
                price_over_up = float(s_data[3]) - float(s_data[2])

                # 获取下影线 (开盘-最低) +
                price_over_down = float(s_data[1]) - float(s_data[-4])
                # 装载
                testtest(price_over_up,price_over_down)

            elif price < 0 :
                # 获取上影线(最高-开盘) +
                price_over_up = float(s_data[3]) - float(s_data[1])
                # 获取下影线(收盘 - 最低) +
                price_over_down = float(s_data[2]) - float(s_data[-4])
                testtest(price_over_up, price_over_down)
            # 平
            else:
                # 获取上影线(最高-收盘) +
                price_over_up = float(s_data[3]) - float(s_data[2])
                # 获取下影线 (开盘-最低) +
                price_over_down = float(s_data[1]) - float(s_data[-4])
                testtest(price_over_up, price_over_down)

        return quantity_list, price_list, up_over_list, down_over_list

    # 102 获取总结好的周数据
    def Week_test(self,get_data_num: int) -> Tuple:

        # 102 获取周数据
        resp_text = self.resp_url(klt=102)
        re_szk = re.findall(r'jQuer.+\((.+)\)', str(resp_text))
        json_szk = json.loads(re_szk[0]).get("data").get("klines")

        # 最近模式 忽略正在运行的单位
        if self.week_now_or_lately == 'lately':
            # 判断最新的一次是不是 完整的一周
            if time.strftime('%w') != 5 or time.strftime('%w') != 6 or time.strftime('%w') != 7:  # 7可能要改
                # 获取近8周k数据 返回列表
                lately_data = json_szk[len(json_szk) - 1:len(json_szk) - (get_data_num) - 1:-1]
                quantity, price_up_down, up_over_price, down_over_price = self.back_data(lately_data=lately_data)
                return quantity, price_up_down, up_over_price, down_over_price
            else:
                lately_data = json_szk[len(json_szk):len(json_szk) - get_data_num:-1]
                quantity, price_up_down, up_over_price, down_over_price = self.back_data(lately_data=lately_data)
                return quantity, price_up_down, up_over_price, down_over_price

        # 现在模式 立刻判断(适合最后一个时间点去判断 例如:周五最后十分钟)
        elif self.week_now_or_lately == 'now':
            lately_data = json_szk[len(json_szk):len(json_szk) - get_data_num:-1]
            quantity, price_up_down, up_over_price, down_over_price = self.back_data(lately_data=lately_data)
            return quantity, price_up_down, up_over_price, down_over_price

    # 单纯量判断(适合不是连阴连阳的局面)(格局为4)(能力 : 断续阳阴)
    def quantity_4_test(self,quantity_list: List) -> str:

        # 连涨(量)统计        # 连跌(量)统计
        quantity_up_count = quantity_down_count = 0


        # 方法1 只判断前4个
        for each_data_num in range(2, -1, -1):

            if quantity_down_count > 1 and quantity_list[each_data_num + 1] - quantity_list[each_data_num] <= 0:
                return "下周超买"
                # 后量 - 前量 突然增量
            elif quantity_up_count > 1 and quantity_list[each_data_num + 1] - quantity_list[each_data_num] >= 0:
                return "下周超卖"
            elif quantity_down_count > 1:
                return "下周买"
            elif quantity_up_count > 1:
                return "下周卖"
            # 后量 - 前量 为 +
            # 210
            if quantity_list[each_data_num + 1] - quantity_list[each_data_num] > 0:
                if quantity_up_count > 0 and quantity_list[each_data_num + 1] - quantity_list[each_data_num] < 0:
                    quantity_down_count = 0
                else:
                    quantity_down_count += 1
            # 后量 - 前量 为 -
            elif quantity_list[each_data_num + 1] - quantity_list[each_data_num] < 0:
                if quantity_down_count > 0 and quantity_list[each_data_num + 1] - int(quantity_list[each_data_num]) > 0:
                    quantity_up_count = 0
                else:
                    quantity_up_count += 1
            else:
                pass
        # print("up_count:%s"%quantity_up_count,"down_count:%s"%quantity_down_count)
        return "无法判断"

    # 纯价格判断 (格局为7)(判断3-5-7) (能力: 连涨连阳，断续不能判断)
    def price_7_test(self, price_list:List , up_over_list:List , down_over_list:List ) -> Any:
        '''
        :param price_list: [21.86, 99.62, -47.14, -165.26, 195.48, 179.73, 12.65]
        :param up_over_list:[38.66, 23.78, 138.07, 79.4, 73.65, 0, 3.89]
        :param down_over_list: [24.47, 35.73, 11.81, 32.86, 0, 21.31, 17.05]
        :return:
        '''

        # 上下影线均数
        up_over_avg = round(sum(up_over_list) / float(len(up_over_list)),2)

        down_over_avg = round(sum(down_over_list) / float(len(down_over_list)),2)

        # 连涨 连跌判断

        # 连涨(指数)统计 # 连跌(指数)统计
        price_up_count = price_down_count = 0
        # 最近 为 +
        if price_list[0] > 0 :
            for each_price in price_list[::-1]:
                if each_price > 0:
                    price_up_count += 1
                elif each_price < 0:
                    price_up_count = 0
            # 连跌突然涨
            for each_price in price_list[:0:-1]:
                if each_price < 0:
                    price_down_count += 1
                elif each_price > 0:
                    price_down_count = 0
            if price_down_count >= 3:
               return "连跌转阳买"
            elif price_down_count > 3:
                return "连跌转阳超买"

        elif price_list[0] <0 :
            for each_price in price_list[::-1]:
                if each_price < 0:
                    price_down_count += 1
                elif each_price > 0:
                    price_down_count = 0
            # 连涨突然跌
            for each_price in price_list[:0:-1]:
                if each_price > 0:
                    price_up_count += 1
                elif each_price < 0:
                    price_up_count = 0
            if price_up_count >= 3:
                return "连涨转阴卖"
            elif price_up_count >3 :
                return "连涨转阴超卖"
        # 十字星
        else:
            return "顶/底出现平 -> 卖/买"
        # print(price_up_count,price_down_count)

        #  2. 在连涨连跌的情况下添加上下影线

        # 连涨情况
        # price_down_count,price_up_count
        if price_up_count >= 3 and up_over_list[0] > up_over_avg :
            sale_count_test = 2
            return "卖出系数(1-3) : %d"%sale_count_test

        # 连跌情况
        elif price_down_count >= 3 and down_over_list[0] > down_over_avg:
            buy_count_test = 2
            return "买入系数(1-3) : %d" % buy_count_test
        else:
            return "无法判断"

        # 倒锤子线判断


def Kline_run(week_now_or_lately:str,get_data_num:int):
    logging.config.fileConfig('logging_conf.conf')
    logger_cons = logging.getLogger("outputlog")
    logger_file = logging.getLogger("outputfile")

    # 立刻判断还是最近的判断(周五收盘前)
    k_test = _K_lines_test(week_now_or_lately=week_now_or_lately)

    try:
        quantity_list, price_list, up_over_list, down_over_list = k_test.Week_test(get_data_num=get_data_num)
        # print('上证指数(周k) 纯量判断 : '+ k_test.quantity_4_test(quantity_list))
        # print('上证指数(周k) 纯价判断 : '+ k_test.price_7_test(price_list=price_list, up_over_list=up_over_list, down_over_list=down_over_list))

        logger_cons.debug('上证指数(周k) 纯量判断 : '+ k_test.quantity_4_test(quantity_list))
        logger_cons.debug('上证指数(周k) 纯价判断 : '+ k_test.price_7_test(price_list=price_list, up_over_list=up_over_list, down_over_list=down_over_list))
        logger_file.debug('上证指数(周k) 纯量判断 : '+ k_test.quantity_4_test(quantity_list))
        logger_file.debug('上证指数(周k) 纯价判断 : '+ k_test.price_7_test(price_list=price_list, up_over_list=up_over_list, down_over_list=down_over_list))
    except IndexError as e:
        logger_cons.error("填入至少四周")

if __name__ == "__main__":
    Kline_run(week_now_or_lately='lately',get_data_num=7)