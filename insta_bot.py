from time import sleep
import argparse
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging


# Remove: from credentials import USERNAME, PASSWORD

__author__ = 'Modified for Direct Post Commenting'
__version__ = '2.0.0'
__status__ = 'Dev'

# Setup logging
logging.basicConfig(
    format='%(levelname)s [%(asctime)s] %(message)s', 
    datefmt='%m/%d/%Y %r', 
    level=logging.INFO
)
logger = logging.getLogger()


class InstagramCommentBot:
    def __init__(self, headless=False, log_callback=None, profile_name="default", username=None, password=None):
        """Initialize the Instagram comment bot."""
        self.browser = None
        self.wait = None
        self.headless = headless
        self.log_callback = log_callback
        self.profile_name = profile_name
        self.username = username
        self.password = password
        self.waiting_for_manual_login = False
        
    def log(self, message, level=logging.INFO):
        """Log message and send to callback if available."""
        if level == logging.INFO:
            logger.info(message)
        elif level == logging.ERROR:
            logger.error(message)
        elif level == logging.WARNING:
            logger.warning(message)
            
        if self.log_callback:
            self.log_callback(message, level)

    def setup_browser(self):
        """Setup Chrome browser with appropriate options."""
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Add persistence via User Data Directory
        # Move all sessions into a dedicated subfolder to keep root clean
        base_session_dir = "Instagram_session"
        if not os.path.exists(base_session_dir):
            os.makedirs(base_session_dir)
            
        profile_path = os.path.abspath(os.path.join(base_session_dir, self.profile_name))
        options.add_argument(f"user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            # Important for headless reliability
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize chrome driver using Selenium Manager (built-in to Selenium 4.6+)
        # This will automatically handle downloading and setting up the correct driver
        self.browser = webdriver.Chrome(service=Service(), options=options)
        self.wait = WebDriverWait(self.browser, 10)
        
        self.log(f"Browser initialized for profile '{self.profile_name}' at: {profile_path}")
        
    def type_slowly(self, element, text):
        """Type text slowly like a human."""
        element.clear()
        for char in text:
            element.send_keys(char)
            sleep(0.1) # 100ms delay between keys
        
    def is_logged_in(self):
        """Check if user is already logged in to Instagram."""
        try:
            current_url = self.browser.current_url
            self.log(f"Current URL: {current_url}")
            
            # Wait a bit for page to load
            sleep(3)
            
            # Look for multiple indicators of being logged in
            # We check for common icons (Home, Messenger, New Post) or the search bar
            indicators = [
                "//svg[@aria-label='Home' or @aria-label='New post' or @aria-label='Direct message' or @aria-label='Explore' or @aria-label='Reels' or @aria-label='Messenger']",
                "//input[@placeholder='Search']",
                "//div[@role='navigation']",
                "//img[contains(@alt, \"profile picture\")]"
            ]
            
            for xpath in indicators:
                try:
                    self.browser.find_element(By.XPATH, xpath)
                    self.log(f"Detected logged-in state (found: {xpath})")
                    return True
                except NoSuchElementException:
                    continue
            
            # Check if we clearly see a login form
            try:
                self.browser.find_element(By.NAME, 'username')
                self.log("Clearly not logged in: login form detected")
                return False
            except NoSuchElementException:
                pass
            
            if 'accounts/login' in current_url:
                self.log("Clearly not logged in: on login URL")
                return False
            
            # If we don't see a login form but can't find clear "Home" icons, 
            # we might be on a landing page or partial load.
            self.log("Login status unclear (no navigation icons found yet)")
            return None # Return None for 'unclear'
            
        except Exception as e:
            self.log(f"Error checking login status: {e}", logging.ERROR)
            return False
    
    def login(self):
        """Login to Instagram - Automated with manual fallback."""
        try:
            self.log("Opening Instagram for login...")
            self.browser.get('https://www.instagram.com/accounts/login/')
            sleep(5)
            
            # Check if already logged in (maybe session was active)
            if self.is_logged_in() == True:
                self.log("Session active: Already logged in!")
                return True
            
            # 1. Try Automated Login
            self.log(f"Attempting automated login for user: {self.username}")
            try:
                # Handle possible Cookie Consent banner
                try:
                    cookie_btn = WebDriverWait(self.browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow all cookies') or contains(text(), 'Allow Essential and Optional')]"))
                    )
                    cookie_btn.click()
                    self.log("Dismissed cookie consent banner")
                    sleep(2)
                except:
                    pass

                # Find username field using multiple possible selectors
                user_selectors = ["username", "//*[@name='username']", "//*[@aria-label='Phone number, username, or email']"]
                user_field = None
                for selector in user_selectors:
                    try:
                        by = By.NAME if selector == "username" else By.XPATH
                        user_field = WebDriverWait(self.browser, 5).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        if user_field: break
                    except: continue

                if not user_field:
                    raise Exception("Could not find username field with any known selectors")

                # Find password field
                pass_field = self.browser.find_element(By.NAME, "password")
                
                # Human-like typing
                self.type_slowly(user_field, self.username)
                sleep(1)
                self.type_slowly(pass_field, self.password)
                sleep(1)
                
                # Submit
                submit_selectors = ["//button[@type='submit']", "//div[text()='Log in']", "//button[contains(., 'Log In')]"]
                for selector in submit_selectors:
                    try:
                        submit_btn = self.browser.find_element(By.XPATH, selector)
                        submit_btn.click()
                        break
                    except:
                        if selector == submit_selectors[-1]: # If last one failing, try Enter key
                            pass_field.send_keys(Keys.ENTER)
                
                self.log("Login form submitted. Waiting for load...")
                sleep(12) # Increased wait for potential redirects/popups
                
                # Check for "Save Login Info"
                try:
                    save_info_btn = WebDriverWait(self.browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Save info' or text()='Save Info']"))
                    )
                    save_info_btn.click()
                    self.log("Handled 'Save Login Info' prompt")
                    sleep(3)
                except:
                    pass
                
                # Check for "Turn on Notifications"
                try:
                    not_now_btn = WebDriverWait(self.browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now' or text()='Not now']"))
                    )
                    not_now_btn.click()
                    self.log("Handled 'Turn on Notifications' prompt")
                    sleep(3)
                except:
                    pass
                
                # Verify if login worked
                if self.is_logged_in() == True:
                    self.log("Automated login successful!")
                    return True
                else:
                    self.log("Automated login verification failed.", logging.WARNING)
                    
            except Exception as e:
                self.log(f"Automated login failed or fields not found: {e}", logging.WARNING)
            
            # 2. Manual Fallback
            self.log("=" * 60)
            self.log("MANUAL LOGIN REQUIRED (Automation failed)")
            self.log("=" * 60)
            self.log("1. Please login to Instagram in the browser window.")
            self.log("2. Complete any CAPTCHA or Two-Factor Authentication.")
            self.log("3. IMPORTANT: Wait until you see your Instagram Home Feed.")
            
            if self.log_callback:
                self.log("Waiting for manual login to complete (monitoring browser)...")
                # Loop and wait for login detection
                max_retries = 60 # 2 minutes
                for _ in range(max_retries):
                    if self.is_logged_in() == True:
                        self.log("Manual login detected! Proceeding...")
                        return True
                    sleep(2)
                self.log("Manual login timeout reached.", logging.ERROR)
                return False
            else:
                self.log("4. Then, press Enter HERE in the terminal to continue...")
                self.log("=" * 60)
                input()
                
                # Final verification
                sleep(2)
                if self.is_logged_in() == True:
                    self.log("Manual login verified. Proceeding...")
                    return True
                else:
                    self.log("Still not logged in! Exiting.", logging.ERROR)
                    return False
                
        except Exception as e:
            self.log(f"Execution error during login: {e}", logging.ERROR)
            return False

    def navigate_to_post(self, post_url):
        """Navigate to a specific Instagram post."""
        try:
            self.log(f"Navigating to post: {post_url}")
            self.browser.get(post_url)
            sleep(5)
            
            # Check for the "Login to see more" modal which often blocks post pages
            try:
                # Look for the close button on the login modal or the login button in the modal
                login_modal_close = self.browser.find_element(By.XPATH, "//div[@role='dialog']//svg[@aria-label='Close']")
                login_modal_close.click()
                self.log("Closed login modal on post page")
                sleep(1)
            except NoSuchElementException:
                pass

            # Verify we're on the post page and can see the comment section
            try:
                # Instagram sometimes hides the comment box behind a "Log In" button
                self.browser.find_element(By.XPATH, "//textarea[@placeholder='Add a comment…' or @placeholder='Add a comment...' or contains(@aria-label, 'Add a comment')]")
                self.log("Successfully navigated to post and found comment section")
                return True
            except NoSuchElementException:
                # Check if there's a "Log In" button where the comment box should be
                try:
                    self.browser.find_element(By.XPATH, "//a[text()='Log in' or text()='Log In']")
                    self.log("Post page loaded but still asking for login. Redirecting to homepage for login...", logging.WARNING)
                    return False
                except NoSuchElementException:
                    self.log("Post page loaded but comment section not found", logging.WARNING)
                    # Try scrolling down to trigger loading
                    self.browser.execute_script("window.scrollTo(0, 500);")
                    sleep(2)
                    return True # Continue anyway as post_comment has nested retries
        except Exception as e:
            self.log(f"Error navigating to post: {e}", logging.ERROR)
            return False
    
    def post_comment(self, comment_text, count=1):
        """Post a comment on the current Instagram post."""
        comments_posted = 0
        
        for i in range(count):
            try:
                self.log(f"Attempting to post comment {i+1}/{count}")
                
                # Find the comment textarea - try multiple selectors
                try:
                    comment_box = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Add a comment…' or @placeholder='Add a comment...' or contains(@aria-label, 'Add a comment')]"))
                    )
                except TimeoutException:
                    self.log("Standard comment box not found, trying fallback...", logging.WARNING)
                    # Fallback: try finding any textarea
                    comment_box = self.browser.find_element(By.TAG_NAME, "textarea")
                
                comment_box.click()
                sleep(1)
                
                # Re-find to avoid stale element
                comment_box = self.browser.find_element(By.XPATH, "//textarea[contains(@aria-label, 'Add a comment')]")
                # Type the comment human-like
                self.type_slowly(comment_box, comment_text)
                self.log(f"Comment {i+1} entered: {comment_text}")
                sleep(2)
                
                # Find and click the Post button - try multiple common XPaths
                post_button_selectors = [
                    "//div[text()='Post']",
                    "//button[contains(., 'Post')]",
                    "//div[@role='button' and text()='Post']",
                    "//button[@type='submit' and contains(., 'Post')]"
                ]
                
                post_clicked = False
                for selector in post_button_selectors:
                    try:
                        # Shorter wait for each attempt
                        button = WebDriverWait(self.browser, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        button.click()
                        self.log(f"Comment {i+1} posted via button")
                        post_clicked = True
                        comments_posted += 1
                        break
                    except:
                        continue
                
                if not post_clicked:
                    self.log("Could not find Post button, trying Enter key fallback...", logging.WARNING)
                    comment_box.send_keys(Keys.ENTER)
                    self.log(f"Comment {i+1} submitted via Enter key")
                    comments_posted += 1
                
                # Wait between comments to avoid rate limiting
                if i < count - 1:
                    wait_time = 10 + (i * 3) # More generous wait time for reliability
                    self.log(f"Waiting {wait_time} seconds before next comment...")
                    sleep(wait_time)
                
            except Exception as e:
                self.log(f"Error posting comment {i+1}: {e}", logging.ERROR)
                continue
        
        self.log(f"Successfully posted {comments_posted}/{count} comments")
        return comments_posted
    
    def run(self, post_url, comment_text, comment_count=1):
        """Main execution flow."""
        try:
            self.setup_browser()
            
            # First, go to Instagram homepage and login
            self.log("Opening Instagram homepage...")
            self.browser.get('https://www.instagram.com/')
            sleep(5)
            
            # Check if already logged in
            if not self.is_logged_in():
                # Login if not authenticated
                if not self.login():
                    self.log("Login failed. Exiting.", logging.ERROR)
                    return False
            else:
                self.log("Already logged in!")
            
            # Now navigate to the post - with retry logic if login is requested
            self.log(f"Navigating to post: {post_url}")
            if not self.navigate_to_post(post_url):
                self.log("Redirected due to login request. Retrying login flow...")
                if not self.login():
                    self.log("Login retry failed. Exiting.", logging.ERROR)
                    return False
                # Try navigating again after second login attempt
                if not self.navigate_to_post(post_url):
                    self.log("Still unable to reach post after login retry. Exiting.", logging.ERROR)
                    return False
            
            # Post comments
            posted = self.post_comment(comment_text, comment_count)
            
            if posted > 0:
                self.log(f"✓ Successfully posted {posted} comment(s)!")
                return True
            else:
                self.log("Failed to post any comments", logging.ERROR)
                return False
                
        except KeyboardInterrupt:
            self.log("\nBot stopped by user")
            return False
        except Exception as e:
            self.log(f"Error in main execution: {e}", logging.ERROR)
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.log("Closing browser in 10 seconds...")
            sleep(10)
            if self.browser:
                self.browser.quit()
            self.log("Browser closed")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Instagram Comment Bot - Post comments on specific Instagram posts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python insta-bot.py "https://www.instagram.com/p/ABC123/" "Great post!"
  python insta-bot.py "https://www.instagram.com/p/ABC123/" "Nice!" --count 3
  python insta-bot.py "https://www.instagram.com/p/ABC123/" "Amazing" --count 5 --headless
        """
    )
    
    parser.add_argument('post_url', help='Instagram post URL')
    parser.add_argument('comment', help='Comment text to post')
    parser.add_argument('--count', type=int, default=1, help='Number of times to post the comment (default: 1)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Validate post URL
    if 'instagram.com' not in args.post_url:
        logger.error("Invalid Instagram URL")
        sys.exit(1)
    
    # Validate comment count
    if args.count < 1:
        logger.error("Comment count must be at least 1")
        sys.exit(1)
    
    if args.count > 10:
        logger.warning("Posting more than 10 comments may trigger Instagram's spam detection!")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            logger.info("Aborted by user")
            sys.exit(0)
    
    # Run the bot
    bot = InstagramCommentBot(headless=args.headless)
    success = bot.run(args.post_url, args.comment, args.count)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
