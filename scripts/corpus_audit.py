"""Validate the standalone claim-centered evidence map and bibliography.

The audit is intentionally conservative.  It proves internal bindings and locked
corpus obligations; it does not prove that the literature search is exhaustive or
that source interpretation is independently correct.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import json
import hashlib
import math
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
LOCKED_CORPUS_SIZE = 97
CORPUS_REQUIRED = {
    "record_id", "bib_key", "title", "year", "stratum", "role",
    "publication_evidence", "reading_depth", "evidence_object",
    "claim_ceiling", "source_basis", "source_url_or_access_note",
    "access_date", "verification_status", "included",
}
EXTRACTION_REQUIRED = {
    "extraction_id", "record_id", "bib_key", "source_location",
    "source_url_or_access_note", "verification_date", "evidence_object",
    "observation", "transformation_model", "oracle_or_policy",
    "claim_ceiling", "counter_history", "evidence_grade", "reading_depth",
    "verification_status", "inference_limit",
}
SOURCE_LOCATION_REQUIRED = {
    "record_id", "bib_key", "title", "consumed_source_url", "representation",
    "locations", "reading_boundary", "publication_or_version_evidence",
    "access_date", "offline_full_text", "verification_route", "boundary_note",
    "content_check_status", "fulltext_url", "content_check_date",
}
SEARCH_PROVENANCE_REQUIRED = {
    "record_id", "bib_key", "title", "discovery_route", "seed_or_slice",
    "selection_basis", "source_basis", "date", "denominator_scope",
    "reconstruction_status",
}
BIB_VERIFY_REQUIRED = {
    "record_id", "bib_key", "title", "publication_status",
    "canonical_identifier", "canonical_record_url", "metadata_basis",
    "verification_date", "version_status", "included_status",
    "status_check_scope", "notes",
}
EXCLUDED_REQUIRED = {
    "bib_key", "title", "status", "official_record_url", "decision", "reason",
    "checked_date", "downstream_cleanup", "boundary",
}
VALID_STRATA = {
    "review_and_method", "android_artifact", "third_party_library",
    "supply_chain", "ai_mediated",
}
VALID_ROLES = {"primary_or_system", "secondary_or_method"}
VALID_PUBLICATION = {"venue_recorded", "preprint_record", "technical_method_report"}
VALID_DEPTH = {"full_or_selected_source", "publisher_abstract_or_selected_source"}
MATRIX_DIMS = [
    "android_repackaging", "component_version", "supply_chain_provenance",
    "authorization_policy", "behavioral_assurance", "ai_mediated_workflow",
    "claim_ceiling_binding",
]
GENERIC_OBSERVATION_PREFIXES = (
    "The work organizes, reviews, or methodologically structures",
    "The work analyzes Android artifacts using the feature family indicated by its title and venue record",
    "The work analyzes library regions, families, versions, updates, or vulnerability links",
    "The work reports repository, signing, attestation, transparency, build, CI, or package-ecosystem evidence",
    "The work reports generated-code, assistant interaction, dependency recommendation, mobile generation, privacy, or security evidence",
)


def read_csv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), set(reader.fieldnames or [])


def parse_bib(text):
    entries = []
    i = 0
    while True:
        match = re.search(r"@(\w+)\{([^,]+),", text[i:])
        if not match:
            break
        entry_type, key = match.group(1).lower(), match.group(2).strip()
        start = i + match.end()
        pos, depth = start, 1
        while pos < len(text) and depth:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        if depth:
            raise ValueError(f"unbalanced bibliography entry {key}")
        block = text[start:pos - 1]
        fields = {}
        for fm in re.finditer(r"(?m)^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*\{", block):
            name = fm.group(1).lower()
            cursor, field_depth = fm.end(), 1
            begin = cursor
            while cursor < len(block) and field_depth:
                if block[cursor] == "{":
                    field_depth += 1
                elif block[cursor] == "}":
                    field_depth -= 1
                cursor += 1
            fields[name] = block[begin:cursor - 1].strip()
        entries.append({"type": entry_type, "key": key, "fields": fields})
        i = pos
    return entries


def nonblank(row, required):
    return [c for c in required if not row.get(c, "").strip()]


def duplicates(values):
    counts = Counter(values)
    return sorted(k for k, v in counts.items() if v > 1)


def normalize_bibliographic_text(value):
    """Normalize BibTeX/plain-text titles for conservative equality checks."""
    value = value.replace(r"\&", "&").replace(r"\_", "_").replace("---", "-").replace("--", "-")
    # Remove simple LaTeX accent/formatting wrappers while retaining their text.
    value = re.sub(r"\\[A-Za-z]+\s*\{([^{}]*)\}", r"\1", value)
    value = value.replace("{", "").replace("}", "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def nonindependent_status(value):
    """Recognize explicit single-extractor disclosure, not a spelling ritual."""
    tokens = {t.strip().lower() for t in value.split(';')}
    if tokens & {'independent', 'independent=true', 'independent_coding', 'dual_coding'}:
        return False
    return 'single_extractor' in tokens or any(t.endswith('not_independent') for t in tokens)


def review_coverage_status(rows):
    """Direct means all seven cells are 1; P is partial, ? is unresolved.

    Empty observed witnesses do not imply a gap when an unresolved row could
    become a witness. This is bookkeeping, not source-content validation.
    """
    values = [[r[d] for d in MATRIX_DIMS] for r in rows]
    if any(v not in {'0', 'P', '1', '?'} for row in values for v in row):
        raise ValueError('invalid review coverage cell')
    lower = any(all(v == '1' for v in row) for row in values)
    upper = any(all(v in {'1', '?'} for v in row) for row in values)
    return 'covered' if lower else ('undetermined' if upper else 'gap')


def specific_content_locator(locator):
    """Accept numbered PDF pages or numbered primary-HTML sections, not access claims."""
    if 'linked full text or selected' in locator:
        return False
    return bool(re.search(r'PDF pp?\.\s*\d|HTML Sections?\s+\d', locator))


def content_check_counts(rows):
    """Count scoped and selected readings without upgrading legacy depth labels."""
    statuses = Counter(r.get('content_check_status') for r in rows)
    selected = statuses['selected_fulltext_checked']
    scoped = statuses['complete_scope_checked']
    return {
        'selected_fulltext_checked_records': selected,
        'complete_scope_checked_records': scoped,
        'content_checked_records': selected + scoped,
        'legacy_not_reverified_records': statuses['legacy_not_reverified'],
    }


CODING_FIELDS = ('evidence_object', 'observation', 'transformation_model',
                 'oracle_or_policy', 'claim_ceiling', 'counter_history', 'inference_limit')


def field_evidence_summary(rows, extractions, source_locations, source_readings):
    """Check declared field bindings, not whether a reader understood the source.

    Only records with seven located fields enter this supplementary denominator.
    Inherited content statuses are not silently promoted to full recoding.
    """
    extraction = {r['bib_key']: r for r in extractions}
    locations = {r['bib_key']: r for r in source_locations}
    readings = {}
    for row in source_readings:
        key = row['bib_key']
        if key in readings or key not in extraction:
            raise ValueError('duplicate or unbound source reading')
        if (row['fulltext_url'] != locations[key]['fulltext_url'] or
                row['reading_scope'] != 'retrieved_pdf_locator_binding' or
                row['extractor'] != 'AI-assisted single extractor; not independent' or
                not re.fullmatch(r'[0-9a-f]{64}', row['source_sha256'])):
            raise ValueError('source reading lacks exact representation boundary')
        pages = int(row['pdf_page_count'])
        if not 1 <= pages <= 10000:
            raise ValueError('invalid retrieved PDF page count')
        readings[key] = (row['source_sha256'], pages)
    seen = set()
    for row in rows:
        key, field = row['bib_key'], row['field']
        if (key, field) in seen or key not in extraction or field not in CODING_FIELDS:
            raise ValueError('duplicate or unbound field evidence')
        seen.add((key, field))
        if row['coded_value'] != extraction[key][field]:
            raise ValueError('stale field evidence: ' + key + '/' + field)
        if (not specific_content_locator(row['source_location']) or
                row['fulltext_url'] != locations[key]['fulltext_url'] or
                locations[key]['content_check_status'] != 'complete_scope_checked'):
            raise ValueError('field evidence lacks bound scoped fulltext: ' + key)
        if key not in readings or row['source_sha256'] != readings[key][0]:
            raise ValueError('field evidence lacks exact source version: ' + key)
        # Physical PDF indices, not printed folios or section numbers. This
        # bounds a declared locator; it does not verify the cited page's meaning.
        match = re.search(r'\bPDF\s+pp?\.\s*([\d\s,\-\u2013]+)(?=[:;(])', row['source_location'])
        if match is None:
            raise ValueError('field evidence needs physical PDF pages: ' + key)
        for part in match.group(1).strip().split(','):
            span = re.fullmatch(r'\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?\s*', part)
            if span is None:
                raise ValueError('invalid physical PDF page locator: ' + key)
            start, end = int(span.group(1)), int(span.group(2) or span.group(1))
            if not 1 <= start <= end <= readings[key][1]:
                raise ValueError('field evidence page outside retrieved PDF: ' + key)
        if row['basis'] not in {'source_report', 'analytical_classification'} or not row['evidence_note'].strip():
            raise ValueError('field evidence lacks interpretation boundary')
    keys = {key for key, _ in seen}
    if keys != set(readings):
        raise ValueError('source readings and located recodings differ')
    if any((key, field) not in seen for key in keys for field in CODING_FIELDS):
        raise ValueError('incomplete seven-field recoding')
    return {'located_field_rows': len(seen), 'located_recoded_records': len(keys),
            'total_coding_fields': len(extractions) * len(CODING_FIELDS),
            'records_without_supplementary_field_bindings': len(extractions) - len(keys),
            'semantic_interpretation_verified_by_code': False}


def recoding_transition_summary(transitions, rechecks, extractions, source_readings):
    """Bind historical rechecks to a newer located recoding without rewriting history.

    This checks an explicitly declared transition, not the truth of either ceiling.
    A changed historical value, current value, source version or date breaks it.
    """
    history = {r['bib_key']: r for r in rechecks}
    current = {r['bib_key']: r for r in extractions}
    readings = {r['bib_key']: r for r in source_readings}
    bound = {}
    for row in transitions:
        key = row['bib_key']
        if key in bound or key not in history or key not in current or key not in readings:
            raise ValueError('duplicate or unbound recoding transition')
        old, new, reading = history[key], current[key], readings[key]
        if (row['historical_recheck_id'] != old['recheck_id'] or
                row['previous_ceiling'] != old['rechecked_ceiling'] or
                row['current_ceiling'] != new['claim_ceiling'] or
                row['previous_ceiling'] == row['current_ceiling'] or
                row['source_sha256'] != reading['source_sha256'] or
                row['recoding_date'] != new['verification_date'] or
                row['recoding_date'] != reading['read_date'] or
                not re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['recoding_date']) or
                row['recoding_date'] <= old['date']):
            raise ValueError('broken historical-to-current recoding binding: ' + key)
        bound[key] = row['current_ceiling']
    return bound


def semantic_reading_summary(rows, extractions, source_readings):
    """Bind explicit reader assessments to sources/fields, not certify understanding."""
    extracted = {r['bib_key']: r for r in extractions}
    sources = {r['bib_key']: r for r in source_readings}
    seen = set()
    for row in rows:
        key = row.get('bib_key')
        if key in seen or key not in extracted or key not in sources:
            raise ValueError('duplicate or unbound semantic-reading assessment')
        seen.add(key)
        digest = hashlib.sha256('\x1f'.join(extracted[key][f] for f in CODING_FIELDS).encode('utf-8')).hexdigest()
        if (row.get('source_sha256') != sources[key]['source_sha256'] or
                row.get('fields_sha256') != digest):
            raise ValueError('stale semantic-reading source or fields: ' + key)
        date = row.get('assessment_date', '')
        if (not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date) or
                date < sources[key]['read_date'] or
                row.get('reading_extent') != 'complete_retrieved_pdf_and_seven_fields' or
                row.get('independent') != 'false'):
            raise ValueError('invalid semantic-reading boundary: ' + key)
    return {'declared_complete_seven_field_codings': len(seen),
            'acquired_records_without_complete_coding': len(sources) - len(seen),
            'semantic_interpretation_verified_by_code': False,
            'independent_second_coder': False}


def main(out=None) -> int:
    corpus, corpus_fields = read_csv("data/corpus.csv")
    extractions, extraction_fields = read_csv("data/study_extractions.csv")
    field_evidence, _ = read_csv('data/field_evidence.csv')
    source_readings, _ = read_csv('data/source_readings.csv')
    semantic_readings, _ = read_csv('data/semantic_readings.csv')
    recoding_transitions, _ = read_csv('data/recoding_transitions.csv')
    reviews, _ = read_csv("data/review_gap_matrix.csv")
    rechecks, _ = read_csv("data/source_rechecks.csv")
    screening, _ = read_csv("data/screening_ledger.csv")
    source_locations, source_location_fields = read_csv("data/source_locations.csv")
    search_provenance, search_provenance_fields = read_csv("data/search_provenance.csv")
    bib_verify, bib_verify_fields = read_csv("data/bibliography_verification.csv")
    excluded, excluded_fields = read_csv("data/excluded_publications.csv")
    unresolved_leads, _ = read_csv("data/unresolved_leads.csv")
    resolved_leads, _ = read_csv("data/resolved_leads.csv")
    claims, _ = read_csv("data/synthesis_claims.csv")
    material_claims, material_claim_fields = read_csv("claim_evidence_ledger.csv")
    external_resources, _ = read_csv("external_resources.csv")
    pilot_records, _ = read_csv("data/records.csv")
    pilot_extractions, _ = read_csv("data/extractions.csv")
    pilot_coverage, _ = read_csv("data/coverage.csv")
    bib_entries = parse_bib((ROOT / "data/references.bib").read_text(encoding="utf-8"))

    errors = []
    schema_pairs = [
        ("corpus", CORPUS_REQUIRED, corpus_fields),
        ("extraction", EXTRACTION_REQUIRED, extraction_fields),
        ("source-location", SOURCE_LOCATION_REQUIRED, source_location_fields),
        ("search-provenance", SEARCH_PROVENANCE_REQUIRED, search_provenance_fields),
        ("bibliography-verification", BIB_VERIFY_REQUIRED, bib_verify_fields),
        ("excluded-publication", EXCLUDED_REQUIRED, excluded_fields),
    ]
    for label, required, found in schema_pairs:
        if not required <= found:
            errors.append(f"missing {label} columns: {sorted(required - found)}")

    keys = [r.get("bib_key", "").strip() for r in corpus]
    ids = [r.get("record_id", "").strip() for r in corpus]
    bib_keys = [e["key"] for e in bib_entries]
    extraction_keys = [r.get("bib_key", "").strip() for r in extractions]
    extraction_ids = [r.get("extraction_id", "").strip() for r in extractions]
    for label, values in (
        ("corpus bib_key", keys), ("record_id", ids),
        ("bibliography key", bib_keys), ("extraction bib_key", extraction_keys),
        ("extraction_id", extraction_ids),
    ):
        if duplicates(values):
            errors.append(f"duplicate {label}: {duplicates(values)}")
    active_key_set = set(keys)
    if active_key_set != set(bib_keys) or active_key_set != set(extraction_keys):
        errors.append("corpus, bibliography, and extraction key sets are not identical")
    if len(corpus) != LOCKED_CORPUS_SIZE:
        errors.append(f"expected {LOCKED_CORPUS_SIZE} retained records, found {len(corpus)}")

    bib_by_key = {e["key"]: e for e in bib_entries}
    corpus_by_key = {r["bib_key"]: r for r in corpus}
    extraction_by_key = {r['bib_key']: r for r in extractions}
    corpus_by_id = {r["record_id"]: r for r in corpus}
    for line_no, row in enumerate(corpus, 2):
        missing = nonblank(row, CORPUS_REQUIRED)
        if missing:
            errors.append(f"corpus line {line_no}: blank required fields {missing}")
        if row.get("stratum") not in VALID_STRATA:
            errors.append(f"corpus line {line_no}: invalid stratum")
        if row.get("role") not in VALID_ROLES:
            errors.append(f"corpus line {line_no}: invalid role")
        if row.get("publication_evidence") not in VALID_PUBLICATION:
            errors.append(f"corpus line {line_no}: invalid publication evidence")
        if row.get("reading_depth") not in VALID_DEPTH:
            errors.append(f"corpus line {line_no}: invalid reading depth")
        if row.get("included") != "true":
            errors.append(f"corpus line {line_no}: included must be true")
        if not row.get("source_url_or_access_note", "").startswith(("https://", "http://")):
            errors.append(f"corpus line {line_no}: direct scholarly/official source URL missing")
        if "not recorded" in row.get("source_url_or_access_note", "").lower():
            errors.append(f"corpus line {line_no}: placeholder source locator remains")
        try:
            year = int(row.get("year", ""))
            if not 2000 <= year <= 2030:
                errors.append(f"corpus line {line_no}: implausible year {year}")
        except ValueError:
            errors.append(f"corpus line {line_no}: invalid year")
        entry = bib_by_key.get(row.get("bib_key"), {})
        typ = entry.get("type")
        fields = entry.get("fields", {})
        if normalize_bibliographic_text(fields.get("title", "")) != normalize_bibliographic_text(row.get("title", "")):
            errors.append(f"corpus line {line_no}: bibliography title mismatch")
        if fields.get("year", "").strip() != row.get("year", "").strip():
            errors.append(f"corpus line {line_no}: bibliography year mismatch")
        if row.get("publication_evidence") == "venue_recorded" and typ == "misc":
            errors.append(f"corpus line {line_no}: venue-recorded work is still misc in bibliography")
        if row.get("publication_evidence") == "preprint_record" and typ != "misc":
            errors.append(f"corpus line {line_no}: preprint status disagrees with bibliography type")

    primary = sum(r["role"] == "primary_or_system" for r in corpus)
    secondary = sum(r["role"] == "secondary_or_method" for r in corpus)
    primary_venue_recorded = sum(
        r["role"] == "primary_or_system" and r["publication_evidence"] == "venue_recorded"
        for r in corpus
    )
    if not 60 <= primary <= 140:
        errors.append(f"primary/system count {primary} outside 60--140")
    if primary_venue_recorded < 60:
        errors.append(f"only {primary_venue_recorded} primary/system records have venue publication evidence; at least 60 required")
    if secondary < 12:
        errors.append(f"only {secondary} review/method records; at least 12 required")

    for line_no, row in enumerate(extractions, 2):
        missing = nonblank(row, EXTRACTION_REQUIRED)
        if missing:
            errors.append(f"extraction line {line_no}: blank required fields {missing}")
        c = corpus_by_key.get(row.get("bib_key", ""), {})
        if row.get("record_id") != c.get("record_id"):
            errors.append(f"extraction line {line_no}: record/key mismatch")
        if row.get("reading_depth") != c.get("reading_depth"):
            errors.append(f"extraction line {line_no}: stale reading depth")
        if row.get("source_url_or_access_note") != c.get("source_url_or_access_note"):
            errors.append(f"extraction line {line_no}: stale source locator")
        if any(row.get("observation", "").startswith(prefix) for prefix in GENERIC_OBSERVATION_PREFIXES):
            errors.append(f"extraction line {line_no}: templated observation remains")
        if not nonindependent_status(row.get("verification_status", "")):
            errors.append(f"extraction line {line_no}: independence boundary missing")

    # Exact one-to-one source-location and retrospective-provenance bindings.
    for label, ledger, required, key_name in (
        ("source-location", source_locations, SOURCE_LOCATION_REQUIRED, "bib_key"),
        ("search-provenance", search_provenance, SEARCH_PROVENANCE_REQUIRED, "bib_key"),
    ):
        ledger_keys = [r.get(key_name, "").strip() for r in ledger]
        ledger_ids = [r.get("record_id", "").strip() for r in ledger]
        if len(ledger) != len(corpus):
            errors.append(f"{label} ledger has {len(ledger)} rows; expected {len(corpus)}")
        if duplicates(ledger_keys) or duplicates(ledger_ids):
            errors.append(f"duplicate {label} key or record id")
        if set(ledger_keys) != active_key_set or set(ledger_ids) != set(ids):
            errors.append(f"{label} ledger does not bind exactly to the retained corpus")
        for line_no, row in enumerate(ledger, 2):
            # Unknown content has no invented PDF URL or inspection date.
            # The columns are required by the schema; values are conditional.
            value_required = required - {'fulltext_url', 'content_check_date'} if label == 'source-location' else required
            missing = nonblank(row, value_required)
            if missing:
                errors.append(f"{label} line {line_no}: blank fields {missing}")
            c = corpus_by_key.get(row.get("bib_key", ""), {})
            if row.get("record_id") != c.get("record_id"):
                errors.append(f"{label} line {line_no}: record/key mismatch")
            if label == "source-location":
                if row.get("consumed_source_url") != c.get("source_url_or_access_note"):
                    errors.append(f"source-location line {line_no}: locator disagrees with corpus")
                boundary = row.get("reading_boundary", "")
                if "not necessarily cover-to-cover" not in boundary and "no full-text completeness claim" not in boundary:
                    errors.append(f"source-location line {line_no}: reading boundary is not explicit")
                content_status = row.get('content_check_status')
                if content_status not in {'legacy_not_reverified', 'selected_fulltext_checked', 'complete_scope_checked'}:
                    errors.append(f'source-location line {line_no}: invalid content-check status')
                if content_status != 'legacy_not_reverified':
                    if not row.get('fulltext_url', '').startswith('https://'):
                        errors.append(f'source-location line {line_no}: checked full-text URL missing')
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', row.get('content_check_date', '')):
                        errors.append(f'source-location line {line_no}: checked date missing')
                    locator = row.get('locations', '')
                    if not specific_content_locator(locator):
                        errors.append(f'source-location line {line_no}: checked content has no specific page/section locator')
                    if extraction_by_key.get(row['bib_key'], {}).get('verification_date') != row.get('content_check_date'):
                        errors.append(f'source-location line {line_no}: extraction/check date mismatch')
                    extracted_locator = extraction_by_key.get(row['bib_key'], {}).get('source_location', '')
                    if locator not in extracted_locator:
                        errors.append(f'source-location line {line_no}: extraction does not bind checked content locator')
                    urls = set(re.findall(r'https://[^\s;]+', extracted_locator))
                    if urls and urls != {row.get('fulltext_url')}:
                        errors.append(f'source-location line {line_no}: extraction has conflicting fulltext URL')
            else:
                if "not a complete database-search hit denominator" not in row.get("denominator_scope", ""):
                    errors.append(f"search-provenance line {line_no}: denominator boundary missing")
                if "retrospective" not in row.get("reconstruction_status", ""):
                    errors.append(f"search-provenance line {line_no}: retrospective status missing")

    # Version/status ledger and excluded-publication quarantine.
    verify_keys = [r.get("bib_key", "") for r in bib_verify]
    if len(bib_verify) != len(corpus) or set(verify_keys) != active_key_set or duplicates(verify_keys):
        errors.append("bibliography-verification ledger does not bind one-to-one to active corpus")
    identifiers = []
    for line_no, row in enumerate(bib_verify, 2):
        missing = nonblank(row, BIB_VERIFY_REQUIRED)
        if missing:
            errors.append(f"bibliography-verification line {line_no}: blank fields {missing}")
        c = corpus_by_key.get(row.get("bib_key", ""), {})
        if row.get("record_id") != c.get("record_id") or row.get("title") != c.get("title"):
            errors.append(f"bibliography-verification line {line_no}: record/title mismatch")
        if row.get("publication_status") != c.get("publication_evidence"):
            errors.append(f"bibliography-verification line {line_no}: publication status mismatch")
        canonical_url = row.get("canonical_record_url", "").strip()
        if not canonical_url.startswith("https://"):
            errors.append(f"bibliography-verification line {line_no}: canonical URL is not HTTPS")
        joined = " ".join(row.values()).lower()
        if "withdrawn" in joined or "retracted" in joined:
            errors.append(f"bibliography-verification line {line_no}: excluded status in active corpus")
        if row.get("included_status") != "eligible_current_record":
            errors.append(f"bibliography-verification line {line_no}: active eligibility marker missing")
        identifiers.append(row.get("canonical_identifier", ""))
        entry = bib_by_key.get(row.get("bib_key"), {})
        doi = entry.get("fields", {}).get("doi", "").strip().lower()
        identifier = row.get("canonical_identifier", "").strip().lower()
        if doi:
            if identifier != "doi:" + doi:
                errors.append(f"bibliography-verification line {line_no}: DOI identifier mismatch")
            if canonical_url.lower() != "https://doi.org/" + doi:
                errors.append(f"bibliography-verification line {line_no}: DOI canonical URL mismatch")
        elif not identifier:
            errors.append(f"bibliography-verification line {line_no}: stable identifier missing")
    if duplicates(identifiers):
        errors.append(f"duplicate canonical identifier: {duplicates(identifiers)}")

    if not excluded:
        errors.append("excluded-publication ledger is empty")
    excluded_keys = {r.get("bib_key", "") for r in excluded}
    if excluded_keys & active_key_set:
        errors.append(f"excluded publication leaked into active corpus: {sorted(excluded_keys & active_key_set)}")
    for line_no, row in enumerate(excluded, 2):
        missing = nonblank(row, EXCLUDED_REQUIRED)
        if missing:
            errors.append(f"excluded-publication line {line_no}: blank fields {missing}")
        if row.get("status") not in {"withdrawn", "retracted", "superseded_ineligible"}:
            errors.append(f"excluded-publication line {line_no}: unsupported status")
        if not row.get("official_record_url", "").startswith("https://"):
            errors.append(f"excluded-publication line {line_no}: official status URL missing")
    if "sbomslr2025" not in excluded_keys:
        errors.append("withdrawn SBOM record is absent from exclusion ledger")
    active_text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in [
        "data/references.bib", "data/corpus.csv", "data/study_extractions.csv",
        "data/review_gap_matrix.csv", "data/source_rechecks.csv", "data/synthesis_claims.csv",
    ])
    if "sbomslr2025" in active_text:
        errors.append("withdrawn SBOM key remains in an active synthesis dataset")

    if unresolved_leads:
        errors.append(f"{len(unresolved_leads)} stale unresolved leads remain")
    expected_resolved = {"staticandroid", "sufatrio", "xuandroid"}
    if {r.get("bib_key") for r in resolved_leads} != expected_resolved:
        errors.append("resolved-leads ledger does not contain the three previously stale leads")

    if len(reviews) < 12:
        errors.append(f"closest-review matrix has only {len(reviews)} rows")
    review_keys = [r.get('bib_key', '') for r in reviews]
    secondary_keys = {r['bib_key'] for r in corpus if r['role'] == 'secondary_or_method'}
    if duplicates(review_keys) or set(review_keys) != secondary_keys:
        errors.append('review matrix does not bind one-to-one to secondary/method corpus')
    direct_all = []
    location_by_key = {r['bib_key']: r for r in source_locations}
    for line_no, row in enumerate(reviews, 2):
        values = [row.get(d, "") for d in MATRIX_DIMS]
        if any(v not in {"0", "P", "1", "?"} for v in values):
            errors.append(f"review matrix line {line_no}: invalid cell")
        if all(v == "1" for v in values):
            direct_all.append(row.get("bib_key"))
        if row.get("bib_key") not in corpus_by_key:
            errors.append(f"review matrix line {line_no}: unknown bib key")
        elif row.get('record_id') != corpus_by_key[row['bib_key']]['record_id']:
            errors.append(f'review matrix line {line_no}: record/key mismatch')
        source_status = location_by_key.get(row.get('bib_key'), {}).get('content_check_status')
        if any(v in {'1', 'P'} for v in values) and source_status == 'legacy_not_reverified':
            errors.append(f'review matrix line {line_no}: positive coverage lacks checked full-text basis')
        if '0' in values and source_status != 'complete_scope_checked':
            errors.append(f'review matrix line {line_no}: absence lacks complete scoped reading')
    if direct_all:
        errors.append(f"direct all-dimension prior(s) require repositioning: {direct_all}")

    threshold = math.ceil(0.15 * len(extractions))
    if len(rechecks) < threshold:
        errors.append(f"only {len(rechecks)} rechecks; need at least {threshold}")
    recheck_keys = [r.get("bib_key", "") for r in rechecks]
    if duplicates(recheck_keys):
        errors.append("duplicate source recheck key")
    if set(recheck_keys) - active_key_set:
        errors.append("recheck references unknown corpus key")
    if any(r.get("independent") != "false" for r in rechecks):
        errors.append("same-process rechecks must not be labeled independent")
    try:
        recoding_bindings = recoding_transition_summary(recoding_transitions, rechecks, extractions, source_readings)
    except (KeyError, ValueError) as error:
        errors.append(str(error))
        recoding_bindings = {}
    for line_no, row in enumerate(rechecks, 2):
        key = row.get('bib_key', '')
        if row.get('record_id') != corpus_by_key.get(key, {}).get('record_id'):
            errors.append(f'source recheck line {line_no}: record/key mismatch')
        if (row.get('rechecked_ceiling') != extraction_by_key.get(key, {}).get('claim_ceiling') and
                key not in recoding_bindings):
            errors.append(f'source recheck line {line_no}: stale rechecked ceiling')
        source = row.get("source_url_or_access_note", "")
        if not source.startswith(("https://", "http://")) or "not recorded" in source.lower():
            errors.append(f"source recheck line {line_no}: direct source locator missing")
        if source != corpus_by_key.get(row.get("bib_key", ""), {}).get("source_url_or_access_note"):
            errors.append(f"source recheck line {line_no}: source locator disagrees with corpus")

    included_screen = [r.get("bib_key") for r in screening if r.get("decision") == "include"]
    if set(included_screen) != active_key_set or duplicates(included_screen):
        errors.append("screening ledger does not include every retained key exactly once")
    excluded_screen = {r.get("bib_key") for r in screening if r.get("decision", "").startswith("exclude")}
    if not excluded_keys <= excluded_screen:
        errors.append("excluded-publication ledger is not reflected in screening decisions")

    for claim_no, claim in enumerate(claims, 2):
        supporting = {k.strip() for k in claim.get("supporting_bib_keys", "").split(";") if k.strip()}
        if not supporting or supporting - active_key_set:
            errors.append(f"synthesis claim line {claim_no}: missing or unknown support")
        for required in ("synthesis_id", "proposition", "claim_levels", "evidence_strata", "counter_history", "boundary"):
            if not claim.get(required, "").strip():
                errors.append(f"synthesis claim line {claim_no}: blank {required}")

    metadata_warnings = []
    dois = []
    for entry in bib_entries:
        f, key, typ = entry["fields"], entry["key"], entry["type"]
        for required in ("author", "title", "year"):
            if not f.get(required):
                errors.append(f"bibliography {key}: missing {required}")
        if typ == "article" and not f.get("journal"):
            errors.append(f"bibliography {key}: article missing journal")
        if typ == "inproceedings":
            for required in ("booktitle", "publisher", "address"):
                if not f.get(required):
                    errors.append(f"bibliography {key}: proceedings entry missing {required}")
            if not f.get("pages") and not f.get("numpages"):
                metadata_warnings.append(f"{key}: no pages or numpages recorded")
        if f.get("doi"):
            dois.append(f["doi"].lower())
    if duplicates(dois):
        errors.append(f"duplicate DOI in bibliography: {duplicates(dois)}")

    required_material = {"claim_id", "claim", "source_or_input", "proof_or_checker", "raw_result", "maturity", "fresh_recheck_and_boundary"}
    if not required_material <= material_claim_fields:
        errors.append(f"missing material-claim columns: {sorted(required_material - material_claim_fields)}")
    material_ids = [r.get("claim_id", "").strip() for r in material_claims]
    if duplicates(material_ids) or not material_ids:
        errors.append("duplicate or empty material claim ids")
    for line_no, row in enumerate(material_claims, 2):
        missing = nonblank(row, required_material)
        if missing:
            errors.append(f"material claim line {line_no}: blank fields {missing}")

    # Historical pilot is retained only as a finite semantics regression fixture.
    sbom = next((r for r in pilot_records if r.get("record_id") == "R07"), None)
    if not sbom or sbom.get("publication_evidence") != "withdrawn" or sbom.get("main_corpus_included") != "false":
        errors.append("historical R07 withdrawal/exclusion status is not enforced")
    for row in [r for r in pilot_extractions if r.get("record_id") == "R07"] + [r for r in pilot_coverage if r.get("record_id") == "R07"]:
        if "withdraw" not in " ".join(str(v) for v in row.values()).lower():
            errors.append("historical R07 row does not disclose withdrawal status")
            break

    scholarly_resources = [r for r in external_resources if r.get("resource_type", "").startswith("scholarly_")]
    if len(scholarly_resources) != len(corpus):
        errors.append("external-resources scholarly rows do not match corpus size")
    resource_urls = [r.get("scholarly_or_official_url", "") for r in scholarly_resources]
    if Counter(resource_urls) != Counter(r["source_url_or_access_note"] for r in corpus):
        errors.append("external-resources scholarly URLs do not bind exactly to corpus")

    strata = Counter(r["stratum"] for r in corpus)
    depths = Counter(r["reading_depth"] for r in corpus)
    publication = Counter(r["publication_evidence"] for r in corpus)
    try:
        located_coding = field_evidence_summary(field_evidence, extractions, source_locations, source_readings)
    except (ValueError, KeyError) as exc:
        errors.append(str(exc))
        located_coding = {'status': 'invalid', 'semantic_interpretation_verified_by_code': False}
    try:
        semantic_coding = semantic_reading_summary(semantic_readings, extractions, source_readings)
    except (ValueError, KeyError) as exc:
        errors.append(str(exc))
        semantic_coding = {'status': 'invalid', 'semantic_interpretation_verified_by_code': False}
    summary = {
        "status": "passed" if not errors else "failed",
        "records": len(corpus),
        "unique_bib_keys": len(active_key_set),
        "bibliography_entries": len(bib_entries),
        "bibliography_verification_records": len(bib_verify),
        "excluded_publications": len(excluded),
        "claim_level_extractions": len(extractions),
        "closest_review_records": len(reviews),
        "direct_all_dimension_reviews": direct_all,
        "review_direct_coverage_status": review_coverage_status(reviews) if all(
            r.get(d) in {'0', 'P', '1', '?'} for r in reviews for d in MATRIX_DIMS
        ) else 'invalid',
        "review_unknown_cells": sum(r.get(d) == '?' for r in reviews for d in MATRIX_DIMS),
        **content_check_counts(source_locations),
        'supplementary_located_coding': located_coding,
        'declared_semantic_coding': semantic_coding,
        'historical_to_current_recoding_transitions': len(recoding_bindings),
        "source_rechecks": len(rechecks),
        "source_recheck_fraction": len(rechecks) / len(extractions) if extractions else 0,
        "source_rechecks_independent": False,
        "screening_rows": len(screening),
        "source_location_records": len(source_locations),
        "retained_record_provenance_records": len(search_provenance),
        "unresolved_leads": len(unresolved_leads),
        "resolved_leads": len(resolved_leads),
        "templated_observations": sum(
            any(r.get("observation", "").startswith(prefix) for prefix in GENERIC_OBSERVATION_PREFIXES)
            for r in extractions
        ),
        "placeholder_source_locators": sum("not recorded" in r.get("source_url_or_access_note", "").lower() for r in corpus),
        "material_claims": len(material_claims),
        "venue_recorded": publication["venue_recorded"],
        "active_preprints": publication["preprint_record"],
        "technical_method_reports": publication["technical_method_report"],
        "primary_or_system": primary,
        "primary_venue_recorded": primary_venue_recorded,
        "secondary_or_method": secondary,
        "reading_depth": dict(sorted(depths.items())),
        "strata": dict(sorted(strata.items())),
        "bibliography_optional_metadata_warnings": metadata_warnings,
        "errors": errors,
        "boundary": (
            "The checks validate supplied ledgers, exact active/excluded key quarantine, record-level publication-status metadata, "
            "review bindings, recheck coverage, and retained corpus counts. They do not prove search exhaustiveness, "
            "a comprehensive retraction-registry search, independent source interpretation, detector performance, or worldwide novelty."
            " A source URL, complete row, legacy reading-depth label or lack of an observed all-dimension row does not certify content or a gap."
        ),
    }
    results = Path(out) if out is not None else ROOT / "results"
    results.mkdir(parents=True, exist_ok=True)
    (results / "corpus_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    tex = results / "tex"
    tex.mkdir(exist_ok=True)
    macros = (
        f"\\newcommand{{\\CorpusWorks}}{{{len(corpus)}}}\n"
        f"\\newcommand{{\\VenueRecordedWorks}}{{{summary['venue_recorded']}}}\n"
        f"\\newcommand{{\\PrimaryWorks}}{{{primary}}}\n"
        f"\\newcommand{{\\PrimaryVenueWorks}}{{{primary_venue_recorded}}}\n"
        f"\\newcommand{{\\SecondaryWorks}}{{{secondary}}}\n"
        f"\\newcommand{{\\ReviewMatrixWorks}}{{{len(reviews)}}}\n"
        f"\\newcommand{{\\SourceRechecks}}{{{len(rechecks)}}}\n"
        f"\\newcommand{{\\SourceRecheckPercent}}{{{100 * len(rechecks) / len(extractions):.1f}}}\n"
        f"\\newcommand{{\\AndroidWorks}}{{{strata['android_artifact']}}}\n"
        f"\\newcommand{{\\TPLWorks}}{{{strata['third_party_library']}}}\n"
        f"\\newcommand{{\\SupplyWorks}}{{{strata['supply_chain']}}}\n"
        f"\\newcommand{{\\AIWorks}}{{{strata['ai_mediated']}}}\n"
        f"\\newcommand{{\\UniqueCitedWorks}}{{{len(corpus)}}}\n"
        f"\\newcommand{{\\FullSelectedWorks}}{{{depths['full_or_selected_source']}}}\n"
        f"\\newcommand{{\\AbstractSelectedWorks}}{{{depths['publisher_abstract_or_selected_source']}}}\n"
        f"\\newcommand{{\\SourceCheckedWorks}}{{{summary['content_checked_records']}}}\n"
        f"\\newcommand{{\\SourceUncheckedWorks}}{{{summary['legacy_not_reverified_records']}}}\n"
        f"\\newcommand{{\\LocatedRecodedRecords}}{{{located_coding.get('located_recoded_records', 0)}}}\n"
        f"\\newcommand{{\\LocatedCodingFields}}{{{located_coding.get('located_field_rows', 0)}}}\n"
        f"\\newcommand{{\\TotalCodingFields}}{{{located_coding.get('total_coding_fields', 0)}}}\n"
        f"\\newcommand{{\\WithoutLocatedCoding}}{{{located_coding.get('records_without_supplementary_field_bindings', 0)}}}\n"
        f"\\newcommand{{\\SemanticReadWorks}}{{{semantic_coding.get('declared_complete_seven_field_codings', 0)}}}\n"
        f"\\newcommand{{\\AcquiredUnreadWorks}}{{{semantic_coding.get('acquired_records_without_complete_coding', 0)}}}\n"
    )
    if not errors:
        (tex / "corpus_counts.tex").write_text(macros, encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    raise SystemExit(main(parser.parse_args().out))
