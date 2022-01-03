# Automated Soft Reset
I saw a similar solution years ago for automating the tedious task of hunting for shiny Pokemon. <br>
1/4096 encounters! Older versions were 1/8192!<br>
So I created an OpenCV solution that runs on a Raspberry Pi that automatically soft resets until a shiny is found.<br>


Shiny Resetter 1.1 for Raspberry Pi.                                                        
                                                                                            
Automatic Shiny Pokemon Soft Resetter for Nintendo DS, Switch.                              
  -  Uses the Pi Camera to detect shiny Pokemon's colors.                                   
                                                                                            
Features:                                                                                   
  -  Determines if a shiny is encountered by checking if the specified color                
     is detected. This allows it to autonomously decide to continue resetting               
     using attached motor servos or stop and notify you                                     
  -  Automatically keeps count                                                              
  -  Email notifications when a shiny is found, with a screenshot and the count             
  -  Displays updated cumulative binomial probability                                       
                                                                                            
Requirements:                                                                               
  -  OpenCV open computer vision                                                            
  -  pipgiod servo control daemon                                                           
                                                                                            
Limitations:                                                                                
  -  Must be static (click A to start battle) encounters, not wild spawns or eggs           
                                                                                            
Usage:                                                                                      
  Search "USER INPUT VALUE" for areas you will need to customize/calibrate for it to work   
  -  Find a picture or screenshot of the shiny desired and use a color tool to get          
     the HSV value. Use it to find a lower and upper range to detect                        
         eg. [43, 55, 85], [90, 195, 195] note opencv scales hsv values to [0-180, 0-255, 0-255]
  -  Attach and calibrate your servo motors so the pressed_pulsewidth is able to press      
     the button on your device. While the neutral_pulsewidth doesn't interfere with it      
  -  Position the Pi Camera above your device's screen where the shiny parts of the         
     encountered sprite are in frame. Being in focus is not necessary.     
