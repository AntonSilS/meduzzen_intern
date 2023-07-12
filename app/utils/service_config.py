import os
from dotenv import load_dotenv


def get_var(const_name):
    load_dotenv()
    return os.getenv(const_name)
