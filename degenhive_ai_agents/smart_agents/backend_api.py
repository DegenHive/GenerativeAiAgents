from graphqlclient import GraphQLClient
from utils import *
import json
import base64
import requests
import asyncio




async def file_to_base64(file):
    try:
        with open(file, "rb") as file:
            base64_string = base64.b64encode(file.read()).decode('utf-8')
            return base64_string
    except FileNotFoundError:
        raise FileNotFoundError("No file provided")



async def upload_media_to_be(img_str):
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({
        "api_key": BE_API_KEY,
        "media": img_str
    })
    # print(payload["api_key"])
    # return
    try:
        response = requests.post(BACKEND_API, headers=headers, json=payload)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        print(e)
        return {"status": "error", "data": None}







def getHiveAnnocements( isStream, last_key = None, limit = 15):
    print("Getting Hive Announcements...")
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
    

    final_data = graphQLClient.execute(
        GET_HIVE_ANNOUNCEMENT,
        variables={"stream": True, "hiveAnnouncements":  not isStream, "lastKey": last_key, "limit": limit}
    )    
    print("Hive Announcements Data: ", final_data)
    final_data = json.loads(final_data)
    print(type(final_data))
    print(final_data)

    return {
        "status": "sucess",
        "completeFeed": final_data["data"]["getSocial"]["hive_announcements"],
        "lastKey": final_data["data"]["getSocial"]["lastKey"] if "lastKey" in final_data["data"]["getSocial"] else None
      }    










def get_profileTimeline(hiveProfileID, last_key = None, limit = 15):
    print("Getting Profile Timeline...")
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
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
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
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
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
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
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
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


def getLikesAndDialogues(user_id: any, network: any):
    print("Getting Likes And Dialogues...")
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
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

def getHiveThread(pk: any, sk: any, network: any):
    print("Getting Hive Thread...")
    graphQLClient = GraphQLClient(GRAPHQL_ENDPOINT)
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



async def main():
    file_path = "../storage/content/welcome_imgs/degenHiveIntro1.png"  # Specify the path to your image file
    img_str = await file_to_base64(file_path)
    # print(img_str)
    result = await upload_media_to_be(img_str)
    # print(result)



if __name__ == '__main__':

    asyncio.run(main())