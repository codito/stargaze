#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for stardict."""
import logging
import pytest
from click.testing import CliRunner

import stardict


@pytest.fixture
def ifo_file():
    return None


def test_parse_ifo_returns_none_for_nonexistent_file(ifo_file):
    pass


def test_parse_ifo_returns_none_for_invalid_file(ifo_file):
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
