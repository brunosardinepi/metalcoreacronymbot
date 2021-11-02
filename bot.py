from collections import OrderedDict
from environ import secrets
import praw
import re
import sqlite3


def main():
    """Convert acronyms in /r/Metalcore into band/album names"""

    # Create the PRAW Reddit instance.
    # The 'secrets' dictionary is in a file called environ.py in the root directory and
    # is excluded from the git repo. Create it yourself with your own PRAW/Reddit values.
    reddit = praw.Reddit(
        client_id=secrets['client_id'],
        client_secret=secrets['client_secret'],
        password=secrets['reddit_password'],
        user_agent="/u/MetalcoreAcronymBot",
        username=secrets['reddit_username'],
    )
    print(f"Logged in as: {reddit.user.me()}")

    # Watch a stream of comments from /r/Metalcore.
    for comment in reddit.subreddit('Metalcore').stream.comments(skip_existing=True):
        # Ignore comments from this bot.
        if comment.author == reddit.user.me():
            continue
        # Check for "!MetalcoreAcronymBot" in the comment.
        print(f"comment.body = {comment.body}")
        if comment.body == "!MetalcoreAcronymBot":
            # In the parent comment, find words that are all caps and
            # have at least two letters.
            acronyms = re.findall(r'[A-Z0-9]{2,}', comment.parent().body)
            print(f"acronyms = {acronyms}")
            # Remove acronyms that are all numbers, which are grabbed by mistake.
            acronyms = [i for i in acronyms if not i.isnumeric()]
            print(f"acronyms = {acronyms}")
            if acronyms:
                # Connect to the sqlite3 database.
                con = sqlite3.connect('metalcore.db')
                cur = con.cursor()

                # Create an empty dict to hold our answers so we can use them in a reply.
                answers = OrderedDict()
                for acronym in acronyms:
                    # Convert the acronmy to uppercase as a safety measure.
                    acronym = acronym.upper()

                    # Create a list to store multiple database results for each acronym.
                    answers[acronym] = []

                    # Search the database for acronym values.
                    cur.execute("SELECT * FROM acronyms WHERE acronym=:acronym", {
                        'acronym': acronym,
                    })
                    results = cur.fetchall()
                    if results:
                        for result in results:
                            # Append each result to the list for this acronym.
                            answers[acronym].append(result[1])

                reply = ""
                # Loop through our acronym, name results and create a reply.
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
            # Send the reply to Reddit.
            comment.reply(reply)

        elif comment.body.startswith("!MetalcoreAcronymBot add"):
            # Convert the comment body into something readable.
            addition = comment.body.split("!MetalcoreAcronymBot add")[1].strip()
            acronym = addition.split(":", 1)[0].strip().upper()
            name = addition.split(":", 1)[1].strip()

            # Connect to the sqlite3 database.
            con = sqlite3.connect('metalcore.db')
            cur = con.cursor()
            # Add the acronym, name pair to the database.
            cur.execute("INSERT INTO acronyms values (:acronym, :name)", {
                'acronym': acronym,
                'name': name,
            })
            # Save the changes.
            con.commit()
            # Close the connection.
            con.close()
            # Send a thank you note.
            comment.reply("Thanks! I added your acronym to the database.")

        elif comment.body.startswith("!MetalcoreAcronymBot delete"):
            # Convert the comment body into something readable.
            deletion = comment.body.split("!MetalcoreAcronymBot delete")[1].strip()
            acronym = deletion.split(":", 1)[0].strip().upper()
            name = deletion.split(":", 1)[1].strip()

            # Connect to the sqlite3 database.
            con = sqlite3.connect('metalcore.db')
            cur = con.cursor()
            # Delete the acronym, name pair from the database.
            cur.execute("DELETE FROM acronyms WHERE EXISTS (SELECT * FROM acronyms WHERE acronym=:acronym AND name=:name)", {
                'acronym': acronym,
                'name': name,
            })
            # Save the changes.
            con.commit()
            # Close the connection.
            con.close()
            # Send a thank you note.
            comment.reply("Thanks! I deleted that acronym from the database.")

if __name__ == "__main__":
    main()
