import requests
import json
import os
import time
from utils import *

# from Scripts.update_count import update_count, update_count_community
# from Scripts.prompt import generate_prompt_object, generate_prompt_attributes, generate_prompt_character
# from Scripts.utils import *


LEONARDO_API_ENDPOINT = "https://cloud.leonardo.ai/api/rest/v1/generations"

HEADERS = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {LEONARDO_AI_API_KEY}"
        }

def get_all_leonardo_models():
    payload = { }
    response = requests.get("https://cloud.leonardo.ai/api/rest/v1/platformModels",  headers=HEADERS)
    response_data = response.text
    data = json.loads(response_data)
    print(data)
    custom_models = data["custom_models"]
    for model in custom_models:
        print(model)
        print("\n")

    with open(f"./leonardo_models.json", "w") as outfile: 
          outfile.write(json.dumps(custom_models, indent=2))

def improve_leonardo_prompt(leonardo_prompt):
    payload = {  "prompt": f"{leonardo_prompt}" }
    response = requests.post("https://cloud.leonardo.ai/api/rest/v1/prompt/improve", json=payload, headers=HEADERS)
    response_data = response.text
    data = json.loads(response_data)


    # print(data)



def make_leonardo_image_request(leonardo_prompt, negative_prompt, modelId, name, width, height, number_of_images):
    print(f"Making Leonardo Image Request with model {name}...")
    try:
        control_net_question = False
        init_strength_question = None
        init_image_id_question = None
        prompt_magic_question = True

        payload = {
                "prompt": f"{leonardo_prompt}",
                "modelId": modelId,
                "width": width,
                "height": height,
                "sd_version": "v1_5",
                "num_images": number_of_images,
                "negative_prompt": negative_prompt,
                "promptMagic": False,
                "num_inference_steps": 30,
                "guidance_scale": 7,
                "init_generation_image_id": None,
                "init_image_id": init_image_id_question,
                "init_strength": init_strength_question,
                "scheduler": "EULER_DISCRETE",
                "presetStyle": "LEONARDO",
                "tiling": False,
                "public": False,
                "controlNet": control_net_question,
                "controlNetType": "DEPTH"
        }

        response = requests.post(LEONARDO_API_ENDPOINT, json=payload, headers=HEADERS)
        response_data = response.text

        # Parse the JSON data
        data = json.loads(response_data)
        print(data)
        # Extract the generationId
        generation_id = data["sdGenerationJob"]["generationId"]
        response.close()
        # print(f"Generation ID: {generation_id}")
        return generation_id
    except Exception as e:
        print(e)
        return None

#     print(f"Downloading generated Leonardo Images.... Please wait for 20 seconds.....")
#     download_images(generation_id, LEONARDO_API_ENDPOINT, HEADERS, theme, character, community, version, age)
        
#         # Load the JSON data from the file
#         with open(r"Records/generation.json", "r") as file:
#             data = json.load(file)



# #============================ This function is for downloading the images from leonardo =============================================================

def download_leonardo_images(generation_id, save_image_path, cur_images_count):
    print(f"Downloading generated Leonardo Images.... Please wait for 20 seconds.....")
    time.sleep(15)

    tries = 10
    while(tries > 0):
        generations_url = LEONARDO_API_ENDPOINT + "/" + generation_id
        response = requests.get(generations_url, headers=HEADERS)
        response_data = response.text
        data = json.loads(response_data)
        if data["generations_by_pk"]["status"] == "PENDING":
            print("Generation is still pending. Trying again in 15 seconds....")
            time.sleep(15)
            tries -= 1
        else:
            break    

    # Extract the image URLs
    image_urls = [item["url"] for item in data["generations_by_pk"].get("generated_images", [])]
    for i, new_url in enumerate(image_urls):
                print(f"Downloading image {i}....")
                response = requests.get(new_url)
                if response.status_code == 200:
                    with open(save_image_path + f"/{cur_images_count}.png", "wb") as file:
                        file.write(response.content)
                    cur_images_count += 1
                    print(f"Image {i+1} downloaded successfully")
                else:
                    print(f"Failed to download image {i+1}")

    return cur_images_count



if __name__ == "__main__":
    # Load the configuration file
    leonardo_prompt = "Create a cyberpunk-inspired Pepe character in full-body style against a clean white background. Channel the futuristic aesthetics of cyberpunk, blending vibrant neon colors with gritty urban elements. Your Pepe should embody the essence of cyberpunk while retaining the classic Pepe charm. Consider incorporating elements like futuristic attire, augmented reality enhancements, and cybernetic enhancements. Let your creativity flow as you design a Pepe that thrives in the neon-lit streets of a cyberpunk world"
    negative_prompt = "negative_prompt"
    modelId = "e71a1c2f-4f80-4800-934f-2c68979d8cc8"
    width = 512
    height = 512
    number_of_images = 4
    # get_all_leonardo_models()
    # make_leonardo_image_request(leonardo_prompt, negative_prompt, modelId, width, height, number_of_images)

    generationId = "c3ff9922-92ae-43cb-937d-42c91c21b65c"
    download_leonardo_images(generationId, LEONARDO_API_ENDPOINT, HEADERS, "theme", "character", "community", "version", "age")
