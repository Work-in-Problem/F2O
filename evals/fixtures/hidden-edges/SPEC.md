# SPEC — VCF-lite, a text format for contact cards

This document is the complete and authoritative specification of the VCF-lite
format and of the required parser module `cardparse.py`. Every behavior of the
parser is defined here; where an example seems to disagree with the prose, the
prose wins.

## 1. Required interface

`cardparse.py` lives in the project root, uses only the Python 3 standard
library, and provides all three of the following:

1. **`CardParseError`** — an exception class, a subclass of `ValueError`,
   raised for every malformed input. Its message is exactly
   `line N: <reason>` where `N` is a 1-based physical line number (§2) and
   `<reason>` is one of the fixed strings enumerated in §9. No other
   exception type may escape `parse` for any string input.
2. **`parse(text)`** — takes the full document as a `str` and returns the
   parsed document: a list of cards in document order, where each card is a
   `dict` mapping each key (a lowercase `str`, §6) to a list of one or more
   value strings (§7, §8). Dict insertion order must equal first-occurrence
   order of the keys (§8).
3. **A command-line interface**: `python3 cardparse.py FILE` reads FILE,
   decodes it as UTF-8, and passes its exact character content to the parser.
   The reading step must not alter line-ending characters in any way —
   opening the file in a mode that translates newlines is non-conforming,
   because CR and CRLF are significant (§2). On success the CLI prints the
   result to stdout as a JSON array (each card a JSON object whose values are
   arrays of strings) and exits with code 0; any valid JSON serialization is
   acceptable provided object member order equals the key order specified in
   §8. On `CardParseError` the CLI prints `error: ` followed by the
   exception's message as one line to stderr and exits with code 1. Invoked
   with anything other than exactly one argument, it prints a usage line to
   stderr and exits with code 2.

## 2. Physical lines and line terminators

- A line terminator is either a single LF (U+000A) or the two-character
  sequence CRLF (U+000D U+000A). Both are valid, and one document may mix
  them freely.
- A CR that is **not** immediately followed by an LF is not a line
  terminator. It has no structural meaning: it is ordinary content and is
  preserved verbatim wherever it appears.
- A **physical line** is a maximal run of characters up to but not including
  the next line terminator (or up to end of input). The terminator after the
  last line is optional: a document may end in the middle of a line, and that
  final unterminated line is a physical line like any other.
- Physical lines are numbered starting at 1. Every error's `N` is a physical
  line number. A logical line assembled from several physical lines (§3)
  reports the number of its **first** physical line.

## 3. Unfolding (line continuation)

- A physical line whose first character is a space (U+0020) is a
  **continuation**: exactly one leading space is removed, and the remainder
  is appended to the previous logical line. The remainder may be empty, and
  it may itself begin with further spaces — those further spaces are content
  and are preserved.
- Only a space marks a continuation. A tab or any other character does not.
- Any number of consecutive continuations is allowed; each appends in turn
  to the same growing logical line.
- Unfolding happens **before any other interpretation**. Markers (§5), blank
  lines (§4), and property lines (§6) are recognized on logical lines only.
  For example, the two physical lines `BEGI` and ` N:CARD` form the single
  logical line `BEGIN:CARD`, which is a begin marker.
- The previous logical line may be any line, including an empty one; the
  combined result is then evaluated by the ordinary rules.
- A continuation as the very first physical line of the document is an
  error: `line 1: continuation before any line`.

## 4. Blank lines

- A logical line containing zero characters is **blank**. Blank lines are
  ignored everywhere: between cards and inside cards alike.
- Only a zero-character logical line is blank. A logical line containing
  only tabs or other whitespace is not blank and is processed under §5/§6
  like any other line. (A physical line starting with a space is a
  continuation per §3 and never reaches this rule on its own.)

## 5. Markers and document structure

- A logical line that is equal to `BEGIN:CARD` under ASCII case-insensitive
  comparison, with no other characters whatsoever, is a **begin marker**.
  Likewise `END:CARD` is an **end marker**. So `begin:card` and `End:Card`
  are markers, but `END:CARD ` (trailing space), ` END:CARD` (impossible
  anyway — leading space folds, §3), and `BEGIN:CARDS` are not markers; a
  non-marker line is processed as a property line (§6) or rejected by the
  structure rules below, exactly as if the marker spelling were coincidental.
