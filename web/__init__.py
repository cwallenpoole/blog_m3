#!/usr/bin/env python


"""web.py: makes web apps (http://webpy.org)"""
__version__ = "0.2"
__revision__ = "$Rev: 62 $"
__author__ = "Aaron Swartz <me@aaronsw.com>"
__license__ = "public domain"
__contributors__ = "see http://webpy.org/changes"

# todo:
#   - some sort of accounts system

from . import utils
from . import net
from . import form
from . import http
from . import webapi
from . import wsgi
from . import db 
from . import httpserver
from . import debugerror
from . import template

from .utils import *
from .db import *
from .net import *
from .wsgi import *
from .http import *
from .webapi import *
from .request import *
from .httpserver import *
from .debugerror import *

try:
    from . import cheetah
    from .cheetah import *
except ImportError:
    pass


def main():
    import doctest
    
    doctest.testmod(utils)
    doctest.testmod(db)
    doctest.testmod(net)
    doctest.testmod(wsgi)
    doctest.testmod(http)
    doctest.testmod(webapi)
    doctest.testmod(request)
    
    try:
        doctest.testmod(cheetah)
    except NameError:
        pass
    
    template.test()
    
    import sys
    urls = ('/web.py', 'source')
    class source:
        def GET(self):
            header('Content-Type', 'text/python')
            print(open(sys.argv[0]).read())
    
    if listget(sys.argv, 1) != 'test':
        run(urls, locals())

if __name__ == "__main__": main()
#"""