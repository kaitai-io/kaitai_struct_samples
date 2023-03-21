#!/usr/bin/env python3

from pathlib import Path

import numpy as np
import safetensors.numpy

import safetensors


__author__ = "KOLANICH"
__copyright__ = "Public domain"
__license__ = "Unlicense"

__reuse__ = """SPDX-FileCopyrightText: Uncopyrightable
SPDX-License-Identifier: Unlicense
"""

thisDir = Path(".").absolute()


ambigiousTypes = set("LPQlpq")  # these letters result into the same arrays


def makeTypeCodes():
	typeCodes = "".join(
		sorted(set("".join(np.typecodes[el] for el in ("Complex", "AllInteger", "AllFloat"))))
	)
	typeCodes = "".join(set(typeCodes) - ambigiousTypes)
	return typeCodes


def makeNumpyDict(typeCodes) -> dict:
	npDict = {}
	shapes = (
		(8,),
		(2, 4),
		(4, 2),
		(2, 2, 2),
	)
	for t in typeCodes:
		a = np.array(range(-3, 5), dtype="<" + t)
		try:
			testDic = {t + "x".join(str(el) for el in shape): a.reshape(shape) for shape in shapes}
			safetensors.numpy.save(testDic)  # testing if the type safetensors-serializeable
		except BaseException as ex:  # pylint:disable=broad-except
			print(t, a.dtype, ex)
		else:
			npDict.update(testDic)
	return npDict


EXT = ".safetensors"


def dumpFile(name: str, data: bytes):
	fn = name + EXT
	(thisDir / fn).write_bytes(data)
	(thisDir / (fn + ".license")).write_text(__reuse__)


def main():
	typeCodes = makeTypeCodes()
	npDict = makeNumpyDict(typeCodes)
	metaDict = {"test": "a"}
	dumpFile("overall", safetensors.numpy.save(npDict, metaDict))

	for k, v in npDict.items():
		dumpFile(k, safetensors.numpy.save({k: v}, metaDict))


if __name__ == "__main__":
	main()
