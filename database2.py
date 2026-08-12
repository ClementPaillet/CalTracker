import sqlite3


# ============================================================
# CONNEXION À LA BASE
# ============================================================

def get_connection(db_name):
    """
    Ouvre une connexion vers la base de données sélectionnée.
    """

    conn = sqlite3.connect(db_name)

    # Active réellement les contraintes FOREIGN KEY
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# INITIALISATION DE LA BASE
# ============================================================

def init_database(db_name):
    """
    Crée les tables nécessaires si elles n'existent pas encore.
    """

    conn = get_connection(db_name)
    cursor = conn.cursor()

    # ========================================================
    # BANQUE D'ACTIVITÉS
    # ========================================================

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

    # ========================================================
    # SEGMENTS DES SÉANCES
    # ========================================================

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

    # ========================================================
    # CALENDRIER
    # ========================================================

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


# ============================================================
# ACTIVITÉS
# ============================================================

def add_activity(
    db_name,
    name,
    activity_type,
    activity_format,
    duration,
    description
):
    """
    Ajoute une activité dans la base sélectionnée.
    """

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO activities
        (
            name,
            type,
            format,
            duration,
            description
        )
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


def get_activities(db_name):
    """
    Récupère toutes les activités de la base sélectionnée.
    """

    conn = get_connection(db_name)
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


def get_activity(db_name, activity_id):
    """
    Récupère une activité précise.
    """

    conn = get_connection(db_name)
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
        WHERE id = ?
    """, (activity_id,))

    activity = cursor.fetchone()

    conn.close()

    return activity


def delete_activity(db_name, activity_id):
    """
    Supprime une activité.

    Grâce au ON DELETE CASCADE, ses segments et les séances
    correspondantes du calendrier sont également supprimés.
    """

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM activities
        WHERE id = ?
    """, (activity_id,))

    conn.commit()
    conn.close()


# ============================================================
# SEGMENTS
# ============================================================

def add_segment(
    db_name,
    activity_id,
    segment_order,
    name,
    duration,
    intensity
):
    """
    Ajoute un segment à une activité.
    """

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO session_segments
        (
            activity_id,
            segment_order,
            name,
            duration,
            intensity
        )
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


def get_segments(db_name, activity_id):
    """
    Récupère les segments d'une activité.
    """

    conn = get_connection(db_name)
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


# ============================================================
# CALENDRIER
# ============================================================

def get_calendar_activities(db_name, year, month):
    """
    Récupère les activités programmées pour un mois donné.
    """

    import calendar

    conn = get_connection(db_name)
    cursor = conn.cursor()

    start_date = f"{year:04d}-{month:02d}-01"

    last_day = calendar.monthrange(year, month)[1]

    end_date = (
        f"{year:04d}-{month:02d}-{last_day:02d}"
    )

    cursor.execute("""
        SELECT
            calendar.id,
            calendar.date,
            activities.id,
            activities.name,
            activities.type,
            activities.format,
            activities.duration
        FROM calendar
        JOIN activities
            ON calendar.activity_id = activities.id
        WHERE calendar.date BETWEEN ? AND ?
        ORDER BY calendar.date
    """, (
        start_date,
        end_date
    ))

    activities = cursor.fetchall()

    conn.close()

    return activities


def add_to_calendar(
    db_name,
    activity_id,
    selected_date
):
    """
    Ajoute une activité au calendrier.
    """

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO calendar
        (
            date,
            activity_id
        )
        VALUES (?, ?)
    """, (
        selected_date,
        activity_id
    ))

    conn.commit()
    conn.close()


def delete_from_calendar(
    db_name,
    calendar_id
):
    """
    Supprime une activité du calendrier.
    """

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM calendar
        WHERE id = ?
    """, (calendar_id,))

    conn.commit()
    conn.close()