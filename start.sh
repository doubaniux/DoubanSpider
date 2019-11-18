# path to venv
source ~/venv/bin/activate
nohup scrapy crawl books -L INFO > spider.log 2>&1 &
echo crawler started