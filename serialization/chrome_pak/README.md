<!--
SPDX-FileCopyrightText: 2021 Petr Pucil <petr.pucil@seznam.cz>

SPDX-License-Identifier: CC0-1.0
-->

## v4.pak

Sample .pak file version 4, directly from a unit test of the `data_pack.py` script in the GRIT repository. Contains four text resources in UTF-8 encoding. Version 4 does not support aliases, so there are none.

Source: https://chromium.googlesource.com/chromium/src/tools/grit/+/8a23eae/grit/format/data_pack_unittest.py#21

## v5.pak

Sample .pak file version 5, directly from a unit test of the `data_pack.py` script in the GRIT repository. Contains three text resources in UTF-8 encoding and one alias with ID 10 referencing the resource with index 1, which has ID 4.

Source: https://chromium.googlesource.com/chromium/src/tools/grit/+/8a23eae/grit/format/data_pack_unittest.py#42

## v5-utf16.pak

File version 5, uses the UTF-16 encoding for text strings. Two resources, no aliases.

Source: own work

Shell commands to generate:

```sh
git clone https://chromium.googlesource.com/chromium/src/tools/grit
cd grit
git checkout 8a23eae
{
cat <<'EOF'
diff --git i/grit/format/data_pack.py w/grit/format/data_pack.py
index 37f29d4..631a7a6 100755
--- i/grit/format/data_pack.py
+++ w/grit/format/data_pack.py
@@ -322,3 +322,5 @@ def main():
   data2 = {1000: 'test', 5: 'five'}
-  WriteDataPack(data2, 'datapack2.pak', UTF8)
+  for k in data2:
+    data2[k] = data2[k].encode('utf-16')
+  WriteDataPack(data2, 'datapack2.pak', UTF16)
   print('wrote datapack1 and datapack2 to current directory.')
EOF
} | git apply -
cd ../
./grit/grit/format/data_pack.py
# wrote datapack1 and datapack2 to current directory.
mv datapack2.pak v5-utf16.pak
```
