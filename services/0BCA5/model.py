import sqlite3, os.path

def create_table():
    if os.path.exists('./db/data.db'):
        return 
    else:
        # Create table
        try:
            sqliteConnection = sqlite3.connect('./db/data.db')
            sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS books (
                                            id VARCHAR(255) PRIMARY KEY,
                                            name VARCHAR(255) NOT NULL,
                                            city VARCHAR(255) NOT NULL,
                                            place VARCHAR(255) NOT NULL,
                                            vanNumber VARCHAR(255) NOT NULL,
                                            cardID VARCHAR(255) NOT NULL);'''

            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print("SQLite table created")

            cursor.close()
            
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if sqliteConnection:
                sqliteConnection.close()
                print("sqlite connection is closed")
                    
            
def book(id, name, city, place, vanNumber, cardID):
    # Insert data
    try:
        sqliteConnection = sqlite3.connect('./db/data.db')
        sqlite_insert_query = f'''INSERT INTO books VALUES ('{id}', '{name}', '{city}', '{place}', '{vanNumber}', '{cardID}');'''

        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_insert_query)
        sqliteConnection.commit()
        print("Data successfully inserted", cursor.rowcount)
        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("sqlite connection is closed")
            
def check(id):
    elements = []
    data = []
    #Check data
    try:
        sqliteConnection = sqlite3.connect('./db/data.db')
        
        # Oooh no SQL injection

        sqlite_select_query = f'''SELECT * FROM books WHERE id = '{id}';'''
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for row in records:
            elements.append(row[0])
            elements.append(row[1])
            elements.append(row[2])
            elements.append(row[3])
            elements.append(row[4])
            elements.append(row[5])
            data.append(elements)
            elements = []   
        
        cursor.close()
        
        return data
    
    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("sqlite connection is closed")