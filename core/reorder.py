"""
Production-Grade Mangal (Unicode) → Kruti Dev 010 (Legacy) Font Converter

This module implements a linguistically-aware converter that respects:
- Devanagari syllable structure
- Matra positioning rules (especially ि → before consonant, reph → after syllable)
- Reph (र्) reordering
- Conjunct handling (including special ri-matra ligatures)
- Word-level tokenization
- Mixed-language support

Verified against: https://unicodetokrutidev.net reference converter

Author: Production Implementation
"""

import re
from typing import List, Tuple


# =============================================================================
# SECTION 1: COMPLETE CHARACTER MAPPING TABLES
# =============================================================================

# Independent Vowels (स्वर)
# IMPORTANT: ए maps to ',' (just comma) — NOT ',s'
#            ऐ maps to ',s' — NOT 'S'
#            Verified against unicodetokrutidev.net reference converter
VOWELS = {
    'अ': 'v',
    'आ': 'vk',
    'इ': 'b',
    'ई': 'bZ',
    'उ': 'm',
    'ऊ': 'Å',
    'ऋ': '_',
    'ए': ',',       # CRITICAL: Just comma, NOT ',s'. एक → ,d
    'ऐ': ',s',      # CRITICAL: Comma + s. ऐसा → ,slk
    'ओ': 'vks',
    'औ': 'vkS',
    'ऑ': 'v‚',      # For English loanwords (Candra A)
}

# Consonants (व्यंजन)
CONSONANTS = {
    # Velar (कंठ्य)
    'क': 'd',
    'ख': '[k',
    'ग': 'x',
    'घ': '?k',
    'ङ': '³',

    # Palatal (तालव्य)
    'च': 'p',
    'छ': 'N',
    'ज': 't',
    'झ': '>',
    'ञ': '¥',

    # Retroflex (मूर्धन्य)
    'ट': 'V',
    'ठ': 'B',
    'ड': 'M',
    'ढ': '<',
    'ण': '.k',

    # Dental (दंत्य)
    'त': 'r',
    'थ': 'Fk',
    'द': 'n',
    'ध': '/k',
    'न': 'u',

    # Labial (ओष्ठ्य)
    'प': 'i',
    'फ': 'Q',
    'ब': 'c',
    'भ': 'Hk',
    'म': 'e',

    # Semi-vowels (अंतस्थ)
    'य': ';',
    'र': 'j',
    'ल': 'y',
    'व': 'o',

    # Sibilants (ऊष्म)
    'श': "'k",
    'ष': '"k',
    'स': 'l',
    'ह': 'g',

    # Additional
    'ळ': 'G',
}

# Half-forms (consonant + halant) — used when consonant precedes another consonant
HALF_FORMS = {
    'क': 'D',
    'ख': '[',
    'ग': 'X',
    'घ': '?',
    'च': 'P',
    'छ': 'N~',      # No distinct half-form
    'ज': 'T',
    'झ': '÷',
    'ञ': '¥~',
    'ट': 'V~',      # No distinct half-form (uses halant)
    'ठ': 'B~',
    'ड': 'M~',
    'ढ': '<~',
    'ण': '.',
    'त': 'R',
    'थ': 'F',
    'द': 'n~',      # Special handling needed
    'ध': '/',
    'न': 'U',
    'प': 'I',
    'फ': '¶',
    'ब': 'C',
    'भ': 'H',
    'म': 'E',
    'य': '¸',
    'र': 'j~',      # Reph — has special handling
    'ल': 'Y',
    'व': 'O',
    'श': "'",
    'ष': '"',
    'स': 'L',
    'ह': 'º',
}

