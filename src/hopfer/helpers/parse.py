import argparse
import os
import textwrap

import platformdirs

CONFIG_FOLDER = platformdirs.user_config_dir("hopfer")
LOG_PATH = os.path.join(CONFIG_FOLDER, "hopfer.log")


def parse_args(version):
    parser = argparse.ArgumentParser(
        prog="hopfer-qml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(f"""\
            A specialized toolkit providing experimental halftoning for print.
            Version: {version}

            Supported formats: .jpg, .png, .tiff, .webp, .jp2, .gif, .bmp
            Source code: https://github.com/crunchpaste/hopfer

            Usage: hopfer-qml [options] [file]
            """),
        usage=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="enable debug logging"
    )
    parser.add_argument(
        "-c", "--clean", action="store_true", help="reset to defaults"
    )
    parser.add_argument(
        "-l",
        "--logfile",
        nargs="?",
        const=LOG_PATH,
        default=None,
        metavar="PATH",
        help="write logs to a file",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {version}"
    )
    parser.add_argument("file", nargs="?", default=None, help=argparse.SUPPRESS)

    return parser.parse_args()
