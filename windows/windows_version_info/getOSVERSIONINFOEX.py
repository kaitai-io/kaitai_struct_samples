import platform
import typing
from ctypes import byref, c_char, c_char_p, c_void_p, windll
from pathlib import Path
from struct import pack

from wine_get_version import wine_get_version  # https://github.com/KOLANICH-libs/wine_get_version.py

__author__ = "KOLANICH"
__license__ = "Unlicense"


GetVersionExA = windll.kernel32.GetVersionExA
GetVersionExA.argtypes = [c_void_p]

GetVersionExW = windll.kernel32.GetVersionExW
GetVersionExW.argtypes = [c_void_p]


def genPlatformString() -> str:
	platformVersion = platform.system() + "_" + platform.version()
	wineVersion = wine_get_version()
	if wineVersion:
		platformVersion += "_Wine_" + wineVersion
	return platformVersion


def getVersionInfoForSize(func, size: int) -> bytes:
	res = bytearray(size)
	res[:4] = pack("<I", len(res))

	func((c_char * len(res)).from_buffer(res))
	return bytes(res)


funcs = [
	(GetVersionExA, {"OSVERSIONINFOA": 148, "OSVERSIONINFOEXA": 156}),
	(GetVersionExW, {"OSVERSIONINFOW": 276, "OSVERSIONINFOEXW": 284}),
]


def getStructs():
	ress = {}
	for func, sizes in funcs:
		for name, size in sizes.items():
			res = getVersionInfoForSize(func, size)
			ress[name] = res
	return ress


def main():
	platformString = genPlatformString()
	print(platformString)

	cwd = Path(".")
	outD = cwd / platformString
	try:
		outD.mkdir(parents=True)
	except FileExistsError:
		pass

	structs = getStructs()
	for name, data in structs.items():
		outF = outD / (name + ".dat")
		with outF.open("wb") as f:
			f.write(data)


if __name__ == "__main__":
	main()
