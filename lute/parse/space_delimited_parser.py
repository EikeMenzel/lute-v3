"""
Parsing for space-delimited languages.

The parser uses some Language settings (e.g., word characters) to
perform the actual parsing.
"""

import re
from typing import List
from lute.models.language import Language
from lute.parse.base import ParsedToken, AbstractParser


class SpaceDelimitedParser(AbstractParser):
    """
    A general parser for space-delimited languages,
    such as English, French, Spanish ... etc.
    """

    def get_parsed_tokens(self, text: str, lang: Language) -> List[ParsedToken]:
        return self.parse_to_tokens(text, lang)

    def preg_match_capture(self, pattern, subject):
        matches = re.finditer(pattern, subject, flags=re.IGNORECASE)
        result = [[match.group(), match.start()] for match in matches]
        return result

    def parse_to_tokens(self, text: str, lang: Language):
        replacements = lang.character_substitutions.split("|")
        for replacement in replacements:
            fromto = replacement.strip().split("=")
            if len(fromto) >= 2:
                rfrom = fromto[0].strip()
                rto = fromto[1].strip()
                text = text.replace(rfrom, rto)

        text = text.replace("\r\n", "\n")
        text = text.replace('{', '[')
        text = text.replace('}', ']')

        tokens = []
        paras = text.split("\n")
        pcount = len(paras)
        for i, para in enumerate(paras):
            self.parse_para(para, lang, tokens)
            if i != (pcount - 1):
                tokens.append(ParsedToken('¶', False, True))

        return tokens

    def parse_para(self, text: str, lang: Language, tokens: List[ParsedToken]):
        termchar = lang.word_characters
        split_sentence = re.escape(lang.regexp_split_sentences)
        splitex = lang.exceptions_split_sentences.replace('.', '\\.')
        m = self.preg_match_capture(fr"({splitex}|[{termchar}]*)", text)
        wordtoks = list(filter(lambda t: t[0] != "", m))

        def add_non_words(s):
            if not s:
                return
            pattern = f"[{split_sentence}]"
            allmatches = self.preg_match_capture(pattern, s)
            has_eos = len(allmatches) > 0
            tokens.append(ParsedToken(s, False, has_eos))

        pos = 0
        for wt in wordtoks:
            w = wt[0]
            wp = wt[1]
            s = text[pos:wp]
            add_non_words(s)
            tokens.append(ParsedToken(w, True, False))
            pos = wp + len(w)

        s = text[pos:]
        add_non_words(s)
