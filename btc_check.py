import requests
import json
import time
from datetime import datetime, date
import os
import telebot
from _config import *



ver = 'BTC Checker - 07/01/2025'
print(ver)
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
    with open(filename) as f:
        return json.load(f)


def load_last_checked():
    if os.path.exists('btc_last_checked.json'):
        with open('btc_last_checked.json', 'r') as f:
            return json.load(f)
    return {}


def save_last_checked(data):
    with open('btc_last_checked.json', 'w') as f:
        json.dump(data, f)

def is_today(timestamp_ms):
    tx_date = date.fromtimestamp(timestamp_ms / 1000)
    return tx_date == date.today()


def get_btc_transactions(address, last_timestamp=0):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
    params = {
        "token": blockcypher_token,
        "limit": 50
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    
    transactions = []
    data = response.json()
    
    for tx in data.get('txs', []):
        # Parse ISO format timestamp
        if tx.get('confirmed'):
            timestamp = int(datetime.strptime(tx['confirmed'], '%Y-%m-%dT%H:%M:%SZ').timestamp() * 1000)
        else:
            timestamp = int(time.time() * 1000)
            
        if timestamp <= last_timestamp or not is_today(timestamp):
            continue
            
        # Check if address is in inputs or outputs
        is_sender = any(address.lower() in [addr.lower() for addr in input.get('addresses', [])] 
                       for input in tx.get('inputs', []))
        is_receiver = any(address.lower() in [addr.lower() for addr in output.get('addresses', [])] 
                         for output in tx.get('outputs', []))
        
        if not (is_sender or is_receiver):
            continue
            
        # Calculate amount based on whether address is sender or receiver
        if is_sender:
            amount = sum(output['value'] for output in tx.get('outputs', []) 
                        if address.lower() not in [addr.lower() for addr in output.get('addresses', [])])
        else:
            amount = sum(output['value'] for output in tx.get('outputs', []) 
                        if address.lower() in [addr.lower() for addr in output.get('addresses', [])])
        
        amount = amount / 1e8  # Convert satoshi to BTC
        
        if amount >= btc_amount:  # BTC threshold
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            from_addr = tx['inputs'][0]['addresses'][0] if tx['inputs'] else 'Unknown'
            to_addr = tx['outputs'][0]['addresses'][0] if tx['outputs'] else 'Unknown'
            
            transactions.append({
                'timestamp': timestamp,
                'time': tx_time,
                'amount': amount,
                'from': from_addr,
                'to': to_addr,
                'is_sender': is_sender,
                'hash': tx['hash']
            })
    
    return transactions


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets = load_wallets('btc_wallets_data.json')  # btc/eth/trc20
            
            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']
                
                last_timestamp = last_checked.get(address, 0)
                transactions = get_btc_transactions(address, last_timestamp)  # btc/eth/usdt
                
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
                            f"{tx['time']}: **{tx['amount']:.2f} BTC**"  # BTC/ETH/USDT
                        )
                        message_telegram = (
                            f"From: {from_name_telegram}\n"
                            f"To: {to_name_telegram}\n"
                            f"{tx['time']}: <b>{tx['amount']:.2f} BTC</b>"  # BTC/ETH/USDT
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

                    time.sleep(60)
            
            time.sleep(600)
            
        except Exception as e:
            print(f' Error occurred: {e}')
            time.sleep(6)


if __name__ == '__main__':
    main()