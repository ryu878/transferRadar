import requests
import json
import time
from datetime import datetime, date
import os
import telebot
from _config import *
import locale



locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

name = 'BTC Checker'
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
    
    for tx in data.get('txs', []):  # Safeguard 'txs' being None
        if tx.get('confirmed'):
            try:
                timestamp = int(datetime.strptime(tx['confirmed'], '%Y-%m-%dT%H:%M:%SZ').timestamp() * 1000)
            except ValueError:
                timestamp = int(time.time() * 1000)
        else:
            timestamp = int(time.time() * 1000)
            
        if timestamp <= last_timestamp or not is_today(timestamp):
            continue
            
        inputs = tx.get('inputs', []) or []
        outputs = tx.get('outputs', []) or []

        is_sender = any(address.lower() in [addr.lower() for addr in input.get('addresses', []) or []] 
                        for input in inputs)
        is_receiver = any(address.lower() in [addr.lower() for addr in output.get('addresses', []) or []] 
                          for output in outputs)
        
        if not (is_sender or is_receiver):
            continue
            
        if is_sender:
            amount = sum(output['value'] for output in outputs 
                         if address.lower() not in [addr.lower() for addr in output.get('addresses', []) or []])
        else:
            amount = sum(output['value'] for output in outputs 
                         if address.lower() in [addr.lower() for addr in output.get('addresses', []) or []])
        
        amount = amount / 1e8  # Convert satoshi to BTC
        
        if amount >= btc_amount:
            tx_time = datetime.fromtimestamp(timestamp / 1000)
            from_addr = tx.get('inputs', [{}])[0].get('addresses', ['Unknown'])[0]
            to_addr = tx.get('outputs', [{}])[0].get('addresses', ['Unknown'])[0]
            
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


def add_wallet_to_file(wallet, title, filename):
    wallets = load_wallets(filename)
    # Check if the wallet already exists
    if any(entry['wallet'] == wallet for entry in wallets):
        return

    # Add the new wallet and save back to the file
    wallets.append({"wallet": wallet, "title": title})
    with open(filename, 'w') as f:
        json.dump(wallets, f, indent=2)
    print(f"New wallet added: {wallet} ({title})")


def main():
    while True:
        try:
            last_checked = load_last_checked()
            wallets = load_wallets('btc_wallets_data.json') or []
            wallet_addresses = {w['wallet'] for w in wallets}

            for wallet_info in wallets:
                address = wallet_info['wallet']
                title = wallet_info['title']

                last_timestamp = last_checked.get(address, 0)
                transactions = get_btc_transactions(address, last_timestamp)

                if transactions:
                    discord_title = f"**{title}**" if title else title
                    telegram_title = f"<b>{title}</b>" if title else title

                    print(f"\nNew transactions for {discord_title} ({address}):")
                    for tx in transactions:
                        from_wallet = tx['from']
                        to_wallet = tx['to']

                        # Add any new wallet found in transactions
                        if from_wallet not in wallet_addresses:
                            add_wallet_to_file(from_wallet, "Unknown Sender", 'btc_wallets_data.json')
                            wallet_addresses.add(from_wallet)

                        if to_wallet not in wallet_addresses:
                            add_wallet_to_file(to_wallet, "Unknown Receiver", 'btc_wallets_data.json')
                            wallet_addresses.add(to_wallet)

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

                        amount_formatted = locale.format_string('%.2f', tx['amount'], grouping=True)

                        message_discord = (
                            f"--------\nFrom: {from_name_discord}\n"
                            f"To: {to_name_discord}\n"
                            f"{tx['time']}: **{amount_formatted} BTC**"
                        )
                        message_telegram = (
                            f"From: {from_name_telegram}\n"
                            f"To: {to_name_telegram}\n"
                            f"{tx['time']}: <b>{amount_formatted} BTC</b>"
                        )

                        print(message_telegram)

                        try:
                            send_discord_message(message_discord)
                            time.sleep(6)
                        except Exception as e:
                            print(f"Discord error: {e}")

                        time.sleep(1)

                        try:
                            bot_channel.send_message(tg_channel_id, message_telegram, parse_mode='HTML')
                            time.sleep(6)
                        except Exception as e:
                            print(f"Telegram error: {e}")

                    last_checked[address] = max(tx['timestamp'] for tx in transactions)
                    save_last_checked(last_checked)

            time.sleep(600)

        except Exception as e:
            print(f'Error occurred: {e}')
            time.sleep(6)


if __name__ == '__main__':
    main()