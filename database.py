import sqlite3

DB_NAME = "training.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ==========================================
    # Banque d'activités
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            format TEXT,
            duration INTEGER,
            description TEXT
        )
    """)

    # ==========================================
    # Segments des séances
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            segment_order INTEGER NOT NULL,
            name TEXT,
            duration INTEGER NOT NULL,
            intensity TEXT,
            FOREIGN KEY(activity_id)
                REFERENCES activities(id)
                ON DELETE CASCADE
        )
    """)

    # ==========================================
    # Calendrier
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            activity_id INTEGER NOT NULL,
            FOREIGN KEY(activity_id)
                REFERENCES activities(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# ACTIVITÉS
# ==========================================

def add_activity(name, activity_type, activity_format,
                  duration, description):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO activities
        (name, type, format, duration, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        activity_type,
        activity_format,
        duration,
        description
    ))

    activity_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return activity_id


def get_activities():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            type,
            format,
            duration,
            description
        FROM activities
        ORDER BY name
    """)

    activities = cursor.fetchall()

    conn.close()

    return activities


def delete_activity(activity_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Suppression des segments
    cursor.execute("""
        DELETE FROM session_segments
        WHERE activity_id = ?
    """, (activity_id,))

    # Suppression de l'activité
    cursor.execute("""
        DELETE FROM activities
        WHERE id = ?
    """, (activity_id,))

    conn.commit()
    conn.close()


# ==========================================
# SEGMENTS
# ==========================================

def add_segment(activity_id, segment_order,
                name, duration, intensity):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO session_segments
        (activity_id, segment_order, name, duration, intensity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        activity_id,
        segment_order,
        name,
        duration,
        intensity
    ))

    conn.commit()
    conn.close()


def get_segments(activity_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            segment_order,
            name,
            duration,
            intensity
        FROM session_segments
        WHERE activity_id = ?
        ORDER BY segment_order
    """, (activity_id,))

    segments = cursor.fetchall()

    conn.close()

    return segments