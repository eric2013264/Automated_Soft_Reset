import os
from os.path import exists
import json

def create_count_file(count_file_path):
  count = 0
  try: # Create and write
    f = open(count_file_path, "w")
    f.write(str(count))
    f.close()
  except (OSError, IOError) as e:
    print("Error: " + str(e) + " Failed to create count file.")
      
def get_count(count_file_path):
  count = 0

  if exists(count_file_path):
    try:
      f = open(count_file_path, "r")
      count = f.read()
      if (count != None and len(count) < 1): # file doesn't exist or was empty?
        print("Count file was empty. Starting count at 0.")
        f.close()
        create_count_file(count_file_path)
        count = 0
      else:
        count = int(count)
        print("Read complete.")
      f.close()
    except (OSError, IOError) as e:
      print("Error: " + str(e) + "\nCreating file 1/1: Count file.")
      create_count_file(count_file_path)
  else:
    print("Creating file 1/1: Count file (" + count_file_path + ")")
    create_count_file(count_file_path)
    
  return count

def save_count(count, count_file_path):
  f = open(count_file_path, "w")
  f.write(str(count))
  f.close()
  print("Count saved.")

def directory_check_read_save(reset_directory, count_file_directory_path, screenshot_directory_path):
  # Check if the main folder is there, create if not
  if not os.path.exists(reset_directory):
    print("Creating folder 1/2: Reset Folder (" + reset_directory + ")")
    os.mkdir(reset_directory)

  # Check if the screenshot folder is there, create if not
  if not os.path.exists(screenshot_directory_path):
    print("Creating folder 2/2: Screenshots (" + screenshot_directory_path + ")")
    os.mkdir(screenshot_directory_path)

  # Check if the count file is there, create if not
  return get_count(count_file_directory_path)

def read_config_file():
  # Get the directory the script is being run from
  curr_dir = os.path.dirname(os.path.realpath(__file__))

  if not exists(curr_dir + "/config.json"):
    print("Config file not found in current working directory.")
    return
  f = open(curr_dir + "/config.json")
  json_data = json.load(f)
  arguments_dict = {}

  for key in json_data:
    value = json_data[key]
    arguments_dict[key] = value
  f.close()
  print("Read complete.")
  
  return arguments_dict
