# Copy and paste your OpenAI API Key
# Put your name
key_owner = "Rahul"

SUI_RPC = "https://fullnode.testnet.sui.io:443/"
BE_API = "https://z2a9d0jtq5.execute-api.eu-central-1.amazonaws.com/api/v1"


# Verbose 
debug = True

GRAPHQL_ENDPOINT = "https://dnlzd29z0k.execute-api.eu-central-1.amazonaws.com/api/v1"
GET_USER_TIMELINES = """
query ExampleQuery($timeline: SocialProfileSpecific, $lastKey: String, $limit: Float) {
  getSocial(timeline: $timeline, lastKey: $lastKey, limit: $limit) {
    timeline
    lastKey
  }
}
"""

GET_HIVE_THREAD = """
query ExampleQuery($threadByAnyId: SocialItemSpecific) {
    getSocial(threadByAnyId: $threadByAnyId) {
      posts
    }
  }
"""

DIALOGUES_FOR_USER = """
query ExampleQuery($lastKey: String, $limit: Float, $dialoguesByUser: SocialProfileSpecific) {
  getSocial(lastKey: $lastKey, limit: $limit, dialoguesByUser: $dialoguesByUser) {
    lastKey
    user_dialogues
  }
}
"""

LIKES_FOR_USER  = """
query ExampleQuery($likesByUser: SocialProfileSpecific, $lastKey: String, $limit: Float) {
  getSocial(likesByUser: $likesByUser, lastKey: $lastKey, limit: $limit) {
    user_likes
    lastKey
  }
}
"""

GET_COMMENTS_FOR_POST = """
query ExampleQuery($dialoguesForPost: SocialItemSpecific, $limit: Float, $lastKey: String) {
    getSocial(dialoguesForPost: $dialoguesForPost, limit: $limit, lastKey: $lastKey) {
      dialogues
    }
  }
"""

GET_POST_BY_ID = """
query GetSocial($postById: SocialItemSpecific) {
    getSocial(postById: $postById) {
      posts
    }
  }
  """

GET_HIVE_ANNOUNCEMENT = """
query ExampleQuery($hiveAnnouncements: Boolean, $stream: Boolean, $lastKey: String, $limit: Float) {
  getSocial(hive_announcements: $hiveAnnouncements, stream: $stream, lastKey: $lastKey, limit: $limit) {
    hive_announcements
  }
}
"""

GET_FEED_DATA  = """
query GetSocial($feed: SocialProfileSpecific, $limit: Float, $lastKey: String) {
  getSocial(feed: $feed, limit: $limit, lastKey: $lastKey) {
    feed
  }
}
"""