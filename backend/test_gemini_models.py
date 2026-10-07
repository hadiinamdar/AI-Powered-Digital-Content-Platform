from google import genai
from app.config import settings


print("Checking Gemini models...")
print()

client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options={
        "timeout": 15000
    }
)

try:
    models = list(client.models.list())

    for model in models:
        name = model.name or ""

        if "image" in name.lower() or "veo" in name.lower():
            print("MEDIA MODEL:")
            print("Name:", name)
            print("Display name:", getattr(model, "display_name", None))
            print("Description:", getattr(model, "description", None))
            print()

    print("Model check completed.")

except Exception as e:
    print("ERROR:")
    print(type(e).__name__)
    print(str(e))