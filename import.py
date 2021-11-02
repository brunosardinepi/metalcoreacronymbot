import sqlite3


def main():
    """Import the acronyms created by /u/OscarRainy"""

    # Open the list of acronyms that I copy/pasted from /u/OscarRainy.
    with open("acronyms.txt", "r") as file:
        for line in file.readlines():
            # Convert the ACRONYM = NAME line into something readable.
            acronym = line.split("=")[0].strip().upper()
            name = line.split("=")[1].strip().title()

            # Connect to the sqlite3 database.
            con = sqlite3.connect('metalcore.db')
            cur = con.cursor()
            # Check if the acronym, name pair already exists.
            cur.execute("SELECT * FROM acronyms WHERE EXISTS (SELECT * FROM acronyms WHERE acronym=:acronym AND name=:name)", {
                'acronym': acronym,
                'name': name,
            })
            results = cur.fetchall()
            if not results:
                # If the acronym, name pair doesn't exist, create it.
                cur.execute("INSERT INTO acronyms values (:acronym, :name)", {
                    'acronym': acronym,
                    'name': name,
                })
                # Save the changes.
                con.commit()
            # Close the database connection.
            con.close()

if __name__ == "__main__":
    main()
