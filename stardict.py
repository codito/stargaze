#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""Stardict can parse and query stardict dictionary files.

 _______ _________ _______  _______  ______  _________ _______ _________
(  ____ \\__   __/(  ___  )(  ____ )(  __  \ \__   __/(  ____ \\__   __/
| (    \/   ) (   | (   ) || (    )|| (  \  )   ) (   | (    \/   ) (
| (_____    | |   | (___) || (____)|| |   ) |   | |   | |         | |
(_____  )   | |   |  ___  ||     __)| |   | |   | |   | |         | |
      ) |   | |   | (   ) || (\ (   | |   ) |   | |   | |         | |
/\____) |   | |   | )   ( || ) \ \__| (__/  )___) (___| (____/\   | |
\_______)   )_(   |/     \||/   \__/(______/ \_______/(_______/   )_(

"""
import logging
import os
from collections import namedtuple

import click

logger = logging.getLogger("stardict")

Configuration = namedtuple("Configuration", "ifo_path")
IFO = namedtuple("IFO", "version")


def parse_ifo(config):
    """Parse an ifo file.

    Specification of IFO file is available at:
    https://github.com/huzheng001/stardict-3/blob/master/dict/doc/StarDictFileFormat
    Note that we're not validating the contents strictly.

    Args:
        config (Config): Configuration for stardict

    Returns:
        return dictionary of entries in IFO file

    """
    if not os.path.exists(config.ifo_path):
        logger.info("IFO file doesn't exist at '{}'".format(config.ifo_path))
        return {}

    magic_header = "StarDict's dict ifo file"
    with open(config.ifo_path, "r", encoding="utf-8") as f:
        magic_string = f.readline().rstrip()
        if (magic_string != magic_header):
            logger.info("IFO: Incorrect header: {}".format(magic_string))
            return {}

        splits = (l.split("=") for l in map(str.rstrip, f) if l is not "")
        return {k.strip(): v.strip() for k, v in splits}

    # Validation
    # version: must be "2.4.2" or "3.0.0".
    # Since "3.0.0", StarDict accepts the "idxoffsetbits" option.

    # Available options:
    # bookname=      // required
    # wordcount=     // required
    # synwordcount=  // required if ".syn" file exists.
    # idxfilesize=   // required
    # idxoffsetbits= // New in 3.0.0
    # author=
    # email=
    # website=
    # description=	// You can use <br> for new line.
    # date=
    # sametypesequence= // very important.
    # dicttype=


@click.command()
@click.argument("dict_path", type=click.Path(exists=True))
@click.argument("word", type=str)
@click.option("--debug", is_flag=True, show_default=True,
              help="Show diagnostic messages.")
def start(dict_path, word, debug):
    """Stardict can parse and query stardict dictionary files."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.info("Verbose messages are enabled.")


if __name__ == '__main__':
    start()
