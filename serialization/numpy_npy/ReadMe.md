<!--
SPDX-FileCopyrightText: 2021 KOLANICH
SPDX-License-Identifier: Unlicense
-->

## `numpy` `npy` files

These are the files that can be parsed with `numpy.load`. They also contain intentionally tampered files that are never emitted by `numpy.save` because of various reasons (i.e. `|` multibyte dtypes don't make much sense, since they are not portable across machines of various endiannesses), but that match the architecture of the format and so are parsed correctly. Also, files created by `numpy.save` are a bit longer, since their header contains unneeded whitespaces. I have trimmed them.

Source: Own work.

Generated with [`generate.py`](./generate.py)
