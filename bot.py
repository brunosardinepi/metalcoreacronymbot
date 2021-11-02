from collections import OrderedDict
from environ import secrets
import praw
import re
import sqlite3


UNKNOWN_ACRONYM = "I don't know this acronym. Please reply with an answer and I'll save it for next time."

def main():
    reddit = praw.Reddit(
        client_id=secrets['client_id'],
        client_secret=secrets['client_secret'],
        password=secrets['reddit_password'],
        user_agent="/u/MetalcoreAcronymBot",
        username=secrets['reddit_username'],
    )
    print(f"Logged in as: {reddit.user.me()}")

    for comment in reddit.subreddit('Metalcore').stream.comments(skip_existing=True):
        if comment.author == reddit.user.me():
            continue
        # Check for "!MetalcoreAcronymBot"
        print(f"comment.body = {comment.body}")
        if comment.body == "!MetalcoreAcronymBot":
            # When we find it, we're going to look at the immediate parent comment
            # of the comment that has our summon.
            # Get the acronyms from the parent comment.
            acronyms = re.findall(r'[A-Z0-9]{2,}', comment.parent().body)
            print(f"acronyms = {acronyms}")
            acronyms = [i for i in acronyms if not i.isnumeric()]
            print(f"acronyms = {acronyms}")
            if acronyms:
                # Check if we have a conversion for the acronym. If so, reply with it.
                con = sqlite3.connect('metalcore.db')
                cur = con.cursor()
                answers = OrderedDict()
                for acronym in acronyms:
                    acronym = acronym.upper()
                    answers[acronym] = []
                    cur.execute("SELECT * FROM acronyms WHERE acronym=:acronym", {
                        'acronym': acronym,
                    })
                    results = cur.fetchall()
                    if results:
                        for result in results:
                            answers[acronym].append(result[1])

                reply = ""
                for acronym, names in answers.items():
                    if not names:
                        reply += f"I don't know what **{acronym}** is.\n\n"
                    else:
                        reply += f"**{acronym}** could mean {', or '.join(names)}.\n\n"

                reply += "---\n\n"
                reply += "^(To add an acronym, reply with `!MetalcoreAcronymBot add ACRONYM:NAME`)\n\n"
                reply += "^(To delete an acronym, reply with `!MetalcoreAcronymBot delete ACRONYM:NAME`)"
            else:
                reply = "I don't see any acronyms in all caps in the parent comment."
            comment.reply(reply)

        elif comment.body.startswith("!MetalcoreAcronymBot add"):
            # Check if this is the right syntax.
            addition = comment.body.split("!MetalcoreAcronymBot add")[1].strip()
            acronym = addition.split(":", 1)[0].strip().upper()
            name = addition.split(":", 1)[1].strip()

            # Add it to the database.
            con = sqlite3.connect('metalcore.db')
            cur = con.cursor()
            cur.execute("INSERT INTO acronyms values (:acronym, :name)", {
                'acronym': acronym,
                'name': name,
            })
            con.commit()
            con.close()
            comment.reply("Thanks! I added your acronym to the database.")

        elif comment.body.startswith("!MetalcoreAcronymBot delete"):
            # Check if this is the right syntax.
            deletion = comment.body.split("!MetalcoreAcronymBot delete")[1].strip()
            acronym = deletion.split(":", 1)[0].strip().upper()
            name = deletion.split(":", 1)[1].strip()

            # Delete it from the database.
            con = sqlite3.connect('metalcore.db')
            cur = con.cursor()
            cur.execute("DELETE FROM acronyms WHERE EXISTS (SELECT * FROM acronyms WHERE acronym=:acronym AND name=:name)", {
                'acronym': acronym,
                'name': name,
            })
            con.commit()
            con.close()
            comment.reply("Thanks! I deleted that acronym from the database.")

if __name__ == "__main__":
    main()
