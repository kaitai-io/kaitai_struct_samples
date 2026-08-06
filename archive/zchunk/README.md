<!--
SPDX-FileCopyrightText: 2026 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## mini-dict.zck

A minimal zchunk file with a custom dictionary (see the [Zchunk
dictionaries](https://github.com/zchunk/zchunk/blob/99e51afa38c723e7c25834c2c3b305d20ef55d04/README.md#zchunk-dictionaries)
section in zchunk's README). It uses a "raw content" zstd dictionary (see
[Zstandard
docs](https://github.com/facebook/zstd/blob/b706286adbba780006a47ef92df0ad7a785666b6/doc/zstd_compression_format.md#dictionary-format)).
The dictionary is stored in chunk 0 of the `.zck` file, right before the data
chunks (chunks 1-3). It was also compressed using zstd, but since it was already
so small, zstd stored it as a single raw (uncompressed) block, so its contents
appear verbatim after the zstd magic, frame header and block header.

The file was generated using the following commands:

```console
$ printf 'chunk %s: the quick brown fox jumps over the lazy dog\n' 1 2 3 > mini-dict.txt
$ printf 'the quick brown fox jumps over the lazy dog\n' > mini-dict.zdict
$ zck --version
zchunk 1.5.2
Copyright (c) 2021 Jonathan Dieter
$ zck -D mini-dict.zdict -s 'chunk ' -o mini-dict.zck mini-dict.txt
```

The `-s` option makes `zck` start a new chunk at the beginning of each
occurrence of the given string. `'chunk '` occurs 3 times in the input, so the
zchunk file has 3 data chunks.

For reference, the output of the `zck_read_header` program is included in
[`mini-dict.zck.txt`](./mini-dict.zck.txt). It was generated as follows:

```console
$ zck_read_header --version
zchunk 1.5.2
Copyright (c) 2021 Jonathan Dieter
$ zck_read_header -c mini-dict.zck > mini-dict.zck.txt
```

> [!NOTE]
> The `zck` and `zck_read_header` utilities are part of zchunk's reference
> implementation, which is available in many package repositories, typically
> under the package name `zchunk` - see
> [Repology](https://repology.org/project/zchunk/versions).

Source: own work
