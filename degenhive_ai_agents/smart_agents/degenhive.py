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
    # e.g., ["Isabella Rodriguez"] = Persona("Isabella Rodriguezs")
    self.personas = dict()
    self.persona_names = []

    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    # Initialize the AI agents.
    for account in simulations_state['persona_accounts']:

      if "username" in account:
        self.personas[account["username"]] = Persona(account["username"], account["private_key"], rpc_url, f"../storage/simulations/personas/{account["username"]}")
        self.persona_names.append(account["username"])
        break


        
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
          file_name = f"../storage/simulations/personas/{agent_persona["username"]}"
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



  
  def make_bees_fly(self):

    with open(f"../storage/simulations/state/meta.json") as json_file:  
      simulations_state = json.load(json_file)

    # Start the simulation
    for username in ["AIExplorer99"]: #]self.persona_names:
      agent_persona = self.personas[username]

      # profileID = agent_persona.get_HiveProfileId()
      # if not profileID or profileID == "":
      #   continue

      # Get the timeline for the persona
      # timeline_feed = agent_persona.getTimeline()

      # Get current persona's overall state 
      agent_persona.getHiveChronicleInfo_OnChain(simulations_state["configuration"])










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
  # ai_agents_simulation = DegenHiveAiAgents("base_the_ville_isabella_maria_klaus", 
  #                    "July1_the_ville_isabella_maria_klaus-step-3-1")
  # ai_agents_simulation = DegenHiveAiAgents("July1_the_ville_isabella_maria_klaus-step-3-20", 
  #                    "July1_the_ville_isabella_maria_klaus-step-3-21")
  # ai_agents_simulation.open_server()

  rpc_url = ""# input("Enter the name of the new simulation: ").strip()
  # SUI_RPC = "https://fullnode.testnet.sui.io:443/"
  SUI_RPC =  "https://sui-testnet-endpoint.blockvision.org"

  ai_agents_simulation = DegenHiveAiAgents(SUI_RPC)


  # rs.initialize_ai_agents(SUI_RPC)
  ai_agents_simulation.make_bees_fly( )
  # asyncio.run(ai_agents_simulation.kraftHiveProfileForAllAgents())
  




















































