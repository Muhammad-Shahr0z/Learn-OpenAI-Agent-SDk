from agents import AsyncOpenAI , OpenAIChatCompletionsModel, Agent , Runner , RunConfig
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")


external_Client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


google_model = OpenAIChatCompletionsModel(
openai_client=external_Client,
model="gemini-2.0-flash",  # S
)


config = RunConfig(
    model_provider=external_Client,
    tracing_disabled=True,
    model=google_model
)

agent = Agent(
    name="Helpful Assistant",
    instructions="You are a helpful assistant.",
)


result = Runner.run_sync(
    agent,
    input="What is the capital of Pakistan ?",
    run_config=config,
    
)


print(result.final_output)

  