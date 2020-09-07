import requests,random,re,json,time
from parsel import Selector
from typing import List, Any, Tuple,Dict
import asyncio,aiohttp
from urllib.parse import urlencode

# 推荐股票判断
class Recommend_stock(object):

    # 请求网页
    __headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }
    # 异步请求
    async def recom_async(self, url: str,enco_type) -> str:
        async with aiohttp.request("GET", url, headers=self.__headers) as r:
            response = await r.text(encoding=enco_type)
            if r.status == 200:
                return response
            else:
                return "请求页面状态不是200"
    # 普通请求
    def resp_text(self,url) -> str:

        resp = requests.get(url=url,headers=self.__headers)
        if resp.status_code == 200:
            return resp.text
        else:
            return "访问页面失败"

    def spider_dfcf(self) -> List:
        zijin_url_list = []
        url = "http://guba.eastmoney.com/remenba.aspx?type=1"
        rtext = self.resp_text(url)
        se = Selector(rtext)
        remen_stock_url = se.xpath("//div[@class='zhutibarlist']/ul/li/a/text()").getall()  # (002400)省广集团吧
        # 获取热门股票的代码
        stock_num_list = []
        for each_storck_num in remen_stock_url:
            stock_num = re.findall(r'(\d{6})', str(each_storck_num))
            stock_num_list.append(stock_num[0])

        for each_stock_num in stock_num_list:
            # 网站需要时间截
            tm1 = str(int(time.time())) + str(random.randint(500, 900))
            # 开头代码的变换
            if each_stock_num.startswith('0'):
                self.secid = '0.'+ str(each_stock_num)
            elif each_stock_num.startswith('6'):
                self.secid = '1.'+ str(each_stock_num)
            elif each_stock_num.startswith('3'):
                self.secid = '0.' + str(each_stock_num)
            '''
            这里有个bug没去弄 有的热门股票时间是两个月前的 但照样爬取了
            判断股票是否有近10天的资金流
            2020-6-29 连续三天同一只股票 将记录的时间减少至5天
            '''
            zijin_url = 'http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid={0}&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18303934775415802567_{1}&_={2}'.format(self.secid,str(tm1),str(int(tm1)+2))

            # 获取东方财富资金流
            zijin_url_list.append(zijin_url)
        return zijin_url_list

    # 暂时只有短线长胜推荐 没有帖子没有中长
    def spider_tgb(self)-> Any:
        tgb_recomshort_stock_list = [] # 装载短线长胜推荐股
        tgb_recomweek_stock_list = [] # 装载一周长胜推荐股
        # 短线长胜
        tgb_recomshort_stock_url = 'https://www.taoguba.com.cn/getChangShengData?rType=1&_={0}'.format(str(int(time.time()))+str(random.randint(600,900)))
        tgb_shorttext = self.resp_text(tgb_recomshort_stock_url)
        json_tgbshort_stock = json.loads(tgb_shorttext)

        for each_dto in json_tgbshort_stock.get('dto'):
            tgb_recom_stock  = re.findall(r'(.+)\(', str(each_dto['stock']))[0]
            tgb_recomshort_stock_list.append(tgb_recom_stock)
        # 一周长胜
        tgb_recomweek_stock_url = 'https://www.taoguba.com.cn/getChangShengData?rType=2&_={0}'.format(str(int(time.time()))+str(random.randint(600,900)))
        tgb_weektext = self.resp_text(tgb_recomweek_stock_url)
        json_tgbweek_stock = json.loads(tgb_weektext)

        for each_dto in json_tgbweek_stock.get('dto'):
            tgb_recomweek_stock  = re.findall(r'(.+)\(', str(each_dto['stock']))[0]
            tgb_recomweek_stock_list.append(tgb_recomweek_stock)

        return tgb_recomshort_stock_list,tgb_recomweek_stock_list

    def spider_ths(self)->Any:
        jigou_url_list = ['http://data.10jqka.com.cn/market/lhbyyb/orgcode/HXZQYXZRGSSHFGS/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/HTZQGFYXGSZB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/SGTZY/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/ZGYHZQGFYXGSSMMHLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/GTJAZQGFYXGSSHJSLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/HGTZY/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/ZGYHZQGFYXGSSXZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/GTJAZQGFYXGSNJTPNLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/ZSZQGFYXGSSZSNDLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/HTZQGFYXGSTYTYLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/HTZQGFYXGSHNFGS/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/SWHYZQYXGSSHMXQDCLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          'http://data.10jqka.com.cn/market/lhbyyb/orgcode/ZGYHZQGFYXGSHZQCLZQYYB/field/ENDDATE/order/desc/page/{0}',
                          ]
        # 获取1页 因日期需选最当前的 后期可改
        PAGE = 1
        # 这个网站为gbk编码
        enco_type = 'gbk'
        tasks = [self.recom_async(each_url.format(str(PAGE)),enco_type=enco_type) for each_url in jigou_url_list]
        event_loop = asyncio.get_event_loop()
        response = event_loop.run_until_complete(asyncio.gather(*tasks))
        event_loop.close()
        return response

    def spider_thsmn(self)->Any:
        base_url = "http://t.10jqka.com.cn/trace/trade/getLastEnOrHold/?"
        time_test = time.strftime("%Y%m%d", time.localtime())

        stock_name_list = [] # 装载股票名
        stock_BS_list = [] # 装载BS
        stock_BS_times_list = [] # 装载BS次数

        # http://t.10jqka.com.cn/trace/trade/getLastEnOrHold/?zidStr=60503016,44983608,36010761,56395121,58626061,40787461,47391107,62884256,25869277,37401557
        # 获取账户名
        for page in range(1,4):
            search_people_url = "http://t.10jqka.com.cn/trace/?page={0}&order=weight&show=pic".format(page)
            text = self.resp_text(search_people_url)
            se = Selector(text)
            people_num = se.xpath("//div[@id='sortshowtable']/ul/li/@data-zid").getall()
            data = {'zidStr': ','.join([each_num for each_num in people_num])}
            new_url = base_url + urlencode(data) + '.html'
            # 再次请求
            response_text = self.resp_text(new_url)
            json_moni = json.loads(response_text)
            result_moni = json_moni.get("result")

            for each_count_num in people_num:
                each_stock_mesg = result_moni.get(each_count_num)
                if each_stock_mesg:
                    # 上传时间
                    updata_time = each_stock_mesg['wtrq']
                    # 股票名
                    stock_name = each_stock_mesg['zqmc']
                    # 买卖
                    BS = each_stock_mesg['mmlb']
                    # 股数
                    stock_times = each_stock_mesg['wtsl']
                    if updata_time == time_test:
                        stock_name_list.append(stock_name)
                        stock_BS_list.append(BS)
                        stock_BS_times_list.append(stock_times)
                    else:
                        pass
        return stock_name_list,stock_BS_list,stock_BS_times_list

#返回数据处理
class Data_manage(object):
    # 基本设置
    __headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }
    # 实例化
    __r = Recommend_stock()


    async def data_async(self,url: str)->str :
        async with aiohttp.request("GET", url,headers=self.__headers) as r:
            response = await r.text(encoding='utf-8')
            if r.status == 200:
                return response
            else:
                return "请求页面状态不是200"

    def DFCF_DATA(self)-> Dict:
        # 名字，
        global stock_name,stock_klines
        name_zijin_dict = {}

        def calculate_jzb(zijin_type,jzb_list:List) -> float:
            global times
            jzb_count = 0
            stock_count = 0
            # 获得资金流类型
            if zijin_type == 'zhuli':
                times = 5
            elif zijin_type == 'chaoda':
                times = 4
            elif zijin_type == 'dadan':
                times = 3
            elif zijin_type == 'zhongdan':
                times = 2
            elif zijin_type == 'xiaodan':
                times = 1
            for each_jzb in jzb_list:
                jzb_count += float(each_jzb)
            # 得出某个类型的资金流入分数 判断
            if jzb_count > 0:
                stock_count = 0.5 * times
            elif jzb_count < 0:
                stock_count = -0.5 * times
            else:
                pass
            # 返回一次资金流的统计(如果为主力 则返回主力资金流的分数统计)
            return stock_count

        zijin_url_list = self.__r.spider_dfcf()
        # 异步获取网页内容
        tasks = [self.data_async(each_url) for each_url in zijin_url_list]
        event_loop = asyncio.get_event_loop()
        response = event_loop.run_until_complete(asyncio.gather(*tasks))

        for each_data in response:
           #  小单，中单，大单，超大，主力净占比
            xiaodan_jzb_list = []
            zhongdan_jzb_list = []
            dadan_jzb_list = []
            chaoda_jzb_list = []
            zhuli_jzb_list = []

            re_zijin = re.findall(r'jQuer.+\((.+)\)', str(each_data))
            json_zijin = json.loads(re_zijin[0]).get("data")
            if json_zijin :
                stock_name = json_zijin.get("name")
                stock_klines = json_zijin.get("klines")
            # 判断热门股是否为当前的而不是几个月前的
            now_data_test = stock_klines[-1].split(',')[0]
            now_data = time.strftime("%Y-%m-%d", time.localtime())
            # print(stock_name,now_data_test,now_data,now_data==now_data_test)
            if now_data_test == now_data:
                day_test = len(stock_klines)
               # 判断有没那么多天
                if day_test < 5:
                   day_end = None
                else:
                    day_end = day_test - 6
                for each_zijin in stock_klines[len(stock_klines):day_end:-1]:
                    zijinliu = each_zijin.split(',')
                    zhuli_jzb = zijinliu[6]
                    chaoda_jzb = zijinliu[10]
                    dadan_jzb = zijinliu[9]
                    zhongdan_jzb = zijinliu[8]
                    xiaodan_jzb = zijinliu[7]

                    zhuli_jzb_list.append(zhuli_jzb)
                    chaoda_jzb_list.append(chaoda_jzb)
                    dadan_jzb_list.append(dadan_jzb)
                    zhongdan_jzb_list.append(zhongdan_jzb)
                    xiaodan_jzb_list.append(xiaodan_jzb)

                zhuli_count = calculate_jzb('zhuli',zhuli_jzb_list)
                chaoda_count = calculate_jzb('chaoda',chaoda_jzb_list)
                dadan_count = calculate_jzb('dadan',dadan_jzb_list)
                zhongdan_count = calculate_jzb('zhongdan',zhongdan_jzb_list)
                xiaodan_count = calculate_jzb('xiaodan',xiaodan_jzb_list)
                all_count = zhuli_count+chaoda_count+dadan_count+zhongdan_count+xiaodan_count
                name_zijin_dict[stock_name] = all_count
                    # 一次可以传入 一个股票的近5天所有资金流
        return name_zijin_dict

    def TGB_DATA(self)->Any:
       tgb_recomshort_stock_list,tgb_recomweek_stock_list = self.__r.spider_tgb()
       return tgb_recomshort_stock_list,tgb_recomweek_stock_list

    def THS_DATA(self)->Dict:
        # 日期设置期限 (同花顺)
        time_test = time.strftime("%Y-%m-%d", time.localtime())
        # 名+净额字典
        name_jinge_dict = {}

        ths_response_list = self.__r.spider_ths()
        for each_ths_response in ths_response_list:
            se = Selector(each_ths_response)
            for each_table in se.xpath("//div[@class='zdph']/table"):
                date = each_table.xpath("//td[1]/text()").get()
                stock_name = each_table.xpath("//td[2]/a/text()").get()
                jinge = each_table.xpath("//td[7]/text()").get()
                if date != time_test:
                    pass
                else:
                    name_jinge_dict[stock_name] = jinge

        return name_jinge_dict

    def THSMN_DATA(self)->List:
        name_BS_times_list = []
        stock_name_list, stock_BS_list, stock_BS_times_list = self.__r.spider_thsmn()
        for name_BS_times in zip(stock_name_list, stock_BS_list, stock_BS_times_list):
            name_BS_times_list.append(name_BS_times)
        return name_BS_times_list

