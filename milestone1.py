import requests
import time
import json
import websocket

cielo_url = "https://feed-api.cielo.finance/api/v1/tracked-wallets"  # URL for Cielo API
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-KEY": "22e3b1e2-df44-4cbf-8b36-207b80a68ac4"   # Set API key in headers for authentication
}

target_wallets = ["DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"]

# Function to add tracked wallets to SHYFT API
def add_tracked_wallets(wallet, label):
    payload = {
        "wallet": wallet,  # Wallet address to be tracked
        "label": label  # Label associated with the wallet
    }
    response = requests.post(cielo_url, json=payload, headers=headers)  # Send POST request to add wallet
    print(f"{wallet} is added to track wallet list {label}") # Log addition of wallet

# Function to retrieve currently tracked wallets from Cielo API
def get_tracked_wallets():
    response = requests.get(cielo_url, headers=headers) # Send GET request to retrieve tracked wallets
    return response.json() # Return JSON response

def send_message_to_telegram(message):
  bot_token = '7897293309:AAGtM0y5fwk-YuNlo1llgRN5LvHgW2DKpcs' # Telegram bot(Bitcoin Lottery) token (replace with your own)
  chat_id = '@whale_monitoring_ch'  # Use the channel name with "@" prefix
#   chat_id1 = '@+186S3MLPRUNmNGUx'
  # Set the content of bot's message
#   print(message)
  message_content = (
    "🆔 {label}\n"
    "⭐️ Swapped {token0_amount} #{token0_symbol} (${token0_usd}) for {token1_amount} #{token1_symbol} @ ${token1_usd}.\n"
    "#Solana | <a href='https://solscan.io/account/{wallet_address}'>Solscan</a> | <a href='https://solscan.io/tx/{hash}'>ViewTx</a>\n"
    ).format(
      label = message['from_label'],
      wallet_address = message['wallet'],
      hash = message['tx_hash'],
      token0_amount = round(message['token0_amount'], 2), token0_symbol = message['token0_symbol'],
      token0_usd = round(float(message['token0_amount']) * float(message['token0_price_usd']), 2), 
      token1_amount = round(message['token1_amount'], 2), token1_symbol = message['token1_symbol'],
      token1_usd = round(float(message['token1_price_usd']), 2), 
      )

  # URL for sending messages
  url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

  # Parameters for the request
  params = {
      'chat_id': chat_id,
      'text': message_content,
      'parse_mode': 'HTML',
      'disable_web_page_preview': True  # Disable link previews
  }
  response = requests.get(url, params=params)

# Function to delete tracked wallets
def delete_tracked_wallets(id):
    payload = { "wallet_ids": id }  # Prepare payload with wallet IDs to delete
    response = requests.delete(cielo_url, json=payload, headers=headers)  # Send DELETE request

def on_open(ws):
    print("Real time tracking started..")  # Log when tracking starts
    subscribe_message = {
        "type": "subscribe_feed",  # Message type for subscription
        "filter": {
            "tx_types": ["swap"],   # Filter for transaction types (swaps)
            "chains": ["solana"]  # Filter for Ethereum chain only
        }
    }
    ws.send(json.dumps(subscribe_message))  # Send subscription message

data = get_tracked_wallets()
tracked_wallet_id = []

for tracked_wallet in data['data']['tracked_wallets']:
    tracked_wallet_id.append(tracked_wallet['id'])
delete_tracked_wallets(tracked_wallet_id)

for wallet in target_wallets:
  add_tracked_wallets(wallet, wallet)

def on_message(ws, message):
    print("Received:", message)   # Log received WebSocket message
    parsed_message = json.loads(message)  # Parse JSON message from WebSocket
    if parsed_message['type']=="tx" and parsed_message['data']['token0_address'] !=parsed_message['data']['token1_address']:
       print(parsed_message['data'])
        #   send_message_to_telegram(parsed_message['data'])  # Call function to send message if it's a swap transaction

def on_error(ws, error):
    print("WebSocket error:", error)  # Log any errors that occur with the WebSocket
    on_open(ws)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")  # Log when WebSocket connection is closed
    print(f"Status code: {close_status_code}, Message: {close_msg}")
    print("Attempting to reconnect...")
    while True:
      time.sleep(2)  # Wait for 2 seconds before reconnecting
      ws.run_forever()  # Attempt to reconnect

WS_URL = 'wss://feed-api.cielo.finance/api/v1/ws'
ws = websocket.WebSocketApp(
    WS_URL,
    header=["X-API-KEY: {}".format("22e3b1e2-df44-4cbf-8b36-207b80a68ac4")],
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

# Run the WebSocket app
ws.run_forever()