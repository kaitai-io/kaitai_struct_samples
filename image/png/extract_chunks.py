#!/usr/bin/env -S uv run --script

# SPDX-FileCopyrightText: 2026 Petr Pucil <petr.pucil@seznam.cz>
#
# SPDX-License-Identifier: MIT

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import argparse
import os
import re
import struct
import typing
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHUNK_TYPE_RE = re.compile(r"[A-Za-z]{4}")

PACKER_U4BE = struct.Struct(">I")


def validate_chunk_type(chunk_type: str) -> None:
    if PNG_CHUNK_TYPE_RE.fullmatch(chunk_type) is None:
        raise ValueError(
            f"expected an ASCII 4-letter chunk type, but got {chunk_type!r}"
        )


@dataclass
class ChunkBodySpan:
    type: str
    offset: int
    length: int


def get_chunk_body_spans(f: typing.BinaryIO) -> list[ChunkBodySpan]:
    chunk_spans = []

    if f.read(8) != PNG_SIGNATURE:
        raise ValueError("not a PNG image")

    while True:
        chunk_len_raw = f.read(4)
        if not chunk_len_raw:
            break
        len_body = PACKER_U4BE.unpack(chunk_len_raw)[0]
        chunk_type = f.read(4).decode("ascii")
        if len(chunk_type) != 4:
            raise ValueError("unexpected EOF in the middle of 4-byte chunk type")
        ofs_body = f.tell()
        f.seek(len_body + 4, os.SEEK_CUR)
        chunk_spans.append(ChunkBodySpan(chunk_type, ofs_body, len_body))
        if chunk_type == "IEND":
            break

    return chunk_spans


def copyfileobj_with_limit(
    src: typing.BinaryIO, dst: typing.BinaryIO, limit: int, *, buffer_size=256 * 1024
) -> int:
    """Like shutil.copyfileobj(), but with a limit on the number of bytes to copy."""

    remaining = limit
    while remaining > 0:
        buf = src.read(min(buffer_size, remaining))
        if not buf:
            break
        dst.write(buf)
        remaining -= len(buf)

    return remaining


def run_single(file_path: Path, chunk_type: str, outfile: Path) -> None:
    validate_chunk_type(chunk_type)

    with file_path.open("rb") as f:
        chunk_body_spans = get_chunk_body_spans(f)

        matching = [span for span in chunk_body_spans if span.type == chunk_type]

        if len(matching) == 0:
            raise ValueError(f"{file_path}: no chunk of type {chunk_type!r} found")
        if len(matching) > 1:
            raise ValueError(
                f"{file_path}: expected exactly one chunk of type {chunk_type!r},"
                f" but found {len(matching)}"
            )

        span = matching[0]
        f.seek(span.offset)
        with outfile.open("wb") as out_f:
            remaining = copyfileobj_with_limit(f, out_f, span.length)

    if remaining > 0:
        raise ValueError(
            f"{file_path}: chunk of type {chunk_type!r} is truncated"
            f" (wanted {span.length} bytes, but only {span.length - remaining} bytes written)"
        )


def run(files: list[Path], chunk_types: set[str], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for chunk_type in chunk_types:
        validate_chunk_type(chunk_type)
        (outdir / chunk_type).mkdir(exist_ok=True)

    for file_path in files:
        with file_path.open("rb") as f:
            chunk_body_spans = get_chunk_body_spans(f)
            for i, span in enumerate(chunk_body_spans):
                chunk_type = span.type
                if chunk_type not in chunk_types:
                    continue
                out_path = outdir / chunk_type / f"{file_path.name}-{i}.bin"
                with out_path.open("wb") as out_f:
                    f.seek(span.offset)
                    remaining = copyfileobj_with_limit(f, out_f, span.length)
                if remaining > 0:
                    print(
                        f"{file_path}: chunk {i} of type {chunk_type!r} is truncated"
                        f" (wanted {span.length} bytes, but only {span.length - remaining} bytes written)"
                    )
                    out_path.replace(
                        outdir / chunk_type / f"{file_path.name}-{i}.bin.trunc"
                    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract specific chunks from PNG files"
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="input PNG (.png) files to process",
        metavar="FILE",
    )
    parser.add_argument(
        "-t",
        "--chunk-type",
        required=True,
        dest="chunk_types",
        action="append",
        help="chunk type(s) to extract",
        metavar="TYPE",
    )
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "-d",
        "--outdir",
        dest="outdir",
        type=Path,
        help="output directory",
        metavar="DIR",
    )
    output_group.add_argument(
        "-o",
        "--outfile",
        dest="outfile",
        type=Path,
        help="output file; requires exactly one input FILE and one -t TYPE,"
        " and the input must contain exactly one chunk of that type",
        metavar="FILE",
    )
    args = parser.parse_args()

    if args.outfile is not None:
        if len(args.files) != 1:
            parser.error("-o/--outfile requires exactly one input file")
        if len(args.chunk_types) != 1:
            parser.error("-o/--outfile requires exactly one -t/--chunk-type")
        run_single(args.files[0], args.chunk_types[0], args.outfile)
    else:
        run(args.files, set(args.chunk_types), args.outdir)


if __name__ == "__main__":
    main()
