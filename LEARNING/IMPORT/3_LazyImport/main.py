import logging
import sys

import core

logger = logging.getLogger()
logger.setLevel("DEBUG")

logger.info("Importing module small")
import small
logger.info("Module small 'imported'")

logger.info(small.x)
logger.info(small.__name__)

logger.info("Done")
