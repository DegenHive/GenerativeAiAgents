"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: scratch.py
Description: Defines the short-term memory module for generative agents.
"""
import datetime
import json
import sys
sys.path.append('../../')

from global_methods import *

class Scratch: 

  def __init__(self, f_saved): 

    # THE CORE IDENTITY OF THE PERSONA 
    self.address = None
    self.hiveProfileID = None
    self.daily_finances = None

    self.username = None
    self.bio = None
    self.age = None
    self.personality = None
    self.ai_skills_behaviour = None
    self.currently = None
    self.o_acc_nativeness = None
    self.native_country = None

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

      self.address = scratch_load["address"]
      self.hiveProfileID = scratch_load["hiveProfileID"]
      self.daily_finances = scratch_load["daily_finances"]

      self.username = scratch_load["username"]
      self.bio = scratch_load["bio"]
      self.age = scratch_load["age"]
      self.personality = scratch_load["personality"]
      self.ai_skills_behaviour = scratch_load["ai_skills_behaviour"]
      self.currently = scratch_load["degen_nativeness"]
      self.o_acc_nativeness = scratch_load["o_acc_nativeness"]
      self.native_country = scratch_load["native_country"]

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


  def save(self, out_json):
    """
    Save persona's scratch. 

    INPUT: 
      out_json: The file where we wil be saving our persona's state. 
    OUTPUT: 
      None
    """
    scratch = dict() 

    scratch["address"] = self.address
    scratch["hiveProfileID"] = self.hiveProfileID
    scratch["daily_finances"] = self.daily_finances

    scratch["username"] = self.username
    scratch["bio"] = self.bio
    scratch["age"] = self.age
    scratch["personality"] = self.personality
    scratch["ai_skills_behaviour"] = self.ai_skills_behaviour
    scratch["degen_nativeness"] = self.currently
    scratch["o_acc_nativeness"] = self.o_acc_nativeness
    scratch["native_country"] = self.native_country
    scratch["daily_finances"] = self.daily_finances

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

    scratch["curr_time"] = self.curr_time.strftime("%B %d, %Y, %H:%M:%S")


    with open(out_json, "w") as outfile:
      json.dump(scratch, outfile, indent=2) 


  def get_str_iss(self): 
    """
    ISS stands for "identity stable set." This describes the commonset summary
    of this persona -- basically, the bare minimum description of the persona
    that gets used in almost all prompts that need to call on the persona. 

    INPUT
      None
    OUTPUT
      the identity stable set summary of the persona in a string form.
    EXAMPLE STR OUTPUT
      "Name: Dolores Heitmiller
       Age: 28
       personality traits: hard-edged, independent, loyal
       ai_skills_behaviour traits: Dolores is a painter who wants live quietly and paint 
         while enjoying her everyday life.
       Currently: Dolores is preparing for her first solo show. She mostly 
         works from home.
       o_acc_nativeness: Dolores goes to bed around 11pm, sleeps for 7 hours, eats 
         dinner around 6pm.
       Daily plan requirement: Dolores is planning to stay at home all day and 
         never go out."
    """
    commonset = ""
    commonset += f"Name: {self.username}\n"
    commonset += f"Address: {self.address}\n"
    commonset += f"HiveProfileID: {self.hiveProfileID}\n"
    commonset += f"Daily Finances: {self.daily_finances}\n"
    commonset += f"Bio: {self.bio}\n"
    
    commonset += f"Age: {self.age}\n"
    commonset += f"personality traits: {self.personality}\n"
    commonset += f"ai_skills_behaviour traits: {self.ai_skills_behaviour}\n"
    commonset += f"Currently: {self.currently}\n"
    commonset += f"o_acc_nativeness: {self.o_acc_nativeness}\n"
    commonset += f"Daily plan requirement: {self.daily_finances}\n"
    return commonset


  def get_str_name(self): 
    return self.username


  def get_str_address(self): 
    return self.address

  def get_hiveProfileID(self):
    return self.hiveProfileID

  def get_bio(self):
    return self.bio

  def get_str_age(self): 
    return str(self.age)


  def get_str_personality(self): 
    return self.personality


  def get_str_ai_skills_behaviour(self): 
    return self.ai_skills_behaviour


  def get_str_currently(self): 
    return self.currently


  def get_str_o_acc_nativeness(self): 
    return self.o_acc_nativeness


  def get_str_daily_finances(self): 
    return self.daily_finances





















