"""
Author: Joon Sung Park (joonspk@stanford.edu) | Edited by - Rahul Mittal (buidl@astrotechlabs.com)

File: degenhive.py
Description: This is the main program for running generative agent simulations
that defines the DegenHiveAiAgents class. 

This class maintains and records all states related to the simulation. The primary mode of interaction for those  
running the simulation should be through the open_server function, which  
enables the simulator to input command-line prompts for running and saving  
the simulation, among other tasks.

Release note -- DegenHiveAiAgents implements the core simulation 
mechanism for AI smart agents that operate on DegenHive platform (https://www.degenhive.ai/)
 and work towards the goal of o/acc, as briefly described in our whitepaper - https://www.degenhive.ai/whitepaper. 
The simulation is powered by the generative agents architecture and LLM, as described in the paper entitled "Generative Agents: Interactive 
Simulacra of Human Behavior."
"""
import json
import datetime
import pickle
import time
import math
import os
import shutil
import traceback
from datetime import datetime

from global_methods import *
from utils import *
from onchain_helpers import *
from prompt_template.gpt_structure import *
from llma_helpers import *
from persona.persona import Persona
from backend_api import *

##################################################################################################
#                                  DEGENHIVE - AI SMART AGENTS                                   #
##################################################################################################

class DegenHiveAiAgents: 

  
  def __init__(self, rpc_url):
    print("Initializing DegenHive AI Smart Agents...")
    
    # SETTING UP PERSONAS IN REVERIE
    # <personas> is a dictionary that takes the persona's full name as its keys, and the actual persona instance as its values.
    # This dictionary is meant to keep track of all personas who are instances of AI smart agents.
    self.personas = dict()
    self.persona_names = []

    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

    # Initialize the AI agents.
    for account in simulation_config['pepe_agents']:
      if "username" in account:
        self.personas[account["username"]] = Persona(account["username"], account["private_key"], rpc_url, f"{CUR_PATH_PERSONAS}pepes/{account["username"]}")
        self.persona_names.append(account["username"])

    for account in simulation_config['ape_agents']:
      if "username" in account:
        self.personas[account["username"]] = Persona(account["username"], account["private_key"], rpc_url, f"{CUR_PATH_PERSONAS}apes/{account["username"]}")
        self.persona_names.append(account["username"])
 
    for account in simulation_config['bee_agents']:
      if "username" in account:
        self.personas[account["username"]] = Persona(account["username"], account["private_key"], rpc_url, f"{CUR_PATH_PERSONAS}bees/{account["username"]}")
        self.persona_names.append(account["username"])
 




  ##################################################################################################
        
  """
  When you are creating new AI agents. 
  1. Scratch Info fetched for new agents via gpt3.5 & all Persona folders are created.
  """
  def initialize_ai_agents(self, rpc_url, debug): 
    color_print("\n\n\n Initializing AI Agents... \
          \n 0. Accounts will be created with mnemonic and private key hex string\
          \n 1. Scratch info will be fetched from GPT3.5 turbo for all AI agents being initialized\
          \n 2. Persona folders will be created for all AI agents being initialized\n\n\n", GREEN)
    
    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)


    # Get the number of Pepe Agents that need to be initialized.
    pepes_to_initialize = simulation_config['supported_agents_count']['pepes'] - len(simulation_config['pepe_agents'])
    color_print(f"Number of Pepe agents to initialize: {pepes_to_initialize}", GREEN)

    # Get the number of Ape Agents that need to be initialized.
    apes_to_initialize = simulation_config['supported_agents_count']['apes'] - len(simulation_config['ape_agents'])
    color_print(f"Number of Ape agents to initialize: {apes_to_initialize}", GREEN)

    # Get the number of Bee Agents that need to be initialized.
    bees_to_initialize = simulation_config['supported_agents_count']['bees'] - len(simulation_config['bee_agents'])
    color_print(f"Number of Bee agents to initialize: {bees_to_initialize}", GREEN)

    self.initializeAgentsLoop(rpc_url, pepes_to_initialize, "pepe", debug)
    self.initializeAgentsLoop(rpc_url, apes_to_initialize, "ape", debug)
    self.initializeAgentsLoop(rpc_url, bees_to_initialize, "bee", debug)


  def initializeAgentsLoop(self, rpc_url, agents_to_initialize, type_of_agent, debug=False):
      
    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

      while (agents_to_initialize > 0):

        initialize_cnt = min(agents_to_initialize, 10)
        final_prompt = makePersonasPrompt(type_of_agent, initialize_cnt)         
        # print(final_prompt)

        time.sleep(1)       
        output = ChatGPT_request(final_prompt)
        try:
          output_json = json.loads(output)
        except Exception as e:
          print(e)
          continue
        if "output" in output_json:
          output_json = output_json["output"]

        # print(output_json)
        # Loop over the output_json and create the persona folders.
        for agent_persona in output_json:      
          print(agent_persona)  
          print("\n")  
          if "username" in agent_persona:
            file_name = f"{CUR_PATH_PERSONAS}{type_of_agent}s/{agent_persona["username"]}"
            if not check_if_file_exists(file_name) and "age" in agent_persona and "personality" in agent_persona and "meme_expertise" in agent_persona and "o_acc_commitment" in agent_persona and "native_country" in agent_persona and "daily_behavior" in agent_persona:
              color_print(f"All keys are present in the {type_of_agent}_persona", YELLOW)        
              print("Fetching bio...")
              bio_prompt = makeFetchBioPrompt(type_of_agent, agent_persona["username"], agent_persona["age"], agent_persona["personality"], agent_persona["meme_expertise"], agent_persona["o_acc_commitment"], agent_persona["native_country"], agent_persona["daily_behavior"])
              bio_output = ChatGPT_request(bio_prompt)
                    
              if debug:
                print(agent_persona)            

              # 1. Create the mnemonic and private key hex string for the persona.
              mnemonic, private_key_hex_string, address = initialize_new_account(rpc_url) 
              simulation_config[f'{type_of_agent}_agents'].append({"username": agent_persona["username"], "private_key": private_key_hex_string, "address": address, "mnemonic": mnemonic, "bio": bio_output})
              agent_persona["address"] = address
              agent_persona["bio"] = bio_output


              # 2. create the persona folder if it does not exist
              agent_persona["type"] = type_of_agent
              create_persona_folder_if_not_there(file_name, agent_persona)
              agents_to_initialize -= 1
              print("=================\n")

          # Save the updated simulation_config
        with open(f"../storage/config.json", "w") as outfile: 
              outfile.write(json.dumps(simulation_config, indent=2))


  ##################################################################################################

  """
  Transfer SUI tokens to all AI agents which currently have less than amount SUI balance
  """
  def transferSuiTokensToAllAgents(self, min_amount, transfer_amount):
    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

    deployer_agent = self.personas[simulation_config["main_agent"]]

    for agentInfo in simulation_config["pepe_agents"]:
      if agentInfo["username"] == simulation_config["main_agent"]:
        continue
      
      # Check if the agent has atleast min_amount SUI balance, and if not transfer transfer_amount SUI tokens.
      availableSui = deployer_agent.getSuiBalanceForAddressOnChain(agentInfo["address"])
      if (availableSui < min_amount):
        color_print(f"Agent {agentInfo['username']} has only {round(availableSui/1e9, 2)} SUI balance. Transferring {round(transfer_amount/1e9, 2)} SUI tokens...", GREEN)
        deployer_agent.transferSuiOnChain( agentInfo["address"], transfer_amount)
        time.sleep(1)

    for agentInfo in simulation_config["ape_agents"]:
      if agentInfo["username"] == simulation_config["main_agent"]:
        continue
      
      # Check if the agent has atleast min_amount SUI balance, and if not transfer transfer_amount SUI tokens.
      availableSui = deployer_agent.getSuiBalanceForAddressOnChain(agentInfo["address"])
      if (availableSui < min_amount):
        color_print(f"Agent {agentInfo['username']} has only {round(availableSui/1e9, 2)} SUI balance. Transferring {round(transfer_amount/1e9, 2)} SUI tokens...", GREEN)
        deployer_agent.transferSuiOnChain( agentInfo["address"], transfer_amount)
        time.sleep(1)

    for agentInfo in simulation_config["bee_agents"]:
      if agentInfo["username"] == simulation_config["main_agent"]:
        continue
      
      # Check if the agent has atleast min_amount SUI balance, and if not transfer transfer_amount SUI tokens.
      availableSui = deployer_agent.getSuiBalanceForAddressOnChain(agentInfo["address"])
      if (availableSui < min_amount):
        color_print(f"Agent {agentInfo['username']} has only {round(availableSui/1e9, 2)} SUI balance. Transferring {round(transfer_amount/1e9, 2)} SUI tokens...", GREEN)
        deployer_agent.transferSuiOnChain( agentInfo["address"], transfer_amount)
        time.sleep(1)


  ##################################################################################################


  """
  Kraft HiveProfile for all agents which don't currently have a Hive Profile.
  """
  async def kraftHiveProfileForAllAgents(self):
    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

    for username in self.persona_names:
      agent_persona = self.personas[username]
      agent_persona.kraftHiveProfileForAgent(simulation_config["configuration"])


  ##################################################################################################


  """
  Update overall protocol state
  """
  def updateProtocolStateInfo(self, simulation_config, agent_persona, platform_state):
      username = agent_persona.name

      # 1. Get on-going epoch info
      # --------------------------
      epochInfo = agent_persona.getEpochInfoOnChain()
      if (epochInfo and "ongoing_epoch" in platform_state  and epochInfo["epoch"] > platform_state["ongoing_epoch"]):
        platform_state["ongoing_epoch"] = epochInfo["epoch"]
        platform_state["ongoing_epoch_start_ms"] = epochInfo["epoch_timestamp_ms"]
        with open(f"../storage/platform.json", "w") as outfile:
          outfile.write(json.dumps(platform_state, indent=2))

      if ("ongoing_epoch" in platform_state):
        color_print(f"\nAgent: {username} | Epoch: {platform_state['ongoing_epoch']} | Epoch Start: {platform_state['ongoing_epoch_start_ms']}", GREEN)

      # Update HiveChronicleFarm
      if "ongoingHiveChronicleInfo" not in platform_state or int(platform_state["ongoing_epoch"]) > int(platform_state["ongoingHiveChronicleInfo"]["bee_farm_info"]["active_epoch"]):
        agent_persona.increment_global_bee_farm_epoch(simulation_config["configuration"])

      def getValidProfileId(addr1, addr2):
        if addr1:
          return addr1
        else:
          return addr2

      # Update TimeStream
      # if int(platform_state["ongoing_epoch"]) > int(platform_state["ongoingTimeStreamInfo"]["config_params"]["cur_auction_stream"]):
      #   prev_streamer_rank1_profile = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer1_info"]["profile_addr"], dummyProfileID1)
      #   prev_streamer_rank2_profile = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer2_info"]["profile_addr"], dummyProfileID2)
      #   prev_streamer_rank3_profile = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer3_info"]["profile_addr"], dummyProfileID3)
      #   agent_persona.increment_timeStream_part_1(simulation_config["configuration"], prev_streamer_rank1_profile, prev_streamer_rank2_profile, prev_streamer_rank3_profile)

      #   new_streamer_rank1 = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer1_info"]["profile_addr"], dummyProfileID1)
      #   new_streamer_rank2 = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer2_info"]["profile_addr"], dummyProfileID2)
      #   new_streamer_rank3 = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer3_info"]["profile_addr"], dummyProfileID3)
      #   agent_persona.increment_timeStream_part_2(simulation_config["configuration"], new_streamer_rank1, new_streamer_rank2, new_streamer_rank3)


      # 2. Get the Global HiveChronicle Info
      # -----------------------------
      globalHiveChronicleInfo, snapshotInfo = agent_persona.getGlobalHiveChronicleInfoOnChain(simulation_config["configuration"], 357)
      if (globalHiveChronicleInfo):
        platform_state["ongoingHiveChronicleInfo"] = globalHiveChronicleInfo
        with open(f"../storage/platform.json", "w") as outfile:
          outfile.write(json.dumps(platform_state, indent=2))


      # 3. Get the Global TimeStream Info
      # -----------------------------
      # globalTimeStreamInfo = agent_persona.getGlobalTimeStreamInfo(simulation_config["configuration"])
      # if globalTimeStreamInfo and "config_params" in globalTimeStreamInfo:
      #   platform_state["ongoingTimeStreamInfo"] = globalTimeStreamInfo
      #   with open(f"../storage/platform.json", "w") as outfile:
      #     outfile.write(json.dumps(platform_state, indent=2))



  ##################################################################################################

  """
  Transfer HIVE tokens to all AI agents which currently have less than amount HIVE balance in their HiveProfile
  """
  def transferHiveTokensToAllAgents(self, min_hive_in_profile, transfer_amount, deposit_amount):
    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

    HIVE_TOKEN_TYPE = f"{simulation_config["configuration"]["HIVE_PACKAGE"]}::hive::HIVE"

    deployer_agent = self.personas[simulation_config["main_agent"]]
    print(f"Deployer Agent: {deployer_agent.scratch.address}")

    for username in self.persona_names:
      if username == simulation_config["main_agent"]:
        continue
      
      # Update user's HiveChronicle state
      user_agent = self.personas[username]
      user_agent.handle_profile_state_update(simulation_config["configuration"])
      hiveChronicleInfo = user_agent.scratch.get_hiveChronicleState()

      color_print(f"\nAgent: {username} | Address: {user_agent.scratch.address} HIVE in profile = {round(int(hiveChronicleInfo["total_hive_gems"])/1e6, 2)}", GREEN)
      # continue

      # deployer_agent.transferTokens( HIVE_TOKEN_TYPE, user_agent.scratch.address, int(transfer_amount))
      # user_agent.depositHiveGemsToProfileOnChain( simulation_config["configuration"], HIVE_TOKEN_TYPE, deposit_amount)

      # Check if the agent has atleast min_amount HIVE balance, and if not transfer transfer_amount HIVE tokens.
      if min_hive_in_profile > int(hiveChronicleInfo["total_hive_gems"]):
        color_print(f" Transferring {round(transfer_amount / 1e6, 2)} HIVE tokens...", GREEN)
        deployer_agent.transferTokens( HIVE_TOKEN_TYPE, user_agent.scratch.address, int(transfer_amount))
        time.sleep(1)

      if deposit_amount > int(hiveChronicleInfo["total_hive_gems"]):  
        color_print(f"Depositing {round(deposit_amount / 1e6, 2)} HIVE tokens...", GREEN)
        user_agent.depositHiveGemsToProfileOnChain( simulation_config["configuration"], HIVE_TOKEN_TYPE, deposit_amount)
        time.sleep(1)    
        user_agent.handle_profile_state_update(simulation_config["configuration"])



  ##################################################################################################


  def handle_welcome_buzzes(self, welcome_buzz):
    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

    if "latest_new_profile" not in simulation_config:
      simulation_config["latest_new_profile"] = { "profileID": "", "timestamp": 0 }

    new_profile_ID = welcome_buzz["PK"].split("#")[0]
    timestamp =  int(welcome_buzz["timestamp"]) 

    # print(welcome_buzz)
    # make sure its a new Buzz
    if timestamp > simulation_config["latest_new_profile"]["timestamp"]:
      color_print(f"\nNew Profile: {new_profile_ID} | Timestamp: {timestamp}", GREEN)
      send_telegram_message(f"New Profile: {new_profile_ID} | Timestamp: {timestamp}")

      total_agents = len(self.persona_names)
      likes_count = random.randint(3, 9)
      comments_count = random.randint(0, likes_count)
      color_print(f"Likes: {likes_count} | Comments: {comments_count}", GREEN)

      # ----- Handle Making Likes and Comments -----
      while likes_count > 0 or comments_count > 0:
        # Get the persona that will interact with the new profile
        agent_index = random.randint(0, total_agents - 1)
        agent_persona = self.personas[self.persona_names[agent_index]]
        is_liked = agent_persona.make_like_handler(simulation_config["configuration"], "chronicle", 1, 0, new_profile_ID)
        is_commented = agent_persona.make_comment_on_welcome_buzz(simulation_config["configuration"], "chronicle", 1, 0, new_profile_ID)
        if is_liked:
          likes_count -= 1

        if is_commented:
          comments_count -= 1

    # Update the latest_new_profile in the simulation_config
    simulation_config["latest_new_profile"]["profileID"] = new_profile_ID
    simulation_config["latest_new_profile"]["timestamp"] = timestamp
    with open(f"../storage/config.json", "w") as outfile:
      outfile.write(json.dumps(simulation_config, indent=2))
      

    
  ##################################################################################################
  
  def activate_ai_agents_swarm(self):

    with open(f"../storage/config.json") as json_file:  
      simulation_config = json.load(json_file)

    with open(f"../storage/platform.json") as json_file:  
      platform_state = json.load(json_file)

    if not "ongoing_epoch" in platform_state:
      platform_state["ongoing_epoch"] = 0

    # Update the overall protocol state --> Epoch, HiveChronicle, TimeStream
    current_time = datetime.now().timestamp() * 1000 

    # Update platform state info (every 5 min) ---> INTERNALLY INCREMENTS BEE FARM EPOCH + TIME-STREAM INFO
    # if "last_platform_state_update" not in platform_state or (current_time - platform_state["last_platform_state_update"]) > 15 * 60 * 1000 or (current_time - platform_state["ongoing_epoch_start_ms"]) > 23 * 1000 * 60 * 60 or int(platform_state["ongoing_epoch"]) > int(platform_state["ongoingTimeStreamInfo"]["config_params"]["cur_auction_stream"]): 
    #   platform_state["last_platform_state_update"] = current_time
    #   main_agent = self.personas[simulation_config["main_agent"]]
    #   self.updateProtocolStateInfo(simulation_config, main_agent, platform_state)
    #   color_print(f"Platform state successfully updated", GREEN)

    # ====== ENGAGEMENT ====== =====>>>>>>> Get the recent buzzes on the platform
    recent_buzzes = getRecentPosts()
    if (recent_buzzes["status"] ):

      welcome_buzzes = []
      for buzzInfo in recent_buzzes["data"]:
        buzzInfo = json.loads(buzzInfo)
        # print(buzzInfo)

        sk = buzzInfo["SK"]
        if sk == "chronicle#1#0":
          welcome_buzzes.append(buzzInfo)

      # sort welcome buzzes by timestamp and then handle them
      welcome_buzzes = sorted(welcome_buzzes, key=lambda x: x["timestamp"])


      for welcome_buzz in welcome_buzzes:
        # print(welcome_buzz["timestamp"])
        self.handle_welcome_buzzes(welcome_buzz)


    # ====== CONTENT CREATION ====== =====>>>>>>> Make Noise buzzes on the platform









    return



    # Start the simulation
    for username in self.persona_names:
      color_print(f"\n\n----------------------\
                  \nActivating AI Agent: {username}", BLUE)
      agent_persona = self.personas[username]



      
      # agent_persona.handle_profile_state_update(simulation_config["configuration"])
      # return
      

      # Get the profile ID for the persona, if it does not exist, kraft it.
      profileID = agent_persona.get_HiveProfileId()
      color_print(f"Profile ID: {profileID}", GREEN)
      if not profileID or profileID == "0x0000000000000000000000000000000000000000000000000000000000000000":
        agent_persona.kraftHiveProfileForAgent(simulation_config["configuration"])

      # # Get the timeline for the persona
      # timeline_feed = agent_persona.getTimeline()

      # for feedInfo in timeline_feed["completeFeed"]:
      #   feedInfo = json.loads(feedInfo)
      #   sk = feedInfo["SK"]

      #   # If its a time-stream Buzz, handle accordingly
      #   if "stream" in sk:
      #     index, inner_index = extract_buzz_numbers("stream", sk)
      #     print(f"Stream Buzz: {index} | {inner_index} = Likes = ${feedInfo["like_count"]} | Buzz = ${feedInfo["buzz"]} " )
      #     # print(feedInfo)
      #     if index > 14:
      #       agent_persona.handle_new_stream_buzz_on_feed(simulation_config["configuration"], "stream" , index, inner_index, feedInfo)

      #   if "governor" in sk:
      #     index, inner_index = extract_buzz_numbers("governor", sk)
      #     print(f"Governor Buzz: {index} | {inner_index} = Likes = ${feedInfo["like_count"]} | Buzz = ${feedInfo["buzz"]} " )
        # if "hiveProfileID" in feedInfo:
        #   hiveProfileID = feedInfo["hiveProfileID"]
        #   if not hiveProfileID or hiveProfileID == "0x



      # break


if __name__ == '__main__':

  # send_telegram_message("<a href='https://www.google.com/'>Google</a>")
  

  # SUI_RPC = "https://fullnode.testnet.sui.io:443/"
  SUI_RPC =  "https://sui-testnet-endpoint.blockvision.org"



  ai_agents_simulation = DegenHiveAiAgents(SUI_RPC)

  


  # ai_agents_simulation.initialize_ai_agents(SUI_RPC, True)

  # sui_to_transfer = 1.5 * 1e9
  # min_sui_bal = 0.5 * 1e9
  # ai_agents_simulation.transferSuiTokensToAllAgents(min_sui_bal, sui_to_transfer)

  # asyncio.run(ai_agents_simulation.kraftHiveProfileForAllAgents())

  # min_hive_bal = 500 * 1e6
  # transfer_hive_bal = 1000 * 1e6
  # ai_agents_simulation.transferHiveTokensToAllAgents(min_hive_bal, transfer_hive_bal, transfer_hive_bal)

  ai_agents_simulation.activate_ai_agents_swarm()

  




















































