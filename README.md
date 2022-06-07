#   Automated Soft Reset: A Shiny Soft Reset Program for Raspberry Pi.  
<h4> Python program that runs on most Raspberry Pi, works on Nintendo DS and Nintendo Switch </h4>

Example Circuit Diagram    |  Screenshot of Shiny Found in HGSS    | Screenshot of Shiny Found in BDSP
:-------------------------:|:-------------------------:|:-------------------------:
<img src="https://user-images.githubusercontent.com/10005573/147976917-bfce26ea-17a5-4122-a78c-d959c8213df3.jpg" alt="Example Circuit Diagram" width='300' height='300'>  |  <img src="https://user-images.githubusercontent.com/10005573/148609658-8228224d-41ef-449e-a2bc-73d8da9e29ff.png" alt="Screenshot of Shiny Found in HGSS" width='228' height='365'>  |  <img src="https://user-images.githubusercontent.com/10005573/148609662-f953214b-d322-4e09-b80f-e0396c851982.png" alt="Screenshot of Shiny Found in BDSP" width='228' height='365'>
      
<h4> Background </h4>
Shiny Pokemon are rare and time consuming to find. Prior to gen 5, the probability of randomly encountering a shiny Pokemon was 1/8192 or 0.01220703125% (The rate for Gen 5 and onwards is 1/4096). Using pre gen 5 odds of 1/8192, to reach a cumulative probability of 50%, you'd need to reset 5678 times. Given an average reset time of 50 seconds, that's >78 hours of non-stop resetting.

So I used a Raspberry Pi and created an OpenCV solution that automatically soft resets until a shiny is found.<br>
It uses a standard Pi Camera, and 2-3 micro servos. 

---                                                        
                                                                  
<h4>Description:</h4>                                                                                   
<ul>
  <li>Determines if a shiny is encountered by checking if the specified color is detected.</li>
	<li>Customizable reset cycle, the sequence of button presses and wait times.</li>
	<li>Automatically keeps count.</li>
	<li>Notifies you via email notifications when a shiny is found, with a screenshot, count, and other stats.</li>
	<li>Displays updated cumulative binomial probability.</li>
	<li>Records a frame/image from every check.</li>
</ul>

---

<h4>Requirements:</h4>
<ul>
  <li>OpenCV</li>
  <li>Pipgiod</li>
</ul>         

---

<h4>Usage</h4>

- Attach PiCamera to the Raspberry Pi and position camera and servos in position.
- Download or clone the entire directory from the repo.
- Fill in the config file. See additional details below.
- Run with the below command:
```
python shiny_reset_1.3.py   
```
  - Each check will generate a screenshot that is saved under the folder: 
```
<pokemon_name>_Shiny_Reset/Screenshots
```
  - Current count is saved under in the file: 
```
<pokemon_name>_Shiny_Reset/<pokemon_name>_reset_count.txt
```
 ---   

<h4>Config</h4>

	example config: 	
	{
		"pokemon_name": "Charizard", 
		"color_detection_lower_range": [130, 70, 100],
		"color_detection_upper_range": [180, 235, 195],
		"shiny_check_duration": 3.6, 
		"servo1_MENU_pin": 24,
		"servo2_XA_pin": 18,
		"servo3_UP_pin": 17,
		"servo1_MENU_Pressed_Pulsewidth": 2375,
		"servo1_MENU_Neutral_Pulsewidth": 1850,
		"servo2_XA_A_Pressed_Pulsewidth": 1975,
		"servo2_XA_Neutral_Pulsewidth": 1500,
		"servo2_XA_X_Pressed_Pulsewidth": 1100,
		"servo3_UP_Pressed_Pulsewidth": 2000,
		"servo3_UP_Neutral_Pulsewidth": 1500,
		"keypress_list": [[2, 2.0], [3, 1.0], [1, 3.5], [1, 1.5], [1, 24.5], [1, 3.5], [1, 13.0], [1, 0.7], [1, 1.0], [5, 13.29]],
		"email_from": "from_address@outlook.com",
		"email_to": "to_address@outlook.com",
		"email_from_password": "pwd",
		"email_SMTP_server": "smtp.outlook.com",
		"email_SMTP_server_port": 587
	}

| Config  | Description |
| ------------- | ------------- |
| pokemon_name | Which Pokemon you're resetting for, this will be used in the folder names. Each new Pokemon will create a new folder that will hold the screenshot folder and count file. |
| color_detection_lower_range | The lower HSV (0-180, 0-255, 0-255) range of the shiny color you are looking for. |
| color_detection_upper_range | The upper HSV (0-180, 0-255, 0-255) range of the shiny color you are looking for. |
| shiny_check_duration | How long the program checks for the shiny color until it resets again. |
| servo1_MENU_pin | The GPIO pin of the servo controlling the menu button. |
| servo2_XA_pin | The GPIO pin of the servo controlling the X and/or A buttons. |
| servo3_UP_pin | The GPIO pin of the servo controlling the up joystick or button. |
| servo1_MENU_Pressed_Pulsewidth | The pulse width sent to the menu servo to press the menu button. |
| servo1_MENU_Neutral_Pulsewidth | The pulse width sent to the menu servo to stay clear of the menu button. |
| servo2_XA_A_Pressed_Pulsewidth | The pulse width sent to the menu servo to press the A button. |
| servo2_XA_Neutral_Pulsewidth | The pulse width sent to the menu servo to stay clear of the XA buttons. |
| servo2_XA_X_Pressed_Pulsewidth | The pulse width sent to the menu servo to press the X button. |
| servo3_UP_Pressed_Pulsewidth | The pulse width sent to the menu servo to press the Up joystick or button. |
| servo3_UP_Neutral_Pulsewidth | The pulse width sent to the menu servo to press the Up joystick or button. |
| keypress_list | A list of timings for the reset sequence. The first element of each sublist is the action where 1 is A, 2 is Menu, 3 is X, and 4 is Up, and 5 is wait without action, the second element is how long to sleep/wait until the next step. Eg. [[2, 2.0], [3, 1.0]] is Menu button, 2 second wait and then X button and 1 second wait. |
| email_from | The email account username that email notifications are sent from. |
| email_to | The email account username that email notifications are sent to. |
| email_from_password | The email account password that email notifications are sent from. |
| email_SMTP_server | The email account SMTP server that notifications are sent from. |
| email_SMTP_server_port | The email account SMTP server port that notifications are sent from. |
