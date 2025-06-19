from agents import AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig ,Agent , Runner
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    print("GOOGLE API KEY NOT FOUND")


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


agent = Agent(
    name="Helpful Assistant",
    instructions="You Are A helpful Assitant"  
)



async def main():
    result = await Runner.run(
    agent,
    input="What is the capital of Pakistan ?",
    run_config=config)
    
    print(result.final_output)



asyncio.run(main())