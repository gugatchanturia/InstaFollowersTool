"""
Instagram Followers Analysis Tool
This script analyzes your Instagram followers and following to find users who don't follow you back.
It uses Instagram's mobile API for reliable data collection and your existing Chrome profile for authentication.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import requests
import re
import sys
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_driver_with_profile():
    """
    Sets up and returns a Chrome WebDriver instance using the existing Chrome profile.
    This allows the script to use your existing Instagram login session.
    
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    options = Options()
    # Use existing Chrome profile - CHANGE THIS PATH TO YOUR USERNAME
    options.add_argument("user-data-dir=C:\\Users\\Guga\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("profile-directory=Default")
    # Add necessary options to prevent crashes
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    return webdriver.Chrome(options=options)

def get_actual_counts(driver, username):
    """
    Gets the actual follower and following counts by counting users in the dialogs.
    
    Args:
        driver (WebDriver): Chrome WebDriver instance
        username (str): Instagram username
        
    Returns:
        tuple: (followers_count, following_count)
    """
    print("Getting actual counts from Instagram...")
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(1)  # Reduced from 3 to 1
    
    try:
        # Wait for the profile page to load
        wait = WebDriverWait(driver, 10)
        
        # Function to count users in a dialog
        def count_users_in_dialog(link_text):
            try:
                # Click the followers/following link
                link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, link_text)))
                link.click()
                time.sleep(1)  # Reduced from 2 to 1
                
                # Wait for the dialog to appear
                dialog = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']")))
                
                # Scroll to load all users
                last_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
                while True:
                    # Scroll down
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
                    time.sleep(0.5)  # Reduced from 1 to 0.5
                    
                    # Calculate new scroll height
                    new_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
                    
                    # Break if no more scrolling possible
                    if new_height == last_height:
                        break
                    last_height = new_height
                
                # Count unique users
                user_links = dialog.find_elements(By.CSS_SELECTOR, "a[role='link']")
                usernames = set()
                for link in user_links:
                    href = link.get_attribute("href")
                    if href and "/" in href:
                        username = href.split("/")[-2]
                        if username and username != username:  # Avoid counting the profile being viewed
                            usernames.add(username)
                
                # Close the dialog
                close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button']")))
                close_button.click()
                time.sleep(0.5)  # Reduced from 1 to 0.5
                
                return len(usernames)
            except Exception as e:
                print(f"Error counting {link_text}: {str(e)}")
                return 0
        
        # Count followers
        followers_count = count_users_in_dialog("followers")
        time.sleep(1)  # Reduced from 2 to 1
        
        # Count following
        following_count = count_users_in_dialog("following")
        
        print(f"Actual counts - Followers: {followers_count}, Following: {following_count}")
        return followers_count, following_count
        
    except Exception as e:
        print(f"Error getting actual counts: {str(e)}")
        return 0, 0

def get_page_count(driver, data_type):
    """
    Gets the actual count of followers or following from the page.
    
    Args:
        driver (WebDriver): Chrome WebDriver instance
        data_type (str): Either "followers" or "following"
        
    Returns:
        int: The actual count from the page
    """
    try:
        # Wait for the count to be visible
        wait = WebDriverWait(driver, 10)
        
        # Try different selectors to find the count
        selectors = [
            f"//a[contains(@href, '/{data_type}')]/span",
            f"//a[contains(@href, '/{data_type}')]/span/span",
            f"//a[contains(@href, '/{data_type}')]//span[contains(@class, '_ac2a')]"
        ]
        
        for selector in selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                text = element.get_attribute("title") or element.text
                if text:
                    # Remove commas and convert to integer
                    return int(text.replace(',', ''))
            except:
                continue
        
        # If we couldn't find it in visible elements, try page source
        page_source = driver.page_source
        if data_type == "followers":
            pattern = r'"edge_followed_by":{"count":(\d+)}'
        else:
            pattern = r'"edge_follow":{"count":(\d+)}'
            
        match = re.search(pattern, page_source)
        if match:
            return int(match.group(1))
            
        return 0
    except Exception as e:
        print(f"Error getting {data_type} count: {str(e)}")
        return 0

