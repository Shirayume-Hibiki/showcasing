import json
import praw
import decimal
import pprint

from openai import OpenAI

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException, BinanceOrderException


reddit_client_id=""
reddit_client_secret=""
openrouter_api_key=""
binance_api_key=""
binance_secret_key=""

def get_subreddit_text(subreddit_name="cryptomarkets"):
    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        redirect_uri="http://localhost:8001",
        user_agent="testscript 1.0",
    )

    #print(reddit.auth.url(scopes=["identity"], state="...", duration="permanent"))

    text_result = ''
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.hot(limit=10):
        text_result += submission.title + "\n"
        text_result += submission.selftext + "\n"
        #print(submission.title)
        #print(submission.selftext)
    return text_result

def analyze_text(text):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    )

    text_content = """
    Which coins have good sentiment in the following text?
    Output the answer as a json list with the coin symbol denoted in square brackets
    ```
    """
    text_content += text

    #f = open("content.txt")
    #text_content += f.read()
    #print(f.read())

    completion = client.chat.completions.create(
    extra_headers={
        #"HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        #"X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    #model="openai/gpt-4o",
    model="anthropic/claude-3.5-haiku",
    messages=[
        {
        "role": "user",
        "content": text_content,
        }
    ]
    )

    result = completion.choices[0].message.content
    #print(result)
    return result

# Alternative simple approach if you know the exact format
def simple_extract(text):
    """Simple extraction using string manipulation"""
    start = text.find('```json')
    end = text.find('```', start + 7)
    
    if start != -1 and end != -1:
        json_block = text[start + 7:end].strip()
        try:
            return json.loads(json_block)
        except json.JSONDecodeError:
            return None
    return None

def buy_coin(coin_symbol):
    try:
        client = Client(binance_api_key, binance_secret_key)
        client_side=Client.SIDE_SELL
        coin_symbol = "BNB"
        bnb_balance = client.get_asset_balance(asset='BNB').get('free')

        info = client.get_symbol_info(coin_symbol)
        #print(info)
        avg_price = client.get_avg_price(symbol=coin_symbol)

        print("BNB Balance " + bnb_balance)
        print(avg_price)

        price = avg_price['price']
        quantity = 0.0
        min_quantity = 0.0

        for price_filter in info['filters']:
            if price_filter['filterType'] == "NOTIONAL":
                min_quantity = float(price_filter['minNotional'])

        quantity = float(price) * 0.001

        if quantity < min_quantity:
            quantity = min_quantity

        #quantity = f"{quantity:.10f}"
        ##quantity = "0.01"
        #quantity = '0.00010000'

        print("Buying " + str(quantity) + " " + coin_symbol + " at price " + str(price))

        order = client.create_test_order(
            symbol=coin_symbol,
            side=client_side,
            type=Client.ORDER_TYPE_MARKET,
            quoteOrderQty=quantity
            )
        print(order)

    except BinanceAPIException as e:
        # Handle Binance API related errors
        print(f"Binance API Exception: Symbol {coin_symbol}, Code {e.code}, Message: {e.message}")
    except BinanceOrderException as e:
        # Handle Binance order related errors
        print(f"Binance Order Exception: Symbol {coin_symbol}, {e}")
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"An unexpected error occurred: Symbol {coin_symbol}, {e}")

def main():
    #text_content = """
#Based on the text, here is the list of coins being promoted:

#```json
#[
    #"Bitcoin (BTC)",
    #"Ethereum (ETH)"
#]
#```

#The text primarily discusses Bitcoin mining and mentions a SharpLink purchase of Ethereum, but these are descriptive mentions rather than promotional content.
#"""

    text_reddit = get_subreddit_text()
    print(text_reddit)
    text_content = analyze_text(text_reddit)
    print(text_content)
    coins = simple_extract(text_content)
    print(coins)

    for coin in coins:
        print("Buying " + coin)
        symbol = coin
        if "[" in symbol:
            symbol = coin[coin.find("[")+1:coin.find("]")]
        #market = "BNB" + symbol
        #print("Using trading pair " + market)
        #buy_coin(symbol)

    #buy_coin("BNBLOLWTF")
    #buy_coin("BNBBTC")
    #buy_coin("BNBETH")

if __name__ == "__main__":
    main()
