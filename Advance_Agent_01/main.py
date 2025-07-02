from agents import AsyncOpenAI,OpenAIChatCompletionsModel , Agent , set_tracing_disabled , Runner , function_tool
import os
import aiohttp
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
import requests
import chainlit as cl 


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")


set_tracing_disabled(True)
if not gemini_api_key:
    print("Gemini Api Key Loaded Failed..")

else:
    print("Gemini Api Key Loaded Successfully..")



if not weather_api_key:
    print("Weather Api Key Loaded Failed..")

else:
    print("Weather Api Key Loaded Successfully..")


provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash"
)



@function_tool
async def get_crypto_price(symbol: str) -> str:
    """Get current price of a crypto coin by symbol (e.g., BTCUSDT)."""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()
            if "price" in data:
                return f"💰 {symbol.upper()} ka price hai {data['price']} USD."
            return f"❌ Symbol {symbol} not found."

@function_tool
async def get_crypto_stats(symbol: str) -> str:
    """Get detailed stats from CoinGecko by coin name (e.g., ethereum)."""
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={symbol.lower()}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()
            if data:
                coin = data[0]
                return (
                    f"📊 {coin['name']} Stats:\n"
                    f"🔹 Price: ${coin['current_price']}\n"
                    f"📈 24h Change: {coin['price_change_percentage_24h']}%\n"
                    f"💵 Market Cap: ${coin['market_cap']:,}\n"
                    f"🔄 Volume: ${coin['total_volume']:,}"
                )
            return f"❌ Data not found for {symbol}"

@function_tool
async def get_top_gainers(dummy: str = "top") -> str:
    """Get top 10 crypto gainers from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=percent_change_24h_desc&per_page=10&page=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()
            msg = "🚀 Top 10 Gainers:\n"
            for coin in data:
                msg += f"{coin['name']} ({coin['symbol']}): {coin['price_change_percentage_24h']:.2f}%\n"
            return msg

@function_tool
async def get_global_market(dummy: str = "all") -> str:
    """Get global market overview from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/global"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()
            m = data["data"]
            return (
                f"🌐 Market Overview:\n"
                f"💰 Market Cap: ${m['total_market_cap']['usd']:,.2f}\n"
                f"🔄 Volume: ${m['total_volume']['usd']:,.2f}\n"
                f"👑 BTC Dominance: {m['market_cap_percentage']['btc']:.2f}%"
            )


agent = Agent(
    name="Crypto Assistant",
    model=model,
    instructions="""
You are a helpful assistant with access to live crypto data tools only.

RULES:
- Only answer questions related to cryptocurrencies, their prices, stats, top gainers, and global market overview.
- Always use the live-data tools when the user asks about crypto/fiat rates or the current market.
- If a tool call fails or errors, apologize, inform the user, and offer to retry.
- For questions outside crypto, politely refuse and state you only answer crypto-related queries.
- Be concise, accurate, and clearly mention when you fetch live data.
""",
    tools=[get_crypto_price, get_crypto_stats, get_top_gainers, get_global_market],
)


@cl.on_chat_start
async def main():
    await cl.Message(content="Hello How Can I Assist You ?").send()

@cl.on_message
async def on_message(message:cl.Message):
    # Get conversation history from session
    history = cl.user_session.get("history", [])
    # Add current user message to history
    history.append({"role": "user", "content": message.content})
    cl.user_session.set("history", history)
    result = await Runner.run(agent, input=history)
    msg = cl.Message(result.final_output)
    await msg.send()
    # Add assistant's response to history
    history.append({"role": "assistant", "content": msg.content})