def get_instagram_data(driver, username, data_type):
    """
    Fetches followers or following data for a given Instagram username using the mobile API.
    
    Args:
        driver (WebDriver): Chrome WebDriver instance
        username (str): Instagram username to analyze
        data_type (str): Either "followers" or "following"
        
    Returns:
        list: List of usernames (followers or following)
    """
    print(f"\nGetting {data_type} for {username}...")
    
    # Navigate to the user's profile
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(0.5)  # Reduced from 1 to 0.5
    
    try:
        # Get the actual count from the page
        expected_count = get_page_count(driver, data_type)
        if expected_count == 0:
            print(f"Warning: Could not get {data_type} count from page")
        else:
            print(f"Expected {data_type} count: {expected_count}")
        
        # Get session data from Chrome
        cookies = driver.get_cookies()
        session = requests.Session()
        session_id = None
        
        # Extract session ID from cookies
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
            if cookie['name'] == 'sessionid':
                session_id = cookie['value']
        
        if not session_id:
            print("Error: Could not authenticate with Instagram")
            return []
        
        # Extract user ID from the page
        page_source = driver.page_source
        user_id_match = re.search(r'"user_id":"(\d+)"', page_source)
        if not user_id_match:
            print("Error: Could not find user ID")
            return []
        
        user_id = user_id_match.group(1)
        
        # Set up headers for Instagram's mobile API
        headers = {
            'User-Agent': 'Instagram 219.0.0.12.117 Android',
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'X-IG-Capabilities': '3brTvw==',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-App-ID': '567067343352427',
            'X-IG-WWW-Claim': '0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://www.instagram.com/{username}/',
            'Cookie': f'sessionid={session_id}'
        }
        
        # Fetch data using Instagram's mobile API
        usernames = set()
        max_id = None
        retry_count = 0
        max_retries = 2
        last_count = 0
        no_change_count = 0
        consecutive_empty_responses = 0
        total_attempts = 0
        
        while True:
            total_attempts += 1
            # Construct API URL based on data type
            if data_type == "followers":
                url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/"
            else:
                url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/"
            
            # Add pagination parameter if available
            if max_id:
                url += f"?max_id={max_id}"
            
            try:
                # Make API request
                response = session.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"Error: Failed to fetch data (Status code: {response.status_code})")
                    if retry_count < max_retries:
                        retry_count += 1
                        print(f"Retrying... (Attempt {retry_count}/{max_retries})")
                        time.sleep(0.5)  # Reduced from 1 to 0.5
                        continue
                    break
                
                # Reset retry count on successful request
                retry_count = 0
                
                # Parse response
                data = response.json()
                users = data.get('users', [])
                
                # Check if we got any users
                if not users:
                    consecutive_empty_responses += 1
                    if consecutive_empty_responses >= 2:
                        break
                    time.sleep(0.25)  # Reduced from 0.5 to 0.25
                    continue
                
                # Reset empty response counter
                consecutive_empty_responses = 0
                
                # Extract usernames
                new_usernames = set()
                for user in users:
                    username = user.get('username')
                    if username:
                        new_usernames.add(username)
                
                # Calculate actual new users (excluding already seen ones)
                actual_new_users = new_usernames - usernames
                actual_new_count = len(actual_new_users)
                
                # Add new usernames to our set
                usernames.update(new_usernames)
                
                current_count = len(usernames)
                if actual_new_count > 0:
                    print(f"Found {current_count} {data_type} (+{actual_new_count} new)")
                else:
                    print(f"Found {current_count} {data_type} (no new users)")
                
                # Check if we've reached the expected count
                if expected_count > 0 and current_count >= expected_count:
                    print(f"Reached expected count of {expected_count} {data_type}")
                    break
                
                # Check if we're stuck
                if current_count == last_count:
                    no_change_count += 1
                    if no_change_count >= 10:  # Increased from 2 to 10
                        print("\nWarning: No new users found in last 10 attempts")
                        if expected_count > 0 and current_count < expected_count:
                            print(f"Warning: Collected {current_count} users but expected {expected_count}")
                            print("This might be due to blocked or disabled accounts that are counted but not accessible.")
                            print("You can try running the script again, but the count might still be different.")
                            break
                        break
                else:
                    no_change_count = 0
                
                last_count = current_count
                
                # Check for more data
                next_max_id = data.get('next_max_id')
                if not next_max_id:
                    # Try one more time without max_id to ensure we got everything
                    if max_id:
                        print(f"Rechecking {data_type} list to ensure completeness...")
                        max_id = None
                        time.sleep(0.5)  # Reduced from 1 to 0.5
                        continue
                    break
                
                max_id = next_max_id
                time.sleep(0.25)  # Reduced from 0.5 to 0.25
        
            except Exception as e:
                print(f"Error: {str(e)}")
                if retry_count < max_retries:
                    retry_count += 1
                    print(f"Retrying... (Attempt {retry_count}/{max_retries})")
                    time.sleep(0.5)  # Reduced from 1 to 0.5
                    continue
                break
        
        return list(usernames)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def compare_followers_following(username):
    """
    Main function that compares followers and following for a given username.
    
    Args:
        username (str): Instagram username to analyze
    """
    clear_screen()
    print("\n=== Instagram Followers Analysis ===")
    driver = get_driver_with_profile()
    
    try:
        # Get followers
        followers = get_instagram_data(driver, username, "followers")
        print(f"Total followers: {len(followers)}")
        
        # Get following
        following = get_instagram_data(driver, username, "following")
        print(f"Total following: {len(following)}")
        
        # Find users who don't follow back
        not_following_back = set(following) - set(followers)
        print("\nUsers that don't follow you back:")
        for user in sorted(not_following_back):
            print(user)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        input("\nPress Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    try:
        username = input("Enter Instagram username: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            sys.exit(1)
        compare_followers_following(username)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
