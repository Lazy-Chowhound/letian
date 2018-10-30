import requests
from lxml import etree
from selenium import webdriver
import time
import Connection


class LeTian():
    def __init__(self):
        self.url = 'http://chn.lottedfs.com/kr'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}
        self.urls = []
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.database = Connection.ConnectDatabase()

    def get_url(self):
        """
        获取每种商品页面的url
        :return:
        """
        html = requests.get(self.url, headers=self.headers)
        doc = etree.HTML(html.text)
        init_urls = []
        # 获取每个分类
        list = doc.xpath('//*[@id="mainCateInfo"]/li')
        for item in list:
            # 获取每个分类下的每个区域
            areas = item.xpath('div/div/div/dl')
            for area in areas:
                # 去除区域名称
                stuff_lists = area.xpath('dd')
                # 获取每条url
                for stuff in stuff_lists:
                    url = stuff.xpath('a/@href')
                    init_urls.append(url)
        # 将url转换为字符串形式补充完整
        for url_list in init_urls:
            for url in url_list:
                url = str(url)
                if not url.startswith('http'):
                    url = 'http://chn.lottedfs.com' + url
                self.urls.append(url)

    def get_stuff(self, url):
        """
        获取每个url里的商品信息
        :param url:
        :return:
        """
        self.browser.get(url)
        time.sleep(2)
        # 所有商品信息
        info = []
        # 总页数
        count = 0
        # 当前页数
        page = 1
        links = self.browser.find_element_by_class_name('paging').find_elements_by_tag_name('a')
        for link in links:
            count = count + 1
        # 获取每一页的数据
        while page <= count:
            print('正在爬取 ' + url + ' 第' + str(page) + '页 ' + '共' + str(count) + '页')
            commodities = self.browser.find_element_by_id('prdList').find_elements_by_class_name('productMd')
            for commodity in commodities:
                commodity_info = []
                chinese_name = commodity.find_element_by_class_name('brand').find_element_by_tag_name('strong').text
                all_name = commodity.find_element_by_class_name('brand').text
                english_name = self.string_minus(chinese_name, all_name).strip()
                profile = commodity.find_element_by_class_name('product').text
                try:
                    dollars = commodity.find_element_by_class_name('cancel').text
                    discount = commodity.find_element_by_class_name('off').text
                except Exception:
                    try:
                        dollars = commodity.find_element_by_class_name('fc9').text
                        discount = ' '
                    except Exception:
                        dollars = commodity.find_element_by_class_name('price').find_element_by_tag_name('span').text
                        discount = ' '
                discount_price = commodity.find_element_by_class_name('discount').find_element_by_tag_name(
                    'strong').text
                RMB = commodity.find_element_by_class_name('discount').find_element_by_tag_name('span').text
                if not chinese_name == '':
                    commodity_info.append(chinese_name)
                    commodity_info.append(english_name)
                    commodity_info.append(profile)
                    commodity_info.append(dollars)
                    commodity_info.append(discount)
                    commodity_info.append(discount_price)
                    commodity_info.append(RMB)
                    info.append(commodity_info)
            page = page + 1
            if page > count:
                break
            elif page % 10 == 1:
                self.browser.find_element_by_link_text('Next').click()
            else:
                self.browser.find_element_by_link_text(str(page)).click()
            time.sleep(2)
        self.database.multi_insert(info)

    def connect_database(self):
        """
        连接数据库
        :return:
        """
        self.database.open_connection()

    def close_database(self):
        """
        关闭数据库
        :return:
        """
        self.database.close_connection()

    def __del__(self):
        self.browser.close()

    def string_minus(self, s1, s2):
        """
        实现s2-s1
        :param s1:
        :param s2:
        :return:
        """
        result = s2.replace(s1, '', 1)
        if result == '':
            return s2
        else:
            return result


if __name__ == '__main__':
    start_time = time.time()
    lt = LeTian()
    lt.connect_database()
    # lt.get_url()
    # for url in lt.urls:
    lt.get_stuff('http://chn.lottedfs.com/kr/display/category/third?dispShopNo1=1200001&dispShopNo2=1200002&dispShopNo3=1200004&treDpth=3')
    lt.close_database()
    print('共耗时' + str(time.time() - start_time) + 's')
