# -*- coding: utf-8 -*-

from lxml import html
import requests
import os
import telegram
import boto3

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
}

telegram_token = os.environ.get('telegram_token')
telegram_channel = os.environ.get('telegram_channel')
appenv = os.environ.get('app_env')
bot = telegram.Bot(token=telegram_token) if telegram_token else None

dynamodb_table = os.environ.get('dynamodb_table')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table) if dynamodb_table else None

def send_message(message, bot=bot):
    if not bot or not telegram_channel: return print(message)
    
    bot.send_message(chat_id=telegram_channel, text=message)

def send_description_if_new(description):
    if not dynamodb_table: return send_message(description)
    
    try:
        response = table.get_item(
            Key={
                'description': description,
            }
        )
        print("Query result: " + repr(response))

    except Exception as e:
        send_message("CIS threat ERROR, couldn't query DynamoDB")
        raise e
        
    if not response.get('Item'):
        send_message(description)
        table.update_item(
            Key={
                'description': description,
            }
        )

    else:
        print('Duplicate CIS threat')
        
    #if appenv != 'prod': return
    
    #if response.get('Item'):
    #    table.delete_item(Key=response['Item'])
        
 

def handler(event, context):
    try:
        page = requests.get('https://www.cisecurity.org/cybersecurity-threats/', headers=headers)
    except Exception as e:
        send_message("CIS threat ERROR, couldn't load CIS page")
        raise e
        
    try:
        tree = html.fromstring(page.content)
    except Exception as e:
        send_message("CIS threat ERROR, couldn't parse CIS page")
        raise e

    try:
        level = tree.xpath('//div[contains(concat(" ", @class, " "), " alert-level ")]//span[contains(concat(" ", @class, " "), " text-primary ")]/text()')[0]
    except Exception as e:
        send_message("CIS threat ERROR, couldn't find element in main page")
        raise e

    if level in ('LOW', 'GREEN'):
        return 0
    else:
        send_message("WARNING: cyber threat level is " + level)

        try:
            description = tree.xpath('//div[@class="secure-platforms"]//p[@class="read-security-details"]/text()')[-1].strip()
        except Exception as e:
            send_message("CIS threat ERROR, couldn't find element in CIS page")
            raise e
            
        send_description_if_new(description)
