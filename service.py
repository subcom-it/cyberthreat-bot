# -*- coding: utf-8 -*-

from lxml import html
import requests
import os
import telegram
import boto3

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
}

def handler(event, context):
    bot = telegram.Bot(token=os.environ['telegram_token'])
    
    try:
        page = requests.get('https://cisecurity.org', headers=headers)
    except Exception, e:
        bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't load main page"))
        raise e
        
    try:
        tree = html.fromstring(page.content)
    except Exception, e:
        bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't parse main page"))
        raise e

    try:
        level = tree.xpath('//div[contains(concat(" ", @class, " "), " alertLevel ")]//span[contains(concat(" ", @class, " "), " text-primary ")]/text()')[0]
    except Exception, e:
        bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't find element in main page"))
        raise e

    if level in ('LOW', 'GREEN'):
        return 0
    else:
        bot.send_message(chat_id=os.environ['telegram_channel'], text=("WARNING: cyber threat level is " + level))
        try:
            page2 = requests.get('https://www.cisecurity.org/cybersecurity-threats/', headers=headers)
        except Exception, e:
            bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't load description page"))
            raise e

        try:
            tree2 = html.fromstring(page2.content)
        except Exception, e:
            bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't parse description page"))
            raise e

        try:
            description = tree2.xpath('//div[@class="secure-platforms"]//p[@class="read-security-details"]/text()')[-1].strip()
        except Exception, e:
            bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't find element in description page"))
            raise e
            
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('cis_threat_dedup')
            response = table.get_item(
                Key={
                    'description': description,
                }
            )
            if response.get('Item', None) and response['Item']['description'] == description:
                return 0
        except Exception, e:
            bot.send_message(chat_id=os.environ['telegram_channel'], text=("CIS threat ERROR, couldn't query DynamoDB"))
            raise e
            
        bot.send_message(chat_id=os.environ['telegram_channel'], text=(description))
        if response.get('Item', None):
            table.delete_item(Key=response['Item'])
        table.update_item(
            Key={
                'description': description,
            }
        )

