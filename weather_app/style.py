from typing import Final


STRING_PADDING: Final[int] = 20

RED: Final[str] = "\033[1;31m"
BLUE: Final[str] = "\033[1;34m"
CYAN: Final[str] = "\033[1;36m"
GREEN: Final[str] = "\033[0;32m"
YELLOW: Final[str] = "\033[33m"
WHITE: Final[str] = "\033[37m"

REVERSE: Final[str] = "\033[;7m"
RESET: Final[str] = "\033[0m"


def change_color(color) -> None:
  print (color, end = "")
  