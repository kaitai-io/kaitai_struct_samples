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

## mini-dict.zhr

A zchunk detached header file extracted from [mini-dict.zck](#mini-dictzck). It
is bit-for-bit identical to `mini-dict.zck`, except that it only contains the
header and the dictionary (chunk 0), not the data chunks (chunks 1-3; note that
chunk 1 starts on byte 202 - see the "Start" column in
[`mini-dict.zck.txt:14`](./mini-dict.zck.txt#L14), which is exactly the size of
`mini-dict.zhr`), and the magic number is `'\0ZHR1'` instead of `'\0ZCK1'`:

```console
$ cmp -l -b mini-dict.zck mini-dict.zhr
cmp: EOF on ‘mini-dict.zhr’ after byte 202
  3 103 C    110 H
  4 113 K    122 R
```

The file was generated as follows:

```console
$ unzck --version
zchunk 1.5.2
Copyright (c) 2021 Jonathan Dieter
$ unzck --header mini-dict.zck
mini-dict
```

> [!NOTE]
> The `unzck` utility is part of zchunk's reference implementation, which is
> available in many package repositories, typically under the package name
> `zchunk` - see [Repology](https://repology.org/project/zchunk/versions).

Source: own work

## mini-uncomp-cksums.zck

A minimal zchunk file with uncompressed checksums, which means that
["flag 2"](https://github.com/zchunk/zchunk/blob/99e51afa38c723e7c25834c2c3b305d20ef55d04/zchunk_format.txt#L86)
("File may be applied against an uncompressed source") is set in the header.
This adds a second checksum to each index entry: the checksum of the
uncompressed chunk. This allows a client updating the file to also reuse chunks
from a local uncompressed copy (an already extracted file), not just from an
older `.zck` file.

A side effect is that the total data checksum is all zeros (see
[`mini-uncomp-cksums.zck.txt:9`](./mini-uncomp-cksums.zck.txt#L9)), because when
flag 2 is set, it ["must not be checked and should not be
generated"](https://github.com/zchunk/zchunk/blob/99e51afa38c723e7c25834c2c3b305d20ef55d04/zchunk_format.txt#L41-L42).

The file was generated using the following commands:

```console
$ printf '%s\n' 'Hello,' 'world' > mini-uncomp-cksums.txt
$ zck --version
zchunk 1.5.2
Copyright (c) 2021 Jonathan Dieter
$ zck -u -s 'world' -o mini-uncomp-cksums.zck mini-uncomp-cksums.txt
```

The `-u` option makes `zck` add the uncompressed checksums. The `-s` option
starts a new chunk at the beginning of each occurrence of the given string.
`'world'` occurs once in the input, so the zchunk file has 2 data chunks (3
including the empty dictionary chunk).

For reference, the output of the `zck_read_header` program is included in
[`mini-uncomp-cksums.zck.txt`](./mini-uncomp-cksums.zck.txt). It was generated
as follows:

```console
$ zck_read_header --version
zchunk 1.5.2
Copyright (c) 2021 Jonathan Dieter
$ zck_read_header -c mini-uncomp-cksums.zck > mini-uncomp-cksums.zck.txt
```

> [!NOTE]
> The `zck` and `zck_read_header` utilities are part of zchunk's reference
> implementation, which is available in many package repositories, typically
> under the package name `zchunk` - see
> [Repology](https://repology.org/project/zchunk/versions).

Source: own work
