import sys
from importlib import abc
from importlib.machinery import ModuleSpec
import imp
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser

# Debugging
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get links from given url
def _get_links(url):
    class LinkParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                attrs = dict(attrs)
                links.add(attrs.get('href').rstrip('/'))
    links = set()
    try:
        logger.debug("Getting links from %s", url)
        u = urlopen(url)
        parser = LinkParser()
        parser.feed(u.read().decode('utf-8'))
    except Exception as e:
        logger.debug("Could not get links. %s", e)
    logger.debug("Links: %s", links)
    return links

# Module Finder for a URL
class UrlMetaFinder(abc.MetaPathFinder):
    def __init__(self, baseurl):
        self._baseurl = baseurl
        self._links = { }
        self._loaders = { baseurl: UrlModuleLoader(baseurl) }
    
    def find_module(self, fullname, path=None):
        logger.debug("Find module: fullname=%s, path=%s", fullname, path)
        if path is None:
            baseurl = self._baseurl
        else:
            if not path[0].startswith(self._baseurl):
                return None
            baseurl = path[0]
        parts = fullname.split('.')
        basename = parts[-1]
        logger.debug("Find module: baseurl=%s, basename=%s", baseurl, basename)

        # Check link cache
        if basename not in self._links:
            self._links[baseurl] = _get_links(baseurl)

        # Check if it's a package
        if basename in self._links[baseurl]:
            logger.debug("Find module: trying package %s", fullname)
            fullurl = baseurl + '/' + basename
            # Attempt to load the package (which accesses __init__.py)
            loader = UrlPackageLoader(fullurl)
            try:
                loader.load_module(fullname)
                self._links[fullurl] = _get_links(fullurl)
                self._loaders[fullurl] = UrlModuleLoader(fullurl)
                logger.debug("Find module: module %s loaded", fullname)
            except ImportError as e:
                logger.debug("Find module: package failed. %s", e)
                loader = None
            return loader
        # A normal module
        filename = basename + '.py'
        if filename in self._links[baseurl]:
            logger.debug("Find module: module %s found", fullname)
            return self._loaders[baseurl]
        else:
            logger.debug("Find module: module %s not found", fullname)
            return None
    
    def find_spec(self, fullname, path=None, target=None):
        loader = self.find_module(fullname, path)
        if loader is None:
            return None
        return ModuleSpec(fullname, loader, is_package=loader.is_package(fullname))

    def invalidate_caches(self):
        logger.debug("Invalidating link cache")
        self._links.clear()

# Module Loader for a URL
class UrlModuleLoader(abc.SourceLoader):
    def __init__(self, baseurl):
        self._baseurl = baseurl
        self._source_cache = { }
    
    def module_repr(self, module):
        return "<urlmodule %s from %s>" % (module.__name__, module.__file__)
    
    # def load_module(self, fullname):
    #     code = self.get_code(fullname)
    #     mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
    #     mod.__file__ = self.get_filename(fullname)
    #     mod.__loader__ = self
    #     mod.__package__ = fullname.rpartitiom('.')[0]
    #     exec(code, mod.__dict__)
    #     return mod

    def get_code(self, fullname):
        src = self.get_source(fullname)
        return compile(src, self.get_filename(fullname), 'exec')
    
    def get_data(self, path):
        pass

    def get_filename(self, fullname):
        return self._baseurl + '/' + fullname.split('.')[-1] + '.py'
    
    def get_source(self, fullname):
        filename = self.get_filename(fullname)
        logger.debug("Load module: reading %s", filename)
        if filename in self._source_cache:
            logger.debug("Load module: cached %s", filename)
            return self._source_cache[filename]
        try:
            u = urlopen(filename)
            source = u.read().decode('utf-8')
            logger.debug("Load module: %s loaded", filename)
            self._source_cache[filename] = source
            return source
        except ImportError as e:
            logger.debug("Load module: %s failed. %s", filename, e)
            raise ImportError("Can't load %s" % filename)

    def is_package(self, fullname):
        return False

class UrlPackageLoader(UrlModuleLoader):
    def load_module(self, fullname):
        mod = super().load_module(fullname)
        mod.__path__ = [ self._baseurl ]
        mod.__package__ = fullname
    
    def get_filename(self, fullname):
        return self._baseurl + '/' + '__init__.py'
    
    def is_package(self, fullname):
        return True

# Utility functions for installing/uninstalling the loader
_installed_meta_cache = { }

def install_meta(address):
    if address not in _installed_meta_cache:
        finder = UrlMetaFinder(address)
        _installed_meta_cache[address] = finder
        sys.meta_path.append(finder)
        logger.debug('%s installed on sys.meta_path', finder)

def remove_meta(address):
    if address in _installed_meta_cache:
        finder = _installed_meta_cache.pop(address)
        sys.meta_path.remove(finder)
        logger.debug('%s removed from sys.meta_path', finder)


if __name__ == '__main__':
    print("Advanced Url Import.")

