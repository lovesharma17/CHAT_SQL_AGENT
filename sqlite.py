import sqlite3


def main():
    ## Connect to sqlite
    connection = sqlite3.connect("student.db")

    ## Create a cursor object to insert record , create table
    cursor = connection.cursor()

    ## Create the table
    table_info = """
    create table if not exists student(NAME VARCHAR(25) , CLASS VARCHAR(25) , SECTION VARCHAR(25) , MARKS INT)
    """
    cursor.execute(table_info)

    ## Clear the table before inserting new records
    cursor.execute("DELETE FROM student")

    ## Insert some records
    cursor.executemany(
        "INSERT INTO student (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)",
        [
            ('Love',     'Data Science', 'A', 90),
            ('Neha',    'Data Analyst', 'A', 85),
            ('Ananya',   'Data Engineer', 'B', 92),
            ('Reyansh',  'Data Science', 'A', 78),
            ('Saanvi',   'Data Analyst', 'C', 88),
            ('Vihaan',   'Data Science', 'B', 95),
            ('Diya',     'Data Science', 'A', 67),
            ('Arjun',    'Data Analyst', 'C', 81),
            ('Myra',     'Data Science', 'B', 89),
            ('Kabir',    'Data Engineer', 'A', 76),
        ]
    )

    print("The inserted records are")
    data = cursor.execute("""SELECT * FROM student""")
    for row in data:
        print(row)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
