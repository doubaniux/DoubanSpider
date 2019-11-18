import logging
import smtplib
import json
import os
import time
from email.utils import formataddr
from email.mime.text import MIMEText
from douban.definitions import CONFIG_DIR


def send_email(subject, content):
    logger = logging.Logger('email')
    config = load_config(os.path.join(CONFIG_DIR, 'email.json'))
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr([config['sender'], config['sender']])
    msg['To'] = formataddr([config['receiver'], config['receiver']])
    msg['Subject'] = subject
    try:
        server = smtplib.SMTP_SSL(config['server'], config['port'])
        # server.set_debuglevel(1)
        server.login(config['sender'], config['password'])
        server.sendmail(config['sender'], [config['receiver'], ], msg.as_string())
        server.quit()
        logger.info(f"MAIL SENT SUCCESSED: from {config['sender']} to {config['receiver']} at {time.asctime()}")
    except:
        logger.error(f"MAIL SENT FAILED: from {config['sender']} to {config['receiver']} at {time.asctime()}")
    logger.debug(msg)


def load_config(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config
