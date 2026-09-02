#!/usr/bin/env python3

from pathlib import Path

import dateutil.tz

import msgpack

__license__ = "Unlicense"

etalon_dict = {
	"kaitai": ["is", "awesome"],
	"bin": b"bin",
	"int": 2,
	"float": 3.0,
	"NaN": float("nan"),
	"inf": float("inf"),
	"null": None
}


if __name__ == "__main__":
	f = Path("cbor.cbor")
	f.write_bytes(msgpack.dumps(etalon_dict))