# Dependent Vowel Signs (मात्राएं)
MATRAS = {
    'ा': 'k',       # Aa matra — placed after
    'ि': 'f',       # I matra — placed BEFORE consonant (special)
    'ी': 'h',       # Ii matra — placed after
    'ु': 'q',       # U matra — placed after
    'ू': 'w',       # Uu matra — placed after
    'ृ': '`',       # Ri matra — placed after (but has special conjuncts)
    'े': 's',       # E matra — placed after
    'ै': 'S',       # Ai matra — placed after
    'ो': 'ks',      # O matra — placed after
    'ौ': 'kS',      # Au matra — placed after
    'ॉ': '‚',       # Candra O — placed after
    'ॅ': 'W',       # Candra E — placed after
}

# Modifiers (अनुस्वार, चंद्रबिंदु, विसर्ग)
MODIFIERS = {
    'ं': 'a',       # Anusvara
    'ँ': '¡',       # Chandrabindu
    'ः': '%',       # Visarga
    '्': '~',       # Halant/Virama
}

# Nukta consonants (consonant + nukta for Urdu/Persian sounds)
NUKTA_CONSONANTS = {
    'क़': 'd+',
    'ख़': '[k+',
    'ग़': 'x+',
    'ज़': 't+',
    'ड़': 'M+',
    'ढ़': '<+',
    'फ़': 'Q+',
    'य़': ';+',
}

# Special Ri-Matra Conjuncts — these produce SINGLE special characters in Kruti Dev
# Verified against unicodetokrutidev.net reference converter with char code verification
RI_MATRA_SPECIAL = {
    'क': '\u2014',   # कृ → — (Em-dash, U+2014)
    'द': '\u2013',   # दृ → – (En-dash, U+2013)
    'ह': '\u00E2',   # हृ → â (a-circumflex, U+00E2)
}

# Special Conjuncts (संयुक्ताक्षर) — processed BEFORE individual characters
CONJUNCTS = {
    # Ksha group
    'क्ष': '{k',
    'क्ष्': '{',

    # Tra group
    'त्र': '=',
    'त्र्': '«',

    # Gya/Dnya
    'ज्ञ': 'K',

    # Shra
    'श्र': 'J',

    # Common conjuncts
    'क्क': 'ô',
    'क्त': 'Dr',
    'त्त': 'Ùk',
    'त्त्': 'Ù',
    'द्द': 'í',
    'द्ध': ')',
    'द्व': '}',
    'द्य': '|',
    'ट्ट': 'ê',
    'ट्ठ': 'ë',
    'ड्ड': 'ì',
    'ड्ढ': 'ï',
    'न्न': 'é',

    # H-conjuncts
    'ह्न': 'à',
    'ह्य': 'á',
    'ह्म': 'ã',
    'ह्र': 'ºz',
    'ह्ल': 'ày',

    # R-conjuncts (subscript ra / rakar) — consonant + ्र
    'क्र': 'Ø',
    'ग्र': 'xz',
    'प्र': 'ç',
    'फ्र': 'Ý',
    'द्र': 'æ',
    'ट्र': 'Vª',
    'ड्र': 'Mª',
    'ढ्र': '<ª',
    'छ्र': 'Nª',
    'थ्र': 'Fkz',
    'भ्र': 'Hkz',
    'स्र': 'lz',
}

# Hindi Numerals
NUMERALS = {
    '०': '0',
    '१': '1',
    '२': '2',
    '३': '3',
    '४': '4',
    '५': '5',
    '६': '6',
    '७': '7',
    '८': '8',
    '९': '9',
}

# Punctuation (Devanagari specific)
PUNCTUATION = {
    '।': 'A',       # Danda (full stop)
    '॥': 'AA',      # Double Danda
    '॰': 'Œ',       # Abbreviation sign
}

# ASCII/English punctuation → Kruti Dev mapping (in Hindi context)
PUNCTUATION_MAP = {
    '(': '¼',       # Opening parenthesis
    ')': '½',       # Closing parenthesis
    ',': ']',       # Kruti Dev comma
    '.': '-',       # Kruti Dev period
    '?': '\\',      # Kruti Dev question mark
    ':': '%',       # Kruti Dev colon
    ';': '^',       # Kruti Dev semicolon
    '-': '&',       # Kruti Dev hyphen
    '—': '&&',      # Em-dash
    '–': '&',       # En-dash
}

