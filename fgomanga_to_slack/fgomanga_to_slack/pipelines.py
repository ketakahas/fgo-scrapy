# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import slackweb

class FgomangaToSlackPipeline(object):
    #def process_item(self, item, spider):
    #    return item

    def __init__(self, mysql_host, mysql_db, mysql_user, mysql_passwd):
        self.mysql_host = mysql_host
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_passwd = mysql_passwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host = crawler.settings.get('MYSQL_HOST'),
            mysql_db = crawler.settings.get('MYSQL_DB'),
            mysql_user = crawler.settings.get('MYSQL_USER'),
            mysql_passwd = crawler.settings.get('MYSQL_PASSWORD')
        )

    def open_spider(self, spider):
        self.conn = MySQLdb.connect(
            user = self.mysql_user,
            passwd = self.mysql_passwd,
            host = self.mysql_host,
            db = self.mysql_db,
            charset="utf8"
        )
        self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)

    def close_spider(self, spider):
        self.cur.close
        self.conn.close

    def process_item(self, item, spider):
        select_sql = "SELECT * FROM `fgo3_summary`;"
        self.cur.execute(select_sql)

        webhook_url = spider.settings['SLACK_WEBHOOK']
        slack = slackweb.Slack(url=webhook_url)

        # 登録済みなら登録件数と今回取得した件数の比較を行う
        if self.cur.rowcount:
            # 登録件数が異なれば更新
            if self.cur.fetchone()['sum_episode'] != item['count']:
                update_sql = "UPDATE `fgo3_summary` SET sum_episode = %s, updated_at = %s;"
                self.cur.execute(update_sql, (item['count'], item['updated_at']))
                self.conn.commit()

                to_comic_url = "http://www.fate-go.jp/manga_fgo3/images/comic%s/comic.png" % item['count']
                slack.notify(text=to_comic_url)
            else: # 同じならupdated_atのみ更新
                update_sql = "UPDATE `fgo3_summary` SET updated_at = %s WHERE sum_episode = %s;"
                self.cur.execute(update_sql, (item['updated_at'], item['count']))
                self.conn.commit()

        else: # 未登録なら登録する
            insert_sql = "INSERT IGNORE INTO `fgo3_summary` (`sum_episode`, `created_at`, `updated_at`) VALUES (%s, %s, %s);"
            self.cur.execute(insert_sql, (item['count'], item['created_at'], item['updated_at']))
            self.conn.commit()

            to_comic_url = "http://www.fate-go.jp/manga_fgo3/images/comic01/comic.png"
            slack.notify(text=to_comic_url)
