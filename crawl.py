import requests
from lxml import etree
from selenium import webdriver
import pymysql


class letian():
    def __init__(self):
        self.url = 'http://chn.lottedfs.com/kr'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}
        self.urls = []
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.connection = None
        self.cursor = None

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
        print(self.urls)

    def get_stuff(self, url):
        """
        获取每个url里的商品信息
        :param url:
        :return:
        """
        self.browser.get(url)
        commodities = self.browser.find_element_by_id('prdList').find_elements_by_class_name('productMd')
        for commodity in commodities:
            chinese_name = commodity.find_element_by_class_name('brand').find_element_by_tag_name('strong').text
            all_name = commodity.find_element_by_class_name('brand').text
            english_name = self.string_minus(chinese_name, all_name).strip()
            profile = commodity.find_element_by_class_name('product').text
            try:
                dollars = commodity.find_element_by_class_name('cancel').text
                discount = commodity.find_element_by_class_name('off').text
            except Exception:
                dollars = commodity.find_element_by_class_name('fc9').text
                discount = ' '
            discount_price = commodity.find_element_by_class_name('discount').find_element_by_tag_name('strong').text
            RMB = commodity.find_element_by_class_name('discount').find_element_by_tag_name('span').text
            try:
                self.cursor.execute("INSERT INTO letian VALUES (%s,%s,%s,%s,%s,%s,%s)", (chinese_name, english_name,
                                                                                         profile, dollars, discount,
                                                                                         discount_price, RMB))

            except Exception:
                print('插入失败')
                self.connection.rollback()
            else:
                self.connection.commit()

    def connect_database(self):
        """
        连接数据库
        :return:
        """
        self.connection = pymysql.Connect(host='localhost', user='root', password='061210', port=3306, db='letian')
        self.cursor = self.connection.cursor()

    def close_database(self):
        """
        关闭数据库
        :return:
        """
        self.connection.close()
        self.cursor.close()

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
    lt = letian()
    lt.connect_database()
    lt.get_stuff(
        'http://chn.lottedfs.com/kr/display/category/third?dispShopNo1=1200001&dispShopNo2=1200011&dispShopNo3=1200014&treDpth=3')
    lt.close_database()
