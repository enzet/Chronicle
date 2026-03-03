"""Tests for Subject value type."""

from chronicle.value import Language, Subject

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_subject_from_string_multi_level() -> None:
    """`from_string` splits slash-separated path into a list."""
    result = Subject.from_string("/language/en")
    assert isinstance(result, Subject)
    assert result.subject == ["language", "en"]


def test_subject_from_string_single_level() -> None:
    """`from_string` handles a single-segment path."""
    result = Subject.from_string("/fiction")
    assert isinstance(result, Subject)
    assert result.subject == ["fiction"]


def test_subject_from_string_three_level() -> None:
    """`from_string` handles three-segment paths."""
    result = Subject.from_string("/fiction/mystery")
    assert isinstance(result, Subject)
    assert result.subject == ["fiction", "mystery"]


def test_subject_is_language_true() -> None:
    """`is_language` returns True when first segment is "language"."""
    assert Subject(["language", "en"]).is_language() is True


def test_subject_is_language_false() -> None:
    """`is_language` returns False for non-language subjects."""
    assert Subject(["fiction"]).is_language() is False


def test_subject_is_script_true() -> None:
    """`is_script` returns True when first segment is "script"."""
    assert Subject(["script", "arab"]).is_script() is True


def test_subject_is_script_false() -> None:
    """`is_script` returns False for non-script subjects."""
    assert Subject(["language", "ar"]).is_script() is False


def test_subject_get_language_from_language_subject() -> None:
    """`get_language` extracts `Language` from a language subject."""
    assert Subject(["language", "en"]).get_language() == Language("en")


def test_subject_get_language_from_script_arab() -> None:
    """`get_language` resolves Arabic script to `Language("ar")`."""
    assert Subject(["script", "arab"]).get_language() == Language("ar")


def test_subject_get_language_from_script_kana() -> None:
    """`get_language` resolves Kana script to `Language("ja")`."""
    assert Subject(["script", "kana"]).get_language() == Language("ja")


def test_subject_get_language_returns_none_for_other() -> None:
    """`get_language` returns None when subject is unknown."""
    assert Subject(["fiction"]).get_language() is None


def test_subject_get_language_returns_none_no_code() -> None:
    """`get_language` returns None when language segment is missing."""
    assert Subject(["language"]).get_language() is None


def test_subject_to_string() -> None:
    """`to_string` joins segments with "/"."""
    assert Subject(["language", "en"]).to_string() == "language/en"
    assert Subject(["fiction"]).to_string() == "fiction"


def test_subject_hash_deduplication() -> None:
    """Equal `Subject` objects hash to the same value."""
    subjects = {Subject(["language", "en"]), Subject(["language", "en"])}
    assert len(subjects) == 1
