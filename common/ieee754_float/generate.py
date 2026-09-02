#!/usr/bin/env python3

from ast import literal_eval
from io import BytesIO
from pathlib import Path
from struct import Struct

import numpy as np

__license__ = "Unlicense"

sizes = (1, 2, 4, 8, 10, 12, 16, 32)
endians = {
	"le": "<",
	"be": ">"
}

S = Struct("<xxxxxxBB")

vs = {1: Struct("H"), 2: Struct("I")}


def genDTypes():
	for e, eM in endians.items():
		for s in sizes:
			fS = "f" + str(s)
			yield eM + fS, fS + e


def main():
	d = None
	for t, fn in genDTypes():
		f = Path(fn + ".ieee754")

		try:
			a = np.array([np.e], dtype=t)
		except BaseException as e:
			pass
		else:
			p = 0
			with BytesIO() as b:
				np.save(b, a, allow_pickle=False)
				d = b.getvalue()

			preHeader = d[: S.size]
			vMajor, vMinor = S.unpack(preHeader)
			p += S.size
			headerSizeStruct = vs[vMajor]
			headerSize = headerSizeStruct.unpack(d[p : p + headerSizeStruct.size])[0]
			p += headerSizeStruct.size + headerSize
			actualData = d[p:]

			f.write_bytes(actualData)


if __name__ == "__main__":
	main()
