from __future__ import annotations

import sqlite3
from pathlib import Path


DATABASE_DIR = Path("data")
DATABASE_PATH = DATABASE_DIR / "knowledge.db"


class Database:
    """
    Gestionnaire de la base SQLite du Knowledge Engine.
    """

    def __init__(self) -> None:

        DATABASE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self._create_tables()

    def _create_tables(self) -> None:

        cursor = self.connection.cursor()

        # =====================================================
        # Documents
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                source TEXT NOT NULL,

                url TEXT NOT NULL,

                identifier TEXT,

                published_at TEXT,

                language TEXT,

                document_type TEXT,

                publisher TEXT,

                content TEXT,

                description TEXT,

                crop TEXT,

                culture TEXT,

                country TEXT,

                zone_geographique TEXT,

                author TEXT,

                dataset_filename TEXT
            )
            """
        )

        # =====================================================
        # Auteurs
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS authors (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                document_id INTEGER NOT NULL,

                name TEXT NOT NULL,

                FOREIGN KEY(document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE
            )
            """
        )

        # =====================================================
        # Mots-clés
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                document_id INTEGER NOT NULL,

                keyword TEXT NOT NULL,

                FOREIGN KEY(document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE
            )
            """
        )

        # =====================================================
        # Pièces jointes
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attachments (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                document_id INTEGER NOT NULL,

                url TEXT NOT NULL,

                filename TEXT,

                mime_type TEXT,

                file_type TEXT,

                description TEXT,

                checksum TEXT,

                local_path TEXT,

                FOREIGN KEY(document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE
            )
            """
        )

        self.connection.commit()

    def cursor(self) -> sqlite3.Cursor:
        return self.connection.cursor()

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()


database = Database()
