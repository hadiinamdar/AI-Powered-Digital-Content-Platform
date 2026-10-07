from google import genai
from app.config import settings


print("Starting Gemini connection test...")

if not settings.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY is not loaded.")
    raise SystemExit(1)

print("API key loaded successfully.")

try:
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={
            "timeout": 15000
        }
    )

    print("Connecting to Gemini...")
    print("Requesting available models...")

    models = list(client.models.list())

    print("\nSUCCESS: Gemini API connection works.")
    print("Number of models returned:", len(models))

    for model in models[:10]:
        print("-", model.name)

except Exception as e:
    print("\nGEMINI CONNECTION ERROR:")
    print(type(e).__name__)
    print(str(e))