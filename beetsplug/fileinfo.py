from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets.library import Library
from beets.library import Item
import mediafile
import subprocess
import json
# import optparse
# import argparse

# parser = optparse.OptionParser()
# parser.add_option("mode", dest="mode", help="Subcommand to run: write, ls or stats")

fileinfo_cmd = Subcommand(
    "fileinfo",
    # parser=parser,
    help="Read and write file info tags (bitdepth and sample rate)",
    aliases=("fi"))

fileinfo_write = Subcommand("writefileinfo", help="Write bit depth and sample rate as metadata to files.")
fileinfo_ls = Subcommand("fileinfo ls", help="Get bit depth and sample rate from metadata")
fileinfo_stats = Subcommand("getfileinfo", help="Get bit depth and sample rate from metadata")


def base(lib, opts, args):
    try:
        cmd = args[0]
    except BaseException:
        print("Unknown subcommand. Available commands are: write, ls, and stats")
        return
    if cmd == "write":
        write(lib, opts, args[1:])
        return
    if cmd == "ls":
        ls(lib, opts, args[1:])
        return
    if cmd == "stats":
        stats(lib, opts, args[1:])
        return
    print("Unknown subcommand. Available commands are: write, ls, and stats")


def ls(lib: Library, opts, args):
    items = lib.items(" ".join(args))
    item: Item
    for item in items:
        if not any(
            ext in item.destination().decode("utf-8") for ext in [
                "flac",
                "alac",
                "wav"]):  # this list is almost certainly incomplete
            continue
        try:
            bit_depth = item.bitdepth
            sample_rate = round(float(item["samplerate"]) / 1000, 1)
            print(f"{item} - {sample_rate}/{bit_depth}")
        except KeyError:
            print(f"Item {item} does not have file info tags. Try running fileinfo write first.")


def stats(lib: Library, opts, args):
    items = lib.items("".join(args))
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
        try:
            bit_depth = item.bitdepth
            sample_rate = round(float(item["samplerate"]) / 1000, 1)
            key = f"{sample_rate}kHz/{bit_depth} bit"
            try:
                info[key] += 1
            except KeyError:
                info[key] = 1
        except KeyError:
            print(f"Item {item} does not have file info tags. Try running writefileinfo first.")
    print(f"{non_lossless} items are not lossless ({(non_lossless / len(items)) * 100:.2f}%).")
    for key, count in sorted(info.items(), key=lambda item: item[1]):
        print(f"{count} items are {key} ({(count / len(items)) * 100:.2f}%)")


def write(lib: Library, opts, args):
    items = lib.items(" ".join(args))
    item: Item
    for item in items:
        path = item.destination().decode("utf-8")
        if not any(ext in path for ext in ["flac", "alac", "wav"]):  # this list is almost certainly incomplete
            continue
        ffprobe_result = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]))
        if not ("bit_depth" in ffprobe_result["format"]["tags"].keys()
                and "sample_rate" in ffprobe_result["format"]["tags"].keys()):
            flac_stream = ffprobe_result["streams"][0]
            bit_depth = flac_stream["bits_per_raw_sample"]
            sample_rate = flac_stream["sample_rate"]
            print(f"{item} - {sample_rate}/{bit_depth}")
            item["bit_depth"] = bit_depth
            item["sample_rate"] = sample_rate
            item.write()


fileinfo_cmd.func = base

fileinfo_write.func = write
fileinfo_ls.func = ls
fileinfo_stats.func = stats


class FileInfo(BeetsPlugin):
    def __init__(self, name=None):
        bit_depth = mediafile.MediaField(
            mediafile.StorageStyle("bit_depth")
        )
        sample_rate = mediafile.MediaField(
            mediafile.StorageStyle("sample_rate")
        )
        self.add_media_field("bit_depth", bit_depth)
        self.add_media_field("sample_rate", sample_rate)
        self.early_import_stages = []
        self.import_stages = []

    def commands(self):
        return [fileinfo_cmd, fileinfo_write, fileinfo_ls, fileinfo_stats]
