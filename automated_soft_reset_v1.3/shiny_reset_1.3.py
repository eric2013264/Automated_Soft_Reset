#
#   Automated Soft Reset Shiny Soft Reset Program for Raspberry Pi.
# 
#   Automatic Shiny Pokemon Soft Resetter for Nintendo DS, Switch.
#     -  Uses the Pi Camera to detect shiny Pokemon's colors.
#
#   Usage:
#     -  Fill in config.json
#
#   Features:
#     -  Determines if a shiny is encountered by checking if the specified color
#        is detected. This allows it to autonomously decide to continue resetting
#        using attached motor servos or stop and notify you
#     -  Automatically keeps count
#     -  Email notifications when a shiny is found, with a screenshot and the count
#     -  Displays updated cumulative binomial probability
#
#   Requirements:
#     -  OpenCV open computer vision
#     -  pipgiod servo control daemon
#

import numpy as np
import cv2
import os
from os.path import exists
import sys
import time
import math
from datetime import timedelta
import picamera
import picamera.array
import pigpio
import smtplib
from gpiozero import CPUTemperature
from email.MIMEMultipart import MIMEMultipart
from email.MIMEMultipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import threading
# Own modules
import file_ops


def send_email(): 
  msg = MIMEMultipart()
  msg["From"] = email_from
  msg["To"] = email_to
  msg["Subject"] = "Shiny Bot Notification"

  email_body_text = "Found at: " + str(count) + " resets"
  email_body_text += "\n\nShiny check duration remaining: " + str(shiny_check_duration_elapsed) + " sec"
  email_body_text += "\nTime elapsed: " + str(timedelta(seconds=elapsed)).split('.')[0]
  email_body_text += "\nSession resets: " + str(count-saved_count) + "\n\n"
  
  msg_content = MIMEText(email_body_text, "plain", "utf-8")
  msg.attach(msg_content)
  with open(screenshot_directory_path + str(count) + ".jpg", "rb") as f:
    mime = MIMEBase("image", "jpg", filename="img1.jpg")
    mime.add_header("Content-Disposition", "attachment", filename=str(count)+".jpg")
    mime.add_header("X-Attachment-Id", "0")
    mime.add_header("Content-ID", "<0>")
    mime.set_payload(f.read())
    encoders.encode_base64(mime)
    msg.attach(mime)
    
  server = smtplib.SMTP(email_SMTP_server, email_SMTP_server_port)
  server.starttls()
  server.login(email_from, email_from_password)
  server.sendmail(email_from, email_to, msg.as_string())
  print("Email sent.")
  server.quit()

def move_servos(keypress_list):
  print("\nCount: " + str(count))
  if (count-saved_count) > 0:
    print("Session resets: " + str(count-saved_count))
  print("---------------------------------------------------------------")
  total_time = sum(j for i, j in keypress_list)
  running_time = 0
  print("Step\tAction\t\tTime Remaining\tSleep Time")
  for index, delay in enumerate(keypress_list):
    if delay[0] == 1: # A button
      print(str(index+1) + "/" + str(len(keypress_list)+1) + "\tA Button\t" + str(total_time-running_time) + " sec\t" + str(delay[1]) + " sec")
      pi.set_servo_pulsewidth(servo2_XA_pin, servo2_XA_A_Pressed_Pulsewidth)
      time.sleep(0.5)
      pi.set_servo_pulsewidth(servo2_XA_pin, servo2_XA_Neutral_Pulsewidth)

    elif delay[0] == 2: # Menu button
      print(str(index+1) + "/" + str(len(keypress_list)+1) + "\tMenu Button\t" + str(total_time-running_time) + " sec\t" + str(delay[1]) + " sec")
      pi.set_servo_pulsewidth(servo1_MENU_pin, servo1_MENU_Pressed_Pulsewidth)
      time.sleep(0.4)
      pi.set_servo_pulsewidth(servo1_MENU_pin, servo1_MENU_Neutral_Pulsewidth)

    elif delay[0] == 3: # X button
      print(str(index+1) + "/" + str(len(keypress_list)+1) + "\tX Button\t" + str(total_time-running_time) + " sec\t" + str(delay[1]) + " sec")
      pi.set_servo_pulsewidth(servo2_XA_pin, servo2_XA_X_Pressed_Pulsewidth)
      time.sleep(0.5)
      pi.set_servo_pulsewidth(servo2_XA_pin, servo2_XA_Neutral_Pulsewidth)
    
    elif delay[0] == 4: # Up button
      print(str(index+1) + "/" + str(len(keypress_list)+1) + "\tUp button\t" + str(total_time-running_time) + " sec\t" + str(delay[1]) + " sec")
      pi.set_servo_pulsewidth(servo3_UP_pin, servo3_UP_Pressed_Pulsewidth)
      time.sleep(0.5)
      pi.set_servo_pulsewidth(servo3_UP_pin, servo3_UP_Neutral_Pulsewidth)
    
    elif delay[0] == 5: # Wait with no button
      print(str(index+1) + "/" + str(len(keypress_list)+1) + "\tWaiting\t\t" + str(total_time-running_time) + " sec\t" + str(delay[1]) + " sec")

    running_time += delay[1]
    time.sleep(delay[1])
    
  print(str(len(keypress_list)+1) + "/" + str(len(keypress_list)+1) + "\tChecking\t" + str(shiny_check_duration) + " sec\t\t" + str(delay[1]) + " sec\n")

  global start_checking_flag
  start_checking_flag = True

