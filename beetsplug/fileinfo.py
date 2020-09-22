from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets.library import Library
from beets.library import Item
import mediafile
import subprocess
import json

fileinfo_cmd = Subcommand(
    "fileinfo",
    # parser=parser,
    help="Read and write file info tags (bitdepth and sample rate). Subcommands are ls and stats",
    aliases=("fi"))


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
    items = lib.items(" ".join(args))
    item: Item
    for item in items:
        path = item.destination().decode("utf-8")
        flac: bool = any(ext in path for ext in ["flac", "alac", "wav"])
        bit_depth = item.bitdepth
        sample_rate = round(float(item["samplerate"]) / 1000, 1)
        if flac:
            print(f"{item} - {'FLAC' if flac else path[path.rfind('.')+1:].upper()} - {sample_rate}/{bit_depth}")
        else:
            print(f"{item} - {path[path.rfind('.')+1:].upper()} - {item.bitrate//1000}kbps")


def stats(lib, opts, args):
    items = lib.items(" ".join(args))
    info: dict = {}
    non_lossless: int = 0
    item: Item
    for item in items:
        if not any(
            ext in item.destination().decode("utf-8") for ext in [
                "flac",
                "alac",
                "wav"]):  # this list is almost certainly incomplete
            non_lossless += 1
            continue
        bit_depth = item.bitdepth
        sample_rate = round(float(item["samplerate"]) / 1000, 1)
        key = f"{sample_rate}kHz/{bit_depth} bit"
        try:
            info[key] += 1
        except KeyError:
            info[key] = 1
    if len(items) == 0:
        return
    if non_lossless != 0:
        print(f"{non_lossless} items are not lossless ({(non_lossless / len(items)) * 100:.2f}%).")
    for key, count in sorted(info.items(), key=lambda item: item[1])[::-1]:
        print(f"{count} items are {key} ({(count / len(items)) * 100:.2f}%)")


fileinfo_cmd.func = base


class FileInfo(BeetsPlugin):
    def __init__(self, name=None):
        self.early_import_stages = []
        self.import_stages = []

    def commands(self):
        return [fileinfo_cmd]
