from discord.ext.i18n.language import (
    Language,
    LANG_CODE2EMOJIS,
    LANG_NAME2CODE,
    LANG_CODE2NAME,
)


def test_correspondence():
    """
    Test if the properties of the `Language` aligns with the dictionary
    definitions.
    """
    for sub in Language._member_map_.values():
        assert sub.code == sub.value
        assert sub.value == LANG_NAME2CODE[sub.name]
        assert sub.name == LANG_CODE2NAME[sub.value]
        assert sub.emoji == LANG_CODE2EMOJIS.get(sub.value, None)


def test_by_name():
    """
    Test if the function accurately represents the an enum object
    based on the language name.
    """
    assert Language.from_name("chinese (simplified)") is Language.ChineseSimplified
    assert Language.from_name("ukrainian") is Language.Ukrainian
    assert Language.from_name("kurdish (kurmanji)") is Language.KurdishKurmanji
    assert Language.from_name("slovenian") is not Language.Lao
    assert Language.from_name("spanish") is not Language.Slovenian
    assert Language.from_name("lao") is not Language.Spanish

    for sub in Language._member_map_.values():
        assert Language.from_name(sub.name) is sub


def test_by_id():
    """
    Test if the function accurately represents the an enum object
    based on the language id.
    """
    assert Language.from_code("ms") is Language.Malay
    assert Language.from_code("ja") is Language.Japanese
    assert Language.from_code("et") is Language.Estonian
    assert Language.from_code("ms") is not Language.Lithuanian
    assert Language.from_code("ml") is not Language.Hindi
    assert Language.from_code("mi") is not Language.Indonesian

    for sub in Language._member_map_.values():
        assert Language.from_code(sub.value) is sub


def test_dict_complete():
    """
    Test the relative completeness of the `LANG_CODE2NAME` and `LANG_NAME2CODE`
    dictionary.
    """
    k_code2names = set(LANG_CODE2NAME.keys())
    v_code2names = list(LANG_CODE2NAME.values())
    v_name2codes = set(LANG_NAME2CODE.values())

    # Sometimes a language has more than one code,
    # that shouldn't be an issue.
    excess_codes = list(
        filter(lambda item: v_code2names.count(item[1]) == 2, LANG_CODE2NAME.items())
    )
    for code in excess_codes:
        v_name2codes.add(code[0])

    assert k_code2names == v_name2codes


def test_enum_complete():
    """
    Test the completeness of the `Language` enum based on dictionary
    definitions.
    """
    v_code2names = list(LANG_CODE2NAME.values())
    v_enum_codes = set(Language._value2member_map_.keys())
    v_name2codes = set(LANG_NAME2CODE.values())

    e_excess_codes = list(
        filter(
            lambda item: v_code2names.count(item[1].name) == 2,
            Language._value2member_map_.items(),
        )
    )
    for code in e_excess_codes:
        v_enum_codes.add(code[0])

    assert v_name2codes == v_enum_codes
