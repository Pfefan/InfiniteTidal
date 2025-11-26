import random
import time

from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.items import ChromiumElement

from gmail_wrapper import GmailOAuthWrapper, get_gmail_service
from utils import DataGenerator, EnvManager


class TidalWrapper:
    def __init__(self):
        co = ChromiumOptions()
        #co.incognito(True)

        co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

        self.page = ChromiumPage(co)
        self.base_url = "https://tidal.com/"

        self.page.set.window.max()
        self.load_homepage()

    def setup_account(self):
        service = get_gmail_service()
        gmail = GmailOAuthWrapper(service)

        gmail_address = EnvManager().load_env("GMAIL_ADDRESS")
        email = gmail.get_alias_email(gmail_address)

        password = DataGenerator().generate_password()
        print(f"Generated Tidal account: {email} | {password}")

        # 3. Register on Tidal
        self.register(email, password)

        print("Waiting for verification email...")
        verify_link = gmail.wait_for_verification_email(email)

        if verify_link:
            print(f"Verification link received: {verify_link}")
            self.page.get(verify_link)
            time.sleep(5)
            print("Account verified successfully.")
        else:
            print("Failed to receive verification link.")

        self.page.get(self.base_url)

    def load_homepage(self):
        print("Loading Tidal homepage...")
        self.page.get(self.base_url)
        self.human_idle_behavior()
        print(f"Page loaded: {self.page.title}")

    def human_idle_behavior(self):
        """Simulates a user reading the page (scroll down, pause, scroll up)."""
        for _ in range(random.randint(2, 5)):
            scroll_y = random.randint(300, 700)
            self.page.scroll.to_location(0, scroll_y)
            time.sleep(random.uniform(0.8, 2.5))

        self.page.scroll.up(random.randint(100, 300))
        time.sleep(random.uniform(1.0, 2.0))

    def human_type(self, element: ChromiumElement, text: str):
        """Types text with random delays between keystrokes."""
        element.click()
        time.sleep(random.uniform(0.1, 0.3))

        for char in text:
            element.input(char)
            delay = random.uniform(0.05, 0.2)
            if char == ' ':
                delay += 0.1
            time.sleep(delay)

        time.sleep(random.uniform(0.5, 1.0))

    def human_click(self, element: ChromiumElement):
        """Moves mouse to element, hovers, pauses, then clicks."""
        element.hover()
        time.sleep(random.uniform(0.3, 0.7))
        element.click()
        time.sleep(random.uniform(0.5, 1.5))

    def human_select(self, element: ChromiumElement, text: str):
        """Simulates opening a dropdown and selecting an option."""
        element.click()
        time.sleep(random.uniform(0.3, 0.6))
        
        if element.tag == 'select':
            element.select(text)
        else:
            option = self.page.ele(f'text={text}')
            if option:
                option.click()
        
        time.sleep(random.uniform(0.5, 1.0))

    def register(self, email, password):
        try:
            login_btn = self.page.ele('@data-test=signup-button')
            if login_btn:
                self.human_click(login_btn)

            self.page.wait.load_start()

            # Enter email
            email_input = self.page.ele('#email')
            if email_input:
                self.human_type(email_input, email)

            continue_btn = self.page.ele('tag:button@@type=submit')
            if continue_btn:
                self.human_click(continue_btn)

            # Enter password
            password_input = self.page.ele('#new-password')
            if password_input:
                self.human_type(password_input, password)

            # Enter date of birth
            day, month, year = DataGenerator().generate_birth_date()
            tbi_day = self.page.ele('#tbi-day')
            if tbi_day:
                self.human_select(tbi_day, day)

            tbi_month = self.page.ele('#tbi-month')
            if tbi_month:
                self.human_select(tbi_month, month)

            tbi_year = self.page.ele('#tbi-year')
            if tbi_year:
                self.human_select(tbi_year, year)

            # Terms acceptance
            terms_checkbox = self.page.ele('@for=terms1')
            if terms_checkbox:
                self.human_click(terms_checkbox)

            submit_btn = self.page.ele('tag:button@@type=submit')
            if submit_btn:
                self.human_click(submit_btn)

                
        except Exception as e:
            print(f"Registration step failed: {e}")

    def close(self):
        self.page.quit()
