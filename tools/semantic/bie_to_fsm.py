#!/usr/bin/env python3
# coding: utf-8
"""
bie_to_fsm.py

Generates Foundation Semantic Model (FSM) CSV file from UN/CEFACT CCL BIEs.

Designed by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
Written by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)

Creation Date: 2026-01-13
Last Modified: 2026-02-11

ABOUT THIS SCRIPT
Generate a Foundational Semantic Model (FSM) CSV from UN/CEFACT CCL BIE rows.

This script:
- reads a BIE CSV file (ABIE/ASBIE/BBIE rows, stopping at acronym END),
- assigns internal IDs and levels (Class=level 1, Properties=level 2),
- builds a class registry (object_class_dict) and attaches properties under each class,
  merging duplicate properties and widening multiplicity/concatenating definitions where needed,
- derives candidate abstract (super) classes from underscore-based class naming,
- normalises association targets (associated_class) to registered class terms where possible,
- classifies properties in the flattened FSM output with inheritance status flags:
  Shared / Aligned Pool / Distinct / Inheritance / Modified[...] / Aligned / Prohibited,
- outputs a flattened FSM CSV.

PROCESSING POLICY:
1. IDENTIFICATION: Assigns unique internal IDs (e.g., GE0001) and levels (Class=1, Properties=2).
2. NORMALIZATION: Strips contextual acronyms (AAA, CI, etc.) and "Specified" tokens from terms.
3. SEMANTIC MERGING: Consolidates duplicate property terms by widening multiplicity (e.g., 0..1 + 1..1 = 0..1)
   and concatenating distinct definitions.
4. INHERITANCE DERIVATION: 
   - Uses underscore-based naming (e.g., "SPS_ Contact") to automatically build sup_class chains.
   - Promotes "In All Contexts" classes with sufficient properties to "Super Class" status.
5. CLASSIFICATION: Flags properties as Shared, Aligned Pool, Distinct, Inheritance, or Prohibited
   based on their relationship to the derived super_classes.

(c) 2026 SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
MIT License

"""
from __future__ import annotations

import os
import argparse
import sys
import csv
import re
import copy
from collections import OrderedDict, Counter
from collections.abc import Mapping, Sequence
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Tuple, Optional, TextIO
from datetime import datetime

# ----------------------------------------------------------------------
# Configuration defaults
# ----------------------------------------------------------------------

# Default list of contextual acronyms to remove (whole-word matches)
DEFAULT_CONTEXT = [
    "AAA (Accounting And Audit)",
    "AAA", "CI", "CICH", "CICL", "CIDDH", "CIDDL", "CIIH", "CIIL", "CIILB",
    "CIOH", "CIORH", "CIOL", "CIQ", "CIQH", "CIQL", "CIS", "CISCRL", "CISDFL",
    "CISDRL", "CISH", "CISIFL", "CISSIL", "CISSNL", "CIR", "CIRH", "CIRL", "CIRT",
    "FA", "IS", "ISR", "MDH", "MDR", "MSDS", "MSI", "RASFF", "SPS", "TMW", "TT", "XHE"
]

# Synonym / unification rules (multi-line friendly):
# These are applied to *each definition line* after context-term removal.
SUBS: List[Tuple[str, str]] = [
    # Collapse adjectives before "referenced/exchanged document":
    # e.g. "this analysis referenced document" -> "this referenced document"
    (r"\bthis\s+(?:[a-z]+\s+)+(referenced|exchanged)\s+document\b", r"this \1 document"),

    # Unify "this exchanged document" / "this referenced document" -> "this document"
    (r"\bthis\s+(?:exchanged|referenced)\s+document\b", "this document"),

    # Unify starts of sentences; (?m) makes ^ apply to each line in multi-line text
    (r"(?m)^(?:the|a|an)\s+code\s+specifying\b", "a code specifying"),

    # Unify article for subtype
    (r"\ba\s+subtype\b", "the subtype"),

    # Identifier wording normalisation
    (r"(?m)^(?:the|a|an)\s+(?:unique\s+)?identifier\s+(?:for|of)\b", "an identifier for"),
    # (r"(?m)^(?:the|a|an)\s+(?:unique\s+)?issuer\s+assigned\s+identifier\s+(?:for|of)\b", "an identifier for"),

    # Collapse adjectives before certificate/document:
    # e.g. "this product batch certificate" -> "this certificate"
    (r"\bthis\s+(?:[a-z]+\s+)+(certificate|document)\b", r"this \1"),

    # Type-of certificate lines:
    # e.g. "type of agricultural certificate" -> "type of this certificate"
    (r"\btype\s+of\s+(?:[a-z]+\s+)+certificate\b", "type of this certificate"),
]

# ----------------------------------------------------------------------
# File safety
# ----------------------------------------------------------------------

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def file_path(pathname):
    _pathname = pathname.replace("/", os.sep)
    if os.sep == _pathname[0:1]:
        return _pathname
    else:
        dir = os.path.dirname(__file__)
        return os.path.join(dir, _pathname)


def is_file_in_use(file_path: str) -> str:
    """
    Check if an output file is writable.

    Returns:
      - "OK"     : file exists and can be opened read/write
      - "IN_USE" : cannot open due to PermissionError (e.g., locked by Excel)
      - "CREATED": file didn't exist; created placeholder successfully
      - "ERROR_CREATING_FILE": failed to create placeholder
    """
    try:
        # r+ requires the file to exist and be writable
        with open(file_path, "r+"):
            return "OK"
    except PermissionError:
        print(f"[ERROR] Output file is in use: {file_path}", file=sys.stderr)
        return "IN_USE"
    except FileNotFoundError:
        # Create a placeholder to validate path & permissions
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w+", encoding="utf-8"):
                pass
            return "CREATED"
        except Exception as e:
            print(f"[ERROR] Could not create output file: {file_path} ({e})", file=sys.stderr)
            return "ERROR_CREATING_FILE"


# ----------------------------------------------------------------------
# String utility
# ----------------------------------------------------------------------

def abbreviate_term(term: str, max_len: int = 6) -> str:
    """
    Abbreviates each word in the input term according to the following rules:

    - Remove common stop_words (e.g., to, with, on, of, etc.).
    - Remove any symbol characters: !"#$%&'()=~|\^-@`[]{}:;+*/?.,<>\_
    - Capitalize the first letter of each remaining word.
    - Keep the first vowel of each word, remove all other vowels.
    - If the abbreviation length is >= max_len:
        - Keep only the first vowel and remove the rest.
        - If the first character is a vowel and the result is still long,
          shorten further (preserving start/end).
    - Ensure the abbreviated word is shorter than the original word.
    - Words of length 3 or less are returned unchanged.
    """
    if max_len < 4:
        raise ValueError("max_len must be >= 4 to allow meaningful abbreviation.")

    stop_words = {
        'a', 'an', 'the',
        'to', 'with', 'on', 'of', 'in', 'for', 'at', 'by', 'from', 'as',
        'about', 'into', 'over', 'after', 'under', 'above', 'below'
    }
    vowels = 'aeiouAEIOU'

    # Remove symbols
    term = re.sub(r'[!"#$%&\'()=~|\\^\-@`\[\]{}:;+*/?,.<>\_]', '', term)

    def abbreviate_word(word: str) -> str:
        if len(word) <= 3:
            return word  # already short

        chars = [word[0]]  # keep first character
        first_vowel_found = word[0] in vowels

        # Keep consonants; keep only the first vowel encountered (if any)
        for c in word[1:]:
            if c.lower() not in vowels:
                chars.append(c)
            elif not first_vowel_found:
                chars.append(c)
                first_vowel_found = True

        abbr = ''.join(chars)

        # If abbreviation is still too long, remove all vowels except the first vowel
        if len(abbr) >= max_len:
            first_vowel_index = next((i for i, c in enumerate(abbr) if c.lower() in vowels), None)
            if first_vowel_index is not None:
                abbr = ''.join(
                    abbr[i] for i in range(len(abbr))
                    if abbr[i].lower() not in vowels or i == first_vowel_index
                )

            # If the first character is a vowel and abbreviation is still long,
            # preserve the start and end
            if abbr and abbr[0].lower() in vowels and len(abbr) > max_len:
                # keep (max_len-1) prefix + last char
                abbr = abbr[:max_len - 1] + abbr[-1]

        # Final fallback: truncate if still too long
        if len(abbr) > max_len:
            abbr = abbr[:max_len]

        # Must be shorter than original (otherwise return original word)
        return abbr if len(abbr) < len(word) else word

    # Tokenize and filter stop_words
    words = re.findall(r'\w+', term)
    filtered = [w.capitalize() for w in words if w.lower() not in stop_words]

    # Abbreviate remaining words
    abbreviated = [abbreviate_word(w) for w in filtered]
    return ' '.join(abbreviated)


def LC3(term):
    """
    Lower camel case converter (e.g., 'Entity Phone Number' → 'entityPhoneNumber')
    """
    parts = re.split(r'\s+', term.strip())
    return parts[0].lower() + ''.join(p.title() for p in parts[1:])


def split_camel_case(identifier):
    """
    Split camelCase or CamelCase into a list of words,
    allowing numbers and symbols to remain within each chunk.
    Splitting occurs at capital letters.
    """
    # term = re.findall(r'[^A-Z]*[A-Z][^A-Z]*', identifier)
    term = re.findall(r'[A-Z]?[a-z]+(?:[0-9]+)?|[A-Z]+(?:[0-9]+)?(?![a-z])', identifier)
    if not term:
        term = [identifier]
    return term


def normalize_text(text):
    # Remove (choice) or (sequence), including preceding space
    text = re.sub(r'\s*\((choice|sequence)\)', '', text, flags=re.IGNORECASE)
    # string to contain only alphanumeric characters (A–Z, a–z, 0–9)
    text = re.sub(r'[^A-Za-z0-9]+', ' ', text).strip()
    # Replace multiple spaces with a single space and trim leading/trailing spaces
    text = re.sub(r'\s+', ' ', text)
    return text


# ----------------------------------------------------------------------
# Text normalisation helpers
# ----------------------------------------------------------------------

def remove_context_terms(text: str, context_terms: List[str]) -> str:
    """
    Remove contextual terms (acronyms / labels) from free text.

    This function supports terms that are not single "words" (e.g. terms containing
    spaces or punctuation such as "AAA (Accounting And Audit)"), so it does NOT rely
    on \\b word-boundaries. Instead it uses lookarounds:
        (?<!\\w)  TERM  (?!\\w)
    meaning "TERM is not immediately preceded/followed by a word character"
    (word character = [A-Za-z0-9_]).

    Why:
      - "\\bAAA\\b" fails to match terms that end with ")" etc.
      - Lookarounds still avoid partial matches (e.g. won't remove AAA inside "AAAX").

    Example:
      "The set of parameters linked with this AAA (Accounting And Audit) archive."
        -> "The set of parameters linked with this archive."
    """
    if not text:
        return text

    out = text

    # Longest-first avoids partial removals when one term is a prefix of another
    # (e.g. "CI" inside "CIORH").
    for t in sorted(context_terms, key=len, reverse=True):
        # Match the term only when it is not part of a larger word token.
        # This works even if the term contains spaces/punctuation.
        pat = rf"(?<!\w){re.escape(t)}(?!\w)"
        out = re.sub(pat, "", out)

        # Optional: collapse whitespace after each removal to keep the string tidy
        # and reduce the chance of cascading double-spaces.
        out = re.sub(r"\s{2,}", " ", out).strip()

    # Final tidy pass:
    # - collapse any remaining multiple spaces
    # - remove spaces before punctuation
    # - remove empty parentheses created by deletions: "()" or "(   )"
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+([,.;:])", r"\1", out)
    out = re.sub(r"\(\s*\)", "", out)
    out = re.sub(r"\s{2,}", " ", out).strip()

    return out


def tidy_separators(s: str, slash_mode: str = "space") -> str:
    """
    Normalise separators in a term/phrase.

    - Removes trailing underscores used as word markers:
        "Order_" -> "Order"
    - Treats "/" as a separator:
        slash_mode="space" -> replace with one space
        slash_mode="keep"  -> normalise to " / "

    Note:
      This is intended for label-like strings (property_term etc.).
      Do not apply to identifiers like "GE5004_001" unless desired.
    """
    if not s:
        return s

    # Remove trailing '_' that are used for spacing in some term formats
    s = re.sub(r"(?<=\w)_\b", "", s)

    # Normalise slash spacing or replace with space
    if slash_mode == "keep":
        s = re.sub(r"\s*/\s*", " / ", s)
    else:
        s = re.sub(r"\s*/\s*", " ", s)

    # Collapse whitespace
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def remove_specified_keep_single(s: str) -> str:
    s0 = (s or "").strip()
    if not s0:
        return s0
    # If it's exactly "Specified", keep it
    if re.fullmatch(r"specified", s0, flags=re.IGNORECASE):
        return "Specified"
    # Otherwise remove the word Specified (whole word)
    s1 = re.sub(r"\bSpecified\b", "", s0, flags=re.IGNORECASE)
    s1 = re.sub(r"\s{2,}", " ", s1).strip()
    # If removal made it empty, keep one Specified
    return s1 if s1 else "Specified"


