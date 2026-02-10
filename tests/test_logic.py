"""
Comprehensive test suite for the Unicode → Kruti Dev 010 converter.

Expected outputs verified against: https://unicodetokrutidev.net
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.reorder import (
    MangalToKrutiDevConverter,
    SyllableParser,
    SyllableRenderer,
    Tokenizer,
    Mapper,
)


@pytest.fixture
def converter():
    return MangalToKrutiDevConverter()


# =============================================================================
# Independent Vowels
# =============================================================================

class TestIndependentVowels:
    """Test all independent vowels (स्वर)."""

    @pytest.mark.parametrize("input_text, expected", [
        ('अ', 'v'),
        ('आ', 'vk'),
        ('इ', 'b'),
        ('ई', 'bZ'),
        ('उ', 'm'),
        ('ऊ', 'Å'),
        ('ऋ', '_'),
        ('ए', ','),
        ('ऐ', ',s'),
        ('ओ', 'vks'),
        ('औ', 'vkS'),
    ])
    def test_standalone_vowels(self, converter, input_text, expected):
        assert converter.convert(input_text) == expected

    def test_vowel_e_before_consonant(self, converter):
        """ए before consonant — critical regression test."""
        assert converter.convert('एक') == ',d'

    def test_vowel_ai_before_consonant(self, converter):
        """ऐ before consonant — critical regression test."""
        assert converter.convert('ऐसा') == ',slk'


# =============================================================================
# Basic Consonants
# =============================================================================

class TestConsonants:
    """Test basic consonants with inherent 'a' vowel."""

    @pytest.mark.parametrize("input_text, expected", [
        ('क', 'd'),
        ('ख', '[k'),
        ('ग', 'x'),
        ('घ', '?k'),
        ('च', 'p'),
        ('छ', 'N'),
        ('ज', 't'),
        ('ट', 'V'),
        ('ठ', 'B'),
        ('ड', 'M'),
        ('ढ', '<'),
        ('ण', '.k'),
        ('त', 'r'),
        ('थ', 'Fk'),
        ('द', 'n'),
        ('ध', '/k'),
        ('न', 'u'),
        ('प', 'i'),
        ('फ', 'Q'),
        ('ब', 'c'),
        ('भ', 'Hk'),
        ('म', 'e'),
        ('य', ';'),
        ('र', 'j'),
        ('ल', 'y'),
        ('व', 'o'),
        ("श", "'k"),
        ('ष', '"k'),
        ('स', 'l'),
        ('ह', 'g'),
    ])
    def test_consonants(self, converter, input_text, expected):
        assert converter.convert(input_text) == expected


# =============================================================================
# Consonant + Matra
# =============================================================================

class TestMatras:
    """Test consonants with various matras."""

    @pytest.mark.parametrize("input_text, expected", [
        ('का', 'dk'),
        ('कि', 'fd'),    # i-matra goes BEFORE
        ('की', 'dh'),
        ('कु', 'dq'),
        ('कू', 'dw'),
        ('के', 'ds'),
        ('कै', 'dS'),
        ('को', 'dks'),
        ('कौ', 'dkS'),
    ])
    def test_basic_matras(self, converter, input_text, expected):
        assert converter.convert(input_text) == expected

    def test_i_matra_positioning(self, converter):
        """ि matra must appear BEFORE the consonant in Kruti Dev."""
        result = converter.convert('कि')
        assert result == 'fd'
        assert result[0] == 'f'  # i-matra first


# =============================================================================
# Common Words (verified against reference converter)
# =============================================================================

class TestCommonWords:
    """Test complete words verified against unicodetokrutidev.net."""

    @pytest.mark.parametrize("input_text, expected, description", [
        ('नमस्ते', 'ueLrs', 'Namaste'),
        ('भारत', 'Hkkjr', 'Bharat'),
        ('हिंदी', 'fganh', 'Hindi'),
        ('राम', 'jke', 'Ram'),
        ('सरकार', 'ljdkj', 'Sarkar'),
        ('आप', 'vki', 'Aap'),
        ('है', 'gS', 'Hai'),
        ('हैं', 'gSa', 'Hain'),
        ('मैं', 'eSa', 'Main'),
        ('में', 'esa', 'Mein'),
        ('अब', 'vc', 'Ab'),
        ('इस', 'bl', 'Is'),
        ('उस', 'ml', 'Us'),
    ])
    def test_common_words(self, converter, input_text, expected, description):
        assert converter.convert(input_text) == expected, f"Failed: {description}"


# =============================================================================
# Conjuncts
# =============================================================================

class TestConjuncts:
    """Test conjunct consonants (संयुक्ताक्षर)."""

    @pytest.mark.parametrize("input_text, expected, description", [
        ('क्या', 'D;k', 'Kya — half ka + ya'),
        ('वाक्य', 'okD;', 'Vakya — half ka + ya'),
        ('स्कूल', 'Ldwy', 'School — half sa + ka'),
        ('प्रेम', 'çse', 'Prem — pra conjunct'),
        ('प्रदेश', "çns'k", 'Pradesh'),
        ('शुक्रवार', "'kqØokj", 'Shukravar'),
        ('परीक्षण', 'ijh{k.k', 'Parikshan — ksha conjunct'),
        ('शिक्षा', "f'k{kk", 'Shiksha'),
        ('द्वार', '}kj', 'Dwar — dva conjunct'),
        ('उत्तर', 'mÙkj', 'Uttar — tta conjunct'),
    ])
    def test_conjuncts(self, converter, input_text, expected, description):
        assert converter.convert(input_text) == expected, f"Failed: {description}"


# =============================================================================
# Reph and Rakar
# =============================================================================

class TestRephRakar:
    """Test reph (र्) and rakar (्र) handling."""

    @pytest.mark.parametrize("input_text, expected, description", [
        ('धर्म', '/keZ', 'Dharma — reph'),
        ('कर्म', 'deZ', 'Karma — reph'),
        ('विद्यार्थी', 'fo|kFkhZ', 'Vidyarthi — reph'),
        ('राष्ट्र', 'jk"Vª', 'Rashtra — rakar'),
    ])
    def test_reph_and_rakar(self, converter, input_text, expected, description):
        assert converter.convert(input_text) == expected, f"Failed: {description}"


# =============================================================================
# Special ri-matra conjuncts
# =============================================================================

class TestRiMatra:
    """Test special ri-matra (ृ) conjuncts."""

    def test_kri(self, converter):
        """कृ → — (em-dash, U+2014)"""
        assert converter.convert('कृष्ण') == '\u2014".k'

    def test_ri_matra_standalone(self, converter):
        """ऋ as standalone vowel."""
        assert converter.convert('ऋषि') == '_f"k'


# =============================================================================
# Nukta Consonants
# =============================================================================

class TestNukta:
    """Test nukta consonants (ड़, ढ़, etc.)."""

    @pytest.mark.parametrize("input_text, expected", [
        ('ड़', 'M+'),
        ('ढ़', '<+'),
    ])
    def test_nukta_consonants(self, converter, input_text, expected):
        assert converter.convert(input_text) == expected


# =============================================================================
# Mixed Language Text
# =============================================================================

class TestMixedLanguage:
    """Test mixed Hindi-English text handling."""

    def test_mixed_hindi_english(self, converter):
        """English text should pass through unchanged."""
        result = converter.convert('Hello हिंदी World')
        assert 'Hello' in result
        assert 'World' in result
        assert 'fganh' in result

    def test_pure_english(self, converter):
        """Pure English text should be returned as-is."""
        result = converter.convert('Hello World')
        assert result == 'Hello World'

    def test_empty_string(self, converter):
        assert converter.convert('') == ''

    def test_whitespace_only(self, converter):
        assert converter.convert('   ') == '   '


# =============================================================================
# Full Sentence Test
# =============================================================================

class TestSentences:
    """Test complete sentences."""

    def test_sentence_1(self, converter):
        """Reference: unicodetokrutidev.net"""
        # यह एक परीक्षण वाक्य है। → ;g ,d ijh{k.k okD; gSA
        result = converter.convert('यह एक परीक्षण वाक्य है।')
        assert ',d' in result        # 'एक' correct
        assert 'ijh{k.k' in result   # 'परीक्षण'
        assert 'okD;' in result      # 'वाक्य'
        assert 'gS' in result        # 'है'


# =============================================================================
# Tokenizer Tests
# =============================================================================

class TestTokenizer:
    """Test the tokenizer."""

    def test_hindi_tokens(self):
        tokens = Tokenizer.tokenize('हिंदी')
        assert len(tokens) == 1
        assert tokens[0][1] == 'hindi'

    def test_mixed_tokens(self):
        tokens = Tokenizer.tokenize('Hello हिंदी')
        assert len(tokens) == 3
        assert tokens[0][1] == 'english'
        assert tokens[1][1] == 'whitespace'
        assert tokens[2][1] == 'hindi'

    def test_danda_token(self):
        tokens = Tokenizer.tokenize('है।')
        assert any(t[1] == 'hindi_punct' for t in tokens)


# =============================================================================
# Syllable Parser Tests
# =============================================================================

class TestSyllableParser:
    """Test the syllable parser."""

    def test_simple_consonant_vowel(self):
        syllables = SyllableParser.parse_word('का')
        assert len(syllables) == 1
        assert syllables[0]['consonants'] == ['क']
        assert syllables[0]['matra'] == 'ा'

    def test_i_matra(self):
        syllables = SyllableParser.parse_word('कि')
        assert len(syllables) == 1
        assert syllables[0]['matra'] == 'ि'

    def test_reph_detection(self):
        syllables = SyllableParser.parse_word('र्म')
        assert any(s['has_reph'] for s in syllables)

    def test_conjunct_cluster(self):
        syllables = SyllableParser.parse_word('स्त')
        assert len(syllables) == 1
        consonants = syllables[0]['consonants']
        cluster = ''.join(consonants)
        assert 'स' in cluster
        assert 'त' in cluster


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
