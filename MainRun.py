import time
import Kline_quantity
import old_recommend_stock
import function_test
import logging.config

def run():
    logging.config.fileConfig('logging_conf.conf')
    logger_cons = logging.getLogger("outputlog")
    logger_file = logging.getLogger("outputfile")

    start_test = time.time()
    logger_cons.debug("测试开始")
    istrue = function_test.main_run()
    logger_cons.debug("测试结束")
    logger_cons.debug("测试耗时:{0}".format(str(time.time()-start_test)))

    if istrue == True:
        logger_cons.debug("开始爬取分析")
        start_analyze = time.time()
        # 需要立刻判断(周五尾盘十分钟) 输入 now 参数 周数可以以后扩展
        Kline_quantity.Kline_run(week_now_or_lately='lately',get_data_num=7)
        findal_count_dict = old_recommend_stock.final_count()
        logger_cons.debug(findal_count_dict)
        max_count = max(findal_count_dict.values())
        for key, value in findal_count_dict.items():
            if value == max_count:
                logger_cons.debug("明日推荐股票:" + str(key))
                logger_file.debug("明日推荐股票:" + str(key))

        logger_cons.debug("爬取分析耗时:{0}".format(str(time.time()-start_analyze)))
    else:
        logger_cons.warning("系统无法运行")
        logger_file.warning("系统无法运行")

if __name__ == "__main__":
    run()
    # 测试有点慢 可以改进
