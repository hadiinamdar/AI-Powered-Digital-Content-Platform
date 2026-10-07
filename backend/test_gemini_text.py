from google import genai
from app.config import settings


print("Starting Gemini text test...")

if not settings.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY is not loaded.")
    raise SystemExit(1)

print("API key loaded successfully.")

try:
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    print("Sending text request...")

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Reply with exactly: GEMINI TEST SUCCESS"
    )

    print("\nGemini response received:")
    print(response.text)

except Exception as e:
    print("\nGEMINI ERROR:")
    print(type(e).__name__)
    print(str(e))