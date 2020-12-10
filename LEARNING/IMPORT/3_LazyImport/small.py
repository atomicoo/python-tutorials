import logging
import time

logger = logging.getLogger()
logger.setLevel("DEBUG")

logger.info("Sleeping!")
time.sleep(1)
logger.info("Done sleeping!")

x = "Hello from small!"
