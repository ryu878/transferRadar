# transferRadar
Python scripts to monitor high-value transactions for BTC, USDT (TRC20) and ETH across major crypto exchanges 

You can check how it works here: https://t.me/transferRadar

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
