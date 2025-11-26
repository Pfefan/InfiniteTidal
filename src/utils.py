import os
import random
from datetime import datetime

from dotenv import load_dotenv


class DataGenerator:
    def __init__(self):
        pass

    def generate_birth_date(self):
        """Generates a random birth date for someone older than 20 years."""
        current_year = datetime.now().year
        birth_year = random.randint(current_year - 50, current_year - 20)
        birth_month = random.randint(1, 12)

        if birth_month == 2:
            birth_day = random.randint(1, 28)
        elif birth_month in [4, 6, 9, 11]:
            birth_day = random.randint(1, 30)
        else:
            birth_day = random.randint(1, 31)

        month_name = datetime(2000, birth_month, 1).strftime('%B')

        return str(birth_day), month_name, str(birth_year)

    def generate_password(self, length=16):
        """Generates a random password of specified length."""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        return ''.join(random.choice(chars) for _ in range(length))

class EnvManager:
    def __init__(self):
        load_dotenv()

    @staticmethod
    def load_env(key: str):
        return os.environ.get(key)
