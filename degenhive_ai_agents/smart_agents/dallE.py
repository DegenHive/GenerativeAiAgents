from io import BytesIO
import openai 
from utils import *
import json

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


def download_images(new_url ):
    response = requests.get(new_url)
    if response.status_code == 200:
        with open("testing", "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to download image")
        
 



if __name__ == "__main__":
    # makeDalleImage("A painting of a flower in a vase")
    download_images("https://oaidalleapiprodscus.blob.core.windows.net/private/org-jT846vop2X98prq8B2LHexfG/user-pD5mJDl7QSlp0XHaNhq56xua/img-yrtFIL5mBXY6nOK2G3FxNMOq.png?st=2024-05-13T18%3A29%3A58Z&se=2024-05-13T20%3A29%3A58Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-05-12T21%3A58%3A33Z&ske=2024-05-13T21%3A58%3A33Z&sks=b&skv=2021-08-06&sig=rUBmpV%2B15aJ8%2BJ4QGPT6tyDru7TID3QRIqpA%2BXt0Vq8%3D")