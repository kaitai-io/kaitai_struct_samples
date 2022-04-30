<!--
SPDX-FileCopyrightText: 2022 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## pcma-marker.bin

Source: <https://gitlab.com/wireshark/wireshark/-/wikis/uploads/__moin_import__/attachments/SampleCaptures/rtp_example.raw> (from [SampleCaptures > General / Unsorted](https://gitlab.com/wireshark/wireshark/-/wikis/SampleCaptures?version_id=42fba81#general-unsorted))

Shell commands to generate:

```sh
curl -LO https://gitlab.com/wireshark/wireshark/-/wikis/uploads/__moin_import__/attachments/SampleCaptures/rtp_example.raw
tshark -r rtp_example.raw -Y "frame.number == 34" --disable-protocol rtp -T fields -e data | xxd -r -ps > pcma-marker.bin
```

Shell commands to generate the file `pcma-marker.txt`:

```sh
tshark -r rtp_example.raw -Y "frame.number == 34" -O rtp | sed -n '/Real-Time Transport Protocol/,$p'
```
