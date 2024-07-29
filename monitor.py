import requests
import time
import asyncio
from telegram import Bot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
TELEGRAM_BOT_TOKEN = 'Your telegram bot token'
# Replace with your chat ID
TELEGRAM_CHAT_ID = 'your bot group chat id'

# Create the bot instance
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_solscan_transfers():
    url = "https://api-v2.solscan.io/v2/account/transfer"
    params = {
        "address": "wallet you want to monitor",
        "page": 1,
        "page_size": 10,# how much previous transaction you want to get at start.
        "remove_spam": "false",
        "exclude_amount_zero": "false",
        "flow": "out",# monitor outgoing or incoming transactions remove this field if you want to monitor all transactions
        "token": "So11111111111111111111111111111111111111111",#use token contact address you want to monitor, the ca used here is of sol
        "amount[]": ["48", "51.5"]  #range to which trasactions must occur eg-28 sol to 51.5 sol.
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "# input your own solscan cookie from inspect element.",
        "dnt": "1",
        "origin": "https://solscan.io",
        "priority": "u=1, i",
        "referer": "https://solscan.io/",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sol-aut": "Di8TstZYYdOfIhfvapLB9dls0fKu4icQVCh=dfAR",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
    }


    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.RequestException as e:
        logger.error(f"Error fetching transfers: {e}")
        return []

def print_transaction(tx):
    amount = tx.get('amount', 0) / 10**tx.get('token_decimals', 0)
    to_address = tx.get('to_address', 'Unknown')
    return f"MEXC transferred amount {amount} to [{to_address}](https://solscan.io/account/{to_address})"

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')

async def main():
    last_transactions = get_solscan_transfers()
    message = "Initial transactions:\n"
    for tx in last_transactions:
        message += print_transaction(tx) + "\n"
    await send_telegram_message(message)
    print("Monitoring for new transactions...\n")

    while True:
        await asyncio.sleep(10)  # Wait for 10 seconds before fetching again
        new_transactions = get_solscan_transfers()

        # Find new transactions by comparing transaction IDs
        new_tx_ids = {tx['trans_id'] for tx in new_transactions}
        last_tx_ids = {tx['trans_id'] for tx in last_transactions}

        new_entries = [tx for tx in new_transactions if tx['trans_id'] not in last_tx_ids]

        if new_entries:
            message = "New transactions:\n"
            for tx in new_entries:
                message += print_transaction(tx) + "\n"
            await send_telegram_message(message)

        # Update the last_transactions to the latest fetched transactions
        last_transactions = new_transactions

if __name__ == "__main__":
    asyncio.run(main())