# Characters to preserve as-is
PRESERVE_CHARS = set(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    ' \t\n\r@#$%^&*[]{}|\\/><\'\"_+=~`'
)


# =============================================================================
# SECTION 2: TOKENIZER
# =============================================================================

class Tokenizer:
    """Tokenizes input text into processable units."""

    DEVANAGARI_START = 0x0900
    DEVANAGARI_END = 0x097F

    @classmethod
    def is_devanagari(cls, char: str) -> bool:
        """Check if character is Devanagari."""
        if not char:
            return False
        code = ord(char)
        return cls.DEVANAGARI_START <= code <= cls.DEVANAGARI_END

    @classmethod
    def tokenize(cls, text: str) -> List[Tuple[str, str]]:
        """
        Tokenize text into (token, type) pairs.
        Types: 'hindi', 'english', 'number', 'punctuation',
               'whitespace', 'hindi_punct', 'bracket', 'other'
        """
        tokens = []
        current_token = ""
        current_type = None

        for char in text:
            char_type = cls._get_char_type(char)

            if char_type == current_type:
                current_token += char
            else:
                if current_token:
                    tokens.append((current_token, current_type))
                current_token = char
                current_type = char_type

        if current_token:
            tokens.append((current_token, current_type))

        return tokens

    @classmethod
    def _get_char_type(cls, char: str) -> str:
        """Determine the type of a character."""
        # Check Hindi punctuation BEFORE general Devanagari (since they overlap)
        if char in '।॥':
            return 'hindi_punct'
        elif char in NUMERALS:
            return 'number'
        elif cls.is_devanagari(char):
            return 'hindi'
        elif char.isalpha():
            return 'english'
        elif char.isdigit():
            return 'number'
        elif char.isspace():
            return 'whitespace'
        elif char in '.,;:?!\'"':
            return 'punctuation'
        elif char in '()-':
            return 'bracket'
        else:
            return 'other'


# =============================================================================
# SECTION 3: SYLLABLE PARSER
# =============================================================================

