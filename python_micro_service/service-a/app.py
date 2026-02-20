import logging
import time
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | service-a | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),      
        logging.FileHandler("/logs/service-a.log")    
    ]
)

logger = logging.getLogger("service-a")

def run():
    counter = 0
    while True:
        logger.info(f"Processing request number {counter}")
        counter += 1
        time.sleep(3)

if __name__ == "__main__":
    run()
