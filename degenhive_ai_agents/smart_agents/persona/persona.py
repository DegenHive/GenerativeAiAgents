"""
Author: Joon Sung Park (joonspk@stanford.edu) | Rahul Mittal (rahul@astrotechlabs.com)

File: persona.py
Description: Defines the Persona class that powers a DegenHive smart agent. 

"""
import math
import sys
import datetime
import random
sys.path.append('../')

from global_methods import *

from persona.memory_structures.social_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *

from persona.cognitive_modules.retrieve import *
from persona.cognitive_modules.plan import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.execute import *
from onchain_helpers import *
from backend_api import *

class Persona: 

  def __init__(self, name, private_key, rpc_url, folder_mem_saved=False):

    # PERSONA BASE STATE 
    # <name> is the full username of the AI smart agent
    self.name = name
    self.private_key = private_key
    self.rpc_url = rpc_url

    # PERSONA MEMORY 
    # If there is already memory in folder_mem_saved, we load that. Otherwise,
    # we create new memory instances. 
    # <s_mem> is the persona's spatial memory. 
    f_s_mem_saved = f"{folder_mem_saved}/social_memory.json"
    self.s_mem = MemoryTree(f_s_mem_saved)

    # <s_mem> is the persona's associative memory. 
    f_a_mem_saved = f"{folder_mem_saved}/associative_memory"
    self.a_mem = AssociativeMemory(f_a_mem_saved)
    
    # <scratch> is the persona's scratch (short term memory) space. 
    scratch_saved = f"{folder_mem_saved}/scratch.json"
    self.scratch = Scratch(scratch_saved)


  """
  Kraft Hive Profile for Agent
  """
  async def kraftHiveProfileForAgent(self, protocol_config):
    profileID = self.scratch.get_hiveProfileID()
    if not profileID or profileID == "":
      color_print(f"\nKrafting Hive Profile for {self.name}... | Address: {self.scratch.get_str_address()} \n", GREEN)
      await kraftHiveProfileTx(self.rpc_url, self.private_key, protocol_config, self.name, self.scratch.get_bio() )
  
    
  """
  Like a time-stream Buzz
  """
  async def likeTimeStream(self, protocol_config):
    profileID = self.scratch.get_hiveProfileID()
    if not profileID or profileID == "":
      color_print(f"\nKrafting Hive Profile for {self.name}... | Address: {self.scratch.get_str_address()} \n", GREEN)
      await kraftHiveProfileTx(self.rpc_url, self.private_key, protocol_config, self.name, self.scratch.get_bio() )
  
    






  def getTimeline(self):
    profileID = "0x3d8811ac07fef26acf8e957daf160e948e30c336db99ed793cadf492eac88335"  #self.scratch.get_hiveProfileID())
    # get_profileTimeline(profileID)
    # timeStream = getHiveAnnocements(False)
    # getFeedData(profileID)

    # for streamBuzz in timeStream["completeFeed"]:
    #   print(streamBuzz)
    #   print("\n\n\n")

    # return timeStream

  def getHiveChronicleInfo_OnChain(self, protocol_config):
    profileID = "0x3d8811ac07fef26acf8e957daf160e948e30c336db99ed793cadf492eac88335"
    getHiveChronicleInfo(self.rpc_url, self.private_key, protocol_config, profileID)















  def get_private_key(self):
    return self.private_key

  def get_HiveProfileId(self):
    return self.scratch.get_hiveProfileID()



  # def save(self, save_folder): 
  #   """
  #   Save persona's current state (i.e., memory). 

  #   INPUT: 
  #     save_folder: The folder where we wil be saving our persona's state. 
  #   OUTPUT: 
  #     None
  #   """
  #   # Spatial memory contains a tree in a json format. 
  #   # e.g., {"double studio": 
  #   #         {"double studio": 
  #   #           {"bedroom 2": 
  #   #             ["painting", "easel", "closet", "bed"]}}}
  #   f_s_mem = f"{save_folder}/social_memory.json"
  #   self.s_mem.save(f_s_mem)
    
  #   # Associative memory contains a csv with the following rows: 
  #   # [event.type, event.created, event.expiration, s, p, o]
  #   # e.g., event,2022-10-23 00:00:00,,Isabella Rodriguez,is,idle
  #   f_a_mem = f"{save_folder}/associative_memory"
  #   self.a_mem.save(f_a_mem)

  #   # Scratch contains non-permanent data associated with the persona. When 
  #   # it is saved, it takes a json form. When we load it, we move the values
  #   # to Python variables. 
  #   f_scratch = f"{save_folder}/scratch.json"
  #   self.scratch.save(f_scratch)


  # def retrieve_thoughts_based_on_timeline(self, perceived_timeline):
  #   """
  #   This function takes the content that is perceived by the persona as input
  #   and returns a set of related thoughts that the persona would 
  #   need to consider as context when planning. 

  #   INPUT: 
  #     perceive: a list of <ConceptNode> that are perceived and new.  
  #   OUTPUT: 
  #     retrieved: dictionary of dictionary.
  #   """
  #   return retrieve(self, perceived_timeline)


  # def plan_actions(self, perceived_timeline, retrieved_thoughts, new_epoch):
  #   """
  #   Main cognitive function of the agent. It takes the retrieved memory to conduct both the long term and short term planning for the persona. 

  #   OUTPUT 
  #     The target action plan of the persona.
  #   """
  #   return plan(self, maze, perceived_timeline, new_epoch, retrieved_thoughts)


  # def execute_actions(self, perceived_timeline, plan):
  #   """
  #   This function takes the agent's current plan and outputs a concrete execution -- posts that the user will make.
  #   """
  #   return execute(self, perceived_timeline, plan)


  # def reflect(self):
  #   """
  #   Reviews the persona's memory and create new thoughts based on it. 
  #   """
  #   reflect(self)




  # def move(self, perceived_timeline, cur_epoch):
  #   """
  #   This is the main cognitive function where our main sequence is called. 
  #   """

  #   # We figure out whether the persona started a new day, and if it is a new
  #   # day, whether it is the very first day of the simulation. This is 
  #   # important because we set up the persona's long term plan at the start of
  #   # a new day. 
  #   epoch_param = False
  #   if not self.scratch.curr_time: 
  #     epoch_param = "First day"

  #   if ( self.scratch.cur_epoch < cur_epoch): 
  #     epoch_param = True

  #   self.scratch.cur_epoch = cur_epoch

  #   # Main cognitive sequence begins here. 
  #   retrieved_thoughts = self.retrieve_thoughts_based_on_timeline(perceived_timeline)
  #   plan = self.plan_actions(perceived_timeline, retrieved_thoughts, epoch_param)
  #   self.reflect()

  #   self.execute_actions(maze, perceived_timeline, plan)
  #   return 


  # def open_convo_session(self, convo_mode): 
  #   open_convo_session(self, convo_mode)
    




































