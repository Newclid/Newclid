import sys
import importlib.util


def lazy_import(fullname):
    if fullname in sys.modules:
        return sys.modules[fullname]

    spec = importlib.util.find_spec(fullname)
    module = importlib.util.module_from_spec(spec)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    # Make module with proper locking and get it inserted into sys.modules.
    loader.exec_module(module)
    sys.modules[fullname] = module
    return module
