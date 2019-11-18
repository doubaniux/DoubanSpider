# DoubanSpider

A scrapy project scraping data from [douban](https://www.douban.com).

## Prerequisites

- PostgreSQL-11
- Python3.6 or later
- Scrapy
- Psycopg2

## Configuration

### Install PostgreSQL
The following instruction is for **Ubuntu 18.04** only, otherwise please check the [official doc](https://www.postgresql.org/download/).

Add repo source into `/etc/apt/sources.list.d/pgdg.list`
```bash
deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main
```
Import repo signing key and update
```bash
$ wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
$ sudo apt update
```
Install PostgreSQL
```bash
$ sudo apt install postgresql-11 libpq-dev
```
If you are in China, consider use [tencent mirror](https://mirrors.cloud.tencent.com/).

### Configure PostgreSQL
Create user, database, and table from sql file
```bash
$ sudo -i -u postgres
$ psql -a -f /path/to/book_init.sql
```
Edit `/etc/postgresql/11/main/pg_hba.conf` to add entry for our user, append:
```bash
host    all             donotban        127.0.0.1/32            md5
```
Change the IP if your spider runs somewhere else instead of local.

Edit `/etc/postgresql/11/main/postgresql.conf`, modify some settings
```bash
# recommended
client_encoding = 'UTF8'
# only effects postgres functions like now()
timezone = 'Asia/Shanghai'
# optional
default_transaction_isolation = SET_YOUR_LEVEL
```
### Install Scrapy and Psycopg2
```bash
$ pip install scrapy psycopg2
```
### Configure Psycopg2 Connection
Modify host, or also other parameters in `config/postgres.json`

```json
{
    "dbname" : "donotban",
    "user" : "donotban",
    "password" : "pleasedonotban",
    "host" : "127.0.0.1",
    "port" : 5432
}
```
Change isolation level in `pipelines.py`
```python
self.conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED
```

### Configure Scrapy Proxy
In `settings.py`
```python
# API that returns proxy address
# note that also the json key in middlewares.py need to be altered according to your API
PROXY_API = "http://127.0.0.1:5010/get/"
# static prxoy address
PROXY_URL = "http://username:password@yourproxyaddress:port"
```

### Set up Email
Edit `config/email.json`, so that when the spider terminated it will send an email to the receiver
```json
{
    "sender" : "youremail@example.com",
    "receiver" : "anotheremail@example.com",
    "password" : "authcode",
    "server" : "smtp.example.com",
    "port" : 465
}
```
## Start
```bash
$ nohup scrapy crawl book -L INFO > douban_spider.log 2>&1 &
```