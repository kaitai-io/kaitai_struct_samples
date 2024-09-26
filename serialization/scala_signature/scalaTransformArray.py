__license__ = "Apache-2.0 https://github.com/scala/scala/blob/2.13.x/LICENSE"
# https://github.com/scala/scala/blob/ba9701059216c629410f4f23a2175d20ad62484b/src/reflect/scala/reflect/internal/pickling/ByteCodecs.scala

__copyright__ = """
Scala (https://www.scala-lang.org)

Copyright EPFL and Lightbend, Inc.

Licensed under Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

See the NOTICE file distributed with this work for additional information regarding copyright ownership.
"""


def regenerateZero(src: bytearray) -> int:
	i = 0
	srclen = len(src)
	j = 0
	while i < srclen:
		inp: int = src[i] & 0xff
		if inp == 0xc0 and (src[i + 1] & 0xff) == 0x80:
			src[j] = 0x7f
			i += 2
		elif inp == 0:
			src[j] = 0x7f
			i += 1
		else:
			src[j] = inp - 1
			i += 1
		j += 1
	return j


def decode7to8(src: bytearray, srclen: int) -> int:
	i = 0
	j = 0
	dstlen = (srclen * 7 + 7) // 8
	while i + 7 < srclen:
		out: int = src[i]
		inp: Byte = src[i + 1]
		src[j] = out | (inp & 0x01) << 7
		out = inp >> 1
		inp = src[i + 2]
		src[j + 1] = out | (inp & 0x03) << 6
		out = inp >> 2
		inp = src[i + 3]
		src[j + 2] = out | (inp & 0x07) << 5
		out = inp >> 3
		inp = src[i + 4]
		src[j + 3] = out | (inp & 0x0f) << 4
		out = inp >> 4
		inp = src[i + 5]
		src[j + 4] = out | (inp & 0x1f) << 3
		out = inp >> 5
		inp = src[i + 6]
		src[j + 5] = out | (inp & 0x3f) << 2
		out = inp >> 6
		inp = src[i + 7]
		src[j + 6] = out | inp << 1
		i += 8
		j += 7

	if i < srclen:
		out: int = src[i]
		if i + 1 < srclen:
			inp: Byte = src[i + 1]
			src[j] = out | (inp & 0x01) << 7
			j += 1
			out = inp >> 1
			if i + 2 < srclen:
				inp = src[i + 2]
				src[j] = out | (inp & 0x03) << 6
				j += 1
				out = inp >> 2
				if i + 3 < srclen:
					inp = src[i + 3]
					src[j] = out | (inp & 0x07) << 5
					j += 1
					out = inp >> 3
					if i + 4 < srclen:
						inp = src[i + 4]
						src[j] = out | (inp & 0x0f) << 4
						j += 1
						out = inp >> 4
						if i + 5 < srclen:
							inp = src[i + 5]
							src[j] = out | (inp & 0x1f) << 3
							j += 1
							out = inp >> 5
							if i + 6 < srclen:
								inp = src[i + 6]
								src[j] = out | (inp & 0x3f) << 2
								j += 1
								out = inp >> 6

	if j < dstlen:
		src[j] = out

	return dstlen


def decode(xs: bytearray) -> int:
	len = regenerateZero(xs)
	return decode7to8(xs, len)
