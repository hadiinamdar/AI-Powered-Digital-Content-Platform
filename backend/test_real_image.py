import os
import base64
from google import genai
from dotenv import load_dotenv

load_dotenv()

print("Starting Gemini test...", flush=True)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("Client ready.", flush=True)
print("Sending image request...", flush=True)

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Create a simple blue square technology poster with the words JZD Technologies."
)

print("Response received!", flush=True)

if interaction.output_image:
    image_data = base64.b64decode(interaction.output_image.data)

    with open("test_real_image.jpg", "wb") as f:
        f.write(image_data)

    print("SUCCESS!", flush=True)
    print("Saved: test_real_image.jpg", flush=True)
else:
    print("No image returned.", flush=True)