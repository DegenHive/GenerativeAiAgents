from graphqlclient import GraphQLClient
from utils import *
import json
import base64
import requests
import asyncio




def file_to_base64(file):
    try:
        with open(file, "rb") as file:
            base64_string = base64.b64encode(file.read()).decode('utf-8')
            return base64_string
    except FileNotFoundError:
        raise FileNotFoundError("No file provided")
        return None



def upload_media_to_be(img_str):
    print("Uploading Image to BE Now...")
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": BE_API_KEY,
        "media": img_str
    }
    # print(json.loads(payload)["api_key"])
    # return
    try:
        response = requests.post(BACKEND_API, headers=headers, json=payload)
        print(response.json())
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        print("1. Error uploading image to BE")
        print(e)
        return {"status": "error", "data": None}







def getHiveAnnocements( isStream, last_key = None, limit = 15):
    print("Getting Hive Announcements...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    
    final_data = graphQLClient.execute(
        GET_HIVE_ANNOUNCEMENT,
        variables={"stream": True, "hiveAnnouncements":  not isStream, "lastKey": last_key, "limit": limit}
    )    
    # print("Hive Announcements Data: ", final_data)
    final_data = json.loads(final_data)

    return {
        "status": "sucess",
        "completeFeed": final_data["data"]["getSocial"]["hive_announcements"],
        "lastKey": final_data["data"]["getSocial"]["lastKey"] if "lastKey" in final_data["data"]["getSocial"] else None
      }    










def get_profileTimeline(hiveProfileID, last_key = None, limit = 15):
    print("Getting Profile Timeline...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    final_data = graphQLClient.execute(
        GET_USER_TIMELINES,
        variables={"timeline": {"profile_id": hiveProfileID}, "lastKey": last_key, "limit": limit}
    )    
    print("Profile Timeline Data: ", final_data)
    return final_data
    # return {
    #     "status": "sucess",
    #     "completeFeed": final_data?.getSocial?.timeline,
    #     "lastKey": final_data?.getSocial?.lastKey,
    #   }   

def getFeedData(hiveProfileID, last_key = None, limit = 15):
    print("Getting Profile Feed...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    final_data = graphQLClient.execute(
        GET_FEED_DATA,
        variables={"feed": {"profile_id": hiveProfileID}, "lastKey": last_key, "limit": limit}
    )    
    print("Profile Feed Data: ", final_data)

    # return {
    #     "status": "sucess",
    #     "completeFeed": final_data?.getSocial?.feed,
    #     "lastKey": final_data?.getSocial?.lastKey,
    #   }    


def getFeedById( pk: any, sk: any):
    print("Getting Feed By ID...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    final_data = graphQLClient.execute(
        GET_POST_BY_ID,
        variables={"postById": {"PK": pk, "SK": sk, }}
    )    
    print("Feed by ID: ", final_data)
    # return finalData?.getSocial?.posts

    # return {
    #     "status": "sucess",
    #     "completeFeed": final_data?.getSocial?.hive_announcements,
    #     "lastKey": final_data?.getSocial?.lastKey,
    #   }    


def getCommentsForPost(pk: any, sk: any, limit: any, lastKey: None, network: any):
    print("Getting Comments For Post...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    final_data = graphQLClient.execute(
        GET_COMMENTS_FOR_POST,
        variables={"dialoguesForPost": {"PK": pk, "SK": sk}, "limit": limit, "lastKey": lastKey}
    )    
    print("Profile Timeline Data: ", final_data)
    # return finalData?.getSocial?.dialogues

    # try:
    #     if (
    #       finalData?.getSocial?.dialogues &&
    #       Array.isArray(finalData?.getSocial?.dialogues)
    #     ) {
    #       return {
    #         "status": "success",
    #         "data": finalData?.getSocial?.dialogues,
    #       }
    #     } else {
    #       return {
    #         "status": "error",
    #         "data": null,
    #       }
    #     }
    # } catch (err) {
    #     return {
    #       "status": "error",
    #       "data": null,
    #     }
    # }



def getStreamingContent():
    try:
        print("Getting Streaming Content...")
        graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
        final_data = graphQLClient.execute(
            GET_STREAMING_CONTENT,
            variables={"stream": True}
        )    
        print("final_data Data: ", final_data)
        print(type(final_data))       
        final_data = json.loads(final_data) 
        return {
            "status": True,
            "data": final_data["data"]["getSocial"]["results"]
        }
    except Exception as e:
        print(e)
        return {"status": False, "data": None}


def getRecentPosts():
    print("Getting recent posts...")
    try:
        graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
        recentData = graphQLClient.execute(
            GET_RECENT_POSTS,
            variables={"recents":"buzz"}
        )    
        # print("recentData Data: ", recentData)
        # print(type(recentData))
        recentData = json.loads(recentData)
        return {
            "status": True,
            "data": recentData["data"]["getSocial"]["results"]
        }
    except Exception as e:
        print(e)
        return {"status": False, "data": None}




def getLikesAndDialogues(user_id: any, network: any):
    print("Getting Likes And Dialogues...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    likeData = graphQLClient.execute(
        LIKES_FOR_USER,
        variables={"likesByUser": {"profile_id": user_id}}
    )    
    dialogueData = graphQLClient.execute(
        DIALOGUES_FOR_USER,
        variables={"dialoguesByUser": {"profile_id": user_id}}
    )    
    print("Likes Data: ", likeData)
    print("Dialogue Data: ", dialogueData)
    # return {
    #     "status": "sucess",
    #     "likesData": likeData?.getSocial?.user_likes ? likeData?.getSocial?.user_likes : [],

    #     "dialoguesData": dialogueData?.getSocial?.user_dialogues ? dialogueData?.getSocial?.user_dialogues : [],
    #   }

def getDialoguesForPost(pk: any, sk: any):
    try: 
        print("Getting Dialogues For Post...")
        graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
        final_data = graphQLClient.execute(
            GET_COMMENTS_FOR_POST,
            variables={"dialoguesForPost": {"SK": sk, "PK": pk}}
        )    
        print("Profile Timeline Data: ", final_data)
        print(type(final_data))
        recentData = json.loads(final_data)
        return {
            "status": True,
            "data": final_data["data"]["getSocial"]["dialogues"]
        }
    except Exception as e:
        print(e)
        return {"status": False, "data": None}



def getHiveThread(pk: any, sk: any, network: any):
    print("Getting Hive Thread...")
    graphQLClient = GraphQLClient(BE_GRAPHQL_ENDPOINT)
    final_data = graphQLClient.execute(
        GET_HIVE_THREAD,
        variables={"threadByAnyId": {"SK": sk, "PK": pk}}
    )    
    print("Profile Timeline Data: ", final_data)
    # return finalData?.getSocial?.posts

    # try:
    #     if (
    #       finalData?.getSocial?.posts &&
    #       Array.isArray(finalData?.getSocial?.posts)
    #     ) {
    #       return {
    #         "status": "success",
    #         "data": finalData?.getSocial?.posts,
    #       }
    #     } else {
    #       return {
    #         "status": "error",
    #         "data": null,
    #       }
    #     }
    # } catch (err) {
    #     return {
    #       "status": "error",
    #       "data": null,
    #     }
    # }


def upload_image_to_degenhive_be(image_path):
    try:
        print("Uploading Image to DegenHive BE...")
        print(image_path)
        img_str = file_to_base64(image_path)
        if not img_str:
            print("issue with file_to_base64")
            return {"status": "failure", "data": None}
        img_str = "data:image/png;base64," + img_str    
        result = upload_media_to_be(img_str)
        if (result["status"] == "success"):
            return  result["data"]["url"]
    except Exception as e:
        print("Error uploading image to DegenHive BE")
        print(e)
        return None



# async def main():
#     file_path = "../storage/content/welcome_imgs/degenHiveIntro2.png"  # Specify the path to your image file
#     print("Uploading Image to BE... file_to_base64")
#     img_str = await file_to_base64(file_path)
#     img_str = "data:image/png;base64," + img_str
#     # print(img_str)
#     print("Uploading Image to BE... upload_media_to_be")
#     result = await upload_media_to_be(img_str)
#     print(result)



# if __name__ == '__main__':

#     asyncio.run(main())