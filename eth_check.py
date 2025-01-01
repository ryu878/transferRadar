import requests
import json
import time
from datetime import datetime, date
import os
import telebot
from _config import *



bot_channel = telebot.TeleBot(bot_token)


def send_discord_message(message):
    data = {
        "content": message,
        "username": "TransferRadar"
    }
    try:
        requests.post(discord_webhook_url, json=data)
        time.sleep(1)  # Rate limit protection
    except Exception as e:
        print(f'Discord error: {e}')


def load_wallets(filename):
    with open(filename) as f:
        return json.load(f)


def load_last_checked():
    if os.path.exists('eth_last_checked.json'):
        with open('eth_last_checked.json', 'r') as f:
            return json.load(f)
    return {}


def save_last_checked(data):
    with open('eth_last_checked.json', 'w') as f:
        json.dump(data, f)


def is_today(timestamp_ms):
    tx_date = date.fromtimestamp(timestamp_ms / 1000)
    return tx_date == date.today()


def get_eth_transactions(address, last_timestamp=0):
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": etherscan_api_key  # Add this to _config.py
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    
    transactions = []
    data = response.json()
    
    for tx in data.get('result', []):
        timestamp = int(tx['timeStamp']) * 1000
        if timestamp <= last_timestamp or not is_today(timestamp):
            continue
            
        amount = float(tx['value']) / 1e18  # Convert wei to ETH
        
        if amount >= eth_amount:  # 333 ETH threshold
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            transactions.append({
                'timestamp': timestamp,
                'time': tx_time,
                'amount': amount,
                'from': tx['from'],
                'to': tx['to'],
                'hash': tx['hash']
            })
    
    return transactions


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets = load_wallets('eth_wallets_data.json')
            
            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']
                
                last_timestamp = last_checked.get(address, 0)
                transactions = get_eth_transactions(address, last_timestamp)
                
                if transactions:
                    print(f"\nNew ETH transactions for {title} ({address}):")
                    for tx in transactions:
                        print(f" From: {title} {tx['from']}")
                        print(f" To: {tx['to']}\n")
                        print(f"- {tx['time']}: {tx['amount']:.2f} ETH")
                        
                        try:
                            bot_channel.send_message(tg_channel_id, 
                                f"From: <b>{title}</b> {tx['from']}\nTo: {tx['to']}\n{tx['time']}: <b>{tx['amount']:.2f} ETH</b>", 
    parse_mode='HTML')
                            time.sleep(6)
                        except Exception as e:
                            print(f" {e}")
                            pass

                        time.sleep(1)

                        try:
                            send_discord_message(f"--------\nFrom: {title} {tx['from']}\nTo: {tx['to']}\n{tx['time']}: **{tx['amount']:.2f} ETH**")
                        except Exception as e:
                            print(f" {e}")
                            pass
                            
                    last_checked[address] = max(tx['timestamp'] for tx in transactions)
                    save_last_checked(last_checked)
            
            time.sleep(600)
            
        except Exception as e:
            print(f" Error occurred: {e}")
            time.sleep(6)


if __name__ == "__main__":
    main()
