#!/usr/bin/env python
from app import *

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()