<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

# Kaitai Struct: sample library

[![REUSE compliance check](https://github.com/kaitai-io/kaitai_struct_samples/actions/workflows/reuse-lint.yml/badge.svg)](
  https://github.com/kaitai-io/kaitai_struct_samples/actions/workflows/reuse-lint.yml
)

A library of sample files for testing file format specifications from the [Kaitai Struct: format library](https://github.com/kaitai-io/kaitai_struct_formats).

## Contributing

Before adding a new file, it's necessary to find out who owns the copyright and under what license the file was released. If the file is hosted in a repository on GitHub and you know the hash of a commit in which the file was added, this shell command may help you with finding the author, who is usually also the copyright holder (needs [curl](https://curl.se) and [jq](https://stedolan.github.io/jq)):

<details>
  <summary>Shell command for extracting the commit author</summary>

  ```sh
  auth_token=[login]:[token] # get [token] from <https://github.com/settings/tokens> (public access)

  repo=ElyesH/coreboot
  commit_hash=e0af9fcb2d526ffd654d0bb573dd5333d0d76269
  curl \
    -s \
    -u "$auth_token" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$repo/commits/$commit_hash" \
  | jq '{html_url, message: .commit.message | .[0:index("\n\n")], author: .commit.author, spdx: {copyright: (.commit.author.name + " <" + .commit.author.email + ">"), year: (if .commit.author.date | index("-") == 4 then .commit.author.date | .[0:4] else null end)}}'
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

When you know the copyright owner, find the license of the file. Then follow the [REUSE tutorial](https://reuse.software/tutorial/) to find out how to add the information to the repository.

You can use the REUSE helper tool (hosted primarily [on Codeberg](https://codeberg.org/fsfe/reuse-tool), but a mirror is also available [on GitHub](https://github.com/fsfe/reuse-tool)), which helps ensure that this project is compliant with the [REUSE Specification](https://reuse.software/spec/). It is **strongly recommended to use [`uv`](https://github.com/astral-sh/uv)** to install and manage the REUSE tool. This repository contains [`pyproject.toml`](./pyproject.toml) and [`uv.lock`](./uv.lock), which lock the exact versions of [`reuse`](https://pypi.org/project/reuse/) and its dependencies. That means you only need to [install `uv`](https://docs.astral.sh/uv/getting-started/installation/) (which can optionally also be used to [install and manage Python](https://docs.astral.sh/uv/guides/install-python/)), and then always invoke the REUSE tool as `uv run reuse <command>`. This ensures that the version of the `reuse` tool is consistent across all developer machines and in the CI environment (GitHub Actions workflow [`reuse-lint.yml`](./.github/workflows/reuse-lint.yml)).

The most useful command is `reuse annotate`:

```sh
uv run reuse annotate -y 2026 -c 'Jane Doe <jane@example.com>' -l 'CC0-1.0' category/format/sample.bin
```

The usage of all commands is explained in the [documentation](https://reuse.readthedocs.io/en/stable/man/reuse.html#commands).

## Licensing

This repository uses [REUSE](https://reuse.software/) to track copyright and licensing information, so check the comment headers of individual files, or a file of the same name with the `.license` extension appended (in the case of binary, [uncommentable](https://reuse.software/faq/#uncommentable-file) or generated files).
