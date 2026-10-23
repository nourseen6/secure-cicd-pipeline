import os

# Secrets come from the environment, never from the code.
PAYMENT_API_KEY = os.environ.get("PAYMENT_API_KEY", "")
