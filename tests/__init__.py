import logging

logging.basicConfig(filename = 'test.log', level = logging.DEBUG)

from .rest import *
from .auth import *
from .reflection import *
from .ipernity import *
