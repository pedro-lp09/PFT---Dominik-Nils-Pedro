import sqlite3

def add_category(name):
    connection = sqlite3.connect('pft_database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
    connection.commit()
    connection.close()

def add_transaction(amount, description, date, category_id):
    connection = sqlite3.connect('pft_database.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO transactions (amount, description, date, category_id)
        VALUES (?, ?, ?, ?)
    ''', (amount, description, date, category_id))
    connection.commit()
    connection.close()

def get_all_transactions():
    connection = sqlite3.connect('pft_database.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT t.id, t.amount, t.description, t.date, c.name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
    ''')
    rows = cursor.fetchall()
    connection.close()
    return rows

def delete_transaction(transaction_id):
    connection = sqlite3.connect('pft_database.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    connection.commit()
    connection.close()
