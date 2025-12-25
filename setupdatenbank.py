import sqlite3

def setup_database():
    # Erstellt die Datenbank-Datei (PFT.db)
    connection = sqlite3.connect('pft_database.db')
    cursor = connection.cursor()

    # Tabelle für Kategorien (Normalisierung)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Tabelle für Transaktionen (CRUD-Kern)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    connection.commit()
    connection.close()
    print("Datenbank und Tabellen erfolgreich erstellt!")

if __name__ == "__main__":
    setup_database()
