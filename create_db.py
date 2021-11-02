import sqlite3


def main():
    """Create the initial table in sqlite3"""

    con = sqlite3.connect('metalcore.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE acronyms (acronym, name)")
    con.commit()
    con.close()

if __name__ == "__main__":
    main()
