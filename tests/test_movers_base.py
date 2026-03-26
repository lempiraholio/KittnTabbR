"""Tests for movers/base.py — safe(), pretty(), dest_dir() utilities."""

from pathlib import Path

import pytest

from metadata import TabMetadata
from movers.base import dest_dir, pretty, safe


class TestSafe:
    def test_strips_forward_slash(self):
        assert safe("AC/DC") == "ACDC"

    def test_strips_angle_brackets(self):
        assert safe("<hello>") == "hello"

    def test_strips_colon(self):
        assert safe("Led:Zeppelin") == "LedZeppelin"

    def test_strips_backslash(self):
        assert safe("foo\\bar") == "foobar"

    def test_strips_pipe(self):
        assert safe("foo|bar") == "foobar"

    def test_strips_question_mark(self):
        assert safe("what?") == "what"

    def test_strips_asterisk(self):
        assert safe("foo*bar") == "foobar"

    def test_strips_quotes(self):
        assert safe('"quoted"') == "quoted"

    def test_strips_surrounding_whitespace(self):
        assert safe("  foo  ") == "foo"

    def test_clean_name_unchanged(self):
        assert safe("Pantera") == "Pantera"


class TestPretty:
    def test_snake_case(self):
        assert pretty("walk_this_way") == "Walk This Way"

    def test_hyphenated(self):
        assert pretty("walk-this-way") == "Walk This Way"

    def test_space_separated(self):
        assert pretty("walk this way") == "Walk This Way"

    def test_mixed_delimiters(self):
        assert pretty("walk_this-way") == "Walk This Way"

    def test_single_word(self):
        assert pretty("walk") == "Walk"

    def test_already_title_case(self):
        assert pretty("Walk This Way") == "Walk This Way"

    def test_all_caps(self):
        assert pretty("WALK") == "Walk"

    def test_empty_string(self):
        assert pretty("") == ""

    def test_collapses_extra_spaces(self):
        assert pretty("walk  this") == "Walk This"


class TestDestDir:
    def test_with_album(self):
        meta = TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")
        result = dest_dir(Path("/tabs"), meta)
        assert result == Path("/tabs/Pantera/Vulgar Display of Power")

    def test_without_album(self):
        meta = TabMetadata(artist="Pantera", song="Walk", album="Unknown")
        result = dest_dir(Path("/tabs"), meta)
        assert result == Path("/tabs/Pantera")

    def test_artist_with_invalid_chars(self):
        meta = TabMetadata(artist="AC/DC", song="Back in Black", album="Back in Black")
        result = dest_dir(Path("/tabs"), meta)
        assert result == Path("/tabs/ACDC/Back in Black")
