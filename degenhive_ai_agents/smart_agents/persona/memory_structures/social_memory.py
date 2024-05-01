"""
Author: Joon Sung Park (joonspk@stanford.edu) | Rahul Mittal (buidl@degenhive.ai)

File: social_memory.py
Description: Defines the MemoryTree class that serves as the agents' social
memory that provides context over the personas they are engaging with to regulate their behavior in the game world. 
"""
import json
import sys
sys.path.append('../../')

from utils import *
from global_methods import *

class MemoryTree: 


  def __init__(self, f_saved): 
    self.tree = {}
    if check_if_file_exists(f_saved): 
      self.tree = json.load(open(f_saved))


  def print_tree(self): 
    def _print_tree(tree, depth):
      dash = " >" * depth
      if type(tree) == type(list()): 
        if tree:
          print (dash, tree)
        return 

      for key, val in tree.items(): 
        if key: 
          print (dash, key)
        _print_tree(val, depth+1)
    
    _print_tree(self.tree, 0)
    

  def save(self, out_json):
    with open(out_json, "w") as outfile:
      json.dump(self.tree, outfile) 



  def get_str_accessible_users(self, curr_simulation): 
    """
    """
    x = ", ".join(list(self.tree[curr_simulation].keys()))
    return x



if __name__ == '__main__':
  x = f"../../../../environment/frontend_server/storage/the_ville_base_LinFamily/personas/Eddy Lin/social_memory.json"
  x = MemoryTree(x)
  x.print_tree()






