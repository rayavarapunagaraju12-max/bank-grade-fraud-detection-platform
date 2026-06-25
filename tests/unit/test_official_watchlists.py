from compliance.watchlist_ingestion.service import ingest_generic_sanctions_xml, ingest_ofac_csv


def test_ingest_ofac_csv(db_session) -> None:
    result = ingest_ofac_csv(db_session, '123,"Example Sanctioned Person","individual","SDGT"\n')

    assert result["status"] == "loaded"
    assert result["records_loaded"] == 1


def test_ingest_generic_sanctions_xml(db_session) -> None:
    xml = """
    <export>
      <sanctionEntity logicalId="eu-001">
        <nameAlias wholeName="Example Restricted Entity" />
        <citizenship>EU</citizenship>
      </sanctionEntity>
    </export>
    """

    result = ingest_generic_sanctions_xml(db_session, xml, source="EU_TEST")

    assert result["status"] == "loaded"
    assert result["records_loaded"] >= 1
