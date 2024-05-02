#!/usr/bin/env python3
                                                                                            #  R E G U M A T E  #


# Import necessary libraries
import os
import pyautogui
import time
import cv2
import numpy as np
import mysql.connector
from datetime import datetime
import subprocess

# Set environment variable for display
os.environ['DISPLAY'] = ':0'
# Set base_location to get current working directory and there would be no path difference
base_location = os.getcwd()

# Disclaimers
print("Requirements: Run the Libraries file)")
print("Requirements: Download and install Zoom application using this link https://zoom.us/download?os=linux)")
print("Requirements: Do audio and video settings on Zoom app according to audio_setting.png and video_setting.png)")
print("Requirements: Make sure )")
print('You can exit this program using (Ctrl+c) at any time')

# Database connection details
db_host = "localhost"
db_user = "reguuser"
db_password = "regupass"
db_database = "regumate"

# Function to write errors to log file
def log_error(error_message):
    with open("error_log.txt", "a") as file:
        file.write(f"{datetime.now()} - {error_message}\n")

# Function to fetch meeting credentials from the database
def get_meeting_credentials():
    try:
        con = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database,
            auth_plugin='mysql_native_password'
        )

        if con.is_connected():
            cursor = con.cursor(buffered=True)
            cursor.execute("SELECT meeting_id, passcode, meeting_time, total_meeting FROM meetings")
            results = cursor.fetchall()

            if results:
                return results
            else:
                print("No meeting credentials found.")
                return None
        else:
            print("Failed to establish MySQL connection.")
            return None
    except mysql.connector.Error as e:
        error_message = f"MySQL Error: {e}"
        print(error_message)
        log_error(error_message)
        return None
    
    finally:
        if 'con' in locals() and con.is_connected():
            cursor.close()
            con.close()

# Function to join Zoom meeting
def join_zoom_meeting(meet_id, password, meet_time, total_meet):
    try:
        time.sleep(0.2)
        pyautogui.press('esc', interval=0.1)
        time.sleep(0.3)
        pyautogui.press('win', interval=0.5)
        pyautogui.write('Zoom')
        time.sleep(2)
        pyautogui.press('enter', interval=0.5)
        time.sleep(10)
        pyautogui.hotkey('win', 'up')
        time.sleep(10)
        # importing, loading, and matching of the first image named joinIMG.png, which is the join button in the Zoom app
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template_join = cv2.imread(base_location+'/img/joinIMG.png')
        result_join = cv2.matchTemplate(screenshot_cv, template_join, cv2.TM_CCOEFF_NORMED)
        min_val_join, max_val_join, min_loc_join, max_loc_join = cv2.minMaxLoc(result_join)
        threshold_join = 0.8

        if max_val_join >= threshold_join:
            # know the center coordinates of the bounding box
            w_join, h_join = template_join.shape[:-1]
            center_x_join, center_y_join = max_loc_join[0] + w_join // 2, max_loc_join[1] + h_join // 2

            # Click at the center of the bounding box for "joinIMG"
            pyautogui.click(center_x_join, center_y_join)
            time.sleep(10)

            # importing, loading, and matching of the second image named meetidimage.png, which is the write meeting ID button in the Zoom app
            screenshot_after_join = pyautogui.screenshot()
            screenshot_after_join_cv = cv2.cvtColor(np.array(screenshot_after_join), cv2.COLOR_RGB2BGR)
            template_after_join = cv2.imread(base_location+'/img/meetidimage.png')
            result_after_join = cv2.matchTemplate(screenshot_after_join_cv, template_after_join, cv2.TM_CCOEFF_NORMED)
            min_val_after_join, max_val_after_join, min_loc_after_join, max_loc_after_join = cv2.minMaxLoc(result_after_join)
            threshold_after_join = 0.9

            if max_val_after_join >= threshold_after_join:
                # know the center coordinates of the bounding box
                w_after_join, h_after_join = template_after_join.shape[:-1]
                center_x_after_join, center_y_after_join = max_loc_after_join[0] + w_after_join // 2, max_loc_after_join[1] + h_after_join // 2

                # operations on the second image (writing meeting ID and writing password and pressing enter)
                pyautogui.moveTo(center_x_after_join, center_y_after_join)
                pyautogui.click(center_x_after_join, center_y_after_join)
                pyautogui.write(meet_id)
                pyautogui.press('enter', interval=10)
                pyautogui.write(password)
                pyautogui.press('enter', interval=10)
                time.sleep(25)
                pyautogui.hotkey('win', 'up')
        

                # Kill Zoom process
                time.sleep(total_meet * 60)
                subprocess.run(["pkill", "zoom"])

            else:
                error_message = "meetidimage image not found on the screen after joining."
                print(error_message)
                log_error(error_message)
        else:
            error_message = "Join image not found on the screen."
            print(error_message)
            log_error(error_message)
    except Exception as e:
        error_message = f"Error: {e}"
        print(error_message)
        log_error(error_message)

# Main function to check for new meeting entries and join Zoom meetings
def main():
    print("Starting Regumate Daemon Service...")
    while True:
        # Get current date and time
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # Fetch meeting credentials from the database
        credentials = get_meeting_credentials()

        if credentials:
            for credential in credentials:
                meet_id, password, meet_time, total_meet = credential
                if meet_time == current_time:
                    join_zoom_meeting(meet_id, password, meet_time, total_meet)
                    time.sleep(total_meet * 60)  # Wait for the meeting duration
        time.sleep(15)  # Check for new entries every 15 seconds

if __name__ == "__main__":
    main()
                    
                                                                                              #  R E G U M A T E  #
    
