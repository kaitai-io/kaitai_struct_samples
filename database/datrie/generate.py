#!/usr/bin/env python3

from pathlib import Path

import datrie

__license__ = "Unlicense"
__copyright__ = "KOLANICH, 2021"


thisDir = Path(__file__).parent()


def main():
	t = datrie.BaseTrie(ranges=(("a", "z"),))
	t["a"] = 1
	t["ab"] = 2
	t["ac"] = 3
	t["abd"] = 4
	t["abe"] = 5
	t["acf"] = 6
	t["acg"] = 7
	t.save(str(thisDir / "test.datrie"))


if __name__ == "__main__":
	main()
