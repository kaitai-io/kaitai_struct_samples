<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

# Kaitai Struct: sample library

[![REUSE compliant](https://github.com/kaitai-io/kaitai_struct_samples/actions/workflows/reuse_lint.yml/badge.svg)](
  https://github.com/kaitai-io/kaitai_struct_samples/actions/workflows/reuse_lint.yml
)

A library of sample files for testing file format specifications from the [Kaitai Struct: format library](https://github.com/kaitai-io/kaitai_struct_formats).

## Contributing

Before adding a new file, it's necessary to find out who owns the copyright and under what license the file was released. If the file is on GitHub and you know the hash of a commit in which the file was added, this shell command may help you with the copyright (needs [curl](https://curl.se) and [jq](https://stedolan.github.io/jq)):

<details>
  <summary>Shell command for extracting the commit author</summary>

  ```shell
  auth_token=[login]:[token] # get [token] from <https://github.com/settings/tokens> (public access)

  repo=ElyesH/coreboot
  commit_hash=e0af9fcb2d526ffd654d0bb573dd5333d0d76269
  curl \
    -s \
    -u "$auth_token" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$repo/commits/$commit_hash" \
  | jq '{html_url, message: .commit.message | .[0:index("\n\n")], author: .commit.author, spdx: {copyright: (.commit.author.name + " <" + .commit.author.email + ">"), year: (if .commit.author.date | .[4:5] == "-" then .commit.author.date | .[0:4] else null end)}}'
  ```

</details>


<details>
<summary>Example command output</summary>

```json
{
  "html_url": "https://github.com/ElyesH/coreboot/commit/e0af9fcb2d526ffd654d0bb573dd5333d0d76269",
  "message": "tests: Add lib/edid-test test case",
  "author": {
    "name": "Jakub Czapiga",
    "email": "jacz@semihalf.com",
    "date": "2020-10-09T14:02:46Z"
  },
  "spdx": {
    "copyright": "Jakub Czapiga <jacz@semihalf.com>",
    "year": "2020"
  }
}
```
</details>

Now when you know the copyright owner, find the project license and then create the `[file_name.ext].license` text file (for example `sample.bin.license` for `sample.bin`) with this format:

```
SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>

SPDX-License-Identifier: [identifier]
```

`[identifier]` must be a SPDX license identifier from https://spdx.org/licenses/.

## Licensing

This repository uses [REUSE](https://reuse.software/) to keep track of copyright and licensing information, so check the comment headers of individual files, or a file with the same name with the `.license` extension added (for binary files).
