# path to venv
source ~/venv/bin/activate
nohup scrapy crawl book -L INFO > spider.log 2>&1 &
echo crawler started