import base64
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from google import genai
from app.config import settings


def generate_image():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    return client.interactions.create(
        model="gemini-3.1-flash-image",
        input="Create a simple professional blue technology poster for an AI company.",
    )


print("Starting Gemini image test...")

if not settings.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY is not loaded.")
    raise SystemExit(1)

print("API key loaded successfully.")
print("Sending request to Gemini...")
print("Model: gemini-3.1-flash-image")

try:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(generate_image)

        try:
            interaction = future.result(timeout=90)

        except TimeoutError:
            print("\nERROR: Gemini request exceeded 90 seconds.")
            print("The request is taking too long.")
            raise SystemExit(1)

    print("Gemini response received.")

    if interaction.output_image:
        image_bytes = base64.b64decode(
            interaction.output_image.data
        )

        with open("test_generated_image.png", "wb") as file:
            file.write(image_bytes)

        print("SUCCESS!")
        print("Image saved as: test_generated_image.png")

    else:
        print("ERROR: Gemini returned no image.")

except Exception as e:
    print("\nGEMINI ERROR:")
    print(type(e).__name__)
    print(str(e))