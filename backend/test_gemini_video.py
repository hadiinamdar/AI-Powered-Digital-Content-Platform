import time

from google import genai
from google.genai import types
from app.config import settings


MODEL_NAME = "veo-3.1-generate-preview"
POLL_INTERVAL_SECONDS = 10
MAX_WAIT_SECONDS = 360  # video generation usually takes 1-6 minutes
OUTPUT_FILE = "test_generated_video.mp4"


print("Starting Gemini video test...")

if not settings.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY is not loaded.")
    raise SystemExit(1)

print("API key loaded successfully.")
print("Sending request to Gemini...")
print(f"Model: {MODEL_NAME}")

try:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Video generation is a long-running operation: this returns immediately
    # with an operation object that we have to poll until it is done.
    operation = client.models.generate_videos(
        model=MODEL_NAME,
        prompt=(
            "A short cinematic shot of a futuristic blue technology office "
            "with holographic AI dashboards, smooth slow camera movement."
        ),
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",
        ),
    )

    print("Video generation started. Waiting for completion...")

    start_time = time.time()

    while not operation.done:
        elapsed = int(time.time() - start_time)

        if elapsed > MAX_WAIT_SECONDS:
            print(f"\nERROR: Gemini video generation exceeded {MAX_WAIT_SECONDS} seconds.")
            print("The request is taking too long.")
            raise SystemExit(1)

        print(f"  ...still generating ({elapsed}s elapsed)")
        time.sleep(POLL_INTERVAL_SECONDS)
        operation = client.operations.get(operation)

    print("Gemini response received.")

    if operation.error:
        print("\nGEMINI OPERATION ERROR:")
        print(operation.error)
        raise SystemExit(1)

    response = operation.response

    if response and response.generated_videos:
        generated_video = response.generated_videos[0]

        client.files.download(file=generated_video.video)
        generated_video.video.save(OUTPUT_FILE)

        print("SUCCESS!")
        print(f"Video saved as: {OUTPUT_FILE}")

    else:
        print("ERROR: Gemini returned no video.")
        # Veo can filter prompts for safety; show the reason if present.
        if response is not None and getattr(response, "rai_media_filtered_reasons", None):
            print("Filtered reasons:", response.rai_media_filtered_reasons)

except SystemExit:
    raise

except Exception as e:
    print("\nGEMINI ERROR:")
    print(type(e).__name__)
    print(str(e))
