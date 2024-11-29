#!/usr/bin/env python3

import typing
from pathlib import Path
from pprint import pprint

import hyperscan as hs
from hyperscan import Database

__license__ = "Unlicense"
__copyright__ = "KOLANICH, 2021"

thisDir = Path(__file__).parent

# Regular expressions have been taken from https://github.com/KOLANICH-ML/HDDModelDecoder.py
rxs = {
	"HGST": b"([HW])([UDTECMS])([HSCEATNP])(\\d{2}|5C)(\\d{2})(\\d{2})([PDVKA])([L795S])(16|18|36|38|F2|F4|AT|SA|A3|A6|E6|N6|SS|42|52|S6)([0-486M0L])([0-5])",
	"Samsung": b"(HD|HE|HM|HN-M|HS|SP)(\\d{2,3})(HI|HJ|GJ|HX|IX|JX|JI|HA|GA|GB|GI|HB|THB|HC|II|IJ|JB|TJB|JJ|JQ|UJQ|LD|LI|LJ|MBB|RHF|RJF|SI|SJ|UI|UJ|VHF|VJF|WI|\\d[NSC])",
	"WD": b"(WD)(\\dN|\\d{3}M|\\d{2,})([ABCDEFGHJKLMNPSTX][94BDKLRSWYAFZ0123CEJGHMPUV])?([26ABCDEFGHJKLMRSVWPTYZ1U])([RABCDEFGKSTYVWXZ])"
}

modes = {"vectored": hs.HS_MODE_VECTORED, "block": hs.HS_MODE_BLOCK, "stream_large": hs.HS_MODE_STREAM | hs.HS_MODE_SOM_HORIZON_LARGE}


def prepareDatabase(rxs: typing.Dict[str, bytes], mode: int) -> (Database, typing.List[str]):
	flags = hs.HS_FLAG_SOM_LEFTMOST | hs.HS_FLAG_ALLOWEMPTY | hs.HS_FLAG_DOTALL | hs.HS_FLAG_MULTILINE
	xs = list(rxs.values())
	ks = list(rxs.keys())
	fgs = [flags] * len(ks)

	db = hs.Database(mode=mode)
	db.compile(expressions=xs, ids=list(range(len(ks))), flags=fgs)
	return db, ks


def testDb(db: Database, keys: typing.List[str], target: bytes) -> typing.Dict[str, str]:
	res = {}

	def matchesHandler(iD, start, stop, flags, ctx):
		s = slice(start, stop)
		model = target[s].decode("utf-8")
		vendor = keys[iD]
		res[model] = vendor

	db.scan(target, matchesHandler)
	return res


def main() -> None:
	db, keys = prepareDatabase(rxs, modes["block"])
	inputStr = b"dcsgdfw HDN724040ALE640 HDN724040ALE640 SP1614N fafafsfa WD2500AVJS vkjsbvhfjs"
	pprint(testDb(db, keys, inputStr))

	for n, m in modes.items():
		fn = thisDir / (n + ".hyperscan_simple")
		db, keys = prepareDatabase(rxs, m)
		data = hs.dumpb(db)
		print(n, "(", hex(len(data)), ")", ":", db.info().decode("utf8"))
		fn.write_bytes(data)


if __name__ == "__main__":
	main()
