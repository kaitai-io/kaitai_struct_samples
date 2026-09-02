#!/usr/bin/env python3

from ast import literal_eval
from io import BytesIO
from pathlib import Path
from struct import Struct

import numpy as np

__author__ = "KOLANICH"
__copyright__ = "Public domain"
__license__ = "Unlicense"

letters = "uif"
sizes = (1, 2, 4, 8, 10, 12, 16, 32)
endians = "<>|"
lettersInsteadOfSizes = "HLQ"
lettersInsteadOfSizes += lettersInsteadOfSizes.lower()
lettersInsteadOfSizes += "efdg"

S = Struct("<xxxxxxBB")

vs = {1: Struct("H"), 2: Struct("I")}


def genDTypes():
	for e in endians:
		for l in letters:
			for s in sizes:
				yield e + l + str(s)
		for l in lettersInsteadOfSizes:
			yield e + l


def main():
	d = None
	for t in genDTypes():
		f = Path(t + ".npy")

		try:
			a = np.array(range(6), dtype=t)
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
			p += headerSizeStruct.size
			h = literal_eval(d[p : p + headerSize].decode("utf-8"))
			p += headerSize
			actualData = d[p:]
			h["descr"] = t
			hD = repr(h).strip().encode("utf-8")
			res = preHeader + headerSizeStruct.pack(len(hD)) + hD + actualData

			with BytesIO(res) as b:
				aControl = np.load(b)

			if not (a == aControl).all():
				raise Exception("Modified array contents is not equal to the original array contents")

			f.write_bytes(res)


if __name__ == "__main__":
	main()
