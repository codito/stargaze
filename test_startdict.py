#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for stardict."""
import logging
import pytest
from click.testing import CliRunner

import stardict


def test_transaction_output_qif_header():
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
