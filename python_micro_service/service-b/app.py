import logging
import time
import random
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | service-b | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/logs/service-b.log")
    ]
)

logger = logging.getLogger("service-b")

def run():
    while True:
        value = random.randint(1, 10)

        if value > 7:
            logger.warning(f"High value detected: {value}")
        else:
            logger.info(f"Normal value: {value}")

        time.sleep(4)

if __name__ == "__main__":
    run()
