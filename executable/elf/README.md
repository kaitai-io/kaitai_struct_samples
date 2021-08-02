<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## hello_world.o

A minimal runnable Linux x86-64 relocatable object ELF file, generated from [this assembly code](https://cirosantilli.com/elf-hello-world#generate-the-example).

Source: https://cirosantilli.com/elf-hello-world#object-hd

## hello_world.out

A minimal runnable Linux x86-64 executable ELF file, generated from [this assembly code](https://cirosantilli.com/elf-hello-world#generate-the-example).

Source: https://cirosantilli.com/elf-hello-world#executable-hd

## elf-NetBSD-x86_64-echo

Has interesting symbols in `.symtab`  - most have visibility `DEFAULT` but some also have `HIDDEN`; symbol types and bindings are diverse as well.

Source: https://github.com/JonathanSalwan/binary-samples/blob/229c1bb/elf-NetBSD-x86_64-echo

## elf-Linux-ARMv7-ls

Source: https://github.com/JonathanSalwan/binary-samples/blob/229c1bb/elf-Linux-ARMv7-ls

## small.o

A x86 executable with 1 program header and 0 section headers.

Source: https://github.com/mathiasbynens/small/blob/2db083c/elf.o
