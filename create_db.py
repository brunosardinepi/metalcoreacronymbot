import sqlite3


def main():
    con = sqlite3.connect('metalcore.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE acronyms (acronym, name)")
    con.commit()
    con.close()

if __name__ == "__main__":
    main()
