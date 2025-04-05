from typing import Final
from datetime import timedelta
import os

BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_NAME: Final[str] = os.path.join(BASE_DIR, "Data", "connection_graph.csv")

TIME_COST_PER_SEC: Final[int] = 1
CHANGE_COST_PER_CHANGE: Final[int] = 1

MIN_CHANGE_TIME: Final[timedelta] = timedelta(minutes=0)