def clean_property_term(s: str, context_terms: List[str]) -> str:
    """
    Clean a property_term value.

    Steps:
      1) Remove contextual acronyms
      2) Remove token "Specified"
      3) Normalise separators: remove trailing "_" and treat "/" as separator

    Example:
      "Marketplace Order_ Referenced_ CI / Referenced"
        -> "Marketplace Order Referenced Referenced" (CI removed; "/" spaced; "_" removed)
    """
    if not s:
        return s

    s = remove_context_terms(s, context_terms)
    # s = re.sub(r"\bSpecified\b", "", s, flags=re.IGNORECASE)
    s = remove_specified_keep_single(s)
    s = tidy_separators(s, slash_mode="space")
    return s


def normalise_definition_line(s: str, context_terms: List[str]) -> str:
    """
    Normalise a single definition line (not an entire multi-line cell).

    Steps:
      1) Remove contextual terms
      2) Apply synonym/unification regex rules (SUBS)
      3) Tidy separators and punctuation
      4) Ensure trailing period

    Returns the normalised line.
    """
    s = (s or "").strip()
    if not s:
        return ""

    # Remove context terms first to simplify matching
    s = remove_context_terms(s, context_terms)

    # Apply all unification rules
    for pat, rep in SUBS:
        s = re.sub(pat, rep, s, flags=re.IGNORECASE)

    # Light separator normalisation
    s = tidy_separators(s, slash_mode="space")

    # Punctuation/space tidy
    s = re.sub(r"\s+([,.;:])", r"\1", s).strip()
    s = re.sub(r"\s{2,}", " ", s).strip()

    # Ensure trailing period
    s = s.rstrip(".") + "."
    return s


# ----------------------------------------------------------------------
# Generic definition logic (mode + LCS fallback)
# ----------------------------------------------------------------------

def tokenise(s: str) -> List[str]:
    """
    Tokenise a sentence into lowercase word tokens.
    Used for word-level LCS computation.
    """
    return re.findall(r"[A-Za-z0-9']+", s.lower())


def lcs_tokens(a: List[str], b: List[str]) -> List[str]:
    """
    Compute a word-level LCS (Longest Common Subsequence) approximation using difflib blocks.
    Good enough for short, similar definition lines.

    Returns the list of common tokens in order.
    """
    sm = SequenceMatcher(a=a, b=b)
    out: List[str] = []
    for block in sm.get_matching_blocks():
        out.extend(a[block.a: block.a + block.size])
    return out


# ----------------------------------------------------------------------
# Processor for conversion
# ----------------------------------------------------------------------

