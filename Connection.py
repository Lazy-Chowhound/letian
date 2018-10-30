import pymysql


class ConnectDatabase():
    def __init__(self):
        self.connection = None
        self.cursor = None

    def open_connection(self):
        """
        链接数据库
        :return:
        """
        self.connection = pymysql.Connect(host='localhost', user='root', password='061210', port=3306, db='letian')
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """
        关闭数据库
        :return:
        """
        self.connection.close()
        self.cursor.close()

    def multi_insert(self, list):
        """
        插入数据（一次提交）
        :param list:
        :return:
        """
        sql = "INSERT INTO letian VALUES (%s,%s,%s,%s,%s,%s,%s)"
        try:
            self.cursor.executemany(sql, list)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
