"""Type/span checks for LLM-extracted atomic claims and hard mismatch checks.

These checks do NOT decide whether a passage semantically entails a claim.
They protect the subsequent relation judge from obvious attribute mismatches.
"""
from __future__ import annotations
from typing import Any

FIELDS = ("entity", "version", "metric", "comparison_baseline", "condition", "time_period")
VALID_QUANTIFIERS = {"typical", "up_to", "at_least", "exact", "unspecified", None}
VALID_OPS = {"=", ">", ">=", "<", "<=", "approx", None}

class ParseError(ValueError):
    pass


def validate_decomposition(claim: str, result: dict[str, Any]) -> dict[str, Any]:
    """Require exact original-text spans and a recognized logical form.

    A failure triggers review/deferral rather than silently trusting bad atoms.
    """
    if result.get("logical_form") != "AND":
        raise ParseError("MVP accepts single claims and AND conjuncts only")
    atoms = result.get("atoms")
    if not isinstance(atoms, list) or not atoms:
        raise ParseError("atoms must be a nonempty list")
    for atom in atoms:
        span = atom.get("span")
        if (not isinstance(span, list) or len(span) != 2 or
            any(not isinstance(x, int) for x in span) or
            span[0] < 0 or span[1] > len(claim) or span[0] >= span[1]):
            raise ParseError("Missing or invalid atomic claim span")
        if claim[span[0]:span[1]] != atom.get("text"):
            raise ParseError("Atomic text does not match original claim span")
        attr = atom.get("attributes")
        if not isinstance(attr, dict):
            raise ParseError("Missing attributes dict")
        if attr.get("quantifier") not in VALID_QUANTIFIERS:
            raise ParseError("Unsupported quantifier")
        if attr.get("operator") not in VALID_OPS:
            raise ParseError("Unsupported numerical operator")
        number = attr.get("value")
        if number is not None and (not isinstance(number, (int, float)) or isinstance(number, bool)):
            raise ParseError("Numeric value must be a number or null")
    return result


def hard_mismatches(claim_attributes: dict[str, Any], evidence_attributes: dict[str, Any]) -> list[str]:
    """Only call attributes mismatched when both are known and disagree.

    A missing attribute is unresolved, not proof of a match. Semantic judgment
    must still decide applicability, including narrow test results vs broad claims.
    """
    issues=[]
    for field in FIELDS:
        c,e=claim_attributes.get(field),evidence_attributes.get(field)
        if c is not None and e is not None and str(c).strip().lower() != str(e).strip().lower():
            issues.append(f"{field}_mismatch")
    cq,eq=claim_attributes.get("quantifier"),evidence_attributes.get("quantifier")
    if cq in {"typical","exact"} and eq == "up_to":
        issues.append("quantifier_scope_mismatch")
    return issues

CLAIM_EXTRACTION_INSTRUCTIONS = '''Extract checkable atomic propositions from the ORIGINAL claim.
Output a JSON object: {"logical_form":"AND", "atoms":[{"span":[start,end],
"text":"exact substring from original claim", "attributes": {
"entity":string|null, "version":string|null, "metric":string|null,
"comparison_baseline":string|null, "operator":"=|>|>=|<|<=|approx"|null,
"value":number|null, "unit":string|null,
"quantifier":"typical|up_to|at_least|exact|unspecified"|null,
"condition":string|null, "time_period":string|null}}]}.
Do not invent missing values. If the logical structure cannot be represented
faithfully, return {"logical_form":"UNSUPPORTED", "atoms":[]}.
The calling code validates every output and defers unsupported cases.
'''

PAIR_RELATION_INSTRUCTIONS = '''For ONE atomic proposition and ONE passage, return JSON with:
{"applies":boolean, "relation":"SUPPORTS|REFUTES|RELATED_NOT_APPLICABLE|IRRELEVANT",
"confidence":float, "mismatch_reason":string|null, "supporting_quote":string|null}.
Check same entity, version, metric, comparison baseline, testing condition,
time period, and whether "up to" versus typical scope differs. A highly
credible but mismatched source does not apply. Do not count merely discussing
the topic as evidence. If information is missing, mark not applicable instead
of guessing. The calling code checks hard attribute mismatches separately.
'''
