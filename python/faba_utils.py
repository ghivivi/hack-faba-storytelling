"""Shared utilities for Faba scripts."""

import sys

try:
    from colorama import init, Fore, Style
    init(autoreset=True)

    class Colors:
        RED = Fore.RED
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        BOLD = Style.BRIGHT
        NC = Style.RESET_ALL

except ImportError:
    class Colors:
        RED = GREEN = YELLOW = BLUE = CYAN = BOLD = NC = ''


def print_colored(text, color):
    print(f"{color}{text}{Colors.NC}")
