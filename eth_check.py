import requests
import json
import time
from datetime import datetime, date
import os
import telebot
from _config import *


name = 'ETH Checker'
ver = '070225'
print(f' {name} ver: {ver}')
time.sleep(3)

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


def load_wallets(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return []


def update_wallets(filename, new_wallet):
    wallets = load_wallets(filename)
    if not any(wallet['wallet'] == new_wallet for wallet in wallets):
        wallets.append({"wallet": new_wallet, "title": "New Wallet"})
        with open(filename, 'w') as f:
            json.dump(wallets, f, indent=2)
        print(f"New wallet added: {new_wallet}")


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
        "apikey": etherscan_api_key
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
        
        is_sender = tx['from'].lower() == address.lower()
        is_receiver = tx['to'].lower() == address.lower()
        
        if amount >= eth_amount:
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            transactions.append({
                'timestamp': timestamp,
                'time': tx_time,
                'amount': amount,
                'from': tx['from'],
                'to': tx['to'],
                'is_sender': is_sender,
                'is_receiver': is_receiver,
                'hash': tx['hash']
            })
    
    return transactions


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets_file = 'eth_wallets_data.json'
            wallets = load_wallets(wallets_file)
            
            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']
                
                last_timestamp = last_checked.get(address, 0)
                transactions = get_eth_transactions(address, last_timestamp)
                
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

                        def format_number(amount):
                            parts = f"{amount:.2f}".split(".")
                            parts[0] = "{:,}".format(int(parts[0])).replace(",", " ")
                            return ",".join(parts)

                        formatted_amount = format_number(tx['amount'])

                        message_discord = (
                            f"--------\nFrom: {from_name_discord}\n"
                            f"To: {to_name_discord}\n"
                            f"{tx['time']}: **{formatted_amount} ETH**"
                        )
                        message_telegram = (
                            f"From: {from_name_telegram}\n"
                            f"To: {to_name_telegram}\n"
                            f"{tx['time']}: <b>{formatted_amount} ETH</b>"
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

                        # Update wallets with unknown addresses
                        if tx['is_sender']:
                            update_wallets(wallets_file, tx['to'])
                        else:
                            update_wallets(wallets_file, tx['from'])

                    last_checked[address] = max(tx['timestamp'] for tx in transactions)
                    save_last_checked(last_checked)

                    time.sleep(6)
            
            time.sleep(600)
            
        except Exception as e:
            print(f' Error occurred: {e}')
            time.sleep(6)


if __name__ == '__main__':
    main()
