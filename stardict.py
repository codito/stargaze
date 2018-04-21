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
import click

logger = logging.getLogger("stardict")


def parse_ifo(config):
    """Parse an ifo file.

    Args:
        config (Config): Configuration for stardict

    Returns:
        return None

    """
    return None


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