- A document is a sequence of zero or more cards. **Outside** a card, every
  non-blank logical line must be a begin marker; any other non-blank logical
  line there — including an end marker with no open card — is an error:
  `line N: expected BEGIN:CARD`.
- **Inside** a card, a begin marker is an error: `line N: nested
  BEGIN:CARD`. An end marker closes the card. Every other non-blank logical
  line inside a card is a property line (§6).
- End of input while a card is open is an error: `line B: unterminated
  card`, where `B` is the physical line number of that card's begin marker.
- A card containing no property lines is valid and parses to an empty dict.
- The returned list preserves document order of the cards.

## 6. Property lines

- A property line is split at its **first** colon (U+003A): the key is
  everything before that colon and the raw value is everything after it (the
  raw value may be empty). This split happens on the raw logical line,
  before any escape processing; escape sequences are recognized only inside
  the raw value (§7). A property line containing no colon at all is an
  error: `line N: missing colon`.
- The key must be non-empty and must consist only of ASCII letters, ASCII
  digits, and hyphen (`-`); anything else — including spaces, tabs,
  underscores, or non-ASCII characters — is an error: `line N: invalid key`.
- Keys are ASCII case-insensitive. The parser stores and reports every key
  in lowercase, and §8's duplicate rule compares keys case-insensitively.
- Nothing is ever trimmed. Whitespace anywhere in the raw value — leading,
  trailing, or around separators — is content and is preserved verbatim.

## 7. Values: escape sequences and multi-value fields

The raw value is scanned once, left to right:

- A backslash (`\`) begins an escape sequence of exactly two characters.
  The valid escapes and their decoded results are:
  - `\\` → one backslash
  - `\n` → one LF (U+000A). Only lowercase `n` is valid here; `\N` is not
    an escape.
  - `\;` → one semicolon, which does **not** act as a separator
  - `\:` → one colon (valid, though unescaped colons after the property
    line's first colon are also literal)
  - A backslash followed by any other character, or a backslash that is the
    final character of the raw value, is an error: `line N: bad escape`.
- An unescaped semicolon (`;`) is a **separator**: it ends the current value
  part and starts the next one.
- The property's parts are the decoded parts in order. A raw value with no
  unescaped semicolon yields exactly one part. An empty raw value yields
  exactly one part, the empty string — so a property line `note:` parses to
  the list `[""]`. Empty parts are preserved wherever they occur:
  `a;;b` yields `["a", "", "b"]`, and a trailing unescaped separator yields
  a final empty part.
- Every character that is not part of an escape sequence or an unescaped
  separator is preserved verbatim: all Unicode characters, tabs, spaces, and
  lone CRs (§2) included. The parser performs no Unicode normalization and
  no case changes on values.

## 8. Card assembly: duplicates and ordering

- Within one card, the first property line with a given key creates the
  entry `key → parts`. Every later property line whose key is the same under
  case-insensitive comparison **appends** its parts, in order, to that
  existing list.
- The card dict's key order is the order of each key's first occurrence.
  The value list order is encounter order.
- Cards are independent: the same key in two different cards creates two
  unrelated entries.

## 9. Errors — complete list

The document is processed from the start; the first error encountered is
raised as `CardParseError` and processing stops. The complete set of
messages (with `N`/`B` per §2 and §5):

| Message | Condition |
|---|---|
| `line 1: continuation before any line` | first physical line starts with a space (§3) |
| `line N: expected BEGIN:CARD` | non-blank, non-begin-marker logical line outside a card (§5) |
| `line N: nested BEGIN:CARD` | begin marker inside an open card (§5) |
| `line B: unterminated card` | end of input with a card still open; B = its begin marker's line (§5) |
| `line N: missing colon` | property line with no colon (§6) |
| `line N: invalid key` | empty key or key with a character outside `[A-Za-z0-9-]` (§6) |
| `line N: bad escape` | invalid or truncated escape sequence in a value (§7) |
