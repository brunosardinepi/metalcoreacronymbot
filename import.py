import sqlite3


def main():
    with open("acronyms.txt", "r") as file:
        for line in file.readlines():
            print(line)
            acronym = line.split("=")[0].strip().upper()
            name = line.split("=")[1].strip().title()
            print(f"acronym = {acronym}")
            print(f"name = {name}")

            con = sqlite3.connect('metalcore.db')
            cur = con.cursor()
            # Check if it already exists.
            cur.execute("SELECT * FROM acronyms WHERE EXISTS (SELECT * FROM acronyms WHERE acronym=:acronym AND name=:name)", {
                'acronym': acronym,
                'name': name,
            })
            results = cur.fetchall()
            print(f"results = {results}")
            if not results:
                cur.execute("INSERT INTO acronyms values (:acronym, :name)", {
                    'acronym': acronym,
                    'name': name,
                })
                con.commit()
            con.close()


if __name__ == "__main__":
    main()
