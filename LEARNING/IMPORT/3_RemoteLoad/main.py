import logging
import sys

from core import install_meta

logger = logging.getLogger()
logger.setLevel("DEBUG")


install_meta('http://localhost:12800')

logger.info("Importing remoted module grok.base.foo")
import grok.base.foo
logger.info("Remoted module grok.base.foo imported")

logger.info(grok.base.foo.__name__)

logger.info("Done")
