#
#   Automated Soft Reset Shiny Soft Reset Program for Raspberry Pi.                                                        
#                                                                                               
#   Automatic Shiny Pokemon Soft Resetter for Nintendo DS, Switch.                              
#     -  Uses the Pi Camera to detect shiny Pokemon's colors.                                   
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
#   Limitations:                                                                                
#     -  Must be static (click A to start battle) encounters, not wild spawns or eggs           
#                                                                                               
#   Usage:                                                                                      
#     Search "USER INPUT VALUE" for areas you will need to customize/calibrate for it to work   
#     -  Find a picture or screenshot of the shiny desired and use a color tool to get          
#        the HSV value. Use it to find a lower and upper range to detect                        
#            eg. [43, 55, 85], [90, 195, 195] note opencv scales hsv values to [0-180, 0-255, 0-255]
#     -  Attach and calibrate your servo motors so the pressed_pulsewidth is able to press      
#        the button on your device. While the neutral_pulsewidth doesn't interfere with it      
#     -  Position the Pi Camera above your device's screen where the shiny parts of the         
#        encountered sprite are in frame. Being in focus is not necessary.                      

import numpy as np
import cv2
import os
import sys
import time
import math
from datetime import timedelta
import picamera
import picamera.array
import argparse
import pigpio
import smtplib
from gpiozero import CPUTemperature
from email.MIMEMultipart import MIMEMultipart
from email.MIMEMultipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import threading

# Email notifications
def send_email(): 
  msg = MIMEMultipart()
  msg['From'] = "your_from_email@outlook.com"     # USER INPUT VALUE
  msg["To"] = "your_to_email@outlook.com"         # USER INPUT VALUE
  msg["Subject"] = "Shiny Notification"           # USER INPUT VALUE

  msg_content = MIMEText("Found at: " + str(count) + "\n\n", "plain", "utf-8")
  msg.attach(msg_content)
  # attach a frame of each check as an attachment to the email
  with open(screenshot_directory_path + str(count) + ".jpg", "rb") as f:
    mime = MIMEBase("image", "jpg", filename="img1.jpg")
    mime.add_header("Content-Disposition", "attachment", filename=str(count)+".jpg")
    mime.add_header("X-Attachment-Id", "0")
    mime.add_header("Content-ID", "<0>")
    mime.set_payload(f.read())
    encoders.encode_base64(mime)
    msg.attach(mime)
    
  server = smtplib.SMTP("smtp.outlook.com", 587)      # USER INPUT VALUE
  server.starttls()
  server.login("your_from_email@outlook.com", "pwd")  # USER INPUT VALUE
  server.sendmail("your_from_email@outlook.com", "your_to_email@outlook.com", msg.as_string()) # USER INPUT VALUE
  print("Email sent.")
  server.quit()

# Move the servo motors and show which step it's currently on 
def move_servos(keypress_list):
  print("Count: " + str(count))  

  total_time = sum(j for i, j in keypress_list)
  running_time = 0
  
  for index, delay in enumerate(keypress_list):
    if delay[0] == 1: # A button
      print("[Step " + str(index+1) + "/" + str(len(keypress_list)+1) + "]:\tA Button. \n\t\tTime remaining: " + str(total_time-running_time) + " seconds.")
      pi.set_servo_pulsewidth(servoPIN_2, A_pressed_pulsewidth)
      time.sleep(0.5)
      pi.set_servo_pulsewidth(servoPIN_2, XA_neutral_pulsewidth)

    elif delay[0] == 2: # Menu button
      print("[Step " + str(index+1) + "/" + str(len(keypress_list)+1) + "]:\tMenu Button. \n\t\tTime remaining: " + str(total_time-running_time) + " seconds.")
      pi.set_servo_pulsewidth(servoPIN, menu_pressed_pulsewidth)
      time.sleep(0.4)
      pi.set_servo_pulsewidth(servoPIN, menu_neutral_pulsewidth)

    elif delay[0] == 3: # X button
      print("[Step " + str(index+1) + "/" + str(len(keypress_list)+1) + "]:\tX Button. \n\t\tTime remaining: " + str(total_time-running_time) + " seconds.")
      pi.set_servo_pulsewidth(servoPIN_2, X_pressed_pulsewidth)
      time.sleep(0.5)
      pi.set_servo_pulsewidth(servoPIN_2, XA_neutral_pulsewidth)
    
    elif delay[0] == 4: # Up button - Usually not used but 3rd servo can be connected
      print("[Step " + str(index+1) + "/" + str(len(keypress_list)+1) + "]:\t Up button. \n\t\tTime remaining: " + str(total_time-running_time) + " seconds.")
      pi.set_servo_pulsewidth(servoPIN_3, up_pressed_pulsewidth)
      time.sleep(0.5)
      pi.set_servo_pulsewidth(servoPIN_3, up_neutral_pulsewidth)
    
    elif delay[0] == 5: # Wait with no button
      print("[Step " + str(index+1) + "/" + str(len(keypress_list)+1) + "]:\tWaiting for sprite. \n\t\tTime remaining: " + str(total_time-running_time) + " seconds.")
      
    print("\t\tSleeping for: " + str(delay[1]) + " seconds.")
    running_time += delay[1]
    time.sleep(delay[1])
    
  global shiny_check_duration 
  print("[Step " + str(len(keypress_list)+1) + "/" + str(len(keypress_list)+1) + "]:   Checking the sprite. \n\t\tTime Remaining: " + str(shiny_check_duration) + " seconds.")
  global start_checking_flag
  start_checking_flag = True

