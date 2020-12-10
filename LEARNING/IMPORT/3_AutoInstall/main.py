import logging
import sys

import core

logger = logging.getLogger()
logger.setLevel("DEBUG")


logger.info("Import module tornado")
try:
    import tornado
except:
    import tornado
logger.info("Install module tornado")

logger.info(tornado.__name__)
logger.info(tornado.__doc__)

logger.info("Done")
