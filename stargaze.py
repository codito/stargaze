#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""Stargaze can parse and query stardict dictionary files.

 ######  ########    ###    ########   ######      ###    ######## ########
##    ##    ##      ## ##   ##     ## ##    ##    ## ##        ##  ##
##          ##     ##   ##  ##     ## ##         ##   ##      ##   ##
 ######     ##    ##     ## ########  ##   #### ##     ##    ##    ######
      ##    ##    ######### ##   ##   ##    ##  #########   ##     ##
##    ##    ##    ##     ## ##    ##  ##    ##  ##     ##  ##      ##
 ######     ##    ##     ## ##     ##  ######   ##     ## ######## ########

"""
import logging
import os
from collections import namedtuple
from struct import unpack

import click
import idzip

logger = logging.getLogger("stargaze")

Configuration = namedtuple("Configuration", "ifo_path idx_path syn_path"
                           " dict_path")
IFO = namedtuple("IFO", "version")


class DictionaryError(Exception):
    """Raised when dictionary is in invalid state."""

    pass


class Dictionary(object):
    """A stardict dictionary."""

    def __init__(self, dict_path):
        """Create an instance of a stardict dictionary.

        Args:
            dict_path (str): directory containing dictionary files
        """
        if not os.path.exists(dict_path):
            raise ValueError(dict_path)

        self.configs = self._create_config(dict_path)
        self.words = {}
        self.word_offsets = []

        if self.configs == []:
            msg = "No configuration files found in path {}."
            "Does it contain a .ifo file?".format(dict_path)
            raise DictionaryError(msg)

    def lookup(self, word):
        """Look up a word in the dictionary.

        Args:
            word (str): word to look up.

        Returns:
            Definition of the word if available. None otherwise.

        """
        # TODO add support to search through all dictionaries
        c = self.configs[0]

        ifo = parse_ifo(c)
        if self.words == {}:
            word_idx, word_list = parse_idx(c)
            self.words.update({x: [word_idx[x]] for x in word_idx})
            self.words.update(parse_syn(c))
            self.word_offsets.extend(word_list)
        if word in self.words:
            index = self.words[word][0]
            dic = parse_dict(c, ifo, word,
                             self.word_offsets[index][0],
                             self.word_offsets[index][1])
            return dic

    def _create_config(self, dict_path):
        """Create a configuration for given dictionary path.

        Args:
            dict_path (str): path to dictionary

        Returns:
            a configuration object

        """
        configs = []
        for dirpath, dirs, files in os.walk(dict_path):
            # find the .ifo files
            ifo_files = [f for f in files if os.path.splitext(f)[1] == ".ifo"]
            for ifo in ifo_files:
                fname = os.path.splitext(ifo)[0]
                ifo_path = os.path.join(dirpath, fname + ".ifo")
                idx_path = os.path.join(dirpath, fname + ".idx")
                dict_path = os.path.join(dirpath, fname + ".dict")
                syn_path = os.path.join(dirpath, fname + ".syn")
                if not os.path.exists(idx_path):
                    continue
                if not os.path.exists(dict_path):
                    dict_path = os.path.join(dirpath, fname + ".dict.dz")
                    if not os.path.exists(dict_path):
                        continue
                if not os.path.exists(syn_path):
                    syn_path = None

                c = Configuration(ifo_path, idx_path, syn_path, dict_path)
                configs.insert(0, c)

        return configs


def parse_ifo(config):
    """Parse an ifo file.

    Specification of IFO file is available at:
    https://github.com/huzheng001/stardict-3/blob/master/dict/doc/StarDictFileFormat
    Note that we're not validating the contents strictly.

    Args:
        config (Configuration): Configuration for stardict

    Returns:
        return dictionary of entries in IFO file

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

        options = (l.split("=") for l in map(str.rstrip, f) if l is not "")
        return {k.strip(): v.strip() for k, v in options}


def parse_idx(config):
    r"""Parse an IDX file.

    Args:
        config (Configuration): a configuration object

    Returns:
        an iterable list of words.

    The word list is a sorted list of word entries.

    Each entry in the word list contains three fields, one after the other:
         word_str;  // a utf-8 string terminated by '\0'.
         word_data_offset;  // word data's offset in .dict file
         word_data_size;  // word data's total size in .dict file

    """
    word_idx = {}
    word_list = []
    if not os.path.exists(config.idx_path):
        return word_idx, word_list

    count = 0
    with open(config.idx_path, "rb") as f:
        while True:
            word_str = _read_word(f)
            # TODO support 64bit offset in stardict v3.0.0
            offset_size = 8

            word_pointer = f.read(offset_size)
            if not word_pointer:
                break
            word_idx[word_str] = count
            word_list.append(unpack(">II", word_pointer))
            count += 1
    return word_idx, word_list


def parse_dict(config, ifo, word, offset, size):
    """Parse a dictionary file.

    Args:
        config (Configuration): stardict configuration
        ifo (dict): dictionary of IFO file settings
        word (str): word to lookup in the dictionary
        offset (int): offset of the definition in dict file
        size (int): size of the definition data

    Returns:
        definition of a word in the dictionary

    """
    if type(ifo) is not dict:
        raise TypeError("`ifo` must be a dictionary.")

    if type(config) is not Configuration:
        raise TypeError("Invalid type for `config`.")

    if not os.path.exists(config.dict_path):
        logger.info("dict file not found: {}".format(config.dict_path))
        return None

    open_dict = open
    if config.dict_path.endswith(".dz"):
        open_dict = idzip.open

    types = ifo["sametypesequence"] if "sametypesequence" in ifo else "m"
    with open_dict(config.dict_path, "rb") as f:
        f.seek(offset)
        data = f.read(size)
        data_str = data.decode("utf-8").rstrip("\0")

        # We only support sametypesequence=m, h
        if types == "m" and data_str[0] == "m":
            return data_str[1:]

        if types == "h":
            return data_str
        return None


def parse_syn(config):
    r"""Parse a syn file with synonyms.

    Args:
        config (Configuration): stardict configuration

    Returns:
        map of synonyms and the word indices in idx

    The format is simple. Each item contain one string and a number.
    synonym_word;  // a utf-8 string terminated by '\0'.
    original_word_index; // original word's index in .idx file.
    Then other items without separation.
    When you input synonym_word, StarDict will search original_word;

    The length of "synonym_word" should be less than 256. In other
    words, (strlen(word) < 256).
    original_word_index is a 32-bits unsigned number in network byte order.
    Two or more items may have the same "synonym_word" with different
    original_word_index.

    """
    syn_map = {}
    if not os.path.exists(config.syn_path):
        return syn_map

    with open(config.syn_path, "rb") as f:
        while True:
            word_str = _read_word(f)
            word_pointer = f.read(4)
            if not word_pointer:
                break
            if word_str not in syn_map:
                syn_map[word_str] = []
            syn_map[word_str].extend(unpack(">I", word_pointer))

    return syn_map


def _read_word(f):
    r"""Read a unicode `\0` terminated string from a file like object."""
    word = bytearray()
    c = f.read(1)
    while c and c != b'\0':
        word.extend(c)
        c = f.read(1)
    return word.decode("utf-8")


@click.command()
@click.argument("dict_path", type=click.Path(exists=True))
@click.argument("word", type=str)
@click.option("--debug", is_flag=True, show_default=True,
              help="Show diagnostic messages.")
def start(dict_path, word, debug):
    """Stargaze can parse and query stardict dictionary files."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.info("Verbose messages are enabled.")

    d = Dictionary(dict_path)
    print(d.lookup(word))


if __name__ == '__main__':
    start()
