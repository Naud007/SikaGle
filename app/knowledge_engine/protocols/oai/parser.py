from __future__ import annotations

from bs4 import BeautifulSoup

from .record import OAIRecord


class OAIParser:
    """
    Parse les réponses XML OAI-PMH et les convertit
    en objets OAIRecord.
    """

    def parse_records(
        self,
        soup: BeautifulSoup,
    ) -> list[OAIRecord]:

        records: list[OAIRecord] = []

        for record in soup.find_all("record"):

            header = record.find("header")

            if header is None:
                continue

            identifier = ""

            identifier_tag = header.find("identifier")

            if identifier_tag:
                identifier = (
                    identifier_tag.text.strip()
                )

            datestamp = None

            datestamp_tag = header.find(
                "datestamp"
            )

            if datestamp_tag:
                datestamp = (
                    datestamp_tag.text.strip()
                )

            set_specs = [
                tag.text.strip()
                for tag in header.find_all(
                    "setSpec"
                )
            ]

            metadata = {}
            raw_identifiers = []

            metadata_tag = record.find(
                "metadata"
            )

            if metadata_tag:

                for child in metadata_tag.find_all(
                    recursive=True
                ):

                    if (
                        not child.name
                        or child == metadata_tag
                    ):
                        continue

                    key = child.name.split(":")[-1]

                    value = child.get_text(
                        " ",
                        strip=True,
                    )

                    if not value:
                        continue

                    metadata.setdefault(
                        key,
                        [],
                    ).append(value)

                    if key == "identifier":
                        raw_identifiers.append(
                            value
                        )

            records.append(
                OAIRecord(
                    identifier=identifier,
                    datestamp=datestamp,
                    set_specs=set_specs,
                    metadata=metadata,
                    raw_identifiers=raw_identifiers,
                )
            )

        return records

    def parse_resumption_token(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        """
        Extrait le resumptionToken de la réponse OAI.
        """

        token = soup.find(
            "resumptionToken"
        )

        if token is None:
            return None

        value = token.get_text(
            strip=True,
        )

        return value or None
