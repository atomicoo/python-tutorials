import sys
import subprocess
from importlib import import_module

# Debugging
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AutoInstall(object):
    _loaded = set()

    @classmethod
    def find_module(cls, name, path=None, target=None):
        logger.debug("Find module: name=%s, path=%s", name, path)
        if path is None and name not in cls._loaded:
            cls._loaded.add(name)
            logger.debug("Find module: installing %s", name)
            try:
                out = subprocess.check_output([sys.executable, '-m', 'pip', 'install', name])
                logger.debug("Find module: out=%r", out.decode('utf-8'))
            except Exception as e:
                logger.debug("Find module: install failed. %s", e)
        return None

logger.debug("Meta path: add finder `AutoInstall`")
sys.meta_path.append(AutoInstall)
