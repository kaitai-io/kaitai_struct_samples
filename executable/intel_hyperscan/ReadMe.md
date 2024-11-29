<!--
SPDX-FileCopyrightText: KOLANICH, 2021
SPDX-License-Identifier: Unlicense
-->

## Intel Hyperscan

Hyperscan is a library for fast matching regular expressions against binary buffers/streams in large scale.

It serializes precompiled regexps into own binary format. [1](https://github.com/intel/hs/blob/64a995bf445d86b74eb0f375624ffc85682eadfe/src/db.c#L62-L110) [2](https://github.com/intel/hs/blob/64a995bf445d86b74eb0f375624ffc85682eadfe/doc/dev-reference/serialization.rst).


In this dir I have created a demo app extracting HDD model names from text streams and detecting their vendors/brands.

The regexps have been taken from https://github.com/KOLANICH-ML/HDDModelDecoder.py .

The app first generates a "DB", then matches it against the buffer and displays the results for self-check, then generates the serialized representations of "DB"s and stores them into files.

In this dir only "simple" format is present. [Chimera format](https://github.com/intel/hs/blob/64a995bf445d86b74eb0f375624ffc85682eadfe/chimera/ch_db.h) goes to another dir.

```
Version: 5.4.0 Features: AVX2
vectored: Mode: VECTORED
block: Mode: BLOCK
stream_large: Mode: STREAM
```

Source: own work.
