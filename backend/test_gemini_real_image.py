import base64

from google import genai
from app.config import settings


print("========================================")
print("GEMINI REAL IMAGE TEST")
print("========================================")

if not settings.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY is not loaded.")
    raise SystemExit(1)

print("API key: LOADED")

try:
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={
            "timeout": 120000
        }
    )

    print("Client created.")
    print("Model: gemini-3.1-flash-lite-image")
    print("Generating image...")
    print()

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite-image",
        input=(
            "Create a professional corporate technology poster for "
            "JZD Technologies. The topic is Artificial Intelligence "
            "and Digital Innovation. Use a premium modern blue and "
            "violet visual style, clean composition, futuristic "
            "technology elements, professional business appearance, "
            "high quality, suitable for a technology company website."
        ),
    )

    print("Gemini response received.")

    if not interaction.output_image:
        print("ERROR: Gemini did not return an image.")
        raise SystemExit(1)

    print("Image output received.")

    image_bytes = base64.b64decode(
        interaction.output_image.data
    )

    output_file = "test_real_gemini_image.png"

    with open(output_file, "wb") as file:
        file.write(image_bytes)

    print()
    print("========================================")
    print("SUCCESS!")
    print("========================================")
    print("Real AI image generated successfully.")
    print("Saved file:", output_file)
    print("File size:", len(image_bytes), "bytes")

except Exception as e:
    print()
    print("========================================")
    print("GEMINI IMAGE ERROR")
    print("========================================")
    print("Error type:", type(e).__name__)
    print("Error:", str(e))