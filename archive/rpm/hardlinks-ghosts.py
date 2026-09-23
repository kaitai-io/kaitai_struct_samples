# SPDX-FileCopyrightText: 2026 Petr Pucil <petr.pucil@seznam.cz>
#
# SPDX-License-Identifier: CC0-1.0

r"""Build hardlinks-ghosts-v4.rpm and hardlinks-ghosts-v6.rpm.

Both packages are built from the same spec, have an uncompressed payload and
contain the same file tree, which mixes hard links and %ghost files with
other kinds of files. Each file is described by what it looks like in the
payload (index in the header: path):

  0: /dir                     Directory: an entry without data.
  1: /dir/a-hardlink          Hard link set {1, 3}, but not its highest
                              index: an entry without data.
  2: /dir/b-empty             Empty regular file: an entry without data.
  3: /dir/c-hardlink          Hard link set {1, 3}, its highest index (also
                              the last one in the archive): the entry that
                              carries the data.
  4: /dir/d-regular           Regular file whose size isn't a multiple of 4,
                              so its data is followed by padding.
  5: /dir/e-ghost-hardlink    Ghost file with the same inode as {1, 3}: no
                              entry, and not part of the set, although its
                              index is higher than theirs.
  6: /dir/f-ghost             Ghost file with a non-zero size in the header:
                              no entry.
  7: /dir/g-symlink           Symlink: its data is the target path.
  8: /dir/h-symlink-hardlink  Hard link to the symlink 7: same inode in the
                              header, but only regular files form hard link
                              sets, so it carries its target too.

RPM sorts files by path, so the name prefixes `a-` to `h-` determine the
indexes. In the payload, it writes the files that aren't in a hard link set
first, then the members of each set, one right after another, so the archive
order is 0, 2, 4, 7, 8, 1, 3.

The v4 package's payload is a plain cpio archive (magic `070701`), whose
entries carry the file names and sizes. v6 packages always store file sizes
in the `RPMTAG_LONGFILESIZES` tag, and whenever that tag is present, RPM
writes a "stripped" cpio archive (magic `07070X`, except for the plain
`070701` trailer), whose entries contain only the index of the file in the
header. A parser of the v6 payload therefore has to derive the size of each
entry's data from the header, following the rules of RPM's archive reader
(`iterReadArchiveNext()` in `lib/rpmfi.cc`), and can't derive the index from
the entry's position. The v4 package shows what it should read.

RPM 6.0 or later must be installed.
"""

import argparse
import enum
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import typing
from pathlib import Path

PKG_NAME = "hardlinks-ghosts"
# The directory with all the files
TOP_DIR = "/dir"

# Only the tags `rpmbuild` requires. `BuildArch` isn't required, but without
# it the packages would get the architecture of the build host.
SPEC = f"""\
Name: {PKG_NAME}
Version: 1
Release: 1
Summary: Hard link and ghost file test package
License: CC0-1.0
BuildArch: noarch

%description
Hard link and ghost file test package.

%install
d=%{{buildroot}}{TOP_DIR}
mkdir -p "$d"
printf 'shared\\n' > "$d/a-hardlink"
: > "$d/b-empty"
ln "$d/a-hardlink" "$d/c-hardlink"
printf 'hello\\n' > "$d/d-regular"
ln "$d/a-hardlink" "$d/e-ghost-hardlink"
printf 'ghost\\n' > "$d/f-ghost"
ln -s d-regular "$d/g-symlink"
ln -P "$d/g-symlink" "$d/h-symlink-hardlink"

%files
%dir {TOP_DIR}
{TOP_DIR}/a-hardlink
{TOP_DIR}/b-empty
{TOP_DIR}/c-hardlink
{TOP_DIR}/d-regular
%ghost {TOP_DIR}/e-ghost-hardlink
%ghost {TOP_DIR}/f-ghost
{TOP_DIR}/g-symlink
{TOP_DIR}/h-symlink-hardlink
"""

# The file indexes the docstring describes
EXPECTED_PATHS = [TOP_DIR] + [
    f"{TOP_DIR}/{name}"
    for name in (
        "a-hardlink",
        "b-empty",
        "c-hardlink",
        "d-regular",
        "e-ghost-hardlink",
        "f-ghost",
        "g-symlink",
        "h-symlink-hardlink",
    )
]

# Indexes of files that must share an inode in the header - if they don't
# (e.g. because the build file system doesn't support hard links), the
# packages wouldn't test what they're meant to
INODE_GROUPS: list[set[int]] = [{1, 3, 5}, {7, 8}]

# Fix the build time and host, so that a rerun in the same environment
# reproduces the packages byte for byte, and clamp file mtimes to the build
# time, so that both packages have identical file trees
DEFINES: dict[str, str] = {
    "_binary_payload": "w.ufdio",  # Uncompressed
    "_buildtime": "1767225600",  # 2026-01-01T00:00:00Z
    "build_mtime_policy": "clamp_to_buildtime",
    # Some distributions (e.g. Fedora) enable it, but the spec has no
    # `%changelog` to take a date from, so `rpmbuild` would print a warning
    "source_date_epoch_from_changelog": "0",
    "_buildhost": "localhost",
    # Keep the build root exactly as %install created it (e.g. Fedora's
    # `add-determinism` would rewrite files)
    "__os_install_post": "%{nil}",
}


class Column(typing.NamedTuple):
    heading: str
    query: str  # `rpm --queryformat` of the value
    right_align: bool = False


# What a payload parser depends on (path, size, mode, flags for %ghost,
# device and inode for hard link sets), plus what's needed to check the
# extracted files. The 64-bit LONGFILESIZES query falls back to the 32-bit
# FILESIZES tag in v4.
FILE_TABLE_COLUMNS = [
    Column("path", "%{FILENAMES}"),
    Column("size", "%{LONGFILESIZES}", right_align=True),
    Column("mode", "%{FILEMODES:octal}", right_align=True),
    Column("flags", "%{FILEFLAGS}", right_align=True),
    Column("device", "%{FILEDEVICES}", right_align=True),
    Column("inode", "%{FILEINODES}", right_align=True),
    Column("mtime", "%{FILEMTIMES}", right_align=True),
    Column("user", "%{FILEUSERNAME}"),
    Column("group", "%{FILEGROUPNAME}"),
    Column("digest", "%{FILEDIGESTS}"),
    Column("link target", "%{FILELINKTOS}"),
]
FILE_TABLE_QUERY = "[" + "\t".join(c.query for c in FILE_TABLE_COLUMNS) + "\n]"
PATH_COL, DEVICE_COL, INODE_COL = (
    [c.heading for c in FILE_TABLE_COLUMNS].index(heading)
    for heading in ("path", "device", "inode")
)

LEAD_MAGIC = b"\xed\xab\xee\xdb"

# One row of field values per file, in header order
FileTable = list[list[str]]


class RpmFormat(enum.Enum):
    """Package format; the value is what the `_rpmformat` macro is set to."""

    V4 = 4
    V6 = 6

    def __str__(self) -> str:
        return f"v{self.value}"

    @property
    def lead_major(self) -> int:
        """`major` in the lead (the first 96 bytes of the package)."""
        return 4 if self is RpmFormat.V6 else 3

    @property
    def has_stripped_archive(self) -> bool:
        return self is RpmFormat.V6


class GenError(Exception):
    pass


def run(cmd: list[str]) -> str:
    """Run a command and return its stdout.

    Its stderr is passed through so that warnings (e.g. about a misspelled
    macro value) aren't lost.
    """
    try:
        return subprocess.check_output(cmd, encoding="utf-8")
    except FileNotFoundError:
        raise GenError(
            f"{cmd[0]} not found (RPM 6.0+ is required; some distributions "
            "package `rpmbuild` separately, e.g. Fedora as `rpm-build`)",
        ) from None
    except subprocess.CalledProcessError as e:
        raise GenError(
            f"{shlex.join(cmd)} failed with exit code {e.returncode}\n{e.stdout}",
        ) from None


def check_rpm_version() -> str:
    # Check `rpmbuild` rather than `rpm` - on Fedora, `rpm` is preinstalled,
    # but we mainly need `rpmbuild` from the `rpm-build` package, which must
    # be installed manually.
    version = run(["rpmbuild", "--version"]).strip()
    m = re.search(r"(\d+)\.", version)
    if not m or int(m.group(1)) < 6:
        raise GenError(
            f"RPM 6 or newer is needed to build v6 packages, found: {version}",
        )
    return version


def build(topdir: Path, fmt: RpmFormat) -> Path:
    spec = topdir / "SPECS" / f"{PKG_NAME}.spec"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(SPEC)
    cmd = [
        "rpmbuild",
        "-bb",
        "--quiet",
        # Don't check the (nonexistent) `BuildRequires` against the rpmdb, which
        # a non-root user may not be able to open.
        "--nodeps",
        "--define",
        f"_topdir {topdir}",
        "--define",
        f"_rpmformat {fmt.value}",
    ]
    for name, value in DEFINES.items():
        cmd += ["--define", f"{name} {value}"]
    cmd.append(str(spec))
    run(cmd)
    built = list((topdir / "RPMS" / "noarch").glob("*.rpm"))
    if len(built) != 1:
        raise GenError(f"expected one package from `rpmbuild`, found {built}")
    return built[0]


def check_payload(path: Path, fmt: RpmFormat) -> None:
    data = path.read_bytes()
    if data[:4] != LEAD_MAGIC or data[4] != fmt.lead_major:
        raise GenError(f"{path.name}: unexpected lead {data[:6].hex()}")
    # The payload is uncompressed, so the cpio magics are visible in the file.
    # Stripped archives end with a plain `070701` trailer too.
    kind = "stripped" if fmt.has_stripped_archive else "plain"
    if (
        (b"07070X" in data) != fmt.has_stripped_archive
        or b"070701" not in data
        or b"TRAILER!!!" not in data
    ):
        raise GenError(
            f"{path.name}: payload doesn't look like an "
            f"uncompressed {kind} cpio archive",
        )


def file_table(path: Path) -> FileTable:
    # The packages aren't signed, and without `--nosignature`, rpm would try
    # to load the keyring from the rpmdb, which a non-root user may not be
    # able to open.
    out = run(["rpm", "-qp", "--nosignature", "--qf", FILE_TABLE_QUERY, str(path)])
    table = [line.split("\t") for line in out.splitlines()]
    for row in table:
        if len(row) != len(FILE_TABLE_COLUMNS):
            raise GenError(f"{path.name}: unexpected file table row {row}")
    return table


def check_file_table(table: FileTable) -> None:
    paths = [row[PATH_COL] for row in table]
    if paths != EXPECTED_PATHS:
        raise GenError(f"unexpected files in the header: {paths}")
    for group in INODE_GROUPS:
        # Device and inode number, as RPM groups hard links by both
        ids = {(table[i][DEVICE_COL], table[i][INODE_COL]) for i in group}
        if len(ids) != 1:
            names = [paths[i] for i in sorted(group)]
            raise GenError(
                f"files {names} don't share an inode (got {ids}) "
                "- does the build file system support hard links?",
            )


def format_file_table(table: FileTable) -> str:
    """Format the file table as a Markdown table with aligned columns."""
    columns = [Column("index", "", right_align=True)] + FILE_TABLE_COLUMNS
    headings = [col.heading for col in columns]
    rows = [[str(i)] + row for i, row in enumerate(table)]
    widths = [
        max(len(cell) for cell in col) for col in zip(headings, *rows, strict=True)
    ]

    def line(cells: list[str]) -> str:
        return (
            "| "
            + " | ".join(
                cell.rjust(w) if col.right_align else cell.ljust(w)
                for cell, w, col in zip(cells, widths, columns, strict=True)
            )
            + " |"
        )

    delimiter = (
        "| "
        + " | ".join(
            "-" * (w - 1) + ":" if col.right_align else "-" * w
            for w, col in zip(widths, columns, strict=True)
        )
        + " |"
    )
    return "\n".join([line(headings), delimiter] + [line(r) for r in rows])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("outdir", nargs="?", default=".", type=Path)
    args = ap.parse_args()

    rpm_version = check_rpm_version()
    args.outdir.mkdir(parents=True, exist_ok=True)
    outputs: dict[RpmFormat, Path] = {}
    with tempfile.TemporaryDirectory(prefix=f"{PKG_NAME}-") as tmp:
        for fmt in RpmFormat:
            built = build(Path(tmp) / str(fmt), fmt)
            check_payload(built, fmt)
            outputs[fmt] = args.outdir / f"{PKG_NAME}-{fmt}.rpm"
            shutil.copyfile(built, outputs[fmt])

    tables = {fmt: file_table(path) for fmt, path in outputs.items()}
    v4_table, v6_table = tables[RpmFormat.V4], tables[RpmFormat.V6]
    if v4_table != v6_table:
        raise GenError(
            "the file trees of the v4 and v6 packages differ:\n"
            f"v4: {v4_table}\nv6: {v6_table}",
        )
    check_file_table(v6_table)

    print(f"built with {rpm_version}:")
    for path in outputs.values():
        print(f"  {path}")
    print("\nfiles (identical in both packages):\n")
    print(format_file_table(v6_table))


if __name__ == "__main__":
    try:
        main()
    except GenError as e:
        sys.exit(f"Error: {e}")
