from typing import SupportsFloat, cast
from beets.dbcore.db import Results
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets.library import Library
from beets.library import Item

fileinfo_cmd = Subcommand(
    "fileinfo",
    # parser=parser,
    help="Read and write file info tags (bitdepth and sample rate). Subcommands are ls and stats",
    aliases=("fi"),
)


def base(lib, opts, args):
    try:
        cmd = args[0]
    except BaseException:
        print("Unknown subcommand. Available commands are: ls, and stats")
        return
    if cmd == "ls":
        ls(lib, opts, args[1:])
        return
    if cmd == "stats":
        stats(lib, opts, args[1:])
        return
    print("Unknown subcommand. Available commands are: ls, and stats")


def ls(lib: Library, opts, args):
    items: Results = lib.items(" ".join(args))
    item: Item
    for item in items:
        path = item.destination().decode("utf-8")
        ext = path[path.rfind(".") + 1 :].upper()
        is_lossless: bool = ext in [
            "FLAC",
            "ALAC",
            "WAV",
        ]
        #  item.
        # ; any(ext in path for ext in ["flac", "alac", "wav"])
        bit_depth = item.bitdepth
        sample_rate = round(float(cast(SupportsFloat, item.samplerate)) / 1000, 1)
        bit_rate_kbps = round(float(cast(SupportsFloat, item.bitrate)) / 1000, 1)
        print(f"{item} - {ext} - ", end="")
        if is_lossless:
            print(f"{sample_rate}/{bit_depth}")
        else:
            print(f"{bit_rate_kbps}kbps")


def stats(lib, opts, args):
    items: Results = lib.items(" ".join(args))
    info: dict[str, int] = {}
    non_lossless = 0
    item: Item
    for item in items:
        path = item.destination().decode("utf-8")
        ext = path[path.rfind(".") + 1 :].upper()
        is_lossless = ext in [
            "FLAC",
            "ALAC",
            "WAV",
        ]
        if not is_lossless:
            non_lossless += 1
            info[ext] = info.get(ext, 0) + 1
            continue
        bit_depth = item.bitdepth
        sample_rate = round(float(cast(SupportsFloat, item.samplerate)) / 1000, 1)
        key = f"{sample_rate}kHz/{bit_depth} bit"
        info[key] = info.get(key, 0) + 1

    if len(items) == 0:
        return
    print(
        f"{non_lossless} items are not lossless ({(non_lossless / len(items)) * 100:.2f}%)."
    )
    for key, count in sorted(info.items(), key=lambda item: item[0])[::-1]:
        print(f"{count} items are {key} ({(count / len(items)) * 100:.2f}%)")


fileinfo_cmd.func = base  # type: ignore


class FileInfo(BeetsPlugin):
    def __init__(self, name=None):
        self.early_import_stages = []
        self.import_stages = []

    def commands(self):
        return [fileinfo_cmd]
