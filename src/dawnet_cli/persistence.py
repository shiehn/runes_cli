import sqlite3
import uuid
import click

# Database setup
db_path = 'docker_containers.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# CONTAINER STATUS ###############################

# Create table for storing container PIDs
# Update the container_pids table schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS container_pids
(id INTEGER PRIMARY KEY,
 pid INTEGER,
 container_id TEXT,
 remote_name TEXT,
 status INTEGER)
''')
conn.commit()


# Existing UUID Token Table and Functions...

# Updated save_pid function
def save_pid(pid, container_id, remote_name, status):
    cursor.execute("INSERT INTO container_pids (pid, container_id, remote_name, status) VALUES (?, ?, ?, ?)",
                   (pid, container_id, remote_name, status))
    conn.commit()


# New update_status function
def update_status(container_id, status):
    cursor.execute("UPDATE container_pids SET status = ? WHERE container_id = ?", (status, container_id))
    conn.commit()


# New list_pids function
def list_pids(status=None):
    if status is None:
        cursor.execute("SELECT id, pid, container_id, remote_name, status FROM container_pids")
    else:
        cursor.execute("SELECT id, pid, container_id, remote_name, status FROM container_pids WHERE status = ?",
                       (status,))

    return cursor.fetchall()


# CONNECTION TOKEN ###############################

# Extend the database schema to include a table for the UUID token
cursor.execute('''
CREATE TABLE IF NOT EXISTS uuid_token
(id INTEGER PRIMARY KEY, token TEXT)''')
conn.commit()


def generate_uuid():
    return str(uuid.uuid4())


def save_token_to_db(token):
    # Clear the existing token before saving the new one
    cursor.execute("DELETE FROM uuid_token")
    # Insert the new token
    cursor.execute("INSERT INTO uuid_token (token) VALUES (?)", (token,))
    conn.commit()


def read_token_from_db():
    cursor.execute("SELECT token FROM uuid_token LIMIT 1")
    row = cursor.fetchone()
    return row[0] if row else None


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
        return str(uuid_obj) == uuid_to_test and uuid_obj.version == version
    except ValueError:
        return False


def set_or_update_token(token=None):
    if token is None:
        token = generate_uuid()

    if not is_valid_uuid(token):
        click.echo(f"Token: {token}, is not a valid UUID.")
        return None

    save_token_to_db(token)
    return token
