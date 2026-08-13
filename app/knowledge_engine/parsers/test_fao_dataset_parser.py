from app.knowledge_engine.parsers.fao_dataset_parser import FAODatasetParser


def test_fao_dataset_parser():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:dct="http://purl.org/dc/terms/"
        xmlns:dctypes="http://purl.org/dc/dcmitype/">

        <dctypes:BibliographicResource
            xml:id="AGRIS_TEST_001">

            <dc:title>
                Maize production in Benin
            </dc:title>

            <dc:description>
                Study on maize production and agricultural practices in Benin.
            </dc:description>

            <dc:creator>
                Jean Dupont
            </dc:creator>

            <dc:date>
                2024
            </dc:date>

            <dc:type>
                Article
            </dc:type>

            <dc:subject>
                maize
            </dc:subject>

            <dc:subject>
                agriculture
            </dc:subject>

            <dc:language>
                en
            </dc:language>

            <dc:identifier type="url">
                https://example.org/article/001
            </dc:identifier>

            <dc:coverage>
                Benin
            </dc:coverage>

        </dctypes:BibliographicResource>

    </rdf:RDF>
    """

    parser = FAODatasetParser()

    documents = parser.parse(
        xml_content=xml_content,
        filename="test_agris.xml",
        source_url="https://agris.fao.org/"
    )

    assert len(documents) == 1

    document = documents[0]

    assert document.title == "Maize production in Benin"

    assert document.source == "FAO AGRIS"

    assert document.language == "en"

    assert document.country == "Bénin"

    assert document.crop == "maïs"

    assert str(document.url) == "https://example.org/article/001"

    assert document.published_at is not None

    assert document.document_type == "Article"

    print("\n========================================")
    print("FAO DATASET PARSER : TEST OK")
    print("========================================")
    print(f"Titre    : {document.title}")
    print(f"Pays     : {document.country}")
    print(f"Culture  : {document.crop}")
    print(f"Langue   : {document.language}")
    print(f"URL      : {document.url}")
    print(f"Type     : {document.document_type}")
    print("========================================")