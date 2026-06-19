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
import typing
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHUNK_TYPE_RE = re.compile(r"[A-Za-z]{4}")


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
        if len(chunk_len_raw) != 4:
            raise ValueError("unexpected EOF while reading the chunk length")
        len_body = int.from_bytes(chunk_len_raw, "big")
        chunk_type_raw = f.read(4)
        if len(chunk_type_raw) != 4:
            raise ValueError("unexpected EOF while reading the chunk type")
        try:
            chunk_type = chunk_type_raw.decode("ascii")
        except UnicodeDecodeError as e:
            raise ValueError(f"invalid non-ASCII chunk type {chunk_type_raw!r}") from e
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


def open_no_clobber(path: Path) -> typing.BinaryIO:
    """Open `path` for exclusive binary writing, refusing to overwrite.

    Output names in `-d` mode are derived from the input's base name, so inputs
    that share a base name would otherwise clobber each other. The collision can
    even span separate invocations (e.g. when `xargs` splits the file list into
    batches), so we detect it at the actual write rather than up front.
    """
    try:
        return path.open("xb")
    except FileExistsError as e:
        raise ValueError(
            f"refusing to overwrite existing output file {path};"
            f" clean the output directory and re-run"
        ) from e


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
            if not chunk_body_spans:
                continue

            # We want all chunk indices from one input file zero-padded to the
            # same width so that the output file names sort naturally (e.g.
            # `-09.bin` before `-10.bin`), so we need to determine the maximum
            # chunk index width.
            index_width = len(str(len(chunk_body_spans) - 1))

            for i, span in enumerate(chunk_body_spans):
                chunk_type = span.type
                if chunk_type not in chunk_types:
                    continue
                name = f"{file_path.name}-{i:0{index_width}d}.bin"
                out_path = outdir / chunk_type / name
                with open_no_clobber(out_path) as out_f:
                    f.seek(span.offset)
                    remaining = copyfileobj_with_limit(f, out_f, span.length)
                if remaining > 0:
                    print(
                        f"{file_path}: chunk {i} of type {chunk_type!r} is truncated"
                        f" (wanted {span.length} bytes, but only {span.length - remaining} bytes written)"
                    )
                    trunc_path = out_path.with_name(name + ".trunc")
                    if trunc_path.exists():
                        raise ValueError(
                            f"refusing to overwrite existing output file {trunc_path};"
                            f" clean the output directory and re-run"
                        )
                    out_path.rename(trunc_path)


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