class Processor:
    def __init__(
            self,
            bie_file,
            fsm_file,
            encoding,
            trace,
            debug
        ):
        """
        Initializes the Processor with file paths and configurations.
        """
        self.bie_file = file_path(bie_file)
        if not bie_file or not os.path.isfile(self.bie_file):
            print(f'[INFO] No input Business Entity Model (MBIE/RBIE) file {self.bie_file}.')
            sys.exit()

        self.fsm_file = fsm_file.replace('/', os.sep)
        self.fsm_file = file_path(self.fsm_file)
        if 'IN_USE' == is_file_in_use(self.fsm_file):
            print(f'[INFO] Foundation Semantic Model (FSM) file {self.fsm_file} is **IN USE**.')
            sys.exit()

        self.encoding = encoding if encoding else "utf-8-sig"
        self.TRACE = trace
        self.DEBUG = debug

        self.GROUPS = 4 # Characters for id of class
        self.MEMBERS = 3 # Characters for id of property
        self.AT_LEAST = 1 # Inherited number
        self.MORE_THAN = 9 # Inherited number
        self.DEFAULT_CODE = "UCF"

        # Define CSV headers for internal processing and final FSM output
        self.bie_header = ['sequence', 'UNID', 'acronym', 'DEN', 'definition', 'class_term_qualifier', 'class_term', 'property_term_qualifier', 'property_term', 'datatype_qualifier', 'representation_term', 'qualified_data_type_UID', 'associated_class_qualifier', 'associated_class', 'business_term', 'usage_rule', 'sequence_number', 'occurrence_min', 'occurrence_max', 'context_categories', 'TDED', 'publication_source', 'short_name', 'BIE']
        self.header  = ['sequence', 'level', 'property_type', 'identifier', 'class_term', 'property_term', 'representation_term', 'associated_class', 'multiplicity', 'definition', 'context', 'short_name', 'UNID', 'TDED']
        self.out_header = ['sequence', 'level', 'property_type', 'identifier', 'class_term', 'property_term', 'representation_term', 'associated_class', 'multiplicity', 'definition', 'code', 'context', 'short_name', 'UNID', 'id', 'extension', 'inherited', 'group', 'TDED']

        #  Initialize dictionaries and lists
        self.domain_dict = None

        self.object_class_dict = None

        self.current_context = None
        self.code_num = {}
        self.cl_code = None
        self.current_class_term = None
        self.current_class_term = None
        self.class_num = None
        # self.super_classes = set()

        self.TDED_list = []
        self.LIFO_list = []
        self.FSM_list = []
        self.records = []

        self.context_dict = {
			"Accounting Chart of Accounts": {"ab2":"AC", "ab3": "aco"},
			"Accounting, audit": {"ab2":"AA", "ab3": "aau"},
			"Accounting, audit and reporting": {"ab2":"AR", "ab3": "aar"},
			"Acknowledgement": {"ab2":"AK", "ab3": "ack"},
			"Acquisition": {"ab2":"AQ", "ab3": "acq"},
			"Agricultural": {"ab2":"AG", "ab3": "agr"},
			"Agriculture": {"ab2":"AG", "ab3": "agc"},
			"Buy Ship Pay": {"ab2":"BP", "ab3": "bsp"},
			"Buy-Ship-Pay":	{"ab2":"BP", "ab3": "bsp"},
			"Cataloguing": {"ab2":"CL", "ab3": "cat"},
			"Cattle Registration": {"ab2":"CR", "ab3": "ctr"},
			"Conformity": {"ab2":"CF", "ab3": "cnf"},
			"Crop Data Sheet": {"ab2":"CS", "ab3": "cds"},
			"Cross Industry": {"ab2":"CI", "ab3": "cix"},
			"Cross Industry Trade": {"ab2":"CT", "ab3": "cit"},
			"Cross-Border": {"ab2":"CB", "ab3": "xbr"},
			"Customer to bank payment initiation": {"ab2":"CP", "ab3": "ctp"},
			"Dangerous Goods": {"ab2":"DG", "ab3": "dgs"},
			"Delivering": {"ab2":"DV", "ab3": "dlv"},
			"Examination Notification": {"ab2":"EN", "ab3": "exn"},
			"FLUX": {"ab2":"FX", "ab3": "flx"},
			"In All Contexts": {"ab2":"IA", "ab3": "iac"},
			"Invoice": {"ab2":"IV", "ab3": "inv"},
			"Invoicing": {"ab2":"IC", "ab3": "ivc"},
			"Laboratory Observation": {"ab2":"LO", "ab3": "lab"},
			"MSDS Reporting": {"ab2":"MR", "ab3": "msd"},
			"Maritime Transportation": {"ab2":"MT", "ab3": "mar"},
			"Market Survey": {"ab2":"MS", "ab3": "mks"},
			"Negotiation": {"ab2":"NG", "ab3": "neg"},
			"Ordering": {"ab2":"OR", "ab3": "ord"},
			"Partner Identification": {"ab2":"PI", "ab3": "pid"},
			"Pricing": {"ab2":"PR", "ab3": "prc"},
			"Procurement": {"ab2":"PC", "ab3": "prm"},
			"Product Registration": {"ab2":"PG", "ab3": "prg"},
			"Project Management": {"ab2":"PM", "ab3": "prj"},
			"Quotation": {"ab2":"QT", "ab3": "quo"},
			"Rapid Alert System": {"ab2":"RA", "ab3": "ras"},
			"Rapid Alert System; MSDS Reporting": {"ab2":"RM", "ab3": "rmr"},
			"Remittance": {"ab2":"RM", "ab3": "rem"},
			"Sanitary and Phytosanitary Measures": {"ab2":"SP", "ab3": "sps"},
			"Scheduling": {"ab2":"SC", "ab3": "sch"},
			"Statistics": {"ab2":"ST", "ab3": "sta"},
			"Supply Chain": {"ab2":"SU", "ab3": "scn"},
			"Sustainability": {"ab2":"SB", "ab3": "sus"},
			"Tendering": {"ab2":"TD", "ab3": "tnd"},
			"Traceability": {"ab2":"TR", "ab3": "trc"},
			"Trade": {"ab2":"TR", "ab3": "trd"},
			"Trade Billing": {"ab2":"TB", "ab3": "tbl"},
			"Trade Finance": {"ab2":"TF", "ab3": "tfn"},
			"Transport": {"ab2":"TP", "ab3": "trn"},
			"Waste Movement": {"ab2":"WM", "ab3": "wmo"},
			"e-Certificate of Origin": {"ab2":"EO", "ab3": "eco"}
        }


    def debug_print(self, text):
        if self.DEBUG:
            print(f"[DEBUG] {text}")


    def trace_print(self, text):
        if self.TRACE or self.DEBUG:
            print(f"[TRACE] {text}")


    def error_print(self, text):
        print(f"<ERROR> {text}")
        sys.exit()


    def print_record(self, record, extra=""):
        self.debug_print(
            f"{record['level']} {record['sequence']} {record['id']} {record['property_type'][:2]} {record['class_term']}. {record['property_term']}. {record['representation_term'] or record['associated_class']} {record['multiplicity']}"
            + extra
        )


    def init_logger(self, inp_file: str, *, echo: bool = False) -> str:
        """
        Initialise logger under: <input_file_dir>/logs/
        Filename: <script_stem>_YYYYMMDD_HHMMSS.log

        Args:
            inp_file: path to the input file (used only to locate its directory)
            echo:     if True, also print each line to stdout

        Returns:
            The log file path as a string.
        """
        inp_path = Path(inp_file).resolve()
        base_dir = inp_path.parent

        # logs subdirectory under input file directory
        log_dir = base_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # script name (fallback to 'interactive')
        script = Path(sys.argv[0]).name if sys.argv and sys.argv[0] else "interactive"
        stem = Path(script).stem or "interactive"

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"{stem}_{ts}.log"

        self._log_path = log_path
        self._log_echo = bool(echo)
        self._log_fh = log_path.open("w", encoding="utf-8", newline="")  # new run => overwrite

        return str(log_path)


    def log_print(self, msg: str, level: str = "INFO") -> None:
        """Write a timestamped log line to the open log file."""
        fh: Optional[TextIO] = getattr(self, "_log_fh", None)
        if fh is None:
            raise RuntimeError("Logger not initialised. Call init_logger(self, inp_file) first.")

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} [{level}] {msg}\n"

        fh.write(line)
        fh.flush()

        if getattr(self, "_log_echo", False):
            print(line, end="")


    def close_logger(self) -> None:
        """Close the open log file handle if present. Safe to call multiple times."""
        fh: Optional[TextIO] = getattr(self, "_log_fh", None)
        if fh is not None:
            try:
                fh.flush()
            finally:
                fh.close()
            self._log_fh = None


    def set_class_term(self, data, record):
        """
        Build `record['class_term']` and `record['code']`.

        UN/CEFACT BIE rows may carry the context code (e.g. CI, CIIH, CCH, CCI)
        either in `class_term_qualifier` OR directly embedded at the start of
        `class_term` (e.g. 'CIIH_ Supply Chain_ Trade Transaction').

        Policy:
        - If a leading ALL-CAPS token (>=2 chars) is found, treat it as `code`.
        - Remove the leading '<CODE>_' (and any following spaces/underscores) from the term.
        - Preserve remaining '_ ' separators, because they are used for superclass chaining:
              'CIIH_ Supply Chain_ Trade Transaction' -> 'Supply Chain_ Trade Transaction'
        - If no code is found, fall back to the original qualifier-based concatenation.
        """
        code_pat = re.compile(r'^([A-Z]{2,})')
        # trim = re.compile(r'^[ _]+')
        c_qualifier = (data.get("class_term_qualifier") or "").strip()
        c_term = (data.get("class_term") or "").strip()

        class_term = f"{c_qualifier}_ {c_term}".strip() if c_qualifier else (c_term or "").strip()

        record["class_term"] = class_term

        cl_code = ""
        # class_term = ""

        # 1) Prefer the explicit qualifier field if it starts with a code.
        m_cq = code_pat.match(c_qualifier)
        if m_cq:
            cl_code = m_cq.group(1).strip().replace("_", "")
        else:
            # 2) Fallback: detect code embedded in the term itself (common in DEN).
            m_ct = code_pat.match(c_term)
            if m_ct and len(c_term) > m_ct.end() and c_term[m_ct.end():].lstrip().startswith("_"):
                cl_code = m_ct.group(1).strip().replace("_", "")
            else:
                # # 3) No code detected -> keep as-is (or prepend any non-code qualifier).
                cl_code = ""

        # record["class_term"] = class_term
        record["code"] = cl_code
        return cl_code, record


    def sepalate_class_term(self, cterm: str) -> Tuple[str, str]:
        """
        Separate a class_term into (prefix, remainder) using the first occurrence of "_ ".

        Examples:
        "CIIH_ Supply Chain_ Trade Transaction" -> ("CIIH", "Supply Chain_ Trade Transaction")
        "CIIL_ Supply Chain_ Trade Line Item"  -> ("CIIL", "Supply Chain_ Trade Line Item")
        "Supply Chain_ Trade Transaction"      -> ("Supply Chain", "Trade Transaction")
        "Trade Transaction"                    -> ("", "Trade Transaction")

        Rules:
        - Split only on the first "_ " (underscore + space).
        - Case A: If the part before "_ " is a context code (2+ [A-Z0-9]), treat it as the prefix.
        - Case B: Otherwise treat the part before "_ " as a domain prefix (e.g., "Supply Chain").
        - If there is no "_ ", return ("", cterm).
        """
        s = (cterm or "").strip()
        if not s:
            return "", ""

        if "_ " not in s:
            return "", s

        head, tail = s.split("_ ", 1)
        head = head.strip()
        tail = tail.strip()

        # context code prefix: e.g., CIIH, CIILB, TMW
        if re.fullmatch(r"[A-Z0-9]{2,}", head):
            return head, tail

        # domain prefix: e.g., "Supply Chain"
        return head, tail


    def set_associated_class(self, data, record):
        """
        Build `record['associated_class']` and set `record['code']` for association keying.

        Similar to set_class_term(), the context code may appear either in
        `associated_class_qualifier` OR embedded at the start of `associated_class`:

            'CIIH_ Supply Chain_ Trade Agreement' -> 'Supply Chain_ Trade Agreement'

        Policy:
        - Prefer qualifier-based parsing when it starts with a code.
        - Otherwise, if the associated_class itself begins with a code followed by '_',
          strip that prefix.
        - Preserve remaining '_ ' separators for superclass chaining.
        """
        code_pat = re.compile(r'^([A-Z]{2,})')
        # trim = re.compile(r'^[ _]+')
        a_qualifier = (data.get("associated_class_qualifier") or "").strip()
        a_term = (data.get("associated_class") or "").strip()

        associated_class = f"{a_qualifier}_ {a_term}".strip() if a_qualifier else (a_term or "").strip()

        record["associated_class"] = associated_class

        as_code = ""
        # 1) Prefer explicit qualifier field.
        m_aq = code_pat.match(a_qualifier)
        if m_aq:
            as_code = m_aq.group(1).strip().replace("_", "")
        else:
            # 2) Fallback: detect code embedded in the term itself.
            m_at = code_pat.match(a_term)
            if m_at and len(a_term) > m_at.end() and a_term[m_at.end():].lstrip().startswith("_"):
                as_code = m_at.group(1).strip().replace("_", "")
            else:
                as_code = ""

        record["code"] = as_code
        return as_code, record


    def get_p_term(self, record):
        """
        Formats the property term based on its type and associated class.
        """
        property_type = record["property_type"]
        property_term = record["property_term"]
        representation_term = record["representation_term"]
        associated_class = record["associated_class"]
        code = record["code"]
        term = None
        if "Class" in property_type:
            term = ''
        elif "Attribute"==property_type:
            term = f"{property_term}. {representation_term}"
        else:
            term = f"{property_term}. {associated_class}"
        return term


    def set_code_num(self, cl_code: str, class_term: str) -> str:
        if cl_code not in self.code_num:
            self.code_num[cl_code] = []
        if not class_term in self.code_num[cl_code]:
            self.code_num[cl_code].append(class_term)
        class_num = 1 + self.code_num[cl_code].index(class_term)
        return class_num


    def populate_record(self, data, seq):
        """
        Transform a BIE-derived row into an internal record and assign an ID/level.

        Current ID scheme:
        - Class rows:      GE####        (#### = per-class index within the hard-coded context "GE")
        - Property rows:   GE####_###    (### increments within the current class)
        - Specialization:  GE####_00     (reserved form; currently not created from BIE input)

        Level:
        - Class -> 1
        - Others -> 2
        """
        def normalize_ws(s: str) -> str:
            return (s or "").replace("\u00A0", " ").replace("\u2007", " ").replace("\u202F", " ")
        
        sequence = int(data["sequence"]) if data["sequence"].isdigit() else data["sequence"]

        if 'ABIE'==data["acronym"]:
            property_type = "Class"
        elif 'ASBIE'==data["acronym"]:
            property_type = "Composition"
        elif 'BBIE'==data["acronym"]:
            property_type = "Attribute"

        property_term = (
            f"{data['property_term_qualifier']}_ {data['property_term']}"
            if data["property_term_qualifier"]
            else data["property_term"]
        )

        representation_term = (
            f"{data['datatype_qualifier']}_ {data['representation_term']}"
            if data["datatype_qualifier"]
            else data["representation_term"]
        )

        multiplicity = (
            (
                f"{data['occurrence_min']}..{'*' if 'unbounded'==data['occurrence_max'] else data['occurrence_max']}"
            )
            if len(data["occurrence_min"]) > 0
            else ""
        )

        record = {
            "sequence": sequence,
            "level": 1 if "Class" in property_type else 2,
            "property_type": property_type,
            "identifier": "",
            "class_term": "",
            "property_term": property_term,
            "representation_term": representation_term,
            "associated_class": "",
            "sequence_number": data["sequence_number"],
            "multiplicity": multiplicity,
            "definition": normalize_ws(data["definition"]),
            "context": data["context_categories"],
            "short_name": data["short_name"],
            "UNID": data["UNID"],
            "acronym": data["acronym"],
            "DEN": data["DEN"],
        }

        tded = data["TDED"] if bool(re.fullmatch(r"\d{4}", data["TDED"])) else ""
        record["TDED"] = tded
        if tded not in self.TDED_list:
            self.TDED_list.append(tded)

        cl_code, record = self.set_class_term(data, record)
        class_term = record["class_term"]
        # class_term is the full class key used in self.object_class_dict:
        #   - if record["code"] is present: f"{record['code']}_ {record['class_term']}"
        #   - otherwise: record["class_term"]    
        property_type = record["property_type"]
        if "Class" in property_type:
            seq = 0
            record["level"] = 1
            self.cl_code = cl_code or ""

            if self.current_class_term != class_term:
                self.class_num = self.set_code_num("", class_term)
            id = f"{self.DEFAULT_CODE}{str(self.class_num).zfill(self.GROUPS)}"
            record["id"] = id

            self.current_class_term = class_term or ""
        else:
            seq += 1
            record["level"] = 2
            if len(data["associated_class"]) > 0:
                as_code, record = self.set_associated_class(data, record)
                # associated_class is the lookup key for the associated class:
                #   - if record["code"] is present: f"{record['code']}_ {record['associated_class']}"
                #   - otherwise: record["associated_class"]
                record["code"] = as_code
            id = f"{self.DEFAULT_CODE}{str(self.class_num).zfill(self.GROUPS)}_{str(seq).zfill(self.MEMBERS)}"
            record["id"] = id

        if "Class" in property_type:
            msg = f"{sequence} {property_type[:4]} {id} '{record['code']}' '{record['class_term']}' "
        else:
            msg = f"{sequence} {property_type[:4]} {id} '{record['code']}' -- '{record['class_term']}. {self.get_p_term(record)}' "

        # self.debug_print(msg)

        return seq, record


    def check_csv_row(self, row):
        """
        Validate an input CSV row.

        Rules:
        1) Mandatory fields:
        - 'acronym', 'class_term' must be present.

        2) Multiplicity:
        - For non-class rows, multiplicity must be one of:
            1, 1..1, 1..*, 0..1, 0..2, 0..*, 0..0, 0

        3) Conditional fields by acronym:
        - Class rows ('Class', 'Super Class', etc.):
            'property_term', 'representation_term', and 'associated_class' must be empty.
        - Attribute rows:
            if multiplicity is not 0 or 0..0, then 'property_term' and 'representation_term' must be present.
        - Association rows (Reference Association, Aggregation, Composition, Specialization):
            'associated_class' must be present.
        """
        status = False
        #  Check for mandatory fields
        for field in ['acronym', 'class_term']:
            if not row.get(field):
                return status, f"Missing mandatory field '{field}'."
            
        if 'ABIE' == row["acronym"]:
            property_type = "Class"
        elif 'ASBIE' == row["acronym"]:
            property_type = "Composition"
        elif 'BBIE' == row["acronym"]:
            property_type = "Attribute"

        multiplicity = (
            f"{row['occurrence_min']}..{'*' if 'unbounded' == row['occurrence_max'] else row['occurrence_max']}"
            if row["occurrence_min"] else ""
        )
        if "Class" not in property_type:
            if not multiplicity or multiplicity not in ["1", "1..1", "1..*", "0..1", "0..2", "0..*", "0..0", "0"]:
                return status, f"Multiplicity '{multiplicity}' is WRONG."

        #  Conditional checks based on 'property_type'
        if "Class" in property_type:
            for field in ['property_term', 'representation_term', 'associated_class']:
                if row.get(field):
                    return status, f"Field '{field}' must be empty for type {property_type}."
        elif "Attribute" in property_type:
            if multiplicity not in ["0..0", "0"]:
                for field in ["property_term", "representation_term"]:
                    if not row.get(field):
                        return status, f"Field '{field}' cannot be empty for type {property_type}."
        else:
            for field in ["associated_class"]:
                if not row.get(field):
                    return status, f"Field '{field}' cannot be empty for type {property_type}'."

        if None in row:
            del row[None]

        status = True
        return status, "Row is valid."


    def deep_diff(self, a, b, path=""):
        """
        Recursively compare two nested Python objects and return a list of differences.

        Supported structures:
        - Mappings (dict-like): compares keys and values recursively
        - Sequences (list/tuple-like): compares length and elements by index recursively
        - Scalars/others: compares by equality

        Args:
            a: Left-hand object to compare.
            b: Right-hand object to compare.
            path (str): Current "address" within the object tree (dot/bracket notation),
                        used to report where a difference occurs (e.g., "root.key[2].name").

        Returns:
            list[tuple[str, Any, Any, str]]:
                A list of diff records: (path, a_value, b_value, kind)

                kind is one of:
                - "type"    : a and b have different Python types at this path
                - "removed" : key exists in a but not in b (mappings only)
                - "added"   : key exists in b but not in a (mappings only)
                - "len"     : sequences have different lengths at this path
                - "value"   : leaf values differ at this path

        Notes / behaviour:
        - For mappings, keys are processed in sorted order for stable output.
        - For sequences, only overlapping indices are compared (via zip). Any extra
            tail elements beyond the shorter length are not individually reported;
            only the "len" difference is recorded.
        - Strings/bytes are treated as scalar values (not sequences) to avoid
            character-by-character comparison.
        """
        diffs = []

        # If types differ, record immediately and stop descending:
        # comparing e.g. dict vs list doesn't make sense structurally.
        if type(a) != type(b):
            diffs.append((path, a, b, "type"))
            return diffs

        # Dict-like objects: detect removed/added keys and recurse for common keys.
        if isinstance(a, Mapping):
            a_keys, b_keys = set(a), set(b)

            # Keys present in a but missing in b.
            for k in sorted(a_keys - b_keys):
                diffs.append((f"{path}.{k}" if path else str(k), a[k], None, "removed"))

            # Keys present in b but missing in a.
            for k in sorted(b_keys - a_keys):
                diffs.append((f"{path}.{k}" if path else str(k), None, b[k], "added"))

            # Keys present in both: recurse into values.
            for k in sorted(a_keys & b_keys):
                subpath = f"{path}.{k}" if path else str(k)
                diffs.extend(self.deep_diff(a[k], b[k], subpath))

            return diffs

        # List/tuple-like objects (but NOT strings/bytes): compare length and recurse by index.
        if isinstance(a, Sequence) and not isinstance(a, (str, bytes, bytearray)):
            if len(a) != len(b):
                diffs.append((path, len(a), len(b), "len"))

            # Compare overlapping indices only.
            for i, (ai, bi) in enumerate(zip(a, b)):
                diffs.extend(self.deep_diff(ai, bi, f"{path}[{i}]"))

            return diffs

        # Scalar / leaf values: record if different.
        if a != b:
            diffs.append((path, a, b, "value"))

        return diffs


    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------

    def mult_max(self, mult: str) -> str:
        """
        Return the max occurrence from a multiplicity string.

        Examples:
        "0..1" -> "1"
        "1..*" -> "*"
        "0"    -> "0"
        "0..0" -> "0"
        "1"    -> "1"
        """
        m = (mult or "").strip()
        if not m:
            return ""
        if m in ("0", "0..0"):
            return "0"
        if ".." in m:
            return m.split("..", 1)[1].strip()
        return m


    def merge_pipe(self, a: str, b: str) -> str:
        """
        Merge two ' | '-separated strings without duplicates, preserving order.
        """
        a = (a or "").strip()
        b = (b or "").strip()
        if not a:
            return b
        if not b:
            return a

        a_items = [x.strip() for x in a.split("|") if x.strip()]
        b_items = [x.strip() for x in b.split("|") if x.strip()]

        out = list(a_items)
        for x in b_items:
            if x not in out:
                out.append(x)
        return " | ".join(out)

    
    def append_def(self, target: str, incoming: str) -> str:
        """
        Append incoming definition as a new line only when it differs from the last line.
        """
        incoming = (incoming or "").strip()
        target = (target or "").strip()

        if not incoming:
            return target
        if not target:
            return incoming

        last_line = target.split("\n")[-1].strip()
        if incoming == last_line:
            return target
        
        cell = (target + "\n" + incoming).strip()
        result = self.generic_definition(cell, DEFAULT_CONTEXT)
    
        return result


    def merge_multiplicity(self, target_mult: str, incoming_mult: str) -> str:
        """
        Widen multiplicity conservatively.

        - If either max is '*', result max is '*'.
        - Otherwise take the larger numeric max.
        - Min becomes '0' if either side is optional (min == '0'), else keep target min.
        """
        t = (target_mult or "").strip()
        i = (incoming_mult or "").strip()
        if not t:
            return i
        if not i:
            return t

        # If both explicitly remove -> keep removed
        if self.mult_max(t) == "0" and self.mult_max(i) == "0":
            return "0..0"

        # mins
        t_min = t.split("..", 1)[0].strip() if ".." in t else t
        i_min = i.split("..", 1)[0].strip() if ".." in i else i

        # maxes
        t_max = self.mult_max(t)
        i_max = self.mult_max(i)

        out_min = "0" if (t_min == "0" or i_min == "0") else t_min

        if t_max == "*" or i_max == "*":
            out_max = "*"
        else:
            try:
                out_max = str(max(int(t_max), int(i_max)))
            except Exception:
                out_max = t_max or i_max

        if out_min == out_max:
            return out_min if out_min in ("0", "1") else f"{out_min}..{out_max}"
        return f"{out_min}..{out_max}"


    def widen_multiplicity(self, existing: str, incoming: str) -> str:
        """
        Widen incoming multiplicity using existing as the dominating constraints
        (same intent as your current code):
        - keep min '0' if either is optional
        - keep '*' if either max is '*'
        - else keep the larger numeric max
        """
        e = (existing or "").strip()
        i = (incoming or "").strip()
        if not e:
            return i
        if not i:
            return e

        e_min = e.split("..", 1)[0] if ".." in e else e
        i_min = i.split("..", 1)[0] if ".." in i else i
        e_max = self.mult_max(e)
        i_max = self.mult_max(i)

        out_min = "0" if (e_min == "0" or i_min == "0") else i_min  # keep optionality

        if e_max == "*" or i_max == "*":
            out_max = "*"
        else:
            try:
                out_max = str(max(int(e_max), int(i_max)))
            except Exception:
                out_max = e_max or i_max

        if out_min == out_max:
            return out_min
        return f"{out_min}..{out_max}"


    def move_in_all_contexts_last(self, s: str) -> str:
        """Move the item 'In All Contexts' to the end and normalise separators.

        Input may contain either '&' or '|' separators. The output uses ' | ' consistently.
        Items are de-duplicated and sorted case-insensitively, except that
        'In All Contexts' (if present) is always placed last.
        """
        s = (s or "").strip()
        if not s:
            return ""

        # Accept both legacy '&' and the current pipe separator.
        raw_items = re.split(r"[&|]", s)
        items = [x.strip() for x in raw_items if x and x.strip()]

        # De-duplicate while preserving first occurrence.
        seen = set()
        deduped = []
        for x in items:
            if x not in seen:
                seen.add(x)
                deduped.append(x)

        # Detect and remove 'In All Contexts' (case-insensitive).
        has_all = any(x.casefold() == "in all contexts" for x in deduped)
        deduped = [x for x in deduped if x.casefold() != "in all contexts"]

        # Alphabetical order (case-insensitive).
        deduped = sorted(deduped, key=lambda t: t.casefold())

        # Append at the end if it existed.
        if has_all:
            deduped.append("In All Contexts")

        return " | ".join(deduped)


    def merge_context(self, a: str, b: str) -> str:
        a = (a or "").strip()
        b = (b or "").strip()
        if not a:
            return b
        if not b:
            return a
        merged = self.merge_pipe(a, b)
        merged = self.move_in_all_contexts_last(merged)
        return merged


    def inc_inherited(self, v) -> int:
        """
        Increment an inherited counter that may be stored as int or str (or be empty/None).

        Examples:
            0        -> 1
            "0"      -> 1
            ""       -> 1
            None     -> 1
            " 2 "    -> 3
            "abc"    -> 1   (fallback)
        """
        if v is None:
            return 1
        if isinstance(v, int):
            return v + 1
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return 1
            try:
                return int(s) + 1
            except ValueError:
                return 1
        # fallback for other types (float, etc.)
        try:
            return int(v) + 1
        except Exception:
            return 1


    def generic_definition(self, cell: str, context_terms: List[str]) -> str:
        """
        Convert a definition cell (possibly multi-line) into ONE generic definition line.

        Rules:
        - Keep 'The' (capital T) as-is.
        - Only replace lowercase 'the' -> 'a' when:
            * the cell is multi-line, AND
            * across lines there is mixed usage: at least one line contains 'the'
            and at least one line contains 'a' or 'an'.
        In this case, always replace with 'a' (never 'an').

        - If a line break occurs immediately before/after a conjunction ('and', 'or'),
        merge those lines into a single line before normalisation.

        Strategy (robust against unrelated multi-line variants):
        - Single line: normalise and return.
        - Multi-line:
            1) merge conjunction-split lines
            2) apply conditional lowercase 'the' -> 'a' (only when mixed usage)
            3) normalise each line
            4) cluster similar lines (near-duplicates) using token Jaccard similarity
            5) pick ONE best line from the largest cluster (mode or consensus)
            6) optionally use LCS only inside a tight cluster, and only if it yields a coherent sentence

        Returns a single sentence, capitalised.
        """

        # ----------------------------
        # Helpers
        # ----------------------------
        def _merge_conjunction_split_lines(lines: List[str]) -> List[str]:
            """
            Merge lines that were split around conjunctions like 'and'/'or'.

            Examples:
            - "foo and" + "bar"        -> "foo and bar"
            - "foo" + "and bar"        -> "foo and bar"
            - "foo" + "and" + "bar"    -> "foo and bar"
            """
            if not lines:
                return []

            merged: List[str] = []
            i = 0
            while i < len(lines):
                cur = lines[i].strip()
                if not cur:
                    i += 1
                    continue

                if cur.lower() in {"and", "or"}:
                    if merged:
                        merged[-1] = (merged[-1].rstrip() + " " + cur).strip()
                    else:
                        merged.append(cur)
                    i += 1
                    continue

                if merged and re.search(r"\b(and|or)\s*$", merged[-1], flags=re.IGNORECASE):
                    merged[-1] = (merged[-1].rstrip() + " " + cur.lstrip()).strip()
                    i += 1
                    continue

                if merged and re.match(r"^(and|or)\b", cur, flags=re.IGNORECASE):
                    merged[-1] = (merged[-1].rstrip() + " " + cur.lstrip()).strip()
                    i += 1
                    continue

                merged.append(cur)
                i += 1

            return merged

        def _maybe_replace_lower_the_with_a(lines: List[str]) -> List[str]:
            """
            Only replace lowercase 'the' -> 'a' when:
            - the cell is multi-line AND
            - across lines there is mixed usage: at least one line contains 'the'
                and at least one line contains 'a' or 'an' (any case).

            Important:
            - Do NOT change 'The' (capital T).
            - Replace only exact lowercase 'the' with 'a'.
            """
            if len(lines) <= 1:
                return lines

            has_lower_the = any(re.search(r"\bthe\b", ln) for ln in lines)  # case-sensitive => only 'the'
            has_indef = any(re.search(r"\b(a|an)\b", ln, flags=re.IGNORECASE) for ln in lines)

            if not (has_lower_the and has_indef):
                return lines

            return [re.sub(r"\bthe\b", "a", ln) for ln in lines]

        def _cap(s: str) -> str:
            s = (s or "").strip()
            return s[0].upper() + s[1:] if s else s

        def _token_set(s: str) -> set:
            # Use your existing tokenise() for consistency; convert to a set for Jaccard.
            return set(tokenise(s))

        def _jaccard(a: set, b: set) -> float:
            if not a and not b:
                return 1.0
            if not a or not b:
                return 0.0
            return len(a & b) / len(a | b)

        def _looks_like_complete_sentence(tokens: List[str]) -> bool:
            """
            Guard for LCS output: prevent broken fragments.
            """
            if not tokens or len(tokens) < 5:
                return False
            bad_end = {"and", "or", "of", "for", "to", "with", "in", "on", "at", "by", "from", "a", "an", "the"}
            if tokens[-1].lower().strip(".,;:") in bad_end:
                return False
            # Require definition-like anchor (verb-ish) OR a domain noun (noun-phrase defs).
            verbish = {
                "is", "are", "was", "were", "be", "being", "been",
                "represents", "identifies", "indicates", "means", "specifies",
                "contains", "provides", "records", "supports", "describes",
            }
            nounish = {"value", "identifier", "id", "code", "name", "number", "date", "time", "amount"}
            if not any(t.lower().strip(".,;:") in verbish for t in tokens):
                if not any(t.lower().strip(".,;:") in nounish for t in tokens):
                    return False
            return True

        def _cluster_variants(variants: List[str], threshold: float = 0.55) -> List[List[int]]:
            """
            Greedy clustering by Jaccard similarity of token sets.
            Produces clusters as lists of indices into `variants`.
            """
            token_sets = [_token_set(v) for v in variants]
            clusters: List[List[int]] = []

            for i, ts in enumerate(token_sets):
                placed = False
                for cl in clusters:
                    # Compare to cluster "centroid" approximated by the first member
                    j = cl[0]
                    if _jaccard(ts, token_sets[j]) >= threshold:
                        cl.append(i)
                        placed = True
                        break
                if not placed:
                    clusters.append([i])

            return clusters

        def _pick_consensus_line(variants: List[str], idxs: List[int]) -> str:
            """
            Pick the variant with the highest average token Jaccard similarity
            to other variants in the same cluster. Tie-break: shortest.
            """
            toks = {i: _token_set(variants[i]) for i in idxs}
            best_i = idxs[0]
            best_score = -1.0

            for i in idxs:
                score = 0.0
                for j in idxs:
                    if i == j:
                        continue
                    score += _jaccard(toks[i], toks[j])
                if len(idxs) > 1:
                    score /= (len(idxs) - 1)
                if score > best_score or (score == best_score and len(variants[i]) < len(variants[best_i])):
                    best_score = score
                    best_i = i

            return variants[best_i]

        # ----------------------------
        # Main
        # ----------------------------
        cell = (cell or "").strip()
        if not cell:
            return ""

        raw_lines = [ln.strip() for ln in re.split(r"[\r\n]+", cell) if ln.strip()]
        raw_lines = _merge_conjunction_split_lines(raw_lines)
        raw_lines = _maybe_replace_lower_the_with_a(raw_lines)

        # Single-line
        if len(raw_lines) == 1:
            s = normalise_definition_line(raw_lines[0], context_terms)
            return _cap(s)

        # Normalise each line
        norm_lines = []
        for ln in raw_lines:
            s = normalise_definition_line(ln, context_terms)
            if s:
                norm_lines.append(s)

        if not norm_lines:
            return ""

        # If there is a clear mode after normalisation, return it (grammar preserved).
        freq = Counter(norm_lines)
        top_count = freq.most_common(1)[0][1]
        if top_count >= 2 or len(freq) == 1:
            top_candidates = [k for k, v in freq.items() if v == top_count]
            best = min(top_candidates, key=lambda x: (len(x), x.lower()))
            return _cap(best)

        # Otherwise, cluster near-duplicate variants and pick the largest cluster.
        variants = list(freq.keys())
        clusters = _cluster_variants(variants, threshold=0.55)

        # Choose the largest cluster; tie-break by best internal cohesion (average similarity), then shortest consensus.
        def cluster_score(idxs: List[int]) -> Tuple[int, float, int]:
            # (size, cohesion, negative length) for sorting
            if len(idxs) <= 1:
                cohesion = 0.0
            else:
                toks = [_token_set(variants[i]) for i in idxs]
                sims = []
                for a in range(len(toks)):
                    for b in range(a + 1, len(toks)):
                        sims.append(_jaccard(toks[a], toks[b]))
                cohesion = sum(sims) / len(sims) if sims else 0.0
            consensus = _pick_consensus_line(variants, idxs)
            return (len(idxs), cohesion, -len(consensus))

        best_cluster = max(clusters, key=cluster_score)
        cluster_variants = [variants[i] for i in best_cluster]

        # Inside the chosen cluster, try mode again (it might now repeat if multiple raw lines collapsed).
        cfreq = Counter(cluster_variants)
        ctop = cfreq.most_common(1)[0][1]
        if ctop >= 2 or len(cfreq) == 1:
            cands = [k for k, v in cfreq.items() if v == ctop]
            best = min(cands, key=lambda x: (len(x), x.lower()))
            return _cap(best)

        # Optional LCS only within a tight cluster (high similarity), guarded to avoid fragments.
        if len(cluster_variants) >= 2:
            # Compute average similarity to decide whether LCS is safe to try.
            toks = [tokenise(v) for v in cluster_variants]
            sets = [set(t) for t in toks]
            sims = []
            for i in range(len(sets)):
                for j in range(i + 1, len(sets)):
                    sims.append(_jaccard(sets[i], sets[j]))
            avg_sim = sum(sims) / len(sims) if sims else 0.0

            if avg_sim >= 0.70:  # only try LCS for very similar lines
                backbone = toks[0]
                for v in toks[1:]:
                    backbone = lcs_tokens(backbone, v)
                    if not backbone:
                        break
                if backbone and _looks_like_complete_sentence(backbone):
                    sent = " ".join(backbone).strip()
                    # Do not force article edits here; your rule already applied at raw_lines stage.
                    if sent and not sent.endswith("."):
                        sent += "."
                    return _cap(sent)

        # Safe fallback: return a grammatically intact consensus sentence from the best cluster.
        consensus = _pick_consensus_line(variants, best_cluster)
        return _cap(consensus)


    # ----------------------------------------------------------------------
    # Merge function
    # ---------------------------------------------------------------------

    def merge_super_class_contexts(self, a: str, b: str) -> str:
        def extract_items(s: str) -> list[str]:
            parts = [p.strip() for p in s.split("&")]
            return [p for p in parts if p]

        items = []
        seen = set()
        for x in extract_items(a) + extract_items(b):
            if x not in seen:
                seen.add(x)
                items.append(x)

        return " | ".join(items)
    

    def merge_class_record(self, row_number: int, record: dict) -> str:
        """
        Merge a single CSV-oriented record into self.object_class_dict, indexed by class_term.

        - Class rows: register/merge class metadata.
        - Property rows (Attribute/Association): union by p_term, merge overlaps by p_term.

        Returns:
            class_term (string): the class key used in self.object_class_dict
        """
        # ----------------------------
        # main merge
        # ----------------------------
        property_type = (record.get("property_type") or "").strip()
        class_term = (record.get("class_term") or "").strip()

        if not class_term:
            self.error_print(f"Row {row_number}: empty class_term.\n{record}")
            return ""

        # ------------------------------------------------------------
        # 1) Class record
        # ------------------------------------------------------------
        if "Class" in property_type:
            if class_term in self.object_class_dict:
                # warn on mismatch (except sequence)
                d1 = copy.deepcopy(self.object_class_dict[class_term])
                d1.pop("properties", None)
                d2 = copy.deepcopy(record)

                # merge class-level fields (do not destroy existing properties)
                tgt = self.object_class_dict[class_term]
                tgt["context"] = self.merge_context(tgt.get("context", ""), record.get("context", ""))
                tgt["UNID"] = self.merge_pipe(tgt.get("UNID", ""), record.get("UNID", ""))
                tgt["short_name"] = self.merge_pipe(tgt.get("short_name", ""), record.get("short_name", ""))
                tgt["definition"] = self.append_def(tgt.get("definition", ""), record.get("definition", ""))
                tgt["inherited"] = self.inc_inherited(tgt.get("inherited", 0))
            else:
                self.object_class_dict[class_term] = record
                self.object_class_dict[class_term]["properties"] = {}
                self.object_class_dict[class_term]["inherited"] = self.inc_inherited(record.get("inherited", 0))

            return class_term

        # ------------------------------------------------------------
        # 2) Property record (Attribute or Association)
        # ------------------------------------------------------------
        if class_term not in self.object_class_dict:
            self.error_print(f"Row {row_number}: class '{class_term}' not registered before property.\n{record}")
            return class_term

        p_term = self.get_p_term(record)  # p_term uniquely identifies properties (your policy)
        props: Dict[str, dict] = self.object_class_dict[class_term].setdefault("properties", {})

        if p_term in props:
            existing = props[p_term]
            incoming = copy.deepcopy(record)
            # merge property fields (do not destroy existing properties)
            existing["context"] = self.merge_context(existing.get("context", ""), record.get("context", ""))
            existing["UNID"] = self.merge_pipe(existing.get("UNID", ""), record.get("UNID", ""))
            existing["short_name"] = self.merge_pipe(existing.get("short_name", ""), record.get("short_name", ""))
            existing["inherited"] = self.inc_inherited(existing.get("inherited", 0))
            # widen multiplicity
            existing["multiplicity"] = self.widen_multiplicity(existing.get("multiplicity", ""), incoming.get("multiplicity", ""))
            # merge definitions: append if differs, then optionally run your normaliser
            merged_def = self.append_def(existing.get("definition", ""), incoming.get("definition", ""))
            if merged_def != existing.get("definition", ""):
                # if you want to normalise / dedupe further, keep this hook
                merged_def = self.merge_super_class_contexts(existing.get("definition", ""), merged_def)
            existing["definition"] = merged_def
            # merge metadata
            existing["context"] = self.merge_context(existing.get("context", ""), incoming.get("context", ""))
            existing["UNID"] = self.merge_pipe(existing.get("UNID", ""), incoming.get("UNID", ""))
            existing["code"] = self.merge_pipe(existing.get("code", ""), incoming.get("code", ""))
            # inherited++
            existing["inherited"] = self.inc_inherited(existing.get("inherited", 0))

            props[p_term] = existing
        else:
            record["inherited"] = self.inc_inherited(record.get("inherited", 0))
            props[p_term] = record

        return class_term


    def process_record1(self, reader):
        """
        Pass 1: Read BIE rows, assign IDs/levels, and build the class/property registry.

        This pass:
        - populates self.records with all parsed rows (with generated IDs and normalised fields),
        - populates self.object_class_dict with:
            * class entries (ABIE -> 'Class'), each with a 'properties' dict
            * property entries under each class (ASBIE -> 'Composition', BBIE -> 'Attribute')
            keyed by a normalised property term,
        - merges duplicates of the same property term by:
            * widening multiplicity conservatively
            * concatenating definitions when they differ.
        """
        next(reader) # skip header

        # ----------------------------
        # First, register all Class rows so that associations to classes defined later can be resolved.
        # Pass 1 registers:
        # - Class / Super Class rows into self.object_class_dict,
        # - keeps all rows in self.records for the second pass.
        # ----------------------------
        self.current_c_term = ""
        seq = 0

        for row_number, row in enumerate(reader, start=1):
            if not row["sequence"]: continue
            elif "END" == row["acronym"]: break
            
            row = {key: (v if v is not None else "") for key, v in row.items()}
            data = {key: row.get(key, "") for key in self.bie_header}
            
            # ----------------------------
            # Validate an input CSV row.
            # ----------------------------
            valid, msg = self.check_csv_row(data)
            if not valid:
                self.error_print(f"Invalid row {seq}: {msg}")

            # ----------------------------
            # Transform a BIE-derived row into an internal record and assign an ID/level.
            # ----------------------------
            seq, record = self.populate_record(data, seq)

            # merge one row into dict registry
            self.merge_class_record(row_number, record)

            self.records.append(record)

        return self.records



    def process_record2(self):
        """
        Pass 2: Derive super classes and normalise associations.

        Main steps:
        1) Build super (super) classes by aggregating properties across sup_class chains:
        - For class terms containing "_": aggregate into each suffix term in the chain.
        - For classes in context "In All Contexts" (with >= 3 properties): aggregate into itself.
        2) Prune/label super-class properties:
        - keep super classes only if at least one property is inherited by >= AT_LEAST classes,
        - label super-class properties as:
            'Shared' (inherited count > MORE_THAN) or 'Aligned Pool' (otherwise).
        3) Normalise association targets (associated_class) where possible to match registered class terms,
        adjusting the property_term prefix when the associated class term is specialised.
        4) Build self.FSM_list:
        - emit super classes + their properties,
        - emit each concrete class,
        - emit a 'Specialized' marker row when a class specialises a known (super or concrete) sup_class,
        - emit class properties with inheritance status flags:
            Distinct / Inheritance / Modified[...] / Aligned,
            and emit inherited-but-missing sup_class properties as Prohibited (multiplicity set to 0).
        """
        CODE_ONLY = re.compile(r"^[A-Z0-9]{2,}$")
        CODE_WORD = re.compile(r"^([A-Z0-9]{2,})\s+(.+)$")  # e.g. "AAA Archive"

        self.current_class_term = None

        def _sort_properties(d: dict) -> OrderedDict:
            # property_type priority (Attributes first)
            PT_ORDER = {
                "Attribute(PK)": 1,
                "Attribute": 2,
                "Reference": 3,
                "Reference Association": 3,
                "Aggregation": 4,
                "Composition": 5
            }

            # multiplicity priority (Attributes first)
            MULT_ORDER = {
                "1": 1,
                "1..1": 1,
                "0..1": 2,
                "1..*": 3,
                "0..*": 4,
                "0": 5
            }

            # data type priority
            DT_ORDER = {
                "Identifier": 1,
                "Indicator": 2,
                "Code": 3,
                "Text": 4,
                "Date": 5,
                "Date Time": 6,
                "Time": 7,
                "Amount": 8,
                "Quantity": 9,
                "Numeric": 10,
                "Percent": 11,
                "Rate": 12,
                "Value": 13,
                "Measure": 14,
                "Binary Object": 15,
            }

            # inheritance priority (Attributes first)
            INHR_ORDER = {
                "Shared": 1,
                "Aligned Pool": 2
            }

            INHR_ORDER2 = {
                "Inheritance": 1,
                "Modified": 1,
                "Aligned": 2,
                "Distinct": 3,
                "Prohibited": 4
            }

            def key_fn(item):
                k, v = item
                pt = v.get("property_type", "")
                mult = v.get("multiplicity", "")
                id = v.get("id", "")

                inhr = v.get("extension", "")
                if inhr.startswith("Shared"):
                    inhr = "Shared"
                elif inhr.startswith("Aligned Pool"):
                    inhr = "Aligned Pool"
                elif inhr.startswith("Modified"):
                    inhr = "Modified"

                prop = (v.get("property_term") or "").strip()

                representation_term = (v.get("representation_term") or "").strip()
                if "_ " in representation_term:
                    dq, dtype = representation_term.split("_ ", 1)
                    dq = dq.strip()
                    dtype = dtype.strip()
                else:
                    dq = ""
                    dtype = representation_term

                associated_class = (v.get("associated_class") or "").strip()
                if "_ " in associated_class:
                    aq, assoc = associated_class.split("_ ", 1)
                    assoc = assoc.strip()
                else:
                    aq = ""
                    assoc = associated_class

                if str(inhr).startswith("Modified"):
                    inhr = "Modified"

                # Since sequence is a string, convert it to an int
                # (if it is missing or invalid, convert it to a larger value)
                try:
                    seq = int(v.get("sequence", 10**6))
                except Exception:
                    seq = 10**6

                is_super = inhr in ["Shared","Aligned Pool"]
                if is_super:
                    order = (
                        INHR_ORDER.get(inhr, 99),  # 1) Inheritance priority
                        PT_ORDER.get(pt, 99),      # 2) Attribute priority
                        DT_ORDER.get(dtype, 99),   # 3) representation term alphabetical
                        (dq or "").lower(),        # 4) data type qualifier alphabetical
                        (assoc or "").lower(),     # 5) associated class alphabetical
                        (aq or "").lower(),        # 6) associated class qualifier alphabetical
                        (prop or "").lower(),      # 7) property_term alphabetical
                        seq
                        # id
                    )
                else:
                    order = (
                        INHR_ORDER2.get(inhr, 99), # 1) Inheritance priority
                        PT_ORDER.get(pt, 99),      # 2) Attribute priority
                        DT_ORDER.get(dtype, 99),   # 3) representation term alphabetical
                        (dq or "").lower(),        # 4) data type  alphabetical
                        (assoc or "").lower(),     # 5) associated class alphabetical
                        (aq or "").lower(),        # 6) associated class qualifier alphabetical
                        (prop or "").lower(),      # 7) property_term alphabetical
                        seq
                        # id
                   )

                return order

            return OrderedDict(sorted(d.items(), key=key_fn))


        def _super_class_chain(class_term: str, SELF: bool = False):
            """
            Yield (head, tail) pairs by repeatedly removing the leftmost segment separated by "_ ".

            Examples:
            "AAA Archive_ Archive Parameter"
                -> ("AAA", "Archive_ Archive Parameter")
                -> ("Archive", "Archive Parameter")
                -> ("", "Archive Parameter")

            "Archive_ Archive Parameter"
                -> ("Archive", "Archive Parameter")
                -> ("", "Archive Parameter")

            "CIIH_ Supply Chain_ Trade Transaction"
                -> ("CIIH", "Supply Chain_ Trade Transaction")
                -> ("Supply Chain", "Trade Transaction")
                -> ("", "Trade Transaction")

            Rule for the FIRST segment only:
            - If the first segment looks like a code token (2+ uppercase letters/digits),
                AND the next text starts with a word (e.g., "AAA Archive..."), extract that code
                as head and remove it from the start of the term.
            - Otherwise, head is simply the first segment before "_ ".

            If SELF=True, yields the first (head, tail) for the original term as well.
            """
            term = (class_term or "").strip()
            if not term:
                return
            
            first = True
            while True:
                if "_ " in term:
                    head, tail = term.split("_ ", 1)
                    head = head.strip()
                    tail = tail.strip()

                    # Special case: first segment contains "AAA Archive" (code + word)
                    # e.g. "AAA Archive_ Archive Parameter"
                    if first:
                        m = CODE_WORD.match(head)
                        if m:
                            code = m.group(1).strip()
                            rest_of_head = m.group(2).strip()
                            # Emit ("AAA", "Archive_ Archive Parameter")
                            head_out = code
                            tail_out = f"{rest_of_head}_ {tail}".strip() if head_out else (tail or "").strip()
                        else:
                            head_out = head
                            tail_out = tail
                    else:
                        head_out = head
                        tail_out = tail

                    if SELF or not first:
                        if tail_out in self.object_class_dict:
                            return
                        
                        if tail_out in self.super_class_dict:
                            return

                        yield head_out, tail_out

                    term = tail_out
                    first = False
                    continue

                # last base term
                if SELF or not first:
                    yield "", term
                break


        def _ensure_super_class(sup_class_term: str, object_class: dict) -> int:
            """
            Create an entry in self.super_class_dict for the given sup_class_term if it does not exist.
            Returns None. (The registry is updated in-place.)
            """
            if sup_class_term in self.super_class_dict:
                return

            sup_class = copy.deepcopy(object_class)
            sup_class["property_type"] = "Super Class"
            sup_class["class_term"] = sup_class_term
            sup_class["short_name"] = sup_class_term.replace("_", "")
            N = self.set_code_num("", sup_class_term)
            super_class_id = f"{self.DEFAULT_CODE}{str(N).zfill(self.GROUPS)}"
            sup_class["id"] = super_class_id
            sup_class["DEN"] = f"{sup_class_term}. Details"
            unid = sup_class["UNID"]
            sup_class["UNID"] = unid
            n = 0
            for prop in sup_class["properties"].values():
                n += 1
                prop["id"] = f"{super_class_id}_{str(n).zfill(self.MEMBERS)}"
                prop["class_term"] = sup_class_term
                prop_unid = prop["UNID"]
                prop["UNID"] = prop_unid
                prop_den = prop["DEN"]
                prop["DEN"] = f"{sup_class_term}.{prop_den[1+prop_den.index('.') :]}"
                prop["code"] = ""

            self.super_class_dict[sup_class_term] = sup_class

            self.debug_print(f".... {sup_class['id']} self.super_class_dict['{sup_class_term}']")

            return 


        def _move_in_all_contexts_last(s: str) -> str:
            # split items by '&'
            items = [x.strip() for x in s.split("&") if x.strip()]

            # detect and remove "In All Contexts" (case-insensitive)
            has_all = any(x.casefold() == "in all contexts" for x in items)
            items = [x for x in items if x.casefold() != "in all contexts"]

            # alphabetical order (case-insensitive)
            items = sorted(items, key=lambda s: s.casefold())

            # append at the end if it existed
            if has_all:
                items.append("In All Contexts")

            return " | ".join(items)


        def _rekey_super_props_one_level_keep_first(sup_tail: str, tgt_props: Dict[str, dict]) -> None:
            """
            Re-key superclass properties in-place so that association properties drop the
            leftmost '<head>_ ' segment in associated_class, and the dict key (p_term)
            is rebuilt accordingly.

            Policy:
            - If new_key does NOT exist: move (old_key -> new_key)
            - If new_key already exists (collision): KEEP-FIRST (existing), DROP old_key,
                and LOG a warning (no merge).

            This removes stale keys such as:
            "Applicable. CIIH_ Supply Chain_ Trade Agreement"
            leaving only:
            "Applicable. Supply Chain_ Trade Agreement"
            """
            # Collect moves first (don't mutate dict while iterating)
            moves: list[tuple[str, str, dict]] = []

            for old_key, prop in list(tgt_props.items()):
                if not isinstance(prop, dict):
                    continue

                pt = (prop.get("property_type") or "").strip()
                if pt not in ("Composition", "Aggregation", "Reference Association"):
                    continue

                ac = (prop.get("associated_class") or "").strip()
                if not ac or "_ " not in ac:
                    continue

                new_prop = copy.deepcopy(prop)
                # property belongs to the superclass we are rekeying in
                new_prop["class_term"] = sup_tail
                new_prop["associated_class"] = _strip_one_level(ac)

                # Rebuild key from the normalised value
                new_key = self.get_p_term(new_prop)

                if new_key != old_key:
                    moves.append((old_key, new_key, new_prop))

            # Apply moves
            for old_key, new_key, new_prop in moves:
                if new_key in tgt_props:
                    # Collision: keep-first (existing), drop old, log
                    existing = tgt_props[new_key]

                    # Try to include minimal context in the log message
                    cls = (existing.get("class_term") or "").strip()
                    ptype = (existing.get("property_type") or "").strip()
                    old_ac = (tgt_props[old_key].get("associated_class") or "").strip() if old_key in tgt_props else ""
                    new_ac = (new_prop.get("associated_class") or "").strip()

                    msg = (
                        f"Rekey collision in super class '{cls}': {old_key}' -> '{new_key}'. \n"
                        f"        KEEP-FIRST: dropped specialized '{old_key}', kept existing '{new_key}'. \n"
                        f"        type='{ptype}', associated_class '{old_ac}' -> '{new_ac}'."
                    )

                    self.trace_print(f"[INFO] {msg}")

                    # Drop the old key
                    if old_key in tgt_props:
                        del tgt_props[old_key]
                else:
                    # No collision: move
                    tgt_props[new_key] = new_prop
                    if old_key in tgt_props:
                        del tgt_props[old_key]


        def _strip_one_level(term: str) -> str:
            """
            Strip one superclass level from term using "_ " delimiter, with code-aware handling.

            Examples:
            "CIIH_ Supply Chain_ Trade Agreement" -> "Supply Chain_ Trade Agreement"
            "AAA Archive_ Archive Parameter"      -> "Archive_ Archive Parameter"
            "Supply Chain_ Trade Agreement"       -> "Trade Agreement"
            "Trade Agreement"                     -> "Trade Agreement"
            """
            s = (term or "").strip()
            if "_ " not in s:
                return s

            head, tail = s.split("_ ", 1)
            head = head.strip()
            tail = tail.strip()

            # Case 1: head is a pure code like "CIIH"
            if CODE_ONLY.fullmatch(head):
                return tail

            # Case 2: head begins with a code + a word like "AAA Archive"
            m = CODE_WORD.match(head)
            if m:
                # drop the code, keep the word part
                rest = m.group(2).strip()
                return f"{rest}_ {tail}".strip() if rest else (tail or "").strip()

            # Case 3: normal domain prefix like "Supply Chain"
            return tail


        def _check_if_specialized(class_term: str, SELF: bool = False):
            """
            Walk up the superclass chain by stripping one "_ " level at a time, while
            handling code-style prefixes:

            - CODE_ONLY form:  "CIIH_ Supply Chain_ Trade Transaction"
                    -> "Supply Chain_ Trade Transaction" -> "Trade Transaction"

            - CODE_WORD form:  "AAA Archive_ Archive Parameter"
                    -> "Archive_ Archive Parameter" -> "Archive Parameter"

            - DOMAIN form:     "Supply Chain_ Trade Transaction"
                    -> "Trade Transaction"

            At each step, check whether the current remainder exists in:
            (1) self.super_class_dict, then (2) self.object_class_dict.

            Returns:
            (sup_class_term, sup_class_dict_or_None)
            """
            if not class_term:
                return "", None

            # If not SELF and there is no "_ ", it cannot be specialized by this rule.
            if not SELF and "_ " not in class_term:
                return "", None

            def _copy_nonzero_properties(src_class: dict, new_owner: str) -> dict:
                """Copy properties excluding multiplicity max==0, and rewrite class_term."""
                _properties = {}
                for p_term, prop0 in (src_class.get("properties") or {}).items():
                    mult = (prop0.get("multiplicity") or "").strip()
                    maxv = mult.split("..")[-1] if ".." in mult else mult
                    if maxv == "0":
                        continue
                    prop = copy.deepcopy(prop0)
                    prop["class_term"] = new_owner
                    _properties[p_term] = prop
                return _properties

            sup_class = None
            sup_class_term = (class_term or "").strip()

            # If SELF, check the starting term as-is first.
            if SELF:
                if sup_class_term in self.super_class_dict:
                    sup_class = copy.deepcopy(self.super_class_dict[sup_class_term])
                    sup_class["class_term"] = sup_class_term
                    sup_class["properties"] = _copy_nonzero_properties(sup_class, sup_class_term)
                    return sup_class_term, sup_class
                
                if sup_class_term in self.object_class_dict:
                    sup_class = copy.deepcopy(self.object_class_dict[sup_class_term])
                    sup_class["class_term"] = sup_class_term
                    sup_class["properties"] = _copy_nonzero_properties(sup_class, sup_class_term)
                    return sup_class_term, sup_class

            # Walk up the chain
            while "_ " in sup_class_term:
                sup_class_term = _strip_one_level(sup_class_term)
                if not sup_class_term:
                    break

                if sup_class_term in self.super_class_dict:
                    sup_class = copy.deepcopy(self.super_class_dict[sup_class_term])
                    sup_class["class_term"] = sup_class_term
                    sup_class["properties"] = _copy_nonzero_properties(sup_class, sup_class_term)
                    break

                if sup_class_term in self.object_class_dict:
                    sup_class = copy.deepcopy(self.object_class_dict[sup_class_term])
                    sup_class["class_term"] = sup_class_term
                    sup_class["properties"] = _copy_nonzero_properties(sup_class, sup_class_term)
                    break

            # If nothing matched, normalise to blank.
            if sup_class is None:
                return "", None

            return sup_class_term, sup_class


        def _merge_super_class(sup_head: str, sup_tail: str, object_class: dict) -> dict:
            """
            Merge an incoming object_class into self.super_class_dict[cterm] where:

                cterm = f"{sup_head}_ {sup_tail}"  if sup_head else sup_tail

            Also normalises association targets one level "up" for the superclass layer:
            - If associated_class contains "_ ", drop the leftmost segment and keep the remainder.
                (CIIH_ Supply Chain_ Trade Agreement -> Supply Chain_ Trade Agreement
                Supply Chain_ Trade Agreement -> Trade Agreement)

            Indexing policy:
            - self.super_class_dict is indexed by class_term (cterm).
            - Properties are indexed by p_term (dict key). Because we rewrite associated_class,
            we MUST rebuild the p_term for association properties to keep key/value consistent.
            """
            # ----------------------------
            # superclass key
            # ----------------------------
            if CODE_ONLY.fullmatch(sup_head):
                cterm = f"{sup_head} {sup_tail}" if sup_head else (sup_tail or "").strip()
            else:
                cterm = f"{sup_head}_ {sup_tail}" if sup_head else (sup_tail or "").strip()

            _ensure_super_class(cterm, object_class)
            target = self.super_class_dict[cterm]

            # ----------------------------
            # Merge class-level fields
            # ----------------------------
            target["code"] = self.merge_pipe(target.get("code", ""), object_class.get("code", ""))
            target["UNID"] = self.merge_pipe(target.get("UNID", ""), object_class.get("UNID", ""))
            target["context"] = self.merge_context(target.get("context", ""), object_class.get("context", ""))
            target["definition"] = self.append_def(target.get("definition", ""), object_class.get("definition", ""))
            target["inherited"] = self.inc_inherited(target.get("inherited"))

            # ensure properties dict exists
            tgt_props: Dict[str, dict] = target.setdefault("properties", {})
            _rekey_super_props_one_level_keep_first(sup_tail, tgt_props)

            inc_props: Dict[str, dict] = object_class.get("properties") or {}

            # ----------------------------
            # Merge properties (union by p_term)
            # ----------------------------
            for p_term, prop0 in inc_props.items():
                if not isinstance(prop0, dict):
                    continue

                # skip removed
                if self.mult_max(prop0.get("multiplicity", "")) == "0":
                    continue

                # optional: skip specialization rows as properties
                if (prop0.get("property_type") or "").strip() == "Specialization":
                    continue

                # Make a safe copy for edits
                prop = copy.deepcopy(prop0)

                # Set ownership to this superclass term
                prop["class_term"] = cterm

                # If association-type, normalise associated_class ONE level and rebuild key
                pt = (prop.get("property_type") or "").strip()
                if pt in ("Composition", "Aggregation", "Reference Association"):
                    ac = (prop.get("associated_class") or "").strip()
                    if ac:
                        prop["associated_class"] = _strip_one_level(ac)

                # Rebuild p_term for this layer (important if associated_class changed)
                p_term2 = self.get_p_term(prop)

                # New property?
                if p_term2 not in tgt_props:
                    prop["inherited"] = self.inc_inherited(prop.get("inherited"))
                    tgt_props[p_term2] = prop
                    continue

                # merge into existing property
                tgt_prop = tgt_props[p_term2]
                tgt_prop["class_term"] = cterm
                tgt_prop["inherited"] = self.inc_inherited(tgt_prop.get("inherited"))

                tgt_prop["multiplicity"] = self.widen_multiplicity(
                    tgt_prop.get("multiplicity", ""),
                    prop.get("multiplicity", "")
                )
                tgt_prop["module"] = self.merge_pipe(tgt_prop.get("module", ""), prop.get("module", ""))
                tgt_prop["code"] = self.merge_pipe(tgt_prop.get("code", ""), prop.get("code", ""))
                tgt_prop["UNID"] = self.merge_pipe(tgt_prop.get("UNID", ""), prop.get("UNID", ""))
                tgt_prop["context"] = self.merge_context(tgt_prop.get("context", ""), prop.get("context", ""))
                tgt_prop["definition"] = self.append_def(tgt_prop.get("definition", ""), prop.get("definition", ""))

            return target


        def _check_associated_class_refs(dict:dict, super:bool=False) -> list:
            """
            Check whether each property's associated_class refers to an existing class in self.object_class_dict.

            Reference key rule:
            - if prop['code'] is present: f"{code}_ {associated_class}"
            - else: associated_class
            In case super=True, also check if associated_class founds prop['code'].
            """
            missing = set()

            for class_term, obj in (dict or {}).items():
                props = obj.get("properties") or {}
                for p_key, prop in props.items():
                    assoc = (prop.get("associated_class") or "").strip()
                    if not assoc:
                        continue

                    ref_class_term = assoc

                    if super:
                        if ref_class_term not in dict and assoc not in dict:
                            found = False
                            while "_ " in assoc:
                                assoc = assoc.split("_ ", 1)[1]
                                if assoc in dict:
                                    found = True
                                    break
                            if not found:
                                msg = f"'{class_term}. {p_key}' -> '{assoc}'"
                                self.trace_print(f"[WARN] Undefined associated_class reference: {msg}")
                                missing.add(assoc)
                    else:
                        if ref_class_term not in dict:
                            msg = f"'{class_term}. {p_key}' -> '{ref_class_term}'"
                            self.trace_print(f"[WARN] Undefined associated_class reference: {msg}" )
                            missing.add(ref_class_term)

            return missing


        def _register_super_class(sup_class_term:str) -> dict:
            object_class = self.object_class_dict[sup_class_term]
            sup_class = copy.deepcopy(object_class)
            sup_props = sup_class["properties"]

            context = object_class["context"]
            sup_class["context"] = context
            sup_class["property_type"] = "Super Class"
            sup_class["class_term"] = sup_class_term

            N = self.set_code_num("", sup_class_term)
            class_id = f"{self.DEFAULT_CODE}{str(N).zfill(self.GROUPS)}"
            sup_class["id"] = class_id

            for p_term, prop0 in sup_props.items():
                if self.mult_max(prop0.get("multiplicity", "")) == "0":
                    continue
                prop = copy.deepcopy(prop0)  # Do not mutate the source property object.
                prop["class_term"] = sup_class_term
                p_term = self.get_p_term(prop)
                context = prop["context"]
                prop["context"] = context
                m = re.search(r"\(([^)]*)\)", context)
                sup_context = m.group(1) if m else ""
                if context not in sup_context:
                    sup_class["context"] = _move_in_all_contexts_last(f"{sup_class['context'][:-1]} | {context})")                
                n = 1 + len(sup_props)
                prop["id"] = f"{class_id}_{str(n).zfill(self.MEMBERS)}"
                sup_props[p_term] = prop
                sup_props[p_term]["inherited"] = 1

            self.super_class_dict[sup_class_term] = sup_class

            return sup_class


        # ----------------------------
        # Define super class
        # ----------------------------
        self.trace_print("-- Define super class.")

        self.super_class_dict = {}
        for class_term, object_class in self.object_class_dict.items():
            self.debug_print(f"- object_class_dict['{class_term}']")
            # ----------------------------
            # Build/merge super classes for every sup_class term in the chain.
            # ----------------------------
            for sup_head, sup_tail in _super_class_chain(class_term, SELF=False):
                sup_cterm = f"{sup_head}_ {sup_tail}".strip() if sup_head else (sup_tail or "").strip()
                self.debug_print(f"Build/merge sup_class:'{sup_cterm}'")

                _merge_super_class(sup_head, sup_tail, object_class)

        """
        Check associated class regictration.
        """
        self.trace_print("-- Checking associated class reference integrity.")
        # ----------------------------
        # Check association targets (associated_class)
        # ----------------------------
        super_class_missing = _check_associated_class_refs(self.super_class_dict, super=True)
        if len(super_class_missing) > 0:
            self.trace_print(f"-- Missing {list(super_class_missing)} associated class in super_class_dict.")
            for sup_class_term in list(super_class_missing):
                _register_super_class(sup_class_term)

        object_class_missing = _check_associated_class_refs(self.object_class_dict)
        if len(object_class_missing) > 0:
            self.trace_print(f"-- Missing {list(object_class_missing)} associated class in object_class_dict.")
        else:
            self.trace_print(f"-- NO missing associated class in object_class_dict.")

        # ----------------------------
        # STEP 2 ends here.
        # Building the flattened FSM output list is intentionally deferred to STEP 3
        # (process_record3) after merging abstract classes into object_class_dict.
        return


    def write_csv(self, csv_file):
        self.trace_print(f"** Write {csv_file}")

        records = [{k: v for k, v in d.items() if k in self.out_header} for d in self.FSM_list]

        with open(csv_file, "w", encoding = self.encoding, newline="") as f:
            writer = csv.DictWriter(f, fieldnames = self.out_header)
            writer.writeheader()
            writer.writerows(records)


    def list_representation_terms(
        self,
        only_attributes: bool = True,
        show_count: bool = True,
        strip_qualifier: bool = False,
    ):
        """
        Build a unique list of representation_term values used in self.object_class_dict.

        Parameters
        ----------
        only_attributes:
            If True, include only Attribute rows (typically BBIE-derived).
            If False, include other property types as well (many will have empty representation_term).
        show_count:
            If True, print each term with its occurrence count.
        strip_qualifier:
            If True, remove the leading "<qualifier>_ " prefix (if present) and aggregate
            by the bare representation term only.
            Examples:
                "ABC_ Text"   -> "Text"
                "Date Time"   -> "Date Time"   (no qualifier prefix)
        """
        def _normalize(rt: str) -> str:
            """
            Normalise a representation_term value for counting.

            - Trim surrounding whitespace.
            - Optionally drop the leading "<qualifier>_ " prefix.
            We split only on the first occurrence of "_ " because qualifiers may contain underscores.
            """
            rt = (rt or "").strip()
            if not rt:
                return ""
            if strip_qualifier and "_ " in rt:
                rt = rt.split("_ ", 1)[1].strip()
            return rt

        counter = Counter()

        # Walk all classes and their properties; representation_term is stored on property records.
        for class_term, obj in self.object_class_dict.items():
            props = obj.get("properties", {})
            for p_term, prop in props.items():
                # By default, count only Attribute properties (BBIE).
                if only_attributes and prop.get("property_type") != "Attribute":
                    continue

                rt = _normalize(prop.get("representation_term", ""))
                if not rt:
                    continue
                counter[rt] += 1

        # Sort by (count desc, term asc)
        terms = sorted(counter.items(), key=lambda x: (-x[1], x[0].lower()))

        if show_count:
            for rt, n in terms:
                self.debug_print(f"{n}\t{rt}")
        else:
            for rt, _ in terms:
                self.debug_print(rt)

        # Return only the ordered list of terms.
        return [rt for rt, _ in terms]

    
    def process_record3(self):
        """
        Pass 3: Integrate abstract classes (derived super classes) into object_class_dict,
        then build the final flattened FSM output list (self.FSM_list).

        This step performs:
        1) Merge super_class_dict into object_class_dict as 'Abstract Class'.
        - If the same class_term exists in both registries, keep the superclass term as-is,
            and rename the object-side class by prefixing '_' (e.g. 'Note' -> '_Note').
        - For properties whose associated_class refers to a renamed object-side target,
            rewrite associated_class only for object-side owners (superclass owners keep the original term).

        2) Build self.FSM_list from object_class_dict only, in a hierarchy-friendly order:
        - Output Abstract Class first.
        - Within each base term group (unqualified last word), traverse parent -> children so that
            inheritance relationships can be visually checked (e.g. Party -> Archive_ Party -> AAA Archive_ Party).
        """

        # ------------------------------------------------------------
        # Helper: property sorting
        # ------------------------------------------------------------
        def _sort_properties(d: dict) -> OrderedDict:
            PT_ORDER = {
                "Attribute(PK)": 1,
                "Attribute": 2,
                "Reference": 3,
                "Reference Association": 3,
                "Aggregation": 4,
                "Composition": 5,
            }

            MULT_ORDER = {
                "1": 1, "1..1": 1,
                "0..1": 2,
                "0..*": 3, "1..*": 3,
                "*": 3,
                "0": 9
            }

            DT_ORDER = {
                "Identifier": 1,
                "Code": 2,
                "Text": 3,
                "Name": 4,
                "Date": 5,
                "Date Time": 6,
                "Time": 7,
                "Amount": 8,
                "Quantity": 9,
                "Numeric": 10,
                "Percent": 11,
                "Rate": 12,
                "Value": 13,
                "Measure": 14,
                "Binary Object": 15,
            }

            INHR_ORDER = {"Shared": 1, "Aligned Pool": 2}
            INHR_ORDER2 = {
                "Inheritance": 1,
                "Modified": 1,
                "Aligned": 2,
                "Distinct": 3,
                "Prohibited": 4,
            }

            def key_fn(item):
                k, v = item
                pt = v.get("property_type", "") or ""
                mult = (v.get("multiplicity", "") or "").strip()
                if mult in MULT_ORDER:
                    mult_pri = MULT_ORDER[mult]
                else:
                    mult_pri = 99

                inhr = v.get("extension", "") or ""
                if inhr.startswith("Shared"):
                    inhr = "Shared"
                elif inhr.startswith("Aligned Pool"):
                    inhr = "Aligned Pool"
                elif str(inhr).startswith("Modified"):
                    inhr = "Modified"

                prop = (v.get("property_term") or "").strip()

                representation_term = (v.get("representation_term") or "").strip()
                if "_ " in representation_term:
                    dq, dtype = representation_term.split("_ ", 1)
                    dq = dq.strip()
                    dtype = dtype.strip()
                else:
                    dq = ""
                    dtype = representation_term

                associated_class = (v.get("associated_class") or "").strip()
                if "_ " in associated_class:
                    aq, assoc = associated_class.split("_ ", 1)
                    assoc = assoc.strip()
                else:
                    aq = ""
                    assoc = associated_class

                try:
                    seq = int(v.get("sequence", 10**6))
                except Exception:
                    seq = 10**6

                is_super = inhr in ["Shared", "Aligned Pool"]
                if is_super:
                    order = (
                        INHR_ORDER.get(inhr, 99),
                        PT_ORDER.get(pt, 99),
                        DT_ORDER.get(dtype, 99),
                        (dq or "").lower(),
                        (assoc or "").lower(),
                        (aq or "").lower(),
                        (prop or "").lower(),
                        seq,
                    )
                else:
                    order = (
                        INHR_ORDER2.get(inhr, 99),
                        PT_ORDER.get(pt, 99),
                        DT_ORDER.get(dtype, 99),
                        (dq or "").lower(),
                        (assoc or "").lower(),
                        (aq or "").lower(),
                        (prop or "").lower(),
                        seq,
                    )
                return order

            return OrderedDict(sorted(d.items(), key=key_fn))

        def _base_term(ct: str) -> str:
            t = (ct or "").strip()
            while "_ " in t:
                t = t.split("_ ", 1)[1].strip()
            return t

        def _compute_abstract_group_and_extensions(a_entry: dict) -> None:
            props = a_entry.get("properties") or {}
            if not isinstance(props, dict):
                return
            inherited_set = set()
            for _, p in props.items():
                try:
                    inh = int(p.get("inherited", 0) or 0)
                except Exception:
                    inh = 0
                ext = "Shared" if inh > self.MORE_THAN else "Aligned Pool"
                p.setdefault("extension", ext)
                p.setdefault("group", ext)
                inherited_set.add(ext)
            cls_group = "Shared" if "Shared" in inherited_set else "Aligned Pool"
            a_entry.setdefault("extension", cls_group)
            a_entry.setdefault("group", cls_group)

        def _make_unique_object_name(base_term: str) -> str:
            # Always one leading underscore; add numeric suffix if needed.
            candidate = f"_{base_term}"
            if candidate not in existing_keys:
                return candidate
            i = 2
            while f"{candidate}_{i}" in existing_keys:
                i += 1
            return f"{candidate}_{i}"

        obj = self.object_class_dict or {}
        sup = getattr(self, "super_class_dict", {}) or {}
        super_terms = set(sup.keys())

        # ------------------------------------------------------------
        # Conflict handling: keep abstract term, rename object-side term -> _<term>
        # ------------------------------------------------------------
        rename_map = {}
        inverse_rename = {}
        existing_keys = set(obj.keys()) | set(sup.keys())

        conflicts = set(obj.keys()) & set(sup.keys())
        for term in sorted(conflicts):
            new_term = _make_unique_object_name(term)
            existing_keys.add(new_term)
            rename_map[term] = new_term
            inverse_rename[new_term] = term

            o = copy.deepcopy(obj[term])
            o["class_term"] = new_term
            props = o.get("properties")
            if isinstance(props, dict):
                for _, pv in props.items():
                    if isinstance(pv, dict):
                        pv["class_term"] = new_term
            obj[new_term] = o
            del obj[term]

        # Register abstract classes
        for term, s_entry in sup.items():
            a = copy.deepcopy(s_entry)
            a["property_type"] = "Abstract Class"
            _compute_abstract_group_and_extensions(a)
            obj[term] = a

        # Rewrite associated_class only for object-side owners if target renamed
        for owner_term, owner_entry in obj.items():
            owner_is_abstract = owner_term in super_terms
            props = owner_entry.get("properties")
            if not isinstance(props, dict):
                continue
            for _, pv in props.items():
                if not isinstance(pv, dict):
                    continue
                assoc = (pv.get("associated_class") or "").strip()
                if assoc in rename_map and not owner_is_abstract:
                    pv["associated_class"] = rename_map[assoc]

        # ------------------------------------------------------------
        # Conflict-renamed class must specialise abstract class and inherit its properties
        # ------------------------------------------------------------
        for original, renamed in rename_map.items():
            if original not in obj or renamed not in obj:
                continue
            abstract_entry = obj[original]
            child_entry = obj[renamed]

            a_props = copy.deepcopy(abstract_entry.get("properties") or {})
            c_props = copy.deepcopy(child_entry.get("properties") or {})

            merged_props = {}

            # Start from abstract properties (keep them all; mark missing as Prohibited)
            for p_term, ap in a_props.items():
                mp = copy.deepcopy(ap)
                mp["class_term"] = renamed
                if p_term not in c_props:
                    mp["multiplicity"] = "0"
                    mp["extension"] = "Prohibited"
                    mp["inherited"] = ""
                    mp["group"] = ""
                merged_props[p_term] = mp

            # Overlay child property multiplicity and derive extension vs abstract multiplicity
            for p_term, cp in c_props.items():
                if p_term in merged_props:
                    sup_mult = (a_props[p_term].get("multiplicity") or "").strip()
                    child_mult = (cp.get("multiplicity") or "").strip()
                    mp = copy.deepcopy(cp)
                    mp["class_term"] = renamed
                    mp["extension"] = "Inheritance" if child_mult == sup_mult else f"Modified [{sup_mult}]"
                    # mp.setdefault("group", abstract_entry.get("group", ""))
                    merged_props[p_term] = mp
                else:
                    mp = copy.deepcopy(cp)
                    mp["class_term"] = renamed
                    mp.setdefault("extension", "Distinct")
                    # mp.setdefault("group", child_entry.get("group", ""))
                    merged_props[p_term] = mp

            child_entry["properties"] = merged_props
            # child_entry.setdefault("group", abstract_entry.get("group", ""))
            obj[renamed] = child_entry

        self.rename_map = rename_map

        # ------------------------------------------------------------
        # Parent map (suffix-based) + override for renamed conflicts (_Note -> Note)
        # ------------------------------------------------------------
        terms = set(obj.keys())
        candidates = sorted(terms, key=lambda x: len(x), reverse=True)
        parent = {}
        for term in terms:
            p = None
            for cand in candidates:
                if cand == term:
                    continue
                if term.endswith(cand) and len(term) > len(cand) and term[-len(cand) - 1] == " ":
                    p = cand
                    break
            parent[term] = p
        for renamed, original in inverse_rename.items():
            parent[renamed] = original

        # Build children lists
        children = {t: [] for t in terms}
        roots = []
        for t, p in parent.items():
            if p is None or p not in terms:
                roots.append(t)
            else:
                children[p].append(t)

        def _is_abstract(t: str) -> int:
            # sort priority is abstract first
            return 0 if obj[t].get("property_type") == "Abstract Class" else 1

        def _sibling_key(t: str):
            ct = obj[t].get("class_term", t)
            return (_is_abstract(t), ct.lower())

        # Sort children lists
        for p, cs in children.items():
            cs.sort(key=_sibling_key)

        # Group roots by base term for stable top-level ordering.
        roots_by_base = {}
        for r in roots:
            ct = obj[r].get("class_term", r)
            roots_by_base.setdefault(_base_term(ct).lower(), []).append(r)

        for base, rs in roots_by_base.items():
            rs.sort(key=_sibling_key)

        ordered_terms = []
        visited = set()

        def dfs(node: str):
            if node in visited:
                return
            visited.add(node)
            ordered_terms.append(node)
            for c in children.get(node, []):
                dfs(c)

        for base in sorted(roots_by_base.keys()):
            for r in roots_by_base[base]:
                dfs(r)

        # ------------------------------------------------------------
        # Flatten to FSM_list (keep Prohibited rows)
        # ------------------------------------------------------------
        self.FSM_list = []

        for term in ordered_terms:
            qualifier = term[:term.rindex("_ ")] if "_ " in term else ""
            entry = obj[term]
            props = copy.deepcopy(entry.get("properties") or {})
            sup_props = None

            # Ensure prohibited properties exist for normal classes (when parent exists)
            p = parent.get(term)
            if p and p in obj:
                sup_props = obj[p].get("properties") or {}
                if isinstance(sup_props, dict):
                    for spk, sp in sup_props.items():
                        as_class = f"{qualifier}_ {spk[2+spk.index('.'):]}" if qualifier else ""
                        if qualifier and f"{spk[:spk.index('.')]}. {as_class}" in props:
                            pr = copy.deepcopy(sp)
                            pr["class_term"] = term
                            pr["associated_class"] = as_class
                            pr["extension"] = "Inheritance"
                            props[as_class] = pr
                        elif spk not in props:
                            pr = copy.deepcopy(sp)
                            pr["class_term"] = term
                            pr["multiplicity"] = "0"
                            pr["extension"] = "Prohibited"
                            pr["inherited"] = 0
                            pr["group"] = ""
                            props[spk] = pr

            # Populate missing extensions for non-abstract classes
            if entry.get("property_type") != "Abstract Class":
                sup_props = obj[p].get("properties") if (p and p in obj) else None
                if isinstance(sup_props, dict):
                    for pk, pr in props.items():
                        if pr.get("extension"):
                            continue
                        if pk in sup_props:
                            sup_mult = (sup_props[pk].get("multiplicity") or "").strip()
                            my_mult = (pr.get("multiplicity") or "").strip()
                            pr["extension"] = "Inheritance" if my_mult == sup_mult else f"Modified [{sup_mult}]"
                        else:
                            sup_p_term = pk.replace(f"{qualifier}_ ","") if qualifier else pk
                            if sup_p_term not in sup_props:
                                pr["extension"] = "Distinct"
                else:
                    for pk, pr in props.items():
                        pr.setdefault("extension", "Distinct")

                # Derive class extension if missing
                if not entry.get("extension"):
                    ext_set = set()
                    for pr in props.values():
                        ext = (pr.get("extension") or "").strip()
                        if ext.startswith("Modified"):
                            ext = "Modified"
                        ext_set.add(ext)
                    if "Distinct" in ext_set:
                        entry["extension"] = "Distinct"
                    elif "Aligned" in ext_set:
                        entry["extension"] = "Aligned"
                    elif "Modified" in ext_set:
                        entry["extension"] = "Modified"
                    else:
                        entry["extension"] = "Inheritance"

            # Append class row
            class_row = copy.deepcopy(entry)
            class_row.pop("properties", None)
            class_row["class_term"] = term
            self.FSM_list.append(class_row)

            # Append specialisation row
            if p and p.startswith("_"):
                p = p[1:]
                if p in obj:
                    spec_row = copy.deepcopy(class_row)
                    spec_row["level"] = 2
                    spec_row["property_type"] = "Specialization"
                    spec_row["associated_class"] = p
                    spec_row["multiplicity"] = "1"
                    spec_row["identifier"] = ""
                    spec_row["property_term"] = ""
                    spec_row["representation_term"] = ""
                    spec_row["group"] = "Shared" if entry["inherited"] > self.MORE_THAN else "Aligned Pool"
                    self.FSM_list.append(spec_row)
            elif p and p in obj:
                spec_row = copy.deepcopy(class_row)
                spec_row["level"] = 2
                spec_row["property_type"] = "Specialization"
                spec_row["associated_class"] = p
                spec_row["multiplicity"] = "1"
                spec_row["identifier"] = ""
                spec_row["property_term"] = ""
                spec_row["representation_term"] = ""
                spec_row["group"] = "Shared" if entry["inherited"] > self.MORE_THAN else "Aligned Pool"
                self.FSM_list.append(spec_row)

            # Append properties
            if isinstance(props, dict):
                for pk, pr0 in _sort_properties(props).items():
                    pr = copy.deepcopy(pr0)
                    pr["class_term"] = term
                    sup_p_term = pk.replace(f"{qualifier}_ ","") if qualifier in pk else ""
                    if sup_props:
                        if sup_p_term in sup_props:
                            continue
                    # If Identification/Identifier, mark as PK (same rule as STEP 2 output)
                    if pr.get("property_term") == "Identification" and pr.get("representation_term") == "Identifier":
                        pr["identifier"] = "PK"
                    if pr["inherited"]:
                        pr["group"] = "Shared" if pr["inherited"] > self.MORE_THAN else "Aligned Pool"
                    else:
                        pr["group"] = ""
                    self.FSM_list.append(pr)

        return self.FSM_list


    def analyze(self):
        """
        Main entry point for generating an FSM CSV from BIE input rows.

        High-level workflow:
        1) Initialise dictionaries:
        - self.object_class_dict: class registry
        - self.records: all parsed rows

        2) Three-pass processing:
        - Pass 1 (process_record1): read CSV rows, generate IDs/levels, and register all classes
            to enable forward reference resolution.
        - Pass 2 (process_record2): attach properties, derive super classes, and normalise association targets.
        (No output list is generated in this pass.)
        - Pass 3 (process_record3): merge abstract classes into object_class_dict and build the flattened FSM list (self.FSM_list).

        3) Output:
        - Write self.FSM_list to the target FSM CSV with the extended header (out_header).
        """
        logfile = self.init_logger(self.bie_file, echo=False)  # inp is your input CSV path
        self.log_print(f"Log started: {logfile}")

        self.object_class_dict = {}
        self.trace_print(f"** READ {self.bie_file}")
        with open(self.bie_file, encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f, fieldnames=self.bie_header)
            self.trace_print(f"** Process record STEP 1.")
            self.process_record1(reader)

        # self.trace_print("=== representation_term (qualifier stripped) ===")
        # terms = self.list_representation_terms(only_attributes=True, show_count=False, strip_qualifier=True)
        # self.debug_print(sorted(self.TDED_list, key=lambda x: x))

        self.trace_print("** Process record STEP 2.")
        self.process_record2()

        self.trace_print("** Process record STEP 3.")
        self.process_record3()

        file = file_path(self.fsm_file)
        self.write_csv(file)
        self.trace_print(f"-- Log file: {logfile}")

        self.close_logger()
        self.trace_print(f"** END {file}")


    def write_csv(self, csv_file):
        self.trace_print(f"** Write {csv_file}")

        records = [{k: v for k, v in d.items() if k in self.out_header} for d in self.FSM_list]

        with open(csv_file, "w", encoding = self.encoding, newline="") as f:
            writer = csv.DictWriter(f, fieldnames = self.out_header)
            writer.writeheader()
            writer.writerows(records)


    def list_representation_terms(
        self,
        only_attributes: bool = True,
        show_count: bool = True,
        strip_qualifier: bool = False,
    ):
        """
        Build a unique list of representation_term values used in self.object_class_dict.

        Parameters
        ----------
        only_attributes:
            If True, include only Attribute rows (typically BBIE-derived).
            If False, include other property types as well (many will have empty representation_term).
        show_count:
            If True, print each term with its occurrence count.
        strip_qualifier:
            If True, remove the leading "<qualifier>_ " prefix (if present) and aggregate
            by the bare representation term only.
            Examples:
                "ABC_ Text"   -> "Text"
                "Date Time"   -> "Date Time"   (no qualifier prefix)
        """
        def _normalize(rt: str) -> str:
            """
            Normalise a representation_term value for counting.

            - Trim surrounding whitespace.
            - Optionally drop the leading "<qualifier>_ " prefix.
            We split only on the first occurrence of "_ " because qualifiers may contain underscores.
            """
            rt = (rt or "").strip()
            if not rt:
                return ""
            if strip_qualifier and "_ " in rt:
                rt = rt.split("_ ", 1)[1].strip()
            return rt

        counter = Counter()

        # Walk all classes and their properties; representation_term is stored on property records.
        for class_term, obj in self.object_class_dict.items():
            props = obj.get("properties", {})
            for p_term, prop in props.items():
                # By default, count only Attribute properties (BBIE).
                if only_attributes and prop.get("property_type") != "Attribute":
                    continue

                rt = _normalize(prop.get("representation_term", ""))
                if not rt:
                    continue
                counter[rt] += 1

        # Sort by (count desc, term asc)
        terms = sorted(counter.items(), key=lambda x: (-x[1], x[0].lower()))

        if show_count:
            for rt, n in terms:
                self.debug_print(f"{n}\t{rt}")
        else:
            for rt, _ in terms:
                self.debug_print(rt)

        # Return only the ordered list of terms.
        return [rt for rt, _ in terms]

    