# Image filter that will check for the shiny color
def image_filter(frame):
  lower_range = np.array([43, 55, 85])    # USER INPUT VALUE
  upper_range = np.array([90, 195, 195])  # USER INPUT VALUE
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

  for cnt in contours:
    M = cv2.moments(cnt)
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    if (radius > 20): # Positive area is over 20 pixels large
      center = (int(x),int(y))
      radius = int(radius)
      cv2.circle(frame,center,radius,(0,0,255),2)
      shiny_found = True
      count += 1
      if email_sent == False:
        email_sent = True       
        print("Shiny found! Count: " + str(count))
        print("Sending email notification.")
        cv2.imwrite(screenshot_directory_path + str(count) + ".jpg", frame)
        print("Frame recorded.")
        send_email()
        output_stats()

  return frame

# Retrieve the saved number of attempts
def get_count():
  count = 0
  try:
    f = open(count_file_path, "r")
    count = f.read()
    f.close()
  except IOError:
      print("Count file not found, creating file.")
      
  if (count == None or count == ''):
    count = 0
 
  return int(count)

# Save the current number of attempts
def save_count(count):
  f = open(count_file_path, "w")
  f.write(str(count))
  f.close()
  print("Count saved.")

# Display session stats like time elapsed and session resets
def output_stats():
  global startTime
  global initial_count
  elapsed = (time.time() - startTime)
  print('Time elapsed: ' + str(timedelta(seconds=elapsed)))
  print('Resets this session: ' + str(count-initial_count))

# Calculate binomial probabiliy for the current number of attempts
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

# Create a folder for screenshots, screenshots are recorded for each check.
def directoryCreation():
  if not os.path.isdir(screenshot_directory_path):
    print("Creating folder for screenshots: " + screenshot_directory_path)
    os.mkdir(screenshot_directory_path)
  