#最终结果筛选
def final_count()->Dict:
    # 得出整数并统计
    final_dict = {}
    __d = Data_manage()
    # 东方财富数据
    name_zijin_dict = __d.DFCF_DATA()
    # 淘股吧数据
    tgb_recomshort_stock_list, tgb_recomweek_stock_list = __d.TGB_DATA()
    # 同花顺数据
    name_jinge_dict = __d.THS_DATA()
    # 同花顺模拟数据
    name_BS_times_list = __d.THSMN_DATA()


    # 淘股吧判断
    for key in name_zijin_dict.keys():
        if key in tgb_recomshort_stock_list:
            name_zijin_dict[key] += 1.5
        if key in tgb_recomweek_stock_list:
            name_zijin_dict[key] += 1.2

    # 同花顺判断
    for key in name_jinge_dict.keys():
        if key in name_zijin_dict.keys() and float(name_jinge_dict[key]) > 0:
            name_zijin_dict[key] += 1.5
        elif key in name_zijin_dict.keys() and float(name_jinge_dict[key]) < 0:
            name_zijin_dict[key] -= 1.5
        elif key not in name_zijin_dict.keys() and  float(name_jinge_dict[key]) > 0:
            name_zijin_dict[key]  = 1.5
        elif key not in name_zijin_dict.keys() and  float(name_jinge_dict[key]) < 0:
            name_zijin_dict[key] = -1.5


    # 同花顺模拟判断
    for each_data in name_BS_times_list:
        if each_data[0] in name_zijin_dict.keys():
            # 买入
            if each_data[1] == 'B':
                if int(each_data[2]) >= 1000:
                    name_zijin_dict[each_data[0]] += 1
                elif int(each_data[2]) >= 10000:
                    name_zijin_dict[each_data[0]] += 1.5
            # 卖出
            elif each_data[1] == 'S':
                if int(each_data[2]) >= 1000:
                    name_zijin_dict[each_data[0]] -= 1
                if int(each_data[2]) >= 10000:
                    name_zijin_dict[each_data[0]] -= 1.5

    # 最后选出正数
    for each_key,each_value in name_zijin_dict.items():
        if each_value > 0:
            final_dict[each_key] = each_value

    return final_dict


if __name__ == "__main__":
    d = Data_manage()
    r = Recommend_stock()
    name_zijin_dict = d.DFCF_DATA()
    tgb_recomshort_stock_list, tgb_recomweek_stock_list = d.TGB_DATA()
    name_jinge_dict = d.THS_DATA()
    name_BS_times_list = d.THSMN_DATA()
    print("DFCF:",name_zijin_dict)
    print("tgb",tgb_recomshort_stock_list, tgb_recomweek_stock_list)
    print("ths:",name_jinge_dict)
    print("thsmn",name_BS_times_list)
    test_xian = final_count()
    # print("test_xian:",test_xian)



