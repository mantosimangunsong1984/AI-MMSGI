import sqlite3
from datetime import datetime
from pathlib import Path


class ChatHistoryService:

    def __init__(self):

        # ==================================================
        # Database Location
        # ==================================================

        self.db_path = Path(
            "storage/database/maia_chat.db"
        )

        # Pastikan folder database tersedia
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        self.create_tables()


    # ======================================================
    # Database Connection
    # ======================================================

    def connect(self):

        return sqlite3.connect(
            self.db_path
        )



    # ======================================================
    # Create Tables
    # ======================================================

    def create_tables(self):

        conn = self.connect()
        cursor = conn.cursor()


        # Conversation Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TEXT
            )
            """
        )


        # Message Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TEXT,

                FOREIGN KEY(conversation_id)
                REFERENCES conversations(id)
            )
            """
        )


        conn.commit()
        conn.close()



    # ======================================================
    # Create New Conversation
    # ======================================================

    def create_conversation(
        self,
        title="New Chat"
    ):

        conn = self.connect()
        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO conversations
            (
                title,
                created_at
            )
            VALUES (?,?)
            """,
            (
                title,
                datetime.now().isoformat()
            )
        )


        conversation_id = cursor.lastrowid


        conn.commit()
        conn.close()


        return conversation_id



    # ======================================================
    # Save Message
    # ======================================================

    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ):


        conn = self.connect()
        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO messages
            (
                conversation_id,
                role,
                content,
                created_at
            )
            VALUES (?,?,?,?)
            """,
            (
                conversation_id,
                role,
                content,
                datetime.now().isoformat()
            )
        )


        conn.commit()
        conn.close()



    # ======================================================
    # Get Conversation History
    # ======================================================

    def get_history(
        self,
        conversation_id: int
    ):


        conn = self.connect()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT
                role,
                content,
                created_at

            FROM messages

            WHERE conversation_id=?

            ORDER BY id ASC
            """,
            (
                conversation_id,
            )
        )


        rows = cursor.fetchall()


        conn.close()


        messages = []


        for row in rows:

            messages.append(
                {
                    "role": row[0],
                    "content": row[1],
                    "created_at": row[2]
                }
            )


        return messages