<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## apple-sha512-files-gzip.xar

SHA-512 checksums (for both TOC and file verification), using the Apple-specific
enum value to indicate the TOC checksum algorithm in the file header. Files use
*gzip* compression.

Source: https://github.com/jhermsmeier/node-xarchive/blob/93dffe2/test/data/test.xar

Shell commands to generate:

```sh
# Requires `7z` from <https://www.7-zip.org/> - install `p7zip-full` on Debian/Ubuntu
curl -LO https://github.com/jhermsmeier/node-xarchive/raw/93dffe2/test/data/test.xar
mv test.xar apple-sha512-files-gzip.xar
phys_size=$(7z l apple-sha512-files-gzip.xar | sed -En 's/^Physical Size = ([0-9]+)$/\1/p')
[ -n "$phys_size" ] \
  && [ "$phys_size" -ne "$(wc -c < apple-sha512-files-gzip.xar)" ] \
  && truncate -s "$phys_size" apple-sha512-files-gzip.xar
```

## custom-sha224-files-gzip.xar

SHA-224 checksums. SHA-224 is not a common checksum algorithm with an assigned
integer enum value, so its name ("`sha224`") must be written in the file header.
This is not very common and some implementations don't support it.

Contains a file `f1` with contents "`hellohellohello\n`" stored with *gzip* compression.

Source: own work

Shell commands to generate:

```sh
printf %s $'hellohellohello\n' > f1
chmod 0644 f1
env TZ=utc touch -afm -t 197001020000.01 f1
xar --toc-cksum sha224 -cf custom-sha224-files-gzip.xar f1
```

## md5-dir.xar

MD5 checksum of the TOC. Contains only an empty directory `dir1`.

Source: own work

Shell commands to generate (`xar` is from https://mackyle.github.io/xar/):

```sh
mkdir dir1
chmod 0755 dir1
env TZ=utc touch -afm -t 197001020000.01 dir1
xar --toc-cksum md5 -cf md5-dir.xar dir1
```

## nocksum-dir.xar

No checksum of the TOC. Contains only an empty directory `dir1`.

Source: own work

Shell commands to generate (`xar` is from https://mackyle.github.io/xar/):

```sh
mkdir dir1
chmod 0755 dir1
env TZ=utc touch -afm -t 197001020000.01 dir1
xar --toc-cksum none -cf nocksum-dir.xar dir1
```

## sha1-dir.xar

SHA-1 checksum of the TOC. Contains only an empty directory `dir1`.

Source: https://github.com/libarchive/libarchive/blob/1b2c437/libarchive/test/test_read_format_xar.c#L288-L331

## sha1-file-bzip2.xar

The TOC and files use SHA-1 checksums. Contains a file `f1` with contents
"`hellohellohello\n`" stored with *bzip2* compression.

The original `archive8.xar` contents from the byte array literal in the
*libarchive* source code are somehow messed up (the type of the file recorded
in the archive is `hardlink`, not a regular `file`), so the file was regenerated
using the commands specified in the code comment (skipping the `chown` invocation).

Source: https://github.com/libarchive/libarchive/blob/1b2c437/libarchive/test/test_read_format_xar.c#L441-L447

## sha1-file-nocomp.xar

The TOC and files use SHA-1 checksums. Contains a file `f1` with contents
"`hellohellohello\n`" stored with no compression.

The original `archive9.xar` contents from the byte array literal in the
*libarchive* source code are somehow messed up (the type of the file recorded
in the archive is `hardlink`, not a regular `file`), so the file was regenerated
using the commands specified in the code comment (skipping the `chown` invocation).

Source: https://github.com/libarchive/libarchive/blob/1b2c437/libarchive/test/test_read_format_xar.c#L487-L493

---

## macos_MobileDeviceDevelopment.pkg [not in the repo]

> **Note:** I don't know where this file originally comes from, so I have no idea
> what subject holds the copyright and under what license it is released. I guess
> it might be derived from proprietary software so we should ideally purge
> the file from any payloads that may be copyrighted.
>
> Also it could be made smaller in size (it has 83.3 KiB, this repo tries to keep
> files somewhat smaller than that), but that's a secondary issue.

This file appears to be interesting - it's a macOS `.pkg` installer of some
application (I don't know what one) but internally also a XAR archive.
It is signed with a RSA X.509 certificate which can be found inside, checksums
of extracted file contents are in `<unarchived-checksum>` property instead of
the standard `<extracted-checksum>` ([here's an explanation for that](
  https://github.com/apple-opensource/xar/blob/03d10ac/xar/lib/hash.c#L213-L215
)), some files use none and other *bzip2* compression.

Source: https://github.com/martinlindhe/formats/blob/5a59a6e/samples/archive/xar/macos_MobileDeviceDevelopment.pkg
