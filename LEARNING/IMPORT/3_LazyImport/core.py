import sys

from importlib import import_module
from importlib.abc import Finder, Loader
from importlib.machinery import ModuleSpec


# Debugging
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LazyFinder(Finder):
    _lazy_modules = { }

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = cls._lazy_modules.get(fullname, None)
        if spec and spec.import_please:
            logger.debug(f"Attribute in module '{fullname}' requested, actually importing")
            # Returning None means we skip this finder.
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
        self.spec.import_please = True
        del sys.modules[self.spec.name]
        self.module = import_module(self.spec.name)
        sys.modules[self.spec.name] = self.module
        # TODO After this, the LazyModule is still bound.
        # Since I set it here, the import machinery must do it after.
        self.imported = True

    def __getattr__(self, attr):
        if self.imported:
            pass
        # It'd be great to avoid it trying to import this in the first place.
        elif attr in ["__name__", "__loader__", "__package__", "__path__"]:
            return None
        elif not self.imported:
            self._import()
        return self.module.__getattribute__(attr)

sys.meta_path = sys.meta_path[:-1] + [LazyFinder] + sys.meta_path[-1:]
