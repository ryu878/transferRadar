import requests
import json
import time
from datetime import datetime, date
import os
import telebot
from _config import *



ver = 'TRC20 Checker - 02/01/2025-15'
print(ver)
time.sleep(3)

# Define Telegam Bot
bot_channel = telebot.TeleBot(bot_token)  


def send_discord_message(message):
    data = {
        "content": message,
        "username": "Transfer Radar"
    }
    try:
        requests.post(discord_webhook_url, json=data)
        time.sleep(1)  # Rate limit protection
    except Exception as e:
        print(f'Discord error: {e}')


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
            
        try:
            amount = float(tx['value']) / 1e6  # USDT has 6 decimals
            if not 0 < amount < 1e12:  # Sanity check for unrealistic amounts
                continue
        except (ValueError, TypeError):
            continue
            
        if amount >= trc20_amnt:
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            
            # Determine if this wallet is sender or receiver
            is_sender = tx['from'].lower() == address.lower()
            is_receiver = tx['to'].lower() == address.lower()
            
            if is_sender or is_receiver:
                transactions.append({
                    'timestamp': timestamp,
                    'time': tx_time,
                    'amount': amount,
                    'from': tx['from'],
                    'to': tx['to'],
                    'is_sender': is_sender,
                    'hash': tx['transaction_id']
                })
    
    return transactions


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets = load_wallets('trc20_wallets_data.json')  # btc/eth/trc20
            
            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']
                
                last_timestamp = last_checked.get(address, 0)
                transactions = get_usdt_transactions(address, last_timestamp)  # btc/eth/usdt
                
                if transactions:
                    discord_title = f"**{title}**" if title else title
                    telegram_title = f"<b>{title}</b>" if title else title

                    print(f"\nNew transactions for {discord_title} ({address}):")
                    for tx in transactions:
                        if tx['is_sender']:
                            from_name_discord = f"{discord_title} ({tx['from']})" if discord_title else tx['from']
                            to_name_discord = tx['to']
                            from_name_telegram = f"{telegram_title} ({tx['from']})" if telegram_title else tx['from']
                            to_name_telegram = tx['to']
                        else:
                            from_name_discord = tx['from']
                            to_name_discord = f"{discord_title} ({tx['to']})" if discord_title else tx['to']
                            from_name_telegram = tx['from']
                            to_name_telegram = f"{telegram_title} ({tx['to']})" if telegram_title else tx['to']

                        message_discord = (
                            f"--------\nFrom: {from_name_discord}\n"
                            f"To: {to_name_discord}\n"
                            f"{tx['time']}: **{tx['amount']:.2f} USDT** (TRC20)"  # BTC/ETH/USDT
                        )
                        message_telegram = (
                            f"From: {from_name_telegram}\n"
                            f"To: {to_name_telegram}\n"
                            f"{tx['time']}: <b>{tx['amount']:.2f} USDT</b> (TRC20)"  # BTC/ETH/USDT
                        )
                        
                        print(message_telegram)
                        
                        try:
                            send_discord_message(message_discord)
                            time.sleep(6)
                        except Exception as e:
                            print(f" {e}")
                            pass

                        time.sleep(1)

                        try:
                            bot_channel.send_message(tg_channel_id, message_telegram, parse_mode='HTML')
                            time.sleep(6)
                        except Exception as e:
                            print(f" {e}")
                            pass
                            
                    last_checked[address] = max(tx['timestamp'] for tx in transactions)
                    save_last_checked(last_checked)

                    time.sleep(6)
            
            time.sleep(600)
            
        except Exception as e:
            print(f' Error occurred: {e}')
            time.sleep(6)


if __name__ == '__main__':
    main()