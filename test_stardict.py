#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for stardict."""
import logging
import pytest
import idzip
from click.testing import CliRunner

import stardict

IFO_DATA = {}


@pytest.fixture
def config(fs):
    c = stardict.Configuration("/tmp/stardict_test/test.ifo",
                               "/tmp/stardict_test/test.idx",
                               "/tmp/stardict_test/test.syn",
                               "/tmp/stardict_test/test.dict")
    fs.create_file(c.ifo_path)
    fs.create_file(c.idx_path)
    fs.create_file(c.syn_path)
    fs.create_file(c.dict_path)
    return c


def _create_invalid_config():
    return stardict.Configuration("/tmp/stardict_test/non_existent.ifo",
                                  "/tmp/stardict_test/non_existent.idx",
                                  "/tmp/stardict_test/non_existent.syn",
                                  "/tmp/stardict_test/non_existent.dict")


def _create_ifo_file(fs, config, header, content):
    with open(config.ifo_path, "w", encoding="utf-8") as f:
        f.write("{}\n".format(header))
        f.writelines(["{0}={1}\n".format(k, v) for k, v in content.items()])


def _create_idx_file(fs, config, content):
    with open(config.idx_path, "wb") as f:
        f.write(content)


def _create_dict_file(fs, config, content):
    with open(config.dict_path, "wb") as f:
        f.write(content)


def _create_dictzip_file(fs, config, content):
    fs.create_file(config.dict_path)
    with idzip.open(config.dict_path, "wb") as f:
        f.write(content)


def _create_syn_file(fs, config, content):
    with open(config.syn_path, "wb") as f:
        f.write(content)


def test_parse_ifo_returns_none_for_nonexistent_file():
    c = _create_invalid_config()
    r = stardict.parse_ifo(c)
    assert r == {}


def test_parse_ifo_returns_none_for_invalid_file(fs, config):
    _create_ifo_file(fs, config, "", {})
    r = stardict.parse_ifo(config)
    assert r == {}


def test_parse_ifo_returns_info_dict_for_valid_file(fs, config):
    magic_header = "StarDict's dict ifo file"
    ifo_data = {'a': "b", 'aa ': "c\n"}
    _create_ifo_file(fs, config, magic_header, ifo_data)

    r = stardict.parse_ifo(config)

    assert r == {'a': "b", 'aa': "c"}


def test_parse_idx_returns_empty_dict_for_nonexistent_file():
    c = _create_invalid_config()
    r = stardict.parse_idx(c)
    assert r == {}


def test_parse_idx_returns_dict_for_valid_file(fs, config):
    b = b"--\x00\x00\x00bt\x00\x00\x19\xf6-ma\x00\x00\x00\xf5B\x00\x00\tp"
    _create_idx_file(fs, config, b)
    r = stardict.parse_idx(config)

    assert r == {'--': (25204, 6646), '-ma': (62786, 2416)}


def test_parse_dict_returns_empty_definition_for_nonexistent_file():
    c = _create_invalid_config()
    r = stardict.parse_dict(c, "--", 0, 4)
    assert r is None


def test_parse_dict_returns_definitions_for_valid_file(fs, config):
    b = b"\x00\x00\x00bt\x00\x00\x19\xf6-ma\x00\x00\x00\xf5B\x00\x00\tp"
    _create_dict_file(fs, config, b)
    r = stardict.parse_dict(config, "--", 0, 4)

    assert r == b"\x00\x00\x00b"


def test_parse_dictzip_returns_definitions_for_valid_file(fs, config):
    b = b"\x00\x00\x00bt\x00\x00\x19\xf6-ma\x00\x00\x00\xf5B\x00\x00\tp"
    p = config.dict_path + ".dz"
    c = stardict.Configuration(config.ifo_path, config.idx_path, "", p)
    _create_dictzip_file(fs, c, b)
    r = stardict.parse_dict(c, "--", 0, 4)

    assert r == b"\x00\x00\x00b"


def test_parse_syn_returns_empty_map_for_nonexistent_file():
    c = _create_invalid_config()
    r = stardict.parse_syn(c)
    assert r == {}


def test_parse_syn_returns_idx_index_for_valid_file(fs, config):
    b = b"++\x00\x00\x00bt++\x00\x00\x00f6-ma\x00\x00\x00\x19\x00f6"
    _create_syn_file(fs, config, b)
    r = stardict.parse_syn(config)

    assert r == {'++': [25204, 26166], '-ma': [6400]}


def test_start_ignores_dict_without_idx():
    pass


def test_start_ignores_dict_without_dict_or_dictzip():
    pass


def test_start_considers_syn_file_as_optional():
    pass


def test_start_sample(fs, config):
    runner = CliRunner()

    result = runner.invoke(stardict.start, ["/tmp/stardict_test", "word"])

    assert result.exception is None
    assert result.exit_code == 0
    assert "" in result.output


def test_option_debug_configures_logging(caplog):
    runner = CliRunner()

    with caplog.at_level(logging.INFO):
        result = runner.invoke(stardict.start, [".", "word", "--debug"])

    debug = ("stardict", logging.INFO, "Verbose messages are enabled.")
    assert result.exception is None
    assert result.exit_code is 0
    assert debug in caplog.record_tuples
