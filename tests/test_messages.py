"""Tests for messages.py — verify all template lists exist, are non-empty, and well-formed."""

import discord
import messages


# All expected list names and their minimum expected length
EXPECTED_LISTS = {
    "games": 4,
    "morning_greetings": 5,
    "cursed_emojis": 5,
    "funny_nicknames": 20,
    "jumpscare_messages": 5,
    "fake_typing_messages": 5,
    "take_judgements": 5,
    "wrong_channel_messages": 5,
    "fake_mod_reasons": 5,
    "drama_templates": 5,
    "conspiracy_templates": 5,
    "afk_check_messages": 5,
    "random_polls": 5,
    "misquotes": 5,
    "fake_announcements": 5,
    "hype_messages": 5,
    "hot_takes": 10,
    "late_night_messages": 10,
    "gn_phrases": 5,
    "gn_callouts": 5,
    "hype_detector_messages": 5,
    "fake_rules": 5,
    "welcome_messages": 4,
    "typing_callout_messages": 5,
    "essay_responses": 5,
    "k_responses": 5,
    "friday_messages": 5,
}


class TestMessageListsExist:
    """Every expected message list is present and non-empty."""

    def test_all_lists_present(self):
        for name in EXPECTED_LISTS:
            assert hasattr(messages, name), f"messages.py missing list: {name}"

    def test_all_lists_non_empty(self):
        for name, min_len in EXPECTED_LISTS.items():
            lst = getattr(messages, name)
            assert len(lst) >= min_len, f"{name} has {len(lst)} items, expected >= {min_len}"


class TestGamesFormat:
    """Games list entries are (ActivityType, str) tuples."""

    def test_games_are_tuples(self):
        for entry in messages.games:
            assert isinstance(entry, tuple) and len(entry) == 2

    def test_games_have_activity_types(self):
        for activity_type, value in messages.games:
            assert isinstance(activity_type, discord.ActivityType)
            assert isinstance(value, str) and len(value) > 0


class TestTemplateFormatStrings:
    """Templates with format placeholders don't crash when formatted."""

    def test_drama_templates(self):
        for tmpl in messages.drama_templates:
            result = tmpl.format(a="@Alice", b="@Bob")
            assert "@Alice" in result and "@Bob" in result

    def test_conspiracy_templates(self):
        for tmpl in messages.conspiracy_templates:
            result = tmpl.format(user="@User")
            assert "@User" in result

    def test_afk_check_messages(self):
        for tmpl in messages.afk_check_messages:
            result = tmpl.format(user="@User")
            assert isinstance(result, str)

    def test_gn_callouts(self):
        for tmpl in messages.gn_callouts:
            result = tmpl.format(user="@User", mins=25)
            assert isinstance(result, str)

    def test_welcome_messages(self):
        for tmpl in messages.welcome_messages:
            result = tmpl.format(user="@User", nick="CoolNick", num=99, rule="Be cool")
            assert "@User" in result

    def test_typing_callout_messages(self):
        for tmpl in messages.typing_callout_messages:
            result = tmpl.format(user="@User")
            assert "@User" in result

    def test_hype_messages(self):
        for tmpl in messages.hype_messages:
            result = tmpl.format(user="@User")
            assert "@User" in result


class TestRandomPolls:
    """Each poll has a question string and a list of 2+ options."""

    def test_poll_structure(self):
        for question, options in messages.random_polls:
            assert isinstance(question, str) and len(question) > 0
            assert isinstance(options, list) and len(options) >= 2
            for opt in options:
                assert isinstance(opt, str) and len(opt) > 0


class TestMisquotes:
    """Each misquote is a (quote, attribution) tuple."""

    def test_misquote_structure(self):
        for quote, attribution in messages.misquotes:
            assert isinstance(quote, str) and len(quote) > 0
            assert isinstance(attribution, str) and attribution.startswith("\u2014")
