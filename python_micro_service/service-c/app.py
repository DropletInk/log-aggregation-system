import logging
import time
import random
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | service-c | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/logs/service-c.log")
    ]
)

logger = logging.getLogger("service-c")

def run():
    while True:
        x = random.randint(1, 5)

        try:
            if x == 3:
                raise Exception("Simulated failure")
            logger.info(f"Task completed successfully with value {x}")

        except Exception as e:
            logger.error(f"Error occurred: {e}")

        time.sleep(5)

if __name__ == "__main__":
    run()
