import csv
import hashlib
import io
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx
from defusedxml import ElementTree
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import WatchlistEntryRecord, WatchlistIngestionRecord

DEMO_UNSC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<CONSOLIDATED_LIST>
  <INDIVIDUALS>
    <INDIVIDUAL>
      <DATAID>UNSC-DEMO-001</DATAID>
      <FIRST_NAME>Kim</FIRST_NAME>
      <SECOND_NAME>Jong</SECOND_NAME>
      <THIRD_NAME>Un</THIRD_NAME>
      <NATIONALITY><VALUE>KP</VALUE></NATIONALITY>
      <INDIVIDUAL_ALIAS><ALIAS_NAME>Kim Jong-Un</ALIAS_NAME></INDIVIDUAL_ALIAS>
    </INDIVIDUAL>
  </INDIVIDUALS>
  <ENTITIES>
    <ENTITY>
      <DATAID>UNSC-DEMO-002</DATAID>
      <FIRST_NAME>North Korea Trading Corp</FIRST_NAME>
      <ENTITY_ALIAS><ALIAS_NAME>DPRK Trading Corp</ALIAS_NAME></ENTITY_ALIAS>
    </ENTITY>
  </ENTITIES>
</CONSOLIDATED_LIST>
"""

DEMO_SEBI_RECORDS = [
    {
        "name": "Viktor Petrov Capital Advisors",
        "order_reference": "SEBI-DEMO-2026-001",
        "category": "debarred_entity",
        "reason": "Market manipulation watchlist demo record",
        "country": "IN",
    },
    {
        "name": "North Korea Trading Corp",
        "order_reference": "SEBI-DEMO-2026-002",
        "category": "restricted_entity",
        "reason": "Cross-listing demo record",
        "country": "KP",
    },
]


def normalize_name(value: str | None) -> str:
    return " ".join((value or "").casefold().replace(".", " ").replace(",", " ").split())


def ingest_demo_feeds(session: Session) -> dict:
    uns = ingest_unsc_xml(session, DEMO_UNSC_XML, source="UNSC_DEMO")
    sebi = ingest_sebi_records(session, DEMO_SEBI_RECORDS, source="SEBI_DEMO")
    return {"sources": [uns, sebi], "mode": "demo-production-shape"}


def ingest_official_feeds(session: Session) -> dict:
    settings = get_settings()
    sources = [
        ingest_ofac_csv(session, _fetch_text(settings.ofac_sdn_csv_url), source="OFAC_SDN"),
        ingest_unsc_xml(session, _fetch_text(settings.unsc_consolidated_xml_url), source="UNSC"),
        ingest_generic_sanctions_xml(session, _fetch_text(settings.eu_consolidated_xml_url), source="EU"),
    ]
    return {"sources": sources, "mode": "official-feed-refresh"}


def ingest_ofac_csv(session: Session, csv_text: str, source: str = "OFAC_SDN") -> dict:
    errors: list[str] = []
    loaded = 0
    rows = list(csv.reader(io.StringIO(csv_text)))
    for row in rows:
        if len(row) < 2:
            continue
        uid = row[0].strip()
        name = row[1].strip()
        if not uid or not name:
            errors.append("missing OFAC uid/name")
            continue
        session.merge(
            WatchlistEntryRecord(
                entry_id=_stable_id(source, uid),
                source=source,
                list_name="SDN",
                entity_type=str(row[2]).strip().casefold() if len(row) > 2 and row[2] else "unknown",
                name=name,
                normalized_name=normalize_name(name),
                country=None,
                identifiers={"uid": uid, "program": row[3] if len(row) > 3 else None},
                aliases=[],
                payload={"row": row},
                last_seen_at=datetime.now(UTC),
            )
        )
        loaded += 1
    return _record_ingestion(session, source, "loaded" if not errors else "partial", len(rows), loaded, errors)


def ingest_unsc_xml(session: Session, xml_text: str, source: str = "UNSC") -> dict:
    errors: list[str] = []
    loaded = 0
    seen = 0
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        return _record_ingestion(session, source, "failed", 0, 0, [str(exc)])

    records = []
    for node in root.findall(".//INDIVIDUAL"):
        seen += 1
        records.append(_unsc_entity(node, "individual", source))
    for node in root.findall(".//ENTITY"):
        seen += 1
        records.append(_unsc_entity(node, "entity", source))

    for record in records:
        if not record["name"]:
            errors.append(f"missing name for {record['entry_id']}")
            continue
        session.merge(WatchlistEntryRecord(**record))
        loaded += 1

    status = "loaded" if not errors else "partial"
    return _record_ingestion(session, source, status, seen, loaded, errors)


def ingest_generic_sanctions_xml(session: Session, xml_text: str, source: str) -> dict:
    errors: list[str] = []
    loaded = 0
    seen = 0
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        return _record_ingestion(session, source, "failed", 0, 0, [str(exc)])

    for node in root.iter():
        name = _first_text(node, ["WHOLE_NAME", "NAME", "FIRST_NAME", "nameAlias", "alias", "name"])
        if not name:
            continue
        seen += 1
        entry_value = _first_text(node, ["DATAID", "ID", "logicalId", "id"]) or f"{name}:{seen}"
        session.merge(
            WatchlistEntryRecord(
                entry_id=_stable_id(source, entry_value),
                source=source,
                list_name="CONSOLIDATED",
                entity_type="unknown",
                name=name,
                normalized_name=normalize_name(name),
                country=_first_text(node, ["COUNTRY", "country", "citizenship"]),
                identifiers={"source_id": entry_value},
                aliases=[],
                payload=_element_payload(node),
                last_seen_at=datetime.now(UTC),
            )
        )
        loaded += 1
    return _record_ingestion(session, source, "loaded" if not errors else "partial", seen, loaded, errors)


def ingest_sebi_records(session: Session, rows: list[dict], source: str = "SEBI") -> dict:
    errors: list[str] = []
    loaded = 0
    for row in rows:
        name = str(row.get("name") or row.get("entity_name") or "").strip()
        if not name:
            errors.append("missing name in SEBI row")
            continue
        entry_id = _stable_id(source, row.get("order_reference") or name)
        session.merge(
            WatchlistEntryRecord(
                entry_id=entry_id,
                source=source,
                list_name=str(row.get("category") or "sebi_enforcement"),
                entity_type="entity",
                name=name,
                normalized_name=normalize_name(name),
                country=(str(row.get("country")).upper() if row.get("country") else None),
                identifiers={"order_reference": row.get("order_reference")},
                aliases=[],
                payload=row,
                last_seen_at=datetime.now(UTC),
            )
        )
        loaded += 1

    status = "loaded" if not errors else "partial"
    return _record_ingestion(session, source, status, len(rows), loaded, errors)


def list_watchlist_status(session: Session) -> dict:
    entries = session.query(WatchlistEntryRecord).count()
    ingestions = (
        session.query(WatchlistIngestionRecord).order_by(WatchlistIngestionRecord.created_at.desc()).limit(20).all()
    )
    return {
        "entries": entries,
        "recent_ingestions": [
            {
                "ingestion_id": row.ingestion_id,
                "source": row.source,
                "status": row.status,
                "records_seen": row.records_seen,
                "records_loaded": row.records_loaded,
                "errors": row.errors,
                "created_at": row.created_at,
            }
            for row in ingestions
        ],
    }


def _unsc_entity(node: Any, entity_type: str, source: str) -> dict:
    data_id = _text(node, "DATAID") or uuid4().hex
    name_parts = [
        _text(node, "FIRST_NAME"),
        _text(node, "SECOND_NAME"),
        _text(node, "THIRD_NAME"),
        _text(node, "FOURTH_NAME"),
    ]
    name = " ".join(part for part in name_parts if part).strip()
    aliases = [alias.text.strip() for alias in node.findall(".//ALIAS_NAME") if alias.text and alias.text.strip()]
    country = _text(node, ".//NATIONALITY/VALUE")
    return {
        "entry_id": _stable_id(source, data_id),
        "source": source,
        "list_name": "UNSC_CONSOLIDATED",
        "entity_type": entity_type,
        "name": name,
        "normalized_name": normalize_name(name),
        "country": country.upper() if country else None,
        "identifiers": {"data_id": data_id},
        "aliases": aliases,
        "payload": _element_payload(node),
        "last_seen_at": datetime.now(UTC),
    }


def _record_ingestion(
    session: Session,
    source: str,
    status: str,
    seen: int,
    loaded: int,
    errors: list[str],
) -> dict:
    record = WatchlistIngestionRecord(
        ingestion_id=f"ing_{uuid4().hex}",
        source=source,
        status=status,
        records_seen=seen,
        records_loaded=loaded,
        errors=errors,
        metadata_payload={"loaded_at": datetime.now(UTC).isoformat()},
    )
    session.add(record)
    session.commit()
    return {
        "ingestion_id": record.ingestion_id,
        "source": source,
        "status": status,
        "records_seen": seen,
        "records_loaded": loaded,
        "errors": errors,
    }


def _stable_id(source: str, value: Any) -> str:
    digest = hashlib.sha256(f"{source}:{value}".encode()).hexdigest()[:24]
    return f"wl_{digest}"


def _text(node: Any, path: str) -> str | None:
    found = node.find(path)
    if found is None or found.text is None:
        return None
    return found.text.strip()


def _first_text(node: Any, names: list[str]) -> str | None:
    for name in names:
        direct = node.attrib.get(name)
        if direct:
            return direct.strip()
        for found in node.findall(f".//{name}"):
            if found.text and found.text.strip():
                return found.text.strip()
            value = found.attrib.get("wholeName") or found.attrib.get("name")
            if value:
                return value.strip()
    return None


def _fetch_text(url: str) -> str:
    response = httpx.get(url, timeout=30, follow_redirects=True)
    response.raise_for_status()
    return response.text


def _element_payload(node: Any) -> dict:
    payload: dict[str, Any] = {"tag": node.tag}
    for child in list(node):
        if len(list(child)):
            payload[child.tag] = _element_payload(child)
        else:
            payload[child.tag] = child.text
    return payload