def main():
    RAESER = False
    if RAESER:
        # Create the parser
        parser = argparse.ArgumentParser(
            prog="bie_to_bsm.py",
            usage="%(prog)s BIE_file FSM_file -e encoding [options]",
            description="Converts BIE to Foundational Semantic Model (FSM)."
        )
        parser.add_argument("bie_file", metavar="bie_file", type = str, help="Foundational Foundational Semantic Model (FSM) files")
        parser.add_argument("fsm_file", metavar="fsm_file", type = str, help="Business Semantic Model (BSM) file")
        parser.add_argument("-e", "--encoding", required = False, default="utf-8-sig", help="File encoding, default is utf-8-sig")
        parser.add_argument("-t", "--trace", required = False, action="store_true")
        parser.add_argument("-d", "--debug", required = False, action="store_true")

        args = parser.parse_args()

        # Flatten the list if necessary
        bie_files = []
        if args.root:
            for val in args.bie_file:
                if isinstance(val, str) and "+" in val:
                    bie_files.extend(val.split("+"))
                else:
                    bie_files.append(val)
        bie_files = [x.strip() for x in bie_files]            

        processor = Processor(
            bie_file = args.bie_files,
            fsm_file = args.FSM_file.strip(),
            encoding = args.encoding.strip() if args.encoding else None,
            trace = args.trace,
            debug = args.debug
        )
    else:
        BASE_DIR = "UNECE/"
        bie_file = f"{BASE_DIR}MRBIE-D25A.csv"
        fsm_file = f"{BASE_DIR}FSM-D25A_N1-9_2026-02-12.csv"
        encoding = "utf-8"
        processor = Processor(
            bie_file = bie_file,
            fsm_file = fsm_file,
            encoding = encoding,
            trace = True,
            debug = False
        )

    processor.analyze()

if __name__ == "__main__":
    main()
