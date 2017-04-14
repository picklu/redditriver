#!/usr/bin/env python
from app import *

if __name__ == "__main__":
    app = application(urls, globals())
    app.run()
