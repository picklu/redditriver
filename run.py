#!/usr/bin/env python2
from app import *

if __name__ == "__main__":
    app = application(urls, globals())
    app.run()
