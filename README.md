# Announcement: Discontinuation of Free Bots for Bybit 
I regret to inform that I will no longer be updating or maintaining my free trading bots for the Bybit exchange. This decision comes after a deeply disappointing experience with Bybit's unethical practices, particularly regarding their affiliate program and their handling of user earnings.

Despite fully complying with Bybit's rules, including completing KYC (Know Your Customer) requirements, my affiliate earnings were abruptly terminated without valid justification. Bybit cited "one IP address" as the reason, a claim that is both unreasonable and unfair, especially for users in shared living environments or using shared internet connections. This behavior demonstrates a lack of transparency and fairness, and it has eroded my trust in Bybit as a reliable platform.

I want to thank everyone who has supported my work and used my free bots for Bybit. Your trust and feedback have been invaluable, and I hope to continue providing value to the crypto community through my future projects. Stay tuned for updates, and feel free to reach out if you have any questions or need assistance during this transition.

Thank you for your understanding and support.

---

# Transfer Radar
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
To contact me please pm:

Telegram: https://t.me/vi8ilante

Discord: https://discord.gg/zSw58e9Uvf

## Crypto Exchanges

😎 Register on BingX and get a 20% discount on fees: https://bingx.com/invite/HAJ8YQQAG/

👍 MEXC: https://promote.mexc.com/r/f3dtDLZK

🐀 Join Bybit: https://www.bybit.com/invite?ref=P11NJW

## VPS for bots and scripts
I prefer using DigitalOcean.
  
[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%202.svg)](https://www.digitalocean.com/?refcode=3d7f6e57bc04&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)
  
To get $200 in credit over 60 days use my ref link: https://m.do.co/c/3d7f6e57bc04
