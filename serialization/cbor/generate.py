#!/usr/bin/env python3

import datetime
import decimal
from pathlib import Path

import dateutil.tz

import cbor2

__license__ = "Unlicense"

etalon_dict = {
	"kaitai": ["is", "awesome"],
	"bin": b"bin",
	"int": 2,
	"float": 3.0,
	"NaN": float("nan"),
	"inf": float("inf"),
	"decimal": decimal.Decimal(100500),
	"null": None,
	"ts": datetime.datetime(1970, 1, 1, 0, 0, tzinfo=dateutil.tz.tzutc())
}


if __name__ == "__main__":
	f = Path("cbor.cbor")
	f.write_bytes(cbor2.dumps(etalon_dict))
