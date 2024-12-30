import requests
import json
import time
from datetime import datetime, date
import os
import telebot
from _config import *



# Define Telegam Bot
bot_channel = telebot.TeleBot(bot_token)  


def is_today(timestamp_ms):
    tx_date = date.fromtimestamp(timestamp_ms / 1000)
    return tx_date == date.today()


def load_wallets(filename):
    with open(filename) as f:
        return json.load(f)


def load_last_checked():
    if os.path.exists('trc20_last_checked.json'):
        with open('trc20_last_checked.json', 'r') as f:
            return json.load(f)
    return {}


def save_last_checked(data):
    with open('trc20_last_checked.json', 'w') as f:
        json.dump(data, f)


def get_usdt_transactions(address, last_timestamp=0):
    # USDT contract address on TRON
    contract_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
    params = {
        "contract_address": contract_address,
        "limit": 100
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    
    transactions = []
    data = response.json()
    
    for tx in data.get('data', []):
        timestamp = tx['block_timestamp']
        if timestamp <= last_timestamp or not is_today(timestamp):
            continue
            
        amount = float(tx['value']) / 1e6  # USDT has 6 decimals
        
        if amount >= trc20_amnt:  # 1m USDT threshold
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            transactions.append({
                'timestamp': timestamp,
                'time': tx_time,
                'type': 'Transfer',
                'amount': amount,
                'from': tx['from'],
                'to': tx['to'],
                'hash': tx['transaction_id']
            })
    
    return transactions


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets = load_wallets('trc20_wallets_data.json')
            
            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']
                
                last_timestamp = last_checked.get(address, 0)
                transactions = get_usdt_transactions(address, last_timestamp)
                
                if transactions:
                    print(f"\nNew USDT transactions for {title} ({address}):")
                    for tx in transactions:
                        print(f"  From: {title} {tx['from']}")
                        print(f"  To: {tx['to']}\n")
                        print(f"- {tx['time']}: {tx['amount']:,.2f} USDT")
                        # print(f"  Hash: {tx['hash']}")
                        try:
                            bot_channel.send_message(tg_channel_id, f"From: {title} {tx['from']}\nTo: {tx['to']}\n{tx['time']}: {tx['amount']:,.2f} USDT")
                            time.sleep(6)
                        except Exception as e:
                            print(f' {e}')
                            pass
                    
                    last_checked[address] = max(tx['timestamp'] for tx in transactions)
                    save_last_checked(last_checked)
            
            time.sleep(600)  # Wait 10 minutes
            
        except Exception as e:
            print(f' Error occurred: {e}')
            time.sleep(6)  # Wait 6 seconds on error before retrying


if __name__ == "__main__":
    main()