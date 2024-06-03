import sqlite3
import os


def create_db_if_not_exists(db_path):
    """
    Ensure the database file and its directory exist.

    Args:
        db_path (str): Path to the SQLite database.
    """
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def update_file_names_in_db(file_names, db_path):
    """
    Update the file names in a SQLite database.

    Args:
        file_names (list): List of file names to update.
        db_path (str): Path to the SQLite database.
    """
    create_db_if_not_exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Start a transaction
    cursor.execute("BEGIN TRANSACTION")

    # Delete rows not in the new file list
    cursor.execute(
        "DELETE FROM images WHERE path NOT IN ({seq})".format(
            seq=",".join(["?"] * len(file_names))
        ),
        file_names,
    )

    # Insert new files, ignoring duplicates
    cursor.executemany(
        "INSERT OR IGNORE INTO images (path) VALUES (?)",
        [(file_name,) for file_name in file_names],
    )

    # Commit the transaction
    conn.commit()
    conn.close()

    print(f"Database updated with paths of all images in {db_path}")


import os


def search_existing_files(directory, formats):
    """
    Search for existing files in the given directory with the specified formats.

    Args:
        directory (str): Directory to search for files.
        formats (list): List of file formats to search for.

    Returns:
        list: List of full path names of the found files.
    """
    file_names = []
    for root, dirs, files in os.walk(directory):
        with os.scandir(root) as entries:
            for entry in entries:
                if entry.is_file() and any(
                    entry.name.lower().endswith(format) for format in formats
                ):
                    file_names.append(entry.path)
    return file_names


def universal_search():
    # Define the directory to search
    directory_to_search = os.getenv("LOCAL_IMAGE_DIR", "/Users/bytedance/dev/img")

    # Search for files
    file_names = search_existing_files(directory_to_search, [".png", ".jpg", ".jpeg"])

    # Update file names in SQLite database
    update_file_names_in_db(file_names, "db/image_index.db")


if __name__ == "__main__":
    universal_search()
