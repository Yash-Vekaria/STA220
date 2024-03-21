import sys
sys.path.insert(0, '/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/venv/lib/python3.9/site-packages')
BOT_NAME = 'Crawler'
SPIDER_MODULES = ['Crawler.spiders']
NEWSPIDER_MODULE = 'Crawler.spiders'
ROBOTSTXT_OBEY = False
ITEM_PIPELINES = {
    'Crawler.pipelines.DefaultValuesPipeline': 200,
    'Crawler.pipelines.MysqlPipeline': 300
}