def image_filter(frame):
  lower_range = np.array(color_detection_lower_range)
  upper_range = np.array(color_detection_upper_range)
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  mask = cv2.GaussianBlur(hsv, (11, 11), 0)
  mask = cv2.inRange(mask, lower_range, upper_range)

  res = cv2.bitwise_and(hsv, hsv, mask=mask)
  res = cv2.cvtColor(cv2.cvtColor(res, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
  res = cv2.erode(res, None, iterations=3)
  res = cv2.dilate(res, None, iterations=4)

  contours, _ = cv2.findContours(res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cv2.drawContours(frame, contours, -1, (255, 255, 0), 1)

  global count      
  global email_sent
  global shiny_found
  global elapsed
  global shiny_check_duration_elapsed

  for cnt in contours:
    M = cv2.moments(cnt)
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    if (radius > 20):
      center = (int(x),int(y))
      radius = int(radius)
      cv2.circle(frame,center,radius,(0,0,255),2)
      if shiny_found == False:
        count += 1
      shiny_found = True
      if email_sent == False:
        email_sent = True       
        print("Shiny found! Count: " + str(count))
        print("Sending email notification.")
        cv2.imwrite(screenshot_directory_path + str(count) + ".jpg", frame)
        print("Frame recorded.")
        elapsed = time.time() - start_time
        shiny_check_duration_elapsed = round(shiny_check_duration - (time.time()-start),2)
        send_email()      
        output_stats()

  return frame

def output_stats():
  #global start_time
  #global initial_count
  global elapsed
  print("Time elapsed: " + str(timedelta(seconds=elapsed)).split('.')[0])
  print("Shiny check duration remaining: " + str(str(shiny_check_duration_elapsed)) + " sec")
  print("Session resets: " + str(count-saved_count))

def binomial(trials, success):
  required = trials
  a = math.factorial(required)
  b = math.factorial(trials)
  c = math.factorial(trials - required)
  combinations = b / (a * c)
  percent_success = success ** required
  percent_failure = (1 - success) ** (trials - required)
  answer = combinations * percent_success * percent_failure
  rounded = round(answer, 4)
  return rounded
 
def start_servo_thread():
   t = threading.Thread(target=move_servos, args=(keypress_list,))
   t.daemon = True
   t.start() 

if __name__ == "__main__":
  print("\nStarting...\nReading config file...")
  
  # Read the config file for parameters
  arguments_dict = file_ops.read_config_file()

  pokemon_name = arguments_dict["pokemon_name"]
  color_detection_lower_range = arguments_dict["color_detection_lower_range"]
  color_detection_upper_range = arguments_dict["color_detection_upper_range"]
  shiny_check_duration = arguments_dict["shiny_check_duration"]
  servo1_MENU_pin = arguments_dict["servo1_MENU_pin"]
  servo2_XA_pin = arguments_dict["servo2_XA_pin"]
  servo3_UP_pin = arguments_dict["servo3_UP_pin"]
  servo1_MENU_Pressed_Pulsewidth = arguments_dict["servo1_MENU_Pressed_Pulsewidth"]
  servo1_MENU_Neutral_Pulsewidth = arguments_dict["servo1_MENU_Neutral_Pulsewidth"]
  servo2_XA_A_Pressed_Pulsewidth = arguments_dict["servo2_XA_A_Pressed_Pulsewidth"]
  servo2_XA_Neutral_Pulsewidth = arguments_dict["servo2_XA_Neutral_Pulsewidth"]
  servo2_XA_X_Pressed_Pulsewidth = arguments_dict["servo2_XA_X_Pressed_Pulsewidth"]
  servo3_UP_Pressed_Pulsewidth = arguments_dict["servo3_UP_Pressed_Pulsewidth"]
  servo3_UP_Neutral_Pulsewidth = arguments_dict["servo3_UP_Neutral_Pulsewidth"]
  keypress_list = arguments_dict["keypress_list"]
  email_from = arguments_dict["email_from"]
  email_to = arguments_dict["email_to"]
  email_from_password = arguments_dict["email_from_password"]
  email_SMTP_server = arguments_dict["email_SMTP_server"]
  email_SMTP_server_port = arguments_dict["email_SMTP_server_port"]
  # Build the file paths for the 3 directories/files we need to create
  script_running_path = os.path.dirname(os.path.realpath(__file__))
  reset_directory = script_running_path + "/" + pokemon_name + "_Soft_Reset/"
  screenshot_directory_path = reset_directory + "Screenshots/"
  count_file_directory_path = reset_directory + pokemon_name + "_Reset_Count.txt"
  # Keypress list needs more love
  for index, delay in enumerate(keypress_list):
    keypress_list[index] = (delay[0], delay[1])     
  
  # Flags
  email_sent = False
  shiny_found = False
  frame_recorded = False
  # For Stats
  shiny_check_duration_elapsed = 0
  elapsed = timedelta(0)

  print("Reading count file...")
  count = saved_count = file_ops.directory_check_read_save(reset_directory, count_file_directory_path, screenshot_directory_path)
  print("Count read from count file: " + str(saved_count))
  pi = pigpio.pi()

  print("Setting servos to neutral position...")  
  pi.set_servo_pulsewidth(servo1_MENU_pin, servo1_MENU_Neutral_Pulsewidth)
  pi.set_servo_pulsewidth(servo2_XA_pin, servo2_XA_Neutral_Pulsewidth) 
  #pi.set_servo_pulsewidth(servo3_UP_pin, servo3_UP_Neutral_Pulsewidth)
  time.sleep(1)
  print("Servos in neutral position.")  

  # Timers
  start_time = start = time.time() # Start time is when the script begins executing, used for time elapsed. Start is initialized here, used
  start_checking_flag = timer_started_flag = False
  start_servo_thread()         
   
  with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
      cpu = CPUTemperature()
      temperature = int()
      temperature = cpu.temperature
      camera.resolution = (645, 480)
      camera.framerate = 30
      temp_update_time = time.time()
      time_update_interval = 5.0
      
      wait_time_total = sum(j for i, j in keypress_list) + (0.5 * len(keypress_list)) # wait time for servos/reset cycle
      wait_time = time.time()
      while(1):
        camera.capture(output, "bgr")
        try: 
          frame = output.array
          output.truncate(0)
          frame = cv2.flip(frame, -1)
          
          if shiny_found == False:
            if start_checking_flag == True:   # Flipped when servos are done
              if timer_started_flag == False: # As we begin checking, maintain a timer 
                start = time.time()            
                timer_started_flag = True     # Begun checking
              else:
                if time.time()-start >= shiny_check_duration-1 and frame_recorded == False: # One second left in the check and we haven't recorded a frame yet
                  cv2.imwrite(screenshot_directory_path + str(count) + ".jpg", frame)
                  print("Frame recorded.")
                  frame_recorded = True       # We only want one frame per check
                if time.time()-start >= shiny_check_duration: # Done checking, timer > our set duration


                  print("Not Shiny")
                  count+=1                    # Not shiny, increment count
                  file_ops.save_count(count, count_file_directory_path)
                  start_checking_flag = False # Reset flag for next check
                  start_servo_thread()
                  timer_started_flag = False  # Reset timer for next check                    
                  wait_time = time.time()     # Reset the wait time, this counts up and is subtracted from the wait_time_total
                  frame_recorded = False
                else:
                  frame = image_filter(frame)
                  cv2.putText(frame, "Checking..." + str(round(shiny_check_duration - (time.time()-start),1)) + " sec", (12,460), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
          else:
            frame = image_filter(frame)
            cv2.putText(frame, "Found!", (12,460), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)          
          # Get temp
          if time.time() - temp_update_time >= time_update_interval:
              
            temp_update_time = time.time()
            temperature = cpu.temperature
          # Get cumulative probability
          p = 4095.0/4096.0
          prob = 1-binomial(count, p)

          font = cv2.FONT_HERSHEY_SIMPLEX
          cv2.putText(frame, "Temp: " + "{0:.2f}".format(temperature) + "C", (365,40), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)  
          cv2.putText(frame, "Count: " + str(count), (11,40), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA) 
          cv2.putText(frame, "Prob: " + str(round(prob*100, 2)) + "%", (11,80), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
          if start_checking_flag == False:                    # Can this line be simplified? we should only need total - wait? 
            cv2.putText(frame, "Waiting..." + str(round((wait_time_total - (time.time() - wait_time)), 1))  + " sec", (12,460), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)  
          winname = "Live Feed"
          cv2.moveWindow(winname, 0, 550)
          cv2.imshow(winname, frame)

          if 0xFF & cv2.waitKey(5) == 27:
            break
        except KeyboardInterrupt:
          pass
          file_ops.save_count(count, count_file_directory_path)
          print("\nKeyboard interrupt.")
          print("Process Aborted! Setting servos to neutral position...")
          pi.set_servo_pulsewidth(servoPIN, menu_neutral_pulsewidth)
          pi.set_servo_pulsewidth(servoPIN_2, XA_neutral_pulsewidth)
          #pi.set_servo_pulsewidth(servoPIN_3, up_neutral_pulsewidth)
          time.sleep(1)
          print("Servos in neutral position.\nDone.")  
          pi.stop()
          break
        except Exception as e:
          exc_type, exc_obj, tb = sys.exc_info()
          lineno = tb.tb_lineno
          print ("Error caught: " + str(e) + " @ line " + str(lineno))
        finally:
          pass