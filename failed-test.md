app\tests\test_activation_comprehensive.py (trapped) error reading bcrypt version 
┌───────────────────── Traceback (most recent call last) ─────────────────────┐   
│ C:\Users\mksan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_ │   
│ qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\passlib\han │   
│ dlers\bcrypt.py:620 in _load_backend_mixin                                  │   
│                                                                             │   
│    617 │   │   except ImportError: # pragma: no cover                       │   
│    618 │   │   │   return False                                             │   
│    619 │   │   try:                                                         │   
│ >  620 │   │   │   version = _bcrypt.__about__.__version__                  │   
│    621 │   │   except:                                                      │   
│    622 │   │   │   log.warning("(trapped) error reading bcrypt version", ex │   
│    623 │   │   │   version = '<unknown>'                                    │   
│                                                                             │   
│ ┌───── locals ──────┐                                                       │   
│ │ dryrun = False    │                                                       │   
│ │   name = 'bcrypt' │                                                       │   
│ └───────────────────┘                                                       │   
└─────────────────────────────────────────────────────────────────────────────┘   
AttributeError: module 'bcrypt' has no attribute '__about__'

