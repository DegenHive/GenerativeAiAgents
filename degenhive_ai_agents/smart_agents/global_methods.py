"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: global_methods.py
Description: Contains functions used throughout my projects.
"""
import random
import string
import csv
import time
import datetime as dt
import pathlib
import os
import sys
import numpy
import math
import shutil, errno
import json

from os import listdir


""" MAKE PERSONA FOLDER WHICH HOLDS ITS MEMORY """
def create_persona_folder_if_not_there(curr_path, persona_json):
  create_folder_if_not_there(curr_path)

  create_folder_if_not_there(curr_path + "/generations" )
  create_folder_if_not_there(curr_path + "/generations/leonardo" )
  create_folder_if_not_there(curr_path + "/generations/dalle" )
  create_file_if_not_there(curr_path + "/generations" + "/generations.json")  

  # create social memory file and associative memory folder
  create_file_if_not_there(curr_path + "/social_memory.json")
  with open(curr_path + "/social_memory.json", "w") as outfile:
      json.dump({}, outfile, indent=2) 

  create_folder_if_not_there(curr_path + "/associative_memory")
  create_file_if_not_there(curr_path + "/associative_memory"+ "/embeddings.json")
  with open(curr_path + "/associative_memory"+ "/embeddings.json", "w") as outfile:
      json.dump({}, outfile, indent=2)   
  create_file_if_not_there(curr_path + "/associative_memory"+ "/kw_strength.json")
  with open(curr_path + "/associative_memory"+ "/kw_strength.json", "w") as outfile:
      json.dump({}, outfile, indent=2)   
  create_file_if_not_there(curr_path + "/associative_memory"+ "/nodes.json")
  with open(curr_path + "/associative_memory"+ "/nodes.json", "w") as outfile:
      json.dump({}, outfile, indent=2) 
  # create scratch file
  create_file_if_not_there(curr_path + "/scratch.json")

  scratch = dict() 
  scratch["username"] = persona_json["username"]
  scratch["address"] = persona_json["address"]
  scratch["hiveProfileID"] = ""

  if "bio" not in persona_json: 
    scratch["bio"] = ""
  else: 
    scratch["bio"] = persona_json["bio"]

  scratch["type"] = persona_json["type"]
  scratch["age"] = persona_json["age"]
  scratch["personality"] = persona_json["personality"]
  scratch["meme_expertise"] = persona_json["meme_expertise"]
  scratch["o_acc_commitment"] = persona_json["o_acc_commitment"]
  scratch["native_country"] = persona_json["native_country"]
  scratch["daily_behavior"] = persona_json["daily_behavior"]

  scratch["last_stream_interaction"] = None
  scratch["last_dex_dao_interaction"] = None
  scratch["last_hive_dao_interaction"] = None

  scratch["att_bandwidth"] = 8
  scratch["retention"] = 8
  scratch["att_bandwidth"] = 8
  scratch["retention"] = 8
  scratch["concept_forget"] = 100
  scratch["daily_reflection_time"] = 180
  scratch["daily_reflection_size"] = 5
  scratch["overlap_reflect_th"] = 4
  scratch["kw_strg_event_reflect_th"] = 10
  scratch["kw_strg_thought_reflect_th"] = 9
  scratch["recency_w"] = 1
  scratch["relevance_w"] = 1
  scratch["importance_w"] = 1
  scratch["recency_decay"] = 0.995
  scratch["importance_trigger_max"] = 150
  scratch["importance_trigger_curr"] = 150
  scratch["importance_ele_n"] = 0
  scratch["thought_count"] = 5

  with open(curr_path + "/scratch.json", "w") as outfile:
      json.dump(scratch, outfile, indent=2) 



def create_folder_if_not_there(curr_path): 
  """
  Checks if a folder in the curr_path exists. If it does not exist, creates
  the folder. 
  Note that if the curr_path designates a file location, it will operate on 
  the folder that contains the file. But the function also works even if the 
  path designates to just a folder. 
  Args:
    curr_list: list to write. The list comes in the following form:
               [['key1', 'val1-1', 'val1-2'...],
                ['key2', 'val2-1', 'val2-2'...],]
    outfile: name of the csv file to write    
  RETURNS: 
    True: if a new folder is created
    False: if a new folder is not created
  """
  outfolder_name = curr_path.split("/")
  if len(outfolder_name) != 1: 
    # This checks if the curr path is a file or a folder. 
    if "." in outfolder_name[-1]: 
      outfolder_name = outfolder_name[:-1]

    outfolder_name = "/".join(outfolder_name)
    if not os.path.exists(outfolder_name):
      os.makedirs(outfolder_name)
      return True

  return False 


def create_file_if_not_there(curr_file):
  """
  Checks if a file exists. If it does not exist, creates the file. 
  Args:
    curr_file: name of the file to create
  RETURNS: 
    None
  """
  if not os.path.exists(curr_file):
    open(curr_file, 'w').close()



def write_list_of_list_to_csv(curr_list_of_list, outfile):
  """
  Writes a list of list to csv. 
  Unlike write_list_to_csv_line, it writes the entire csv in one shot. 
  ARGS:
    curr_list_of_list: list to write. The list comes in the following form:
               [['key1', 'val1-1', 'val1-2'...],
                ['key2', 'val2-1', 'val2-2'...],]
    outfile: name of the csv file to write    
  RETURNS: 
    None
  """
  create_folder_if_not_there(outfile)
  with open(outfile, "w") as f:
    writer = csv.writer(f)
    writer.writerows(curr_list_of_list)


def write_list_to_csv_line(line_list, outfile): 
  """
  Writes one line to a csv file.
  Unlike write_list_of_list_to_csv, this opens an existing outfile and then 
  appends a line to that file. 
  This also works if the file does not exist already. 
  ARGS:
    curr_list: list to write. The list comes in the following form:
               ['key1', 'val1-1', 'val1-2'...]
               Importantly, this is NOT a list of list. 
    outfile: name of the csv file to write   
  RETURNS: 
    None
  """
  create_folder_if_not_there(outfile)

  # Opening the file first so we can write incrementally as we progress
  curr_file = open(outfile, 'a',)
  csvfile_1 = csv.writer(curr_file)
  csvfile_1.writerow(line_list)
  curr_file.close()


def read_file_to_list(curr_file, header=False, strip_trail=True): 
  """
  Reads in a csv file to a list of list. If header is True, it returns a 
  tuple with (header row, all rows)
  ARGS:
    curr_file: path to the current csv file. 
  RETURNS: 
    List of list where the component lists are the rows of the file. 
  """
  if not header: 
    analysis_list = []
    with open(curr_file) as f_analysis_file: 
      data_reader = csv.reader(f_analysis_file, delimiter=",")
      for count, row in enumerate(data_reader): 
        if strip_trail: 
          row = [i.strip() for i in row]
        analysis_list += [row]
    return analysis_list
  else: 
    analysis_list = []
    with open(curr_file) as f_analysis_file: 
      data_reader = csv.reader(f_analysis_file, delimiter=",")
      for count, row in enumerate(data_reader): 
        if strip_trail: 
          row = [i.strip() for i in row]
        analysis_list += [row]
    return analysis_list[0], analysis_list[1:]


def read_file_to_set(curr_file, col=0): 
  """
  Reads in a "single column" of a csv file to a set. 
  ARGS:
    curr_file: path to the current csv file. 
  RETURNS: 
    Set with all items in a single column of a csv file. 
  """
  analysis_set = set()
  with open(curr_file) as f_analysis_file: 
    data_reader = csv.reader(f_analysis_file, delimiter=",")
    for count, row in enumerate(data_reader): 
      analysis_set.add(row[col])
  return analysis_set


def get_row_len(curr_file): 
  """
  Get the number of rows in a csv file 
  ARGS:
    curr_file: path to the current csv file. 
  RETURNS: 
    The number of rows
    False if the file does not exist
  """
  try: 
    analysis_set = set()
    with open(curr_file) as f_analysis_file: 
      data_reader = csv.reader(f_analysis_file, delimiter=",")
      for count, row in enumerate(data_reader): 
        analysis_set.add(row[0])
    return len(analysis_set)
  except: 
    return False


def check_if_file_exists(curr_file): 
  """
  Checks if a file exists
  ARGS:
    curr_file: path to the current csv file. 
  RETURNS: 
    True if the file exists
    False if the file does not exist
  """
  try: 
    with open(curr_file) as f_analysis_file: pass
    return True
  except: 
    return False


def find_filenames(path_to_dir, suffix=".csv"):
  """
  Given a directory, find all files that ends with the provided suffix and 
  returns their paths.  
  ARGS:
    path_to_dir: Path to the current directory 
    suffix: The target suffix.
  RETURNS: 
    A list of paths to all files in the directory. 
  """
  filenames = listdir(path_to_dir)
  return [ path_to_dir+"/"+filename 
           for filename in filenames if filename.endswith( suffix ) ]


def average(list_of_val): 
  """
  Finds the average of the numbers in a list.
  ARGS:
    list_of_val: a list of numeric values  
  RETURNS: 
    The average of the values
  """
  return sum(list_of_val)/float(len(list_of_val))


def std(list_of_val): 
  """
  Finds the std of the numbers in a list.
  ARGS:
    list_of_val: a list of numeric values  
  RETURNS: 
    The std of the values
  """
  std = numpy.std(list_of_val)
  return std


def copyanything(src, dst):
  """
  Copy over everything in the src folder to dst folder. 
  ARGS:
    src: address of the source folder  
    dst: address of the destination folder  
  RETURNS: 
    None
  """
  try:
    shutil.copytree(src, dst)
  except OSError as exc: # python >2.5
    if exc.errno in (errno.ENOTDIR, errno.EINVAL):
      shutil.copy(src, dst)
    else: raise


if __name__ == '__main__':
  pass
