class SyllableParser:
    """Parses Hindi text into syllables for proper processing."""

    CONSONANT = set(CONSONANTS.keys())
    VOWEL = set(VOWELS.keys())
    MATRA = set(MATRAS.keys())
    HALANT = '्'
    NUKTA = '़'
    ANUSVARA = 'ं'
    CHANDRABINDU = 'ँ'
    VISARGA = 'ः'

    @classmethod
    def parse_word(cls, word: str) -> List[dict]:
        """
        Parse a Hindi word into syllable structures.

        Returns list of syllable dicts:
        {
            'consonants': list of consonants (with halants for conjuncts),
            'matra': the vowel sign if any,
            'modifiers': anusvara, chandrabindu, visarga,
            'has_reph': True if there's a reph on this syllable,
            'has_rakar': True if there's a rakar (subscript r),
            'original': original text consumed,
        }
        """
        syllables = []
        i = 0
        n = len(word)

        while i < n:
            syllable = {
                'consonants': [],
                'matra': None,
                'modifiers': [],
                'has_reph': False,
                'has_rakar': False,
                'original': '',
            }

            start_i = i

            # Check for Reph (र् at the start, followed by another consonant)
            if (i + 1 < n and word[i] == 'र' and word[i + 1] == cls.HALANT):
                if i + 2 < n and word[i + 2] in cls.CONSONANT:
                    syllable['has_reph'] = True
                    i += 2  # Skip र्

            # Collect consonants (with halants between them)
            while i < n:
                char = word[i]

                # Handle nukta
                if char == cls.NUKTA:
                    if syllable['consonants']:
                        syllable['consonants'][-1] += char
                    i += 1
                    continue

                if char in cls.CONSONANT:
                    # Handle reph-like sequence inside a cluster (e.g. धर्म, कर्म):
                    # consonant + र् + consonant → attach reph at syllable end
                    if (
                        char == 'र'
                        and i + 2 < n
                        and word[i + 1] == cls.HALANT
                        and word[i + 2] in cls.CONSONANT
                        and syllable['consonants']
                    ):
                        syllable['has_reph'] = True
                        i += 2  # Skip र् and keep parsing remaining cluster
                        continue

                    syllable['consonants'].append(char)
                    i += 1

                    # Check for halant (conjunct formation)
                    if i < n and word[i] == cls.HALANT:
                        # Check if next char is a consonant (forming conjunct)
                        if i + 1 < n and word[i + 1] in cls.CONSONANT:
                            # Check for rakar (्र)
                            if word[i + 1] == 'र':
                                # Check if र is followed by a matra (then it's rakar)
                                # or if it's end of word (rakar)
                                if i + 2 >= n or word[i + 2] not in cls.CONSONANT:
                                    syllable['has_rakar'] = True
                                    i += 2  # Skip ्र
                                    break
                            syllable['consonants'][-1] += cls.HALANT
                            i += 1
                        else:
                            # Explicit halant at end of syllable/word
                            syllable['consonants'][-1] += cls.HALANT
                            i += 1
                            break
                else:
                    break

            # Check for independent vowel (if no consonants collected)
            if not syllable['consonants'] and i < n and word[i] in cls.VOWEL:
                syllable['consonants'].append(word[i])  # Treat as base
                i += 1

            # Collect matra
            if i < n and word[i] in cls.MATRA:
                syllable['matra'] = word[i]
                i += 1

            # Collect modifiers
            while i < n and word[i] in (cls.ANUSVARA, cls.CHANDRABINDU, cls.VISARGA):
                syllable['modifiers'].append(word[i])
                i += 1

            syllable['original'] = word[start_i:i]

            if syllable['consonants'] or syllable['matra'] or syllable['modifiers']:
                syllables.append(syllable)
            elif i < n:
                # Unknown character, advance
                syllables.append({
                    'consonants': [word[i]],
                    'matra': None,
                    'modifiers': [],
                    'has_reph': False,
                    'has_rakar': False,
                    'original': word[i],
                })
                i += 1

        return syllables


# =============================================================================
# SECTION 4: MAPPER (Character → Kruti Dev)
# =============================================================================

class Mapper:
    """Maps Unicode characters to Kruti Dev equivalents."""

    @classmethod
    def map_consonant(cls, consonant: str, is_half: bool = False) -> str:
        """Map a consonant to Kruti Dev."""
        # Check for nukta
        if consonant.endswith('़'):
            base = consonant[:-1]
            full = base + '़'
            if full in NUKTA_CONSONANTS:
                return NUKTA_CONSONANTS[full]
            result = cls.map_consonant(base, is_half)
            return result + '+'

        # Check if it's a half-form (ends with halant)
        if consonant.endswith('्'):
            base = consonant[:-1]
            if base in HALF_FORMS:
                return HALF_FORMS[base]
            elif base in CONSONANTS:
                return CONSONANTS[base] + '~'
            return consonant

        if is_half and consonant in HALF_FORMS:
            return HALF_FORMS[consonant]

        if consonant in CONSONANTS:
            return CONSONANTS[consonant]

        if consonant in VOWELS:
            return VOWELS[consonant]

        return consonant

    @classmethod
    def map_matra(cls, matra: str) -> str:
        """Map a matra to Kruti Dev."""
        return MATRAS.get(matra, matra)

    @classmethod
    def map_modifier(cls, modifier: str) -> str:
        """Map a modifier to Kruti Dev."""
        return MODIFIERS.get(modifier, modifier)

    @classmethod
    def map_numeral(cls, numeral: str) -> str:
        """Map a numeral to Kruti Dev."""
        return NUMERALS.get(numeral, numeral)

    @classmethod
    def map_punctuation(cls, punct: str) -> str:
        """Map punctuation to Kruti Dev."""
        return PUNCTUATION.get(punct, punct)


