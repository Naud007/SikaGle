class SourceFormatter:
    """
    Formate les métadonnées des documents
    en une liste de sources lisibles.
    """

    def format(
        self,
        metadatas: list[dict],
    ) -> list[dict]:

        sources = []

        seen = set()

        for metadata in metadatas:

            title = metadata.get(
                "title",
                "Document sans titre",
            )

            url = metadata.get(
                "url",
            )

            source = metadata.get(
                "source",
            )

            author = metadata.get(
                "author",
            )

            published_at = metadata.get(
                "published_at",
            )

            key = (
                title,
                url,
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "title": title,
                    "source": source,
                    "author": author,
                    "published_at": published_at,
                    "url": url,
                }
            )

        return sources
