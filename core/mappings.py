
# Detailed Unicode to Kruti Dev 010 (Remington) Mapping
# This mapping includes base chars, matras, and common conjuncts.

# 1. Base Mapping (Direct one-to-one for independent chars)
UNICODE_TO_KRUTIDEV_MAP = {
    # Vowels (Swar)
    'अ': 'v', 'आ': 'vk', 'इ': 'b', 'ई': 'bZ', 'उ': 'm', 'ऊ': 'Å',
    'ए': ',s', 'ऐ': ',ks', 'ओ': 'vks', 'औ': 'vkS',
    'ऋ': '_.KR', # Placeholder, handled in logic?
    
    # Consonants (Vyanjan)
    'क': 'd', 'ख': '[k', 'ग': 'x', 'घ': '?k', 'ङ': '³',
    'च': 'p', 'छ': 'N', 'ज': 't', 'झ': 'Ö', 'ञ': '¥',
    'ट': 'V', 'ठ': 'B', 'ड': 'M', 'ढ': '<', 'ण': '.k',
    'त': 'r', 'थ': 'Fk', 'द': 'n', 'ध': '/k', 'न': 'u',
    'प': 'i', 'फ': 'Q', 'ब': 'c', 'भ': 'Hk', 'म': 'e',
    'य': ';', 'र': 'j', 'ल': 'y', 'व': 'o',
    'श': "'k", 'ष': '\"k', 'स': 'l', 'ह': 'g',
    
    # Nukta Consonants (Consonant + Nukta ़)
    # These are precomposed or decomposed forms
    'क़': 'क़', # Pass-through if using special font? Or map to 'd]' ?
    'ख़': '[+k', # Kha with nukta
    'ग़': 'x+', # Ga with nukta
    'ज़': 'T+', # Za (Ja with nukta) - or 'Þ'? Let's use T+
    'ड़': 'ò', # Alt+0242 (ò)
    'ढ़': 'ô', # Alt+0244 or try 'ú' (Alt+0250)?
    'फ़': 'Ý', # Fa (Pha with nukta) - Alt+0221
    '़': '', # Standalone Nukta - remove it (already handled via combined chars)
    
    # Combined / Special
    'क्ष': '{k', 'त्र': '=k', 'ज्ञ': 'K', 'श्र': 'J',
    'श' + '्' + 'र': 'J', # Shra composite
    
    # Matras
    'ा': 'k',
    'ि': 'f', # Special handling for position
    'ी': 'h',
    'ु': 'q',
    'ू': 'w',
    'ृ': 'C',
    'े': 's',
    'ै': 'S',
    'ो': 'ks',
    'ौ': 'kS',
    'ं': 'a', # Anusvara
    'ँ': '¡', # Chandrabindu
    'ः': '%', # Visarga
    '्': '~', # Halant (generic)
    'ॉ': '‚', # Candra O (Alt+0130 -> '‚')
    'ऑ': 'v‚', # Chandra A (A + Candra O)
    
    # Punctuations & Brackets
    '(': '¼', # Alt+0188
    ')': '½', # Alt+0189
    '{': '¼', # Use same? Or check specific
    '}': '½', 
    '[': '¼',
    ']': '½',
    
    # Numerals (often same, but Kruti has no special numerals, uses ASCII digits usually)
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    
    # Punctuation
    '।': 'A', # Danda
    # '.': '-', # Often dot is hyphen? No.
}

# 2. Half Characters (Consonant + Halant)
# These are mapped to the "Half Form" glyph in Kruti.
# If no half form exists, it remains Consonant+Halant (handled by generalized logic).
HALF_CHAR_MAP = {
    'क': 'D',
    'ख': '[',
    'ग': 'X',
    'घ': '?',
    'च': 'P', 
    'छ': 'N',  # Chha usually doesn't have half form like others
    'ज': 'T',
    'झ': 'Ö',  # Check Jha
    'ञ': '¥',
    'ट': 'V',  # Retroflexes usually use explicit halant
    'ठ': 'B',
    'ड': 'M',
    'ढ': '<',
    'ण': '.',
    'त': 'R',
    'थ': 'F',
    'द': 'n',  # Da usually explicit halant or special conjunct
    'ध': '/',
    'न': 'U',
    'प': 'I',
    'फ': 'Q', # Check Pha
    'ब': 'C',
    'भ': 'H',
    'म': 'E',
    'य': '¸', # Alt+0184? No. Usually ';'
              # Wait, standard Kruti for half Ya is 'È' (Alt+0200) or similar?
              # Let's check standar map. 'u' -> na. 'U' -> half na.
              # ';' -> ya. Half ya? Usually involves 'LF' or similar if conjunct.
              # Let's use 'E' for ma, 'H' for bha.
              # For Ya: often just '¨' or similar. 
              # Let's stick to safe ones.
    'ल': 'Y',
    'व': 'O',
    'श': "'",
    'ष': '"',
    'स': 'L',
    'ह': 'g', # No half
    'क्ष': '{',
    'त्र': '=',
    'ज्ञ': 'K', 
}

# 3. Special Conjuncts (Ligatures) rules
# Unicode Sequence -> Kruti Glyph
# e.g. 'Dda' (Double Da) -> 'nn' logic?
# Kruti has specific keys for some:
# Alt+0221 (dd), Alt+0222 (tt) etc.
# We will mapping these explicitly if possible.

CONJUNCTS_MAP = {
    # Da combinations
    "Z": "Z", # Reph/Rakar logic
}
