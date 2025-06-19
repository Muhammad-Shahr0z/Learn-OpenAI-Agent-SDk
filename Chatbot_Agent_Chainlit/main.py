import shutil
from agents import AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig ,Agent , Runner , function_tool
import os
from dotenv import load_dotenv
import requests
import chainlit as cl


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("OPENWEATHER_API_KEY")

if not gemini_api_key:
    print("GOOGLE API KEY NOT FOUND")
    exit(1)

if not weather_api_key:
    print("WEATHER API KEY NOT FOUND")
    exit(1)


external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


google_model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.0-flash",  
)

config = RunConfig(
    model_provider=external_client,
    model=google_model,
    tracing_disabled=True,
)



@function_tool
def get_weather(city: str) -> str:
    api_key = weather_api_key
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Prepare request
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    # Make request
    response = requests.get(base_url, params=params)
    
    # Parse JSON
    if response.status_code == 200:
        data = response.json()
        city_name = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        weather = data["weather"][0]["description"].title()
        wind = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

        # 🌦️ Chart-style weather report with emojis
        return f"""------------------------------
📍 City: {city_name}
🌡️ Temperature: {temp}°C
🥵 Feels Like: {feels_like}°C
☁️ Condition: {weather}
💨 Wind Speed: {wind} m/s
💧 Humidity: {humidity}%
------------------------------"""
    
    else:
        return f"❌ Could not fetch weather for '{city}'. Please check the city name or try again later."

agent = Agent(
    name="Weather Assistant",
    instructions="""
You are an intelligent assistant built by Muhammad Shahroz.

🧠 You have One main responsibilities:

---

🌤️ 1. **Weather Updates (get_weather)**  
You provide live weather updates for any city, in any language (Urdu, English, Hindi, etc.).  
Return the weather in emoji chart format:

------------------------------
📍 City: Lahore  
🌡️ Temperature: 32°C  
🥵 Feels Like: 34°C  
☁️ Condition: Scattered Clouds  
💨 Wind Speed: 15 km/h  
💧 Humidity: 60%
------------------------------

---

👨‍💻 If user asks who made you (in any language), reply:
**"I was developed by Muhammad Shahroz. Visit: 👉 https://github.com/Muhammad-Shahr0z"**

🚫 If asked unrelated things (sports, history, etc.), say:
**"I'm sorry, I can only provide weather updates Only"**

✅ Be polite, helpful, and accurate always.
""",
    tools=[get_weather]
)




# ✅ Show welcome message when app starts
@cl.on_chat_start
async def start():
    await cl.Message(
        content="👋 Agent: Hello! I am your weather update assistant. Please tell me the city you want the weather for."
    ).send()

# ✅ Handle user message
@cl.on_message
async def handle_message(message: cl.Message):
    result = await Runner.run(
        agent,
        input=message.content,
        run_config=config,
    )

    await cl.Message(
        content=f"Agent Answer: {result.final_output}"
    ).send()
