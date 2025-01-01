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
            
        total_in = sum(input['output_value'] for input in tx.get('inputs', []) 
                      if any(addr == address for addr in input.get('addresses', [])))
        total_out = sum(output['value'] for output in tx.get('outputs', []) 
                       if any(addr == address for addr in output.get('addresses', [])))
        
        amount = abs(total_out - total_in) / 1e8
        
        if amount >= int(btc_amount):
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            from_addr = tx['inputs'][0]['addresses'][0] if tx['inputs'] else 'Unknown'
            to_addr = tx['outputs'][0]['addresses'][0] if tx['outputs'] else 'Unknown'
            
            transactions.append({
                'timestamp': timestamp,
                'time': tx_time,
                'amount': amount,
                'from': from_addr,
                'to': to_addr,
                'hash': tx['hash']
            })
    
    return transactions


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets = load_wallets('btc_wallets_data.json')
            
            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']
                
                last_timestamp = last_checked.get(address, 0)
                transactions = get_btc_transactions(address, last_timestamp)
                
                if transactions:
                    print(f"\nNew BTC transactions for {title} ({address}):")
                    for tx in transactions:
                        print(f" From: {title} {tx['from']}")
                        print(f" To: {tx['to']}\n")
                        print(f"- {tx['time']}: {tx['amount']:.8f} BTC")
                        
                        try:
                            bot_channel.send_message(tg_channel_id, 
                                f"From: <b>{title}</b> {tx['from']}\nTo: {tx['to']}\n{tx['time']}: <b>{tx['amount']:.8f} BTC</b>", 
    parse_mode='HTML')
                            time.sleep(6)
                        except Exception as e:
                            print(f' {e}')
                            pass

                        time.sleep(1)

                        try:
                            send_discord_message(f"--------\nFrom: **{title}** {tx['from']}\nTo: {tx['to']}\n{tx['time']}: **{tx['amount']:.8f} BTC**")
                        except Exception as e:
                            print(f" {e}")
                            pass
                            
                    last_checked[address] = max(tx['timestamp'] for tx in transactions)
                    save_last_checked(last_checked)
            
            time.sleep(600)
            
        except Exception as e:
            print(f' Error occurred: {e}')
            time.sleep(6)


if __name__ == "__main__":
    main()
