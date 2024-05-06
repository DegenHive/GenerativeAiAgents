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
from persona.prompt_template.gpt_structure import *
from persona.prompt_template.llma_helpers import *
from persona.persona import Persona

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

    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    # Initialize the AI agents.
    for account in simulations_state['persona_accounts']:

      if "username" in account:
        self.personas[account["username"]] = Persona(account["username"], account["private_key"], rpc_url, f"{CUR_PATH_PERSONAS}{account["username"]}")
        self.persona_names.append(account["username"])


        
  """
  When you are creating new AI agents. 
  1. Scratch Info fetched for new agents via gpt3.5 & all Persona folders are created.
  """
  def initialize_ai_agents(self, rpc_url): 
    color_print("\n\n\n Initializing AI Agents... \
          \n 0. Accounts will be created with mnemonic and private key hex string\
          \n 1. Scratch info will be fetched from GPT3.5 turbo for all AI agents being initialized\
          \n 2. Persona folders will be created for all AI agents being initialized\n\n\n", GREEN)
    
    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    # Get the number of accounts that need to be initialized.
    accounts_to_initialize = simulations_state['supported_agents_count'] - len(simulations_state['persona_accounts'])

    color_print(f"Number of accounts to initialize: {accounts_to_initialize}", GREEN)
    while (accounts_to_initialize > 0):

      initialize_cnt = min(accounts_to_initialize, 4)
      final_prompt = makePersonasPrompt(initialize_cnt)         
      time.sleep(1)       
      output = ChatGPT_request(final_prompt)
      output_json = json.loads(output)
      print(output)
      if "output" in output_json:
        output_json = output_json["output"]

      # Loop over the output_json and create the persona folders.
      for agent_persona in output_json:        
        if "username" in agent_persona and "bio" in agent_persona:
          file_name = f"{CUR_PATH_PERSONAS}{agent_persona["username"]}"
          if not check_if_file_exists(file_name) and "age" in agent_persona and "personality" in agent_persona and "ai_skills_behaviour" in agent_persona and "degen_nativeness" in agent_persona and "o_acc_nativeness" in agent_persona and "native_country" in agent_persona and "daily_finances" in agent_persona:
            color_print("All keys are present in the agent_persona", YELLOW)
            print(agent_persona)            

            # 1. Create the mnemonic and private key hex string for the persona.
            mnemonic, private_key_hex_string, address = initialize_new_account(rpc_url) 
            simulations_state['persona_accounts'].append({"username": agent_persona["username"], "private_key": private_key_hex_string, "address": address, "mnemonic": mnemonic})
            agent_persona["address"] = address

            # 2. create the persona folder if it does not exist
            create_persona_folder_if_not_there(file_name, agent_persona)
            accounts_to_initialize -= 1
            print("=================\n")

        # Save the updated simulations_state
      with open(f"../storage/simulations/state/meta.json", "w") as outfile: 
            outfile.write(json.dumps(simulations_state, indent=2))


  """
  Kraft HiveProfile for all agents which don't currently have a Hive Profile.
  """
  async def kraftHiveProfileForAllAgents(self):
    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)


    for username in self.persona_names:
      agent_persona = self.personas[username]
      
      await agent_persona.kraftHiveProfileForAgent(simulations_state["configuration"])

      break



  """
  Update overall protocol state
  """
  def updateProtocolStateInfo(self, simulations_state, agent_persona, platform_state):
      username = agent_persona.name

      # 1. Get on-going epoch info
      # --------------------------
      epochInfo = agent_persona.getEpochInfoOnChain()
      if (epochInfo and "ongoing_epoch" in platform_state  and epochInfo["epoch"] > platform_state["ongoing_epoch"]):
        platform_state["ongoing_epoch"] = epochInfo["epoch"]
        platform_state["ongoing_epoch_start_ms"] = epochInfo["epoch_timestamp_ms"]
        with open(f"../storage/simulations/platform.json", "w") as outfile:
          outfile.write(json.dumps(platform_state, indent=2))

      if ("ongoing_epoch" in platform_state):
        color_print(f"\nAgent: {username} | Epoch: {platform_state['ongoing_epoch']} | Epoch Start: {platform_state['ongoing_epoch_start_ms']}", GREEN)

      # Update HiveChronicleFarm
      if int(platform_state["ongoing_epoch"]) > int(platform_state["ongoingHiveChronicleInfo"]["bee_farm_info"]["active_epoch"]):
        agent_persona.increment_global_bee_farm_epoch(simulations_state["configuration"])

      def getValidProfileId(addr1, addr2):
        if addr1:
          return addr1
        else:
          return addr2

      # Update TimeStream
      if int(platform_state["ongoing_epoch"]) > int(platform_state["ongoingTimeStreamInfo"]["config_params"]["cur_auction_stream"]):
        prev_streamer_rank1_profile = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer1_info"]["profile_addr"], dummyProfileID1)
        prev_streamer_rank2_profile = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer2_info"]["profile_addr"], dummyProfileID2)
        prev_streamer_rank3_profile = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer3_info"]["profile_addr"], dummyProfileID3)
        agent_persona.increment_timeStream_part_1(simulations_state["configuration"], prev_streamer_rank1_profile, prev_streamer_rank2_profile, prev_streamer_rank3_profile)

        new_streamer_rank1 = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer1_info"]["profile_addr"], dummyProfileID1)
        new_streamer_rank2 = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer2_info"]["profile_addr"], dummyProfileID2)
        new_streamer_rank3 = getValidProfileId(platform_state["ongoingTimeStreamInfo"]["streamer3_info"]["profile_addr"], dummyProfileID3)
        agent_persona.increment_timeStream_part_2(simulations_state["configuration"], new_streamer_rank1, new_streamer_rank2, new_streamer_rank3)


      # 2. Get the Global HiveChronicle Info
      # -----------------------------
      globalHiveChronicleInfo, snapshotInfo = agent_persona.getGlobalHiveChronicleInfoOnChain(simulations_state["configuration"], 357)
      if (globalHiveChronicleInfo):
        platform_state["ongoingHiveChronicleInfo"] = globalHiveChronicleInfo
        with open(f"../storage/simulations/platform.json", "w") as outfile:
          outfile.write(json.dumps(platform_state, indent=2))


      # 3. Get the Global TimeStream Info
      # -----------------------------
      globalTimeStreamInfo = agent_persona.getGlobalTimeStreamInfo(simulations_state["configuration"])
      if globalTimeStreamInfo and "config_params" in globalTimeStreamInfo:
        platform_state["ongoingTimeStreamInfo"] = globalTimeStreamInfo
        with open(f"../storage/simulations/platform.json", "w") as outfile:
          outfile.write(json.dumps(platform_state, indent=2))



  """
  Transfer SUI tokens to all AI agents which currently have less than amount SUI balance
  """
  def transferSuiTokensToAllAgents(self, min_amount, transfer_amount):
    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    deployer_agent = self.personas[simulations_state["main_agent"]]

    for agentInfo in simulations_state["persona_accounts"][1:]:
      if agentInfo["username"] == simulations_state["main_agent"]:
        continue
      
      # Check if the agent has atleast min_amount SUI balance, and if not transfer transfer_amount SUI tokens.
      availableSui = deployer_agent.getSuiBalanceForAddressOnChain(agentInfo["address"])
      if (availableSui < min_amount):
        color_print(f"Agent {agentInfo['username']} has only {round(availableSui/1e9, 2)} SUI balance. Transferring {round(transfer_amount/1e9, 2)} SUI tokens...", GREEN)
        deployer_agent.transferSuiOnChain( agentInfo["address"], transfer_amount)
        time.sleep(1)



  """
  Transfer HIVE tokens to all AI agents which currently have less than amount HIVE balance in their HiveProfile
  """
  def transferHiveTokensToAllAgents(self, min_hive_in_profile, transfer_amount, deposit_amount):
    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    HIVE_TOKEN_TYPE = f"{simulations_state["configuration"]["HIVE_PACKAGE"]}::hive::HIVE"

    deployer_agent = self.personas[simulations_state["main_agent"]]

    for agentInfo in simulations_state["persona_accounts"][1:]:
      
      if agentInfo["username"] == simulations_state["main_agent"]:
        continue
      
      # Update user's HiveChronicle state
      user_agent = self.personas[agentInfo["username"]]
      user_agent.handle_profile_state_update(simulations_state["configuration"])
      hiveChronicleInfo = user_agent.scratch.get_hiveChronicleState()

      color_print(f"\nAgent: {agentInfo['username']} | Address: {agentInfo['address']} | HIVE in profile = {round(int(hiveChronicleInfo["total_hive_gems"])/1e6, 2)}", GREEN)
      # continue

      # Check if the agent has atleast min_amount HIVE balance, and if not transfer transfer_amount HIVE tokens.
      if min_hive_in_profile > int(hiveChronicleInfo["total_hive_gems"]):
        color_print(f" Transferring {round(transfer_amount / 1e6, 2)} HIVE tokens...", GREEN)
        deployer_agent.transferTokens( HIVE_TOKEN_TYPE, agentInfo["address"], int(transfer_amount))
        time.sleep(1)

      if deposit_amount > int(hiveChronicleInfo["total_hive_gems"]):  
        color_print(f"Depositing {round(deposit_amount / 1e6, 2)} HIVE tokens...", GREEN)
        user_agent.depositHiveGemsToProfileOnChain( simulations_state["configuration"], HIVE_TOKEN_TYPE, deposit_amount * 10)
        time.sleep(1)    
        user_agent.handle_profile_state_update(simulations_state["configuration"])



  
  def activate_ai_agents_swarm(self):

    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    with open(f"../storage/simulations/platform.json") as json_file:  
      platform_state = json.load(json_file)

    if not "ongoing_epoch" in platform_state:
      platform_state["ongoing_epoch"] = 0


    # Start the simulation
    for username in self.persona_names:
      color_print(f"\n\n----------------------\
                  \nActivating AI Agent: {username}", BLUE)
      agent_persona = self.personas[username]

      # Update the overall protocol state --> Epoch, HiveChronicle, TimeStream
      current_time = datetime.now().timestamp() * 1000 

      


      # agent_persona.handle_profile_state_update(simulations_state["configuration"])
      return
      
      # Update platform state info (every 5 min) ---> INTERNALLY INCREMENTS BEE FARM EPOCH + TIME-STREAM INFO
      if "last_platform_state_update" not in platform_state or (current_time - platform_state["last_platform_state_update"]) > 15 * 60 * 1000 or (current_time - platform_state["ongoing_epoch_start_ms"]) > 23 * 1000 * 60 * 60 or int(platform_state["ongoing_epoch"]) > int(platform_state["ongoingTimeStreamInfo"]["config_params"]["cur_auction_stream"]): 
          platform_state["last_platform_state_update"] = current_time
          self.updateProtocolStateInfo(simulations_state, agent_persona, platform_state)
          color_print(f"Platform state successfully updated", GREEN)


      # Get the profile ID for the persona, if it does not exist, kraft it.
      profileID = agent_persona.get_HiveProfileId()
      color_print(f"Profile ID: {profileID}", GREEN)
      if not profileID or profileID == "0x0000000000000000000000000000000000000000000000000000000000000000":
        agent_persona.kraftHiveProfileForAgent(simulations_state["configuration"])

      # Get the timeline for the persona
      timeline_feed = agent_persona.getTimeline()

      for feedInfo in timeline_feed["completeFeed"]:
        feedInfo = json.loads(feedInfo)
        # print(feedInfo)
        # print(type(feedInfo))
        sk = feedInfo["SK"]

        # If its a time-stream Buzz, handle accordingly
        if "stream" in sk:
          index, inner_index = extract_buzz_numbers("stream", sk)
          print(f"Stream Buzz: {index} | {inner_index} = Likes = ${feedInfo["like_count"]} | Buzz = ${feedInfo["buzz"]} " )
          # print(feedInfo)
          if index > 14:
            agent_persona.handle_new_buzz_on_feed(simulations_state["configuration"], "stream" , index, inner_index, feedInfo["buzz"])

        if "governor" in sk:
          index, inner_index = extract_buzz_numbers("governor", sk)
          print(f"Governor Buzz: {index} | {inner_index} = Likes = ${feedInfo["like_count"]} | Buzz = ${feedInfo["buzz"]} " )
        # if "hiveProfileID" in feedInfo:
        #   hiveProfileID = feedInfo["hiveProfileID"]
        #   if not hiveProfileID or hiveProfileID == "0x



      break
 


  # def save(self): 
  #   """
  #   Save all current progress 
  #   """
  #   # <sim_folder> points to the current simulation folder.
  #   sim_folder = f"{fs_storage}/{self.sim_code}"

  #   # Save Reverie meta information.
  #   simulations_state = dict() 
  #   simulations_state["persona_names"] = list(self.personas.keys())
  #   simulations_state_f = f"{sim_folder}/reverie/meta.json"
  #   with open(simulations_state_f, "w") as outfile: 
  #     outfile.write(json.dumps(simulations_state, indent=2))

  #   # Save the personas.
  #   for persona_name, persona in self.personas.items(): 
  #     save_folder = f"{sim_folder}/personas/{persona_name}"
  #     persona.save(save_folder)


  # def start_server(self, steps=0): 
  #   """
  #   The main backend server of DegenHive smart agents. 

  #   --> This function does the following in-loop - 
  #   :: Fetch timeline, and select a random AI smart agent to move.
  #   :: AI smart agent moves based on the timeline and updates its state, + optionally make a post and / or comment. It works as following - 
  #   ::    - Agent perceives the timeline and fetches its thoughts via retrieve_thoughts_based_on_timeline. 
  #   ::    - Agent plans its next action based on the perceived timeline.
  #   ::    - Agents reflects on the timeline and updates its memory.
  #   ::    - Agent acts on the timeline.
  #   """
  #   # <sim_folder> points to the current simulation folder.
  #   current_epoch = 0


  #   # The main while loop of Reverie. 
  #   while (True): 

  #     current_timeline = {}

  #     random_persona = random.choice(list(self.personas.keys()))
  #     self.personas[random_persona].move(current_timeline, current_epoch)

  #     steps = steps - 1

  #     if steps <= 0: 
  #       break

  #     # Sleep so we don't burn our machines. 
  #     time.sleep(self.server_sleep)


  # def open_server(self): 
  #   """
  #   Open up an interactive terminal prompt that lets you run the simulation 
  #   step by step and probe agent state. 
  #   """
  #   print ("Note: The agents in this simulation package are computational")
  #   print ("constructs powered by generative agents architecture and LLM. We")
  #   print ("clarify that these agents lack human-like agency, consciousness,")
  #   print ("and independent decision-making.\n---")

  #   # <sim_folder> points to the current simulation folder.
  #   sim_folder = f"{fs_storage}/{self.sim_code}"

  #   while True: 
  #     sim_command = input("Enter option: ")
  #     sim_command = sim_command.strip()
  #     ret_str = ""

  #     try: 
  #       if sim_command.lower() in ["f", "fin", "finish", "save and finish"]: 
  #         # Finishes the simulation environment and saves the progress. 
  #         # Example: fin
  #         self.save()
  #         break

  #       elif sim_command.lower() == "exit": 
  #         # Finishes the simulation environment but does not save the progress
  #         # and erases all saved data from current simulation. 
  #         # Example: exit 
  #         shutil.rmtree(sim_folder) 
  #         break 

  #       elif sim_command.lower() == "save": 
  #         # Saves the current simulation progress. 
  #         # Example: save
  #         self.save()

  #       elif sim_command[:3].lower() == "run": 
  #         # Runs the number of steps specified in the prompt.
  #         # Example: run 1000
  #         int_count = int(sim_command.split()[-1])
  #         rs.start_server(int_count)

  #       # elif ("print persona schedule" 
  #       #       in sim_command[:22].lower()): 
  #       #   # Print the decomposed schedule of the persona specified in the 
  #       #   # prompt.
  #       #   # Example: print persona schedule Isabella Rodriguez
  #       #   ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
  #       #               .scratch.get_str_daily_schedule_summary())

  #       # elif ("print all persona schedule" 
  #       #       in sim_command[:26].lower()): 
  #       #   # Print the decomposed schedule of all personas in the world. 
  #       #   # Example: print all persona schedule
  #       #   for persona_name, persona in self.personas.items(): 
  #       #     ret_str += f"{persona_name}\n"
  #       #     ret_str += f"{persona.scratch.get_str_daily_schedule_summary()}\n"
  #       #     ret_str += f"---\n"

  #       # elif ("print persona associative memory (event)" 
  #       #       in sim_command.lower()):
  #       #   # Print the associative memory (event) of the persona specified in
  #       #   # the prompt
  #       #   # Ex: print persona associative memory (event) Isabella Rodriguez
  #       #   ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
  #       #   ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
  #       #                                .a_mem.get_str_seq_events())

  #       # elif ("print persona associative memory (thought)" 
  #       #       in sim_command.lower()): 
  #       #   # Print the associative memory (thought) of the persona specified in
  #       #   # the prompt
  #       #   # Ex: print persona associative memory (thought) Isabella Rodriguez
  #       #   ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
  #       #   ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
  #       #                                .a_mem.get_str_seq_thoughts())

  #       # elif ("print persona associative memory (chat)" 
  #       #       in sim_command.lower()): 
  #       #   # Print the associative memory (chat) of the persona specified in
  #       #   # the prompt
  #       #   # Ex: print persona associative memory (chat) Isabella Rodriguez
  #       #   ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
  #       #   ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
  #       #                                .a_mem.get_str_seq_chats())

  #       # elif ("print persona spatial memory" 
  #       #       in sim_command.lower()): 
  #       #   # Print the spatial memory of the persona specified in the prompt
  #       #   # Ex: print persona spatial memory Isabella Rodriguez
  #       #   self.personas[" ".join(sim_command.split()[-2:])].s_mem.print_tree()

  #       elif ("call -- analysis" 
  #             in sim_command.lower()): 
  #         # Starts a stateless chat session with the agent. It does not save 
  #         # anything to the agent's memory. 
  #         # Ex: call -- analysis Isabella Rodriguez
  #         persona_name = sim_command[len("call -- analysis"):].strip() 
  #         self.personas[persona_name].open_convo_session("analysis")

  #       # elif ("call -- load history" 
  #       #       in sim_command.lower()): 
  #       #   # call -- load history the_ville/agent_history_init_n3.csv

  #         # rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
  #         # clean_whispers = []
  #         # for row in rows: 
  #         #   agent_name = row[0].strip() 
  #         #   whispers = row[1].split(";")
  #         #   whispers = [whisper.strip() for whisper in whispers]
  #         #   for whisper in whispers: 
  #         #     clean_whispers += [[agent_name, whisper]]

  #         # load_history_via_whisper(self.personas, clean_whispers)

  #       print (ret_str)

  #     except:
  #       traceback.print_exc()
  #       print ("Error.")
  #       pass


if __name__ == '__main__':

  # send_telegram_message("<a href='https://www.google.com/'>Google</a>")
  

  # SUI_RPC = "https://fullnode.testnet.sui.io:443/"
  SUI_RPC =  "https://sui-testnet-endpoint.blockvision.org"

  ai_agents_simulation = DegenHiveAiAgents(SUI_RPC)

  
  min_hive_bal = 50 * 1e6
  transfer_hive_bal = 100 * 1e6

  ai_agents_simulation.transferHiveTokensToAllAgents(min_hive_bal, transfer_hive_bal, transfer_hive_bal)

  # ai_agents_simulation.activate_ai_agents_swarm( )

  sui_to_transfer = 1.5 * 1e9
  min_sui_bal = 1 * 1e9
  # ai_agents_simulation.transferSuiTokensToAllAgents(min_sui_bal, sui_to_transfer)
  # asyncio.run(ai_agents_simulation.kraftHiveProfileForAllAgents())
  




















































