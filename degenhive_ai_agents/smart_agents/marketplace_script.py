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
#                                  DEGENHIVE - NFTs MARKETPLACE CLEAN-UP                         #
##################################################################################################



  ##################################################################################################
        

async def degenHive_marketplace_meetup():

  loop_in_progress = True
  last_version = ""
  limit = 10
  timestamp = int(datetime.now().timestamp()) * 1000

  while loop_in_progress:
    listed_assets = getSuimarketplaceData(last_version, limit)

    if len(listed_assets) < limit:
      loop_in_progress = False

    # Loop across listed assets
    for listed_asset in listed_assets:
      print(listed_asset )

      if timestamp > listed_asset["expiration_sec"]:
        print("Asset Expired: ", listed_asset["version"])
        # Expire asset
        # await expireAsset(listed_asset["asset_id"])

      break
      last_version = listed_asset["version"]


  ##################################################################################################

 
if __name__ == '__main__':

  # send_telegram_message("<a href='https://www.google.com/'>Google</a>")
  now = datetime.now()
  timestamp = now.timestamp()
  print(f"Starting DegenHive AI Agents Simulation at {timestamp}")
  
  

  SUI_RPC = "https://fullnode.testnet.sui.io:443/"
  # SUI_RPC =  "https://sui-testnet-endpoint.blockvision.org"

 
  asyncio.run( degenHive_marketplace_meetup() )





















































