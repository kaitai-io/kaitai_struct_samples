<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## LongType.class

Has a `CONSTANT_Long_info` constant pool entry, so it can be used to test whether it is handled correctly - see https://github.com/kaitai-io/kaitai_struct_formats/issues/300 for more details.

Run `javap -v LongType.class` to get an overview of the correct indices for the constant pool entries.

Source: own work

Command to generate from `LongType.java`:

```sh
javac -encoding UTF-8 LongType.java
```
