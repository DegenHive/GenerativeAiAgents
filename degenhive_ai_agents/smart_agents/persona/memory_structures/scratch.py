"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: scratch.py
Description: Defines the short-term memory module for generative agents.
"""
import datetime
import json
import sys
from utils import *
sys.path.append('../../')

from global_methods import *

class Scratch: 

  def __init__(self, f_saved): 

    # THE CORE IDENTITY OF THE PERSONA 
    self.type = None
    self.address = None
    self.hiveProfileID = None
    self.daily_behavior = None

    self.username = None
    self.bio = None
    self.age = None
    self.personality = None
    self.meme_expertise = None
    self.o_acc_commitment = None
    self.native_country = None

    self.last_stream_interaction = None
    self.last_dex_dao_interaction = None
    self.last_hive_dao_interaction = None

    self.hiveChronicleState = None
    self.timeStreamState = None

    self.att_bandwidth = 3
    self.retention = 5

    # REFLECTION VARIABLES
    self.concept_forget = 100
    self.daily_reflection_time = 60 * 3
    self.daily_reflection_size = 5
    self.overlap_reflect_th = 2
    self.kw_strg_event_reflect_th = 4
    self.kw_strg_thought_reflect_th = 4

    # New reflection variables
    self.recency_w = 1
    self.relevance_w = 1
    self.importance_w = 1
    self.recency_decay = 0.99
    self.importance_trigger_max = 150
    self.importance_trigger_curr = self.importance_trigger_max
    self.importance_ele_n = 0 
    self.thought_count = 5

    # WORLD INFORMATION
    # Perceived world time. 
    self.curr_time = None
    




    if check_if_file_exists(f_saved): 
      # If we have a bootstrap file, load that here. 
      scratch_load = json.load(open(f_saved))

      if "type" not in scratch_load:
        self.type = ""
      else:
        self.type = scratch_load["type"]  
  
      self.address = scratch_load["address"]
      self.hiveProfileID = scratch_load["hiveProfileID"]
      self.daily_behavior = scratch_load["daily_behavior"]

      self.username = scratch_load["username"]
      self.bio = scratch_load["bio"]
      self.age = scratch_load["age"]
      self.personality = scratch_load["personality"]
      self.meme_expertise = scratch_load["meme_expertise"]
      self.currently = scratch_load["o_acc_commitment"]
      self.native_country = scratch_load["native_country"]

      self.last_stream_interaction = scratch_load.get("last_stream_interaction", None)
      self.last_dex_dao_interaction = scratch_load.get("last_dex_dao_interaction", None)
      self.last_hive_dao_interaction = scratch_load.get("last_hive_dao_interaction", None)

      self.hiveChronicleState = scratch_load.get("hiveChronicleState", None)
      self.timeStreamState = scratch_load.get("timeStreamState", None)

      self.att_bandwidth = scratch_load["att_bandwidth"]
      self.retention = scratch_load["retention"]

      self.concept_forget = scratch_load["concept_forget"]
      self.daily_reflection_time = scratch_load["daily_reflection_time"]
      self.daily_reflection_size = scratch_load["daily_reflection_size"]
      self.overlap_reflect_th = scratch_load["overlap_reflect_th"]
      self.kw_strg_event_reflect_th = scratch_load["kw_strg_event_reflect_th"]
      self.kw_strg_thought_reflect_th = scratch_load["kw_strg_thought_reflect_th"]

      self.recency_w = scratch_load["recency_w"]
      self.relevance_w = scratch_load["relevance_w"]
      self.importance_w = scratch_load["importance_w"]
      self.recency_decay = scratch_load["recency_decay"]
      self.importance_trigger_max = scratch_load["importance_trigger_max"]
      self.importance_trigger_curr = scratch_load["importance_trigger_curr"]
      self.importance_ele_n = scratch_load["importance_ele_n"]
      self.thought_count = scratch_load["thought_count"]


  def save(self, out_json=None):
    """
    Save persona's scratch. 

    INPUT: 
      out_json: The file where we wil be saving our persona's state. 
    OUTPUT: 
      None
    """
    scratch = dict() 

    scratch["type"] = self.type
    scratch["address"] = self.address
    scratch["hiveProfileID"] = self.hiveProfileID
    scratch["daily_behavior"] = self.daily_behavior

    scratch["username"] = self.username
    scratch["bio"] = self.bio
    scratch["age"] = self.age
    scratch["personality"] = self.personality
    scratch["meme_expertise"] = self.meme_expertise
    scratch["o_acc_commitment"] = self.currently
    scratch["native_country"] = self.native_country

    scratch["last_stream_interaction"] = self.last_stream_interaction
    scratch["last_dex_dao_interaction"] = self.last_dex_dao_interaction
    scratch["last_hive_dao_interaction"] = self.last_hive_dao_interaction

    scratch["hiveChronicleState"] = self.hiveChronicleState
    scratch["timeStreamState"] = self.timeStreamState

    scratch["att_bandwidth"] = self.att_bandwidth
    scratch["retention"] = self.retention

    scratch["concept_forget"] = self.concept_forget
    scratch["daily_reflection_time"] = self.daily_reflection_time
    scratch["daily_reflection_size"] = self.daily_reflection_size
    scratch["overlap_reflect_th"] = self.overlap_reflect_th
    scratch["kw_strg_event_reflect_th"] = self.kw_strg_event_reflect_th
    scratch["kw_strg_thought_reflect_th"] = self.kw_strg_thought_reflect_th

    scratch["recency_w"] = self.recency_w
    scratch["relevance_w"] = self.relevance_w
    scratch["importance_w"] = self.importance_w
    scratch["recency_decay"] = self.recency_decay
    scratch["importance_trigger_max"] = self.importance_trigger_max
    scratch["importance_trigger_curr"] = self.importance_trigger_curr
    scratch["importance_ele_n"] = self.importance_ele_n
    scratch["thought_count"] = self.thought_count

    if not out_json:
      out_json = CUR_PATH_PERSONAS + self.type + "s/" + self.username + "/scratch.json"
    with open(out_json, "w", encoding='utf-8') as outfile:
      json.dump(scratch, outfile,  indent=2, ensure_ascii=False)


  def set_hiveProfileID(self, profileId):
    self.hiveProfileID = profileId







  def get_iss(self): 
    """
    ISS stands for "identity stable set." This describes the commonset summary
    of this persona -- basically, the bare minimum description of the persona
    that gets used in almost all prompts that need to call on the persona. 
    """
    commonset = ""
    commonset += f"Name: {self.username}\n"
    commonset += f"Address: {self.address}\n"
    commonset += f"HiveProfileID: {self.hiveProfileID}\n"
    commonset += f"Daily Behaviour: {self.daily_behavior}\n"
    commonset += f"Bio: {self.bio}\n"
    commonset += f"last_stream_interaction: {self.last_stream_interaction}\n"
    commonset += f"last_dex_dao_interaction: {self.last_dex_dao_interaction}\n"
    commonset += f"last_hive_dao_interaction: {self.last_hive_dao_interaction}\n"
    
    commonset += f"Age: {self.age}\n"
    commonset += f"personality traits: {self.personality}\n"
    commonset += f"meme_expertise traits: {self.meme_expertise}\n"


    return commonset


  def set_type(self, type):
    self.type = type

  def set_bio(self, bio):
    self.bio = bio

  def set_hiveChronicleState(self, hiveChronicleState):
    self.hiveChronicleState = hiveChronicleState

  def set_timeStreamState(self, timeStreamState):
    self.timeStreamState = timeStreamState


  def set_last_interacted_buzz(self, type_, buzz_index):
    if type_ == "stream":
      self.last_stream_interaction = buzz_index
    elif type_ == "dex_dao":
      self.last_dex_dao_interaction = buzz_index
    elif type_ == "hive_dao":
      self.last_hive_dao_interaction = buzz_index




  def get_hiveChronicleState(self):
    return self.hiveChronicleState
  
  def get_timeStreamState(self):
    return self.timeStreamState









  def get_last_interacted_buzz(self, type_):
    if type_ == "stream":
      return self.last_stream_interaction
    elif type_ == "dex_dao":
      return self.last_dex_dao_interaction
    elif type_ == "hive_dao":
      return self.last_hive_dao_interaction

  def get_type(self): 
    return self.type

  def get_name(self): 
    return self.username


  def get_address(self): 
    return self.address

  def get_hiveProfileID(self):
    return self.hiveProfileID

  def get_bio(self):
    return self.bio

  def get_age(self): 
    return str(self.age)


  def get_personality(self): 
    return self.personality


  def get_meme_expertise(self): 
    return self.meme_expertise


  def get_currently(self): 
    return self.currently


  def get_o_acc_commitment(self): 
    return self.o_acc_commitment


  def get_daily_behavior(self): 
    return self.daily_behavior





