if __name__ == "__main__":
  screenshot_directory_path = '/home/pi/Desktop/Mewtwo_Soft_Reset/Screenshots/'   # USER INPUT VALUE
  count_file = 'Mewtwo_count.txt'                                                 # USER INPUT VALUE
  count_file_path = '/home/pi/Desktop/Mewtwo_Soft_Reset/' + count_file            # USER INPUT VALUE

  email_sent = False
  shiny_found = False
  frame_recorded = False
  
  startTime = time.time()
  running_time = time.time()
  
  initial_count = count = get_count()  
  print("Saved count read: " + str(initial_count))
  pi = pigpio.pi()

  # Pin of the connected servo motors. Micro 9g ones recommended.
  servoPIN = 24                  # USER INPUT VALUE
  servoPIN_2 = 18                # USER INPUT VALUE
  #servoPIN_3 = 18               # USER INPUT VALUE - Usually not used but 3rd servo can be connected

  menu_pressed_pulsewidth = 2375 # Menu Button USER INPUT VALUE
  menu_neutral_pulsewidth = 1850 # Menu Button USER INPUT VALUE
  
  # One servo motor with an arm that swings both ways can hit X and A
  A_pressed_pulsewidth = 1871    # A Button    USER INPUT VALUE
  XA_neutral_pulsewidth = 1500   # XA Button   USER INPUT VALUE
  X_pressed_pulsewidth = 1125    # X Button    USER INPUT VALUE

  up_pressed_pulsewidth = 2000   # Up Button   USER INPUT VALUE
  up_neutral_pulsewidth = 1500   # Up Button   USER INPUT VALUE

  print("Setting servos to neutral position.")  
  pi.set_servo_pulsewidth(servoPIN, menu_neutral_pulsewidth)
  pi.set_servo_pulsewidth(servoPIN_2, XA_neutral_pulsewidth) 
  #pi.set_servo_pulsewidth(servoPIN_3, up_neutral_pulsewidth) - Usually not used but 3rd servo can be connected
  time.sleep(1)
  print("Servos in neutral position.")  
  
  directoryCreation()
  
  # First element of each tuple is the button identifier, 1-A Button, 2-Menu, 3-X Button, 4-Up, 5-Wait without button
  # Second element is the wait time after each action.
  # USER INPUT VALUE
  keypress_list = [(2, 2),   # Menu button, 2 second wait
                   (3, 1),   # X button, 1 second wait
                   (1, 3.5), # A button, 3.5 second wait
                   (1, 1.5), # A button, 1.5 second wait
                   (1, 24.5),# A button, 24.5 second wait
                   (1, 3.5), # A button, 3.5 second wait
                   (1, 13),  # A button, 13 second wait
                   (1, 0.7), # A button, 0.5 second wait
                   (1, 1),   # A button, 1 second wait
                   (5, 13.6)]# Wait without button, 13.6 second wait

  start_checking_flag = False
  timer_started_flag = False
  t = threading.Thread(target=move_servos, args=(keypress_list,))
  t.daemon = True
  t.start()
  start  = time.time()                 
  
  with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
      cpu = CPUTemperature()
      temperature = int()
      temperature = cpu.temperature
      camera.resolution = (640, 480)
      camera.framerate = 30
      temp_update_time = time.time()
      time_update_interval = 5.0    # Get system temp every 5 seconds, otherwise it updates too often

      wait_time_total = sum(j for i, j in keypress_list) + (0.5 * len(keypress_list))
      wait_time = time.time()
      # How long do we check the sprite before moving on
      shiny_check_duration = 5.4    # USER INPUT VALUE
      while(1):
        camera.capture(output, 'bgr')
        try:
          
          frame = output.array
          output.truncate(0)
          frame = cv2.flip(frame, -1)
          
          if shiny_found == False:
            if start_checking_flag == True:
              if timer_started_flag == False:
                start = time.time()            
                timer_started_flag = True
              else:
                # 1 second before we stop checking, record a frame of the feed. 
                if time.time() - start >= shiny_check_duration-1 and frame_recorded == False:
                  cv2.imwrite(screenshot_directory_path + str(count) + ".jpg", frame)
                  print("Frame recorded.")
                  frame_recorded = True
                # Shiny check timer is done, moving onto next check
                if time.time() - start >= shiny_check_duration:
                  print("Not Shiny")
                  save_count(count)
                  start_checking_flag = False
                  t = threading.Thread(target=move_servos, args=(keypress_list,))
                  t.daemon = True
                  t.start()
                  timer_started_flag = False           
                  count+=1                
                  wait_time = time.time()
                  frame_recorded = False
                # Pass frames to the image filter to check for the shiny color
                else:
                  frame = image_filter(frame)
                  cv2.putText(frame, "Checking...", (12,460), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
                       
          # Get system temp every 5 seconds, otherwise it updates too often
          if time.time() - temp_update_time >= time_update_interval:
            temp_update_time = time.time()
            temperature = cpu.temperature
          # Get cumulative probability for 1/4096 odds
          n = count
          p = 4095.0/4096.0
          prob = 1-binomial(count, p)

          # Place text over the video feed
          font = cv2.FONT_HERSHEY_SIMPLEX
          cv2.putText(frame, "Temp: " + '{0:.2f}'.format(temperature) + "C", (365,40), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)  
          cv2.putText(frame, "Count: " + str(count), (11,40), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA) 
          cv2.putText(frame, "Prob: " + str(round(prob*100, 2)) + "%", (11,80), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
          if start_checking_flag == False:
            cv2.putText(frame, "Waiting..." + str(round((wait_time_total - (time.time() - wait_time)), 1)), (12,460), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)  
          winname = "Live Feed"
          cv2.moveWindow(winname, 0, 564)
          cv2.imshow(winname, frame)

          if 0xFF & cv2.waitKey(5) == 27:
            break
        except KeyboardInterrupt:
          pass
          save_count(count)
          print('\nKeyboard interrupt.')
          print('Process Aborted! Setting servos to neutral position.')
          pi.set_servo_pulsewidth(servoPIN, menu_neutral_pulsewidth)
          pi.set_servo_pulsewidth(servoPIN_2, XA_neutral_pulsewidth)
          #pi.set_servo_pulsewidth(servoPIN_3, up_neutral_pulsewidth)
          time.sleep(1)
          print("Servos in neutral position.")  
          pi.stop()
          output_stats()
          break
        except Exception as e:
          exc_type, exc_obj, tb = sys.exc_info()
          lineno = tb.tb_lineno
          print ('Error caught: ' + str(e) + " @ line " + str(lineno))
        finally:
          pass
