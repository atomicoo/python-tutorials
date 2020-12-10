import logging
import sys

from importlib import import_module
from importlib.abc import Finder, Loader
from importlib.machinery import ModuleSpec


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

class LazyFinder(Finder):
    _lazy_modules = { }

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = cls._lazy_modules.get(fullname, None)
        if spec:
            logger.debug(f"Attribute in module '{fullname}' requested, actually importing")
            return None
        spec = ModuleSpec(fullname, LazyLoader())
        cls._lazy_modules[fullname] = spec
        return spec


class LazyLoader(Loader):
    def create_module(self, spec):
        return LazyModule(spec)

    def exec_module(self, module):
        return module


class LazyModule:
    def __init__(self, spec):
        self.spec = spec
        self.imported = False

    def _import(self):
        del sys.modules[self.spec.name]
        self.module = import_module(self.spec.name)
        sys.modules[self.spec.name] = self.module
        self.imported = True

    def __getattr__(self, attr):
        if attr in ["__name__", "__loader__", "__package__", "__path__"]:
            return None
        elif not self.imported:
            self._import()
        return self.module.__getattribute__(attr)

sys.meta_path = sys.meta_path[:-1] + [LazyFinder] + sys.meta_path[-1:]


if __name__ == '__main__':
    logger.info("Do Lazy Import")

    logger.info("Importing module small")
    import small
    logger.info("Module small 'imported'")
    logger.info(small.x)
    logger.info(small.__name__)
    logger.info("Done")