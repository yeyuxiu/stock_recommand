import requests,random,re,json,time
from parsel import Selector
from urllib.parse import urlencode
import threading

''' # 需要测试的url

#东方财富股吧热门
https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=1&secid=1.601216&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery183029592335505013323_1597046430980&_=1597046431346
#东方财富上证
https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery112408042166051909181_1597046551102&secid=1.000001&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58&klt=102&fqt=0&beg=19900101&end=20220101&_=1597046551105
# 同花顺模拟
http://t.10jqka.com.cn/trace/trade/getLastEnOrHold/?zidStr=60503016%2C44983608%2C36010761%2C56395121%2C58626061%2C40787461%2C47391107%2C62884256%2C25869277%2C37401557
# 同花顺机构
http://data.10jqka.com.cn/market/lhbyyb/orgcode/HXZQYXZRGSSHFGS/field/ENDDATE/order/desc/page/1
# 淘股吧
https://www.taoguba.com.cn/getChangShengData?rType=4&_=1597046647969

'''
class Test_after_run(object):
    __tm1 = str(int(time.time())) + str(random.randint(500, 900))
    __headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }

    def resp_text(self,url,url_name) -> str:

        resp = requests.get(url=url,headers=self.__headers)
        if resp.status_code == 200:
            return resp.text
        else:
            return url_name+"/访问页面返回不是200"

    def dfcf_test(self):

        dfcf_gb_fir = "http://guba.eastmoney.com/remenba.aspx?type=1"
        dfcf_gb_text = self.resp_text(url=dfcf_gb_fir,url_name='东方财富热门股首页')
        dfcf_gb_se = Selector(dfcf_gb_text)
        if not dfcf_gb_se.xpath("//ul[@class='list clearfix']/li"):
            return "东方财富股吧首页热门股板块xpath错了"
        if dfcf_gb_se.xpath("//ul[@class='list clearfix']/li/a/@href"):
            each_storck_num = dfcf_gb_se.xpath("//ul[@class='list clearfix']/li/a/@href").get()
            stock_num = re.findall(r'(\d{6})', str(each_storck_num))[0]
            if stock_num.startswith('0'):
                self.secid = '0.'+ str(stock_num)
            elif stock_num.startswith('6'):
                self.secid = '1.'+ str(stock_num)
            elif stock_num.startswith('3'):
                self.secid = '0.' + str(stock_num)
        else:
            return "东方财富热门股url_xpath错了"

        # 东方财富热门股资金
        zijin_url = 'http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid={0}&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18303934775415802567_{1}&_={2}'.format(
            self.secid, str(self.__tm1), str(int(self.__tm1) + 2))
        dfcf_zijin_text = self.resp_text(url=zijin_url,url_name='东方财富股票资金流页')

        re_zijin = re.findall(r'jQuer.+\((.+)\)', str(dfcf_zijin_text))
        json_zijin = json.loads(re_zijin[0]).get("data")
        stock_name = json_zijin.get("name")
        if stock_name:
            pass
        else:
            return "东方财富资金页api找不到数据"

    def tgb_test(self):
    # 淘股吧
        for type in range(1,3):
            tb_url = "https://www.taoguba.com.cn/getChangShengData?rType={0}&_={1}".format(str(type),self.__tm1)
            tgb_text = self.resp_text(url=tb_url, url_name='淘股吧长胜页')
            json_tgbweek_stock = json.loads(tgb_text)
            if json_tgbweek_stock.get("status") != True:
                return "淘股吧荐股api出错"


    def ths_test(self):
        #同花顺机构
        jigou_url_list = [
            'http://data.10jqka.com.cn/market/lhbyyb/orgcode/HXZQYXZRGSSHFGS/field/ENDDATE/order/desc/page/{0}',
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
        for each_url in jigou_url_list:
            ths_text = self.resp_text(url=each_url.format('1'),url_name="同花顺机构")
            if not ths_text:
                return "同花顺机构url出问题"

    def dfcf_sz_test(self):
        # 东方财富上证数据
        base_K_url = "http://push2his.eastmoney.com/api/qt/stock/kline/get?"  # 原始网址
        # 两个时间截
        klt = 102
        tm_sz1 = str(int(time.time())) + str(random.randint(500, 900))
        tm_sz2 = str(int(time.time())) + str(random.randint(500, 800))
        # path数据
        data = {
            'cb': 'jQuery1124016114332960306132_' + tm_sz1,
            'secid': '1.000001',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
            'klt': str(klt),
            'fqt': '0',
            'beg': '19900101',
            'end': '20220101',
            '_': tm_sz2,
        }
        dfcf_sz_url = base_K_url + urlencode(data)
        dfcf_sz_text = self.resp_text(url=dfcf_sz_url,url_name="东方财富上证周k api")
        re_szk = re.findall(r'jQuer.+\((.+)\)', str(dfcf_sz_text))
        json_szk = json.loads(re_szk[0]).get("data").get("name")
        if not json_szk == "上证指数":
            return "东方财富上证k线api出问题"

    def thsmn_test(self):
        # 同花顺模拟
        thsmn_base_url = "http://t.10jqka.com.cn/trace/trade/getLastEnOrHold/?"
        search_people_url = "http://t.10jqka.com.cn/trace/?page={0}&order=weight&show=pic".format(1)
        thsmn_text = self.resp_text(url=search_people_url,url_name="同花顺模拟页")
        thsmn_se = Selector(thsmn_text)
        people_num = thsmn_se.xpath("//div[@id='sortshowtable']/ul/li/@data-zid").getall()
        if not people_num:
            return "同花顺模拟获取用户账号出问题"
        data = {'zidStr': ','.join([each_num for each_num in people_num])}
        thsmn_url = thsmn_base_url + urlencode(data) + '.html'
        response_text = self.resp_text(url=thsmn_url,url_name="同花顺模拟url")
        json_moni = json.loads(response_text).get("isT")

        if json_moni != True:
            return "同花顺模拟出问题"

def main_run():
    t = Test_after_run()
    t.dfcf_test()
    t.tgb_test()
    t.dfcf_sz_test()
    t.ths_test()
    t.thsmn_test()
    # t = Test_after_run()
    # # 创建线程
    # thread_dfcf = threading.Thread(target=t.dfcf_test)
    # thread_tgb = threading.Thread(target=t.tgb_test)
    # thread_ths = threading.Thread(target=t.ths_test)
    # thread_dfcf_sz = threading.Thread(target=t.dfcf_sz_test)
    # thread_thsmn = threading.Thread(target=t.thsmn_test)
    # # 启动线程
    # thread_dfcf_sz.start()
    # thread_ths.start()
    # thread_tgb.start()
    # thread_dfcf.start()
    # thread_thsmn.start()
    # # 等所有线程结束再运行主程序
    # thread_dfcf.join()
    # thread_tgb.join()
    # thread_thsmn.join()
    # thread_dfcf_sz.join()
    # thread_ths.join()

    istrue = True
    if istrue == True:
        return True

if __name__ == "__main__":
    start = time.time()
    main_run()
    print("end:",time.time()-start)













