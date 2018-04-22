#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for stardict."""
import logging
import pytest
from click.testing import CliRunner

import stardict

IFO_DATA = {}


@pytest.fixture
def config():
    c = stardict.Configuration("/tmp/stardict_test/test.ifo")
    return c


def _create_ifo_file(fs, config, header, content):
    fs.create_file(config.ifo_path)
    with open(config.ifo_path, "w", encoding="utf-8") as f:
        f.write("{}\n".format(header))
        f.writelines(["{0}={1}\n".format(k, v) for k, v in content.items()])


def test_parse_ifo_returns_none_for_nonexistent_file():
    c = stardict.Configuration("/tmp/stardict_test/non_existent.ifo")
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


def test_start_sample():
    runner = CliRunner()

    result = runner.invoke(stardict.start, [".", "word"])

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