# =============================================================================
# SECTION 5: SYLLABLE RENDERER
# =============================================================================

class SyllableRenderer:
    """Renders parsed syllables to Kruti Dev encoding."""

    @classmethod
    def render(cls, syllable: dict) -> str:
        """
        Render a syllable to Kruti Dev.

        Handles:
        - Matra 'i' (ि) positioning — must come BEFORE consonant cluster
        - Reph (र्) positioning — must come AFTER syllable in Kruti Dev
        - Rakar (्र) handling
        - Special ri-matra (ृ) conjuncts for क, द, ह
        """
        result_parts = []

        # Check for 'i' matra (ि) — must be placed BEFORE the consonant cluster
        i_matra = syllable['matra'] == 'ि'
        if i_matra:
            result_parts.append('f')  # 'f' is Kruti Dev for ि

        # --------- Special ri-matra conjunct check ---------
        # If the syllable is a single consonant + ृ matra, check for special ligature
        if (
            syllable['matra'] == 'ृ'
            and len(syllable['consonants']) == 1
            and not syllable['consonants'][0].endswith('्')
        ):
            base_consonant = syllable['consonants'][0]
            if base_consonant in RI_MATRA_SPECIAL:
                result_parts.append(RI_MATRA_SPECIAL[base_consonant])
                # Handle rakar
                if syllable['has_rakar']:
                    result_parts.append('z')
                # Handle reph
                if syllable['has_reph']:
                    result_parts.append('Z')
                # Handle modifiers
                for mod in syllable['modifiers']:
                    result_parts.append(Mapper.map_modifier(mod))
                return ''.join(result_parts)

        # --------- Render consonant cluster ---------
        consonants = syllable['consonants']

        # Reconstruct the original Unicode sequence for conjunct matching
        original_cluster = ''.join(consonants)

        # Also try without trailing halant for matching
        cluster_for_match = original_cluster.rstrip('्')

        # Check if the full cluster is a known conjunct
        conjunct_found = False

        # Try to match the cluster against known conjuncts (longest first)
        for conj_unicode, conj_kruti in sorted(
            CONJUNCTS.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if original_cluster == conj_unicode or cluster_for_match == conj_unicode:
                result_parts.append(conj_kruti)
                # Check if original had trailing halant
                if original_cluster.endswith('्') and not conj_unicode.endswith('्'):
                    result_parts.append('~')
                conjunct_found = True
                break

        if not conjunct_found:
            # Try to find partial conjuncts within the cluster
            remaining = original_cluster
            while remaining:
                matched = False
                for conj_unicode, conj_kruti in sorted(
                    CONJUNCTS.items(), key=lambda x: len(x[0]), reverse=True
                ):
                    if remaining.startswith(conj_unicode):
                        result_parts.append(conj_kruti)
                        remaining = remaining[len(conj_unicode):]
                        matched = True
                        break

                if not matched:
                    # No conjunct match, render individual consonant
                    if remaining:
                        if len(remaining) > 1 and remaining[1] == '्':
                            cons = remaining[:2]
                            remaining = remaining[2:]
                        else:
                            cons = remaining[0]
                            remaining = remaining[1:]
                        result_parts.append(Mapper.map_consonant(cons))

        # Handle rakar (subscript र)
        if syllable['has_rakar']:
            result_parts.append('z')  # 'z' is Kruti Dev for rakar

        # Add matra (except 'i' which was already added, and ri-matra for special)
        if syllable['matra'] and not i_matra:
            result_parts.append(Mapper.map_matra(syllable['matra']))

        # Add reph (र्) — comes AFTER the syllable in Kruti Dev
        if syllable['has_reph']:
            result_parts.append('Z')  # 'Z' is Kruti Dev for reph

        # Add modifiers
        for mod in syllable['modifiers']:
            result_parts.append(Mapper.map_modifier(mod))

        return ''.join(result_parts)


# =============================================================================
# SECTION 6: MAIN CONVERTER
# =============================================================================

class MangalToKrutiDevConverter:
    """
    Production-grade Mangal (Unicode) → Kruti Dev 010 converter.

    Features:
    - Word-level tokenization
    - Proper syllable parsing
    - Linguistic-aware matra positioning
    - Reph and rakar handling
    - Conjunct recognition (including special ri-matra ligatures)
    - Mixed language support
    - Verified against unicodetokrutidev.net reference converter
    """

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.parser = SyllableParser()
        self.renderer = SyllableRenderer()

    def convert(self, text: str) -> str:
        """
        Convert Unicode Devanagari text to Kruti Dev encoding.

        Args:
            text: Input text in Unicode (Mangal font)

        Returns:
            Text encoded for Kruti Dev 010 font
        """
        if not text:
            return ""

        segments = self.convert_segments(text)
        return ''.join(segment for segment, _needs_kruti in segments)

    def convert_segments(self, text: str) -> List[Tuple[str, bool]]:
        """
        Convert text and return (segment, needs_kruti_font) tuples.

        needs_kruti_font=True means the segment is Kruti-encoded and should be
        displayed using Kruti Dev 010.
        """
        if not text:
            return []

        text = self._normalize(text)
        tokens = Tokenizer.tokenize(text)
        segments: List[Tuple[str, bool]] = []

        for i, (token, token_type) in enumerate(tokens):
            if token_type == 'hindi':
                converted = self._convert_hindi(token)
                self._append_segment(segments, converted, True)
            elif token_type == 'hindi_punct':
                converted = self._convert_hindi_punct(token)
                self._append_segment(segments, converted, True)
            elif token_type == 'number':
                converted = self._convert_number(token)
                has_devanagari_numerals = any(char in NUMERALS for char in token)
                self._append_segment(segments, converted, has_devanagari_numerals)
            elif token_type in ('bracket', 'punctuation'):
                if self._is_hindi_context(tokens, i):
                    converted = self._convert_punctuation(token)
                    self._append_segment(segments, converted, True)
                else:
                    self._append_segment(segments, token, False)
            elif token_type in ('english', 'whitespace'):
                self._append_segment(segments, token, False)
            else:
                self._append_segment(segments, token, False)

        return segments

    def _normalize(self, text: str) -> str:
        """Normalize text before processing."""
        # Normalize special dashes to regular hyphen
        text = text.replace('\u2013', '-')   # En-dash → hyphen
        text = text.replace('\u2014', '-')   # Em-dash → hyphen
        text = text.replace('\u2212', '-')   # Minus sign → hyphen
        text = text.replace('\u2010', '-')   # Hyphen Unicode → ASCII hyphen
        text = text.replace('\u2011', '-')   # Non-breaking hyphen → hyphen

        # Normalize quotes
        text = text.replace('\u2018', "'")   # Left single quote → apostrophe
        text = text.replace('\u2019', "'")   # Right single quote → apostrophe
        text = text.replace('\u201C', '"')   # Left double quote → quote
        text = text.replace('\u201D', '"')   # Right double quote → quote

        # Handle decomposed nukta forms
        nukta = '\u093C'
        text = text.replace('क' + nukta, 'क़')
        text = text.replace('ख' + nukta, 'ख़')
        text = text.replace('ग' + nukta, 'ग़')
        text = text.replace('ज' + nukta, 'ज़')
        text = text.replace('ड' + nukta, 'ड़')
        text = text.replace('ढ' + nukta, 'ढ़')
        text = text.replace('फ' + nukta, 'फ़')
        text = text.replace('य' + nukta, 'य़')

        # Remove zero-width characters
        text = text.replace('\u200B', '')     # Zero-width space
        text = text.replace('\u200C', '')     # Zero-width non-joiner
        text = text.replace('\u200D', '')     # Zero-width joiner
        text = text.replace('\uFEFF', '')     # BOM

        return text

    def _convert_hindi(self, word: str) -> str:
        """Convert a Hindi word to Kruti Dev."""
        # Sort conjuncts by length (longest first) to avoid partial matches
        sorted_conjuncts = sorted(
            CONJUNCTS.items(), key=lambda x: len(x[0]), reverse=True
        )

        result = word

        # Replace conjuncts with temporary markers
        markers = {}
        marker_idx = 0
        for conj_unicode, conj_kruti in sorted_conjuncts:
            if conj_unicode in result:
                marker = f'\uE000{marker_idx}\uE001'
                markers[marker] = conj_kruti
                result = result.replace(conj_unicode, marker)
                marker_idx += 1

        # Split by markers and process each part
        parts = re.split(r'(\uE000\d+\uE001)', result)

        output_parts = []
        for part in parts:
            if part.startswith('\uE000') and part.endswith('\uE001'):
                output_parts.append(markers[part])
            elif part:
                syllables = SyllableParser.parse_word(part)
                for syllable in syllables:
                    output_parts.append(SyllableRenderer.render(syllable))

        return ''.join(output_parts)

    def _convert_hindi_punct(self, punct: str) -> str:
        """Convert Hindi punctuation."""
        result = []
        for char in punct:
            result.append(Mapper.map_punctuation(char))
        return ''.join(result)

    def _convert_punctuation(self, punct: str) -> str:
        """Convert ASCII punctuation to Kruti Dev equivalents."""
        result = []
        for char in punct:
            result.append(PUNCTUATION_MAP.get(char, char))
        return ''.join(result)

    def _convert_number(self, token: str) -> str:
        """Convert Devanagari numerals while preserving ASCII digits."""
        return ''.join(Mapper.map_numeral(char) for char in token)

    def _append_segment(
        self,
        segments: List[Tuple[str, bool]],
        text: str,
        needs_kruti: bool,
    ) -> None:
        """Append segment and merge with previous segment when possible."""
        if not text:
            return
        if segments and segments[-1][1] == needs_kruti:
            prev_text, prev_needs_kruti = segments[-1]
            segments[-1] = (prev_text + text, prev_needs_kruti)
            return
        segments.append((text, needs_kruti))

    def _is_hindi_context(
        self, tokens: List[Tuple[str, str]], index: int
    ) -> bool:
        """
        Determine if punctuation is in Hindi context.
        Context search skips whitespace runs (common in DOCX).
        """
        prev_index = index - 1
        while prev_index >= 0 and tokens[prev_index][1] == 'whitespace':
            prev_index -= 1

        next_index = index + 1
        while next_index < len(tokens) and tokens[next_index][1] == 'whitespace':
            next_index += 1

        prev_is_hindi = (
            prev_index >= 0 and self._token_uses_hindi_font(tokens[prev_index])
        )
        next_is_hindi = (
            next_index < len(tokens)
            and self._token_uses_hindi_font(tokens[next_index])
        )
        return prev_is_hindi or next_is_hindi

    def _token_uses_hindi_font(self, token_data: Tuple[str, str]) -> bool:
        """Check if a token belongs to Hindi/Kruti context."""
        token, token_type = token_data
        if token_type in ('hindi', 'hindi_punct'):
            return True
        if token_type == 'number':
            return any(char in NUMERALS for char in token)
        return False


# =============================================================================
# SECTION 7: LEGACY INTERFACE (for compatibility with DocxConverter)
# =============================================================================

class ReorderEngine:
    """Legacy interface for compatibility with existing code."""

    def __init__(self):
        self.converter = MangalToKrutiDevConverter()

    def process(self, text: str) -> str:
        """Convert Unicode Devanagari to Kruti Dev 010."""
        return self.converter.convert(text)

    def process_segments(self, text: str) -> List[Tuple[str, bool]]:
        """Convert and return segment metadata for selective font assignment."""
        return self.converter.convert_segments(text)


# =============================================================================
# SECTION 8: SELF-TEST (verified against unicodetokrutidev.net)
# =============================================================================

def run_tests():
    """Run test cases to validate conversion against reference converter."""
    converter = MangalToKrutiDevConverter()

    # (Input, Expected output from reference converter, Description)
    test_cases = [
        ('भारत', 'Hkkjr', 'Simple word'),
        ('हिंदी', 'fganh', 'Word with i-matra and anusvara'),
        ('नमस्ते', 'ueLrs', 'Word with conjunct'),
        ('एक', ',d', 'Independent vowel ए + consonant'),
        ('ऐसा', ',slk', 'Independent vowel ऐ + consonant'),
        ('कैसे', 'dSls', 'Consonant with ै matra'),
        ('हैं', 'gSa', 'ह + ै + anusvara'),
        ('है', 'gS', 'ह + ै'),
        ('मैं', 'eSa', 'म + ै + anusvara'),
        ('आप', 'vki', 'Independent vowel आ'),
        ('सरकार', 'ljdkj', 'Multi-syllable word'),
        ('परीक्षण', 'ijh{k.k', 'Word with conjunct क्ष'),
        ('वाक्य', 'okD;', 'Word with half-form'),
        ('स्कूल', 'Ldwy', 'Conjunct + uu matra'),
        ('प्रदेश', "çns'k", 'प्र conjunct + श'),
        ('शिक्षा', "f'k{kk", 'श with i-matra + क्ष conjunct'),
        ('विद्यार्थी', 'fo|kFkhZ', 'Complex word with reph'),
        ('राष्ट्र', 'jk"Vª', 'Word with rakar'),
        ('द्वार', '}kj', 'द्व conjunct'),
        ('उत्तर', 'mÙkj', 'त्त conjunct'),
        ('कृष्ण', '\u2014".k', 'Special ri-matra कृ'),
        ('धर्म', '/keZ', 'Word with reph'),
        ('कर्म', 'deZ', 'Word with reph'),
        ('प्रेम', 'çse', 'प्र conjunct + e matra'),
        ('शुक्रवार', "'kqØokj", 'श + u matra + क्र conjunct'),
        ('ड़', 'M+', 'Nukta consonant'),
        ('ढ़', '<+', 'Nukta consonant'),
        ('ऋषि', '_f"k', 'Independent vowel ऋ'),
        ('इस', 'bl', 'Independent vowel इ'),
        ('उस', 'ml', 'Independent vowel उ'),
        ('अब', 'vc', 'Independent vowel अ'),
        ('राम', 'jke', 'Simple word'),
        ('में', 'esa', 'म + े + anusvara'),
    ]

    print("=" * 70)
    print("MANGAL TO KRUTI DEV 010 CONVERTER — AUTOMATED TESTS")
    print("Reference: unicodetokrutidev.net")
    print("=" * 70)

    pass_count = 0
    fail_count = 0
    for input_text, expected, description in test_cases:
        output = converter.convert(input_text)
        if output == expected:
            status = 'PASS'
            pass_count += 1
        else:
            status = 'FAIL'
            fail_count += 1

        print(f"\n{status}: {description}")
        print(f"  Input:    {input_text}")
        print(f"  Output:   {output}")
        if status == 'FAIL':
            print(f"  Expected: {expected}")

    print("\n" + "=" * 70)
    print(f"Results: {pass_count} passed, {fail_count} failed, "
          f"{len(test_cases)} total")
    print("=" * 70)

    return fail_count == 0


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
