# transferRadar
Python scripts to monitor high-value transactions for BTC, USDT (TRC20) and ETH across major crypto exchanges 

![image](https://github.com/user-attachments/assets/5fbc62fb-ae6d-47af-ace2-ad8bcce544f6)


You can check how it works here: https://t.me/transferRadar
or here: https://discord.gg/mZFsY4VDbA

# Installation

To install it you can create conda environment first, like this:
```
conda create --name transferradar -c conda-forge python=3.11
```
Then activate it using command
```
conda activate transferradar && alias -s py=python && clear
```
Then you have to install requests and pytelegrambotapi using commands:
```
pip install requests
pip install pyTelegramBotApi
```
Create wallet files:

```
btc_wallets_data.json
eth_wallets_data.json
trc20_wallets_data.json
```
in this JSON format:
```
[
  {
    "wallet": "WALLET_ADDRESS",
    "title": "Exchange Name/Wallet Label"
  }
]
```
And then you can run scripts this way:
```
btc_check.py
```
```
eth_check.py
```
```
trc20_check.py
```
Of course you also need Telegram bot API key and also you have to set your telegram bot as admin of your tg channel.

## Disclaimer
This project is for informational and educational purposes only. You should not use this information or any other material as legal, tax, investment, financial or other advice. Nothing contained here is a recommendation, endorsement or offer by me to buy or sell any securities or other financial instruments. If you intend to use real money, use it at your own risk. Under no circumstances will I be responsible or liable for any claims, damages, losses, expenses, costs or liabilities of any kind, including but not limited to direct or indirect damages for loss of profits.

## Contacts
I develop trading bots of any complexity, dashboards and indicators for crypto exchanges, forex and stocks.
To contact me:

Discord: https://discord.gg/zSw58e9Uvf

Join Bybit and receive up to $6,045 in Bonuses: https://www.bybit.com/invite?ref=P11NJW


## VPS for bots and scripts
I prefer using DigitalOcean.
  
[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%202.svg)](https://www.digitalocean.com/?refcode=3d7f6e57bc04&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)
  
To get $200 in credit over 60 days use my ref link: https://m.do.co/c/3d7f6e57bc04
