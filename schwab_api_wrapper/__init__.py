import logging
from logging import NullHandler

__version__ = "6.0.1"

logging.getLogger(__name__).addHandler(NullHandler())
