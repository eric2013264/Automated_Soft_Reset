#   Automated Soft Reset: A Shiny Soft Reset Program for Raspberry Pi.  
<h4> Python program that runs on most Raspberry Pi computers, works on Nintendo DS and Nintendo Switch </h4>
Shiny Pokemon are rare and time consuming to find. Prior to gen 5, the probability of randomly encountering a shiny Pokemon was 1/8192 or 0.01220703125% (The rate for Gen 5 and onwards is 1/4096). <br><br>

Ok but how rare is that? Math time: Using pre gen 5 odds of 1/8192, to reach a cumulative probability of 50%, you'd need to reset 5678 times. Given an average reset time of 50 seconds, that's >78 hours of non-stop resetting. <br>

So I used a Raspberry Pi and created an OpenCV solution that automatically soft resets until a shiny is found. 
It uses a standard Pi Camera, and 2-3 micro servos. 


Example Circuit Diagram    |  Screenshot of Shiny Found in HGSS    | Screenshot of Shiny Found in BDSP
:-------------------------:|:-------------------------:|:-------------------------:
<img src="https://user-images.githubusercontent.com/10005573/147976917-bfce26ea-17a5-4122-a78c-d959c8213df3.jpg" alt="Example Circuit Diagram" width='300' height='300'>  |  <img src="https://user-images.githubusercontent.com/10005573/148609658-8228224d-41ef-449e-a2bc-73d8da9e29ff.png" alt="Screenshot of Shiny Found in HGSS" width='228' height='365'>  |  <img src="https://user-images.githubusercontent.com/10005573/148609662-f953214b-d322-4e09-b80f-e0396c851982.png" alt="Screenshot of Shiny Found in BDSP" width='228' height='365'>
                                                                 

                                                                  
<h4>Features:</h4>                                                                                   
<ul>
  <li>Determines if a shiny is encountered by checking if the specified color                
     is detected. This allows it to autonomously decide to continue resetting               
     using attached motor servos or stop and notify you.</li>
  <li>Automatically keeps count.</li>
  <li>Email notifications when a shiny is found, with a screenshot and the count.</li>
  <li>Displays updated cumulative binomial probability.</li>
</ul>
<h4>Requirements:</h4>                                                                               
<ul>
  <li>OpenCV open computer vision.</li>
  <li>pipgiod servo control daemon.</li>
</ul>                                                                                            
<h4>Limitations:</h4>                                                                                
<ul>
  <li>Must be static (click A to start battle) encounters, not wild spawns or eggs.</li>
</ul>
<h4>Usage:</h4>
  Search "USER INPUT VALUE" for areas you will need to customize/calibrate for it to work.<br>
  <ul>
    <li>Find a picture or screenshot of the shiny desired and use a color tool to get
        the HSV value. Use it to find a lower and upper range to detect.
          eg. [43, 55, 85], [90, 195, 195] note opencv scales hsv values to [0-180, 0-255, 0-255]. </li>
    <li>Attach and calibrate your servo motors so the pressed_pulsewidth is able to press
        the button on your device. While the neutral_pulsewidth doesn't interfere with it. 
      You may 3D print a holder or mount them using mounting tape. </li>  
    <li>Position the Pi Camera above your device's screen where the sprite's shiny portions
        are in frame. Having the feed be in focus is not necessary. </li>

