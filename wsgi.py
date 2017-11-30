import sys
import os

from app import create_app
from werkzeug.contrib.fixers import ProxyFix


instance = create_app("testing")
app = ProxyFix(instance)
