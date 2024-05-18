from io import BytesIO
import openai 
from utils import *
import json
import time

openai.api_key = OPEN_AI_API_KEY

def makeDalleImage(prompt):
    response = openai.Image.create(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )
    print(response)

    image_url = response.data[0].url
    print(image_url)


def download_dalle_image(new_url, file_name ):
    print("Downloading DALL-E Image...")
    tries = 3
    while tries > 0:
        try:
            time.sleep(15)
            response = requests.get(new_url)
            # print(response)
            if response.status_code == 200:
                with open(file_name, "wb") as file:
                    file.write(response.content)
                return {"status": True, "path": file_name}
            else:
                print(f"Failed to download image")
                tries -= 1
                continue
        except Exception as e:
            print(e)
            tries -= 1
            continue
    
    return {"status": False, "path": file_name}

