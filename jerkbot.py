#!/usr/bin/env python3

"""
Reddit bot for archiving backpacker comments

It will:
- Get a list of the newest comment/self-post submissions
- Take a screenshot of the linked page
- Upload it to imgur
- Post the screenshot as a comment in the submission

You'll need:
- Python 3
- PRAW (in pip)
- pyimgur (in pip)
- Pillow (in pip)
- selenium (in pip)
- PhantomJS (you can download static builds off their site)
"""

import logging, logging.handlers, os, re, sqlite3, sys
import praw, pyimgur
from PIL import Image
from selenium import webdriver

from config import CONFIG

# fancy logging shit
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

rotate = logging.handlers.RotatingFileHandler(CONFIG["log_file"],
                                              maxBytes=1024*1000,
                                              backupCount=5)
rotate.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
logger.addHandler(rotate)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
logger.addHandler(console)

# make the image dir, parent dir must exist
if not os.path.isdir(CONFIG["image_dir"]):
    os.mkdir(CONFIG["image_dir"])
    logging.info("Created new image_dir: %s" % (CONFIG["image_dir"]))

# db is just for tracking job progess so we don't double up on work
class JerkDB():
    def __init__(self):
        self.db_filename = CONFIG["db_file"]

        if not os.path.isfile(self.db_filename):
            self.init_db()

        self.db = sqlite3.connect(self.db_filename)

    def init_db(self):
        tables = ("create table submissions (name text, url text, status text)",
                  "create table users (name text, status text)")
        db = sqlite3.connect(self.db_filename)
        c = db.cursor()
        for t in tables:
            c.execute(t)
        db.commit()
        db.close()

    def add_submission(self, sub_vars):
        q = "insert into submissions values (?, ?, ?)"
        c = self.db.cursor()
        logging.debug(sub_vars)
        if not self.already_added(sub_vars["name"]):
            c.execute(q, (sub_vars["name"], sub_vars["url"], "pending"))
            logging.info("Added new submission %s as pending" % (sub_vars["name"]))
        self.db.commit()

    def get_pending_submissions(self):
        q = "select * from submissions where status = ?"
        c = self.db.cursor()
        logging.info("Fetching all pending submissions")
        c.execute(q, ("pending",))
        return c.fetchall()

    def already_done(self, name):
        q = "select name from submissions where name = ? and (status = ? or status = ?)"
        c = self.db.cursor()
        c.execute(q, (name, "complete", "failed"))
        if c.fetchone() == None:
            return False
        else:
            return True

    def set_submission_status(self, name, status):
        q = "update submissions set status = ? where name = ?"
        c = self.db.cursor()
        logging.info("Update %s status to %s" % (name, status))
        c.execute(q, (status, name))
        self.db.commit()

    def get_all_submissions(self):
        q = "select * from submissions"
        c = self.db.cursor()
        c.execute(q)
        return c.fetchall()

    def already_added(self, name):
        q = "select name from submissions where name = ?"
        c = self.db.cursor()
        c.execute(q, (name,))
        if c.fetchone() == None:
            return False
        else:
            return True

def should_screenshot(url):
    comment_pattern = "reddit.com/r/\w+/comments/\w+"
    subreddit_pattern = "/%s/" % (CONFIG["subreddit"])

    # we're only interested in comments and self posts
    if re.search(comment_pattern, url, re.I) != None:
        # but not from the subreddit we're submitting to
        if re.search(subreddit_pattern, url, re.I) == None:
            return True

    return False

def is_np(url):
    if re.match("https*://np\.", url):
        return True
    else:
        return False

def get_new_submissions(db):
    reddit = praw.Reddit(user_agent=CONFIG["user_agent"])
    reddit.login(CONFIG["reddit_username"], CONFIG["reddit_password"])
    new_submissions = reddit.get_subreddit(CONFIG["subreddit"]).get_new(limit=CONFIG["result_limit"])
    submissions = [x for x in new_submissions]

    [db.add_submission(vars(x)) for x in submissions]

    return submissions

def take_screenshot(url, name):
    driver = webdriver.PhantomJS(executable_path=CONFIG["phantomjs_exe"])
    filename = os.path.join(CONFIG["image_dir"], "%s.png" % (name))
    driver.set_window_size(*CONFIG["viewport"])
    logging.info("Taking screenshot of %s (%s)" % (name, url))
    driver.get(url)
    driver.get_screenshot_as_file(filename)
    driver.quit()
    return filename

def upload_screenshot(filename):
    imgur = pyimgur.Imgur(client_id=CONFIG["imgur_api_key"])
    uploaded = imgur.upload_image(filename)
    return uploaded.link

def crop_screenshot(filename):
    screenshot = Image.open(filename)
    cropped = screenshot.crop((0, 0, CONFIG["viewport"][0], CONFIG["cropped_height"]))
    cropped_filename = re.sub("\.png$", "-cropped.png", filename)
    cropped.save(cropped_filename)
    return cropped_filename

def mod_submission(db, new):
    """Make sure a submission follows the rules"""

    keys = vars(new)

    # bail out if we already did this one
    if db.already_done(keys["name"]):
        logging.debug("Skip modded %s" % (keys["name"]))
        return

    # TODO: remove submission if user is shitlisted

    # TODO: warn if it's a young account

    # check it is an np link for comment subs
    # if it is, remove it and make a comment
    if should_screenshot(keys["url"]) and not is_np(keys["url"]):
        logging.info("%s is not an np link" % keys["name"])

        # notify user
        # TODO: suggest updated link
        comment = "fam, you need to submit this as an np link. this submission has been removed"
        try:
            if not CONFIG["testing"]:
                new.add_comment(comment)
            logging.info(comment)
        except:
            logging.exception("Error adding comment to %s" % (keys["permalink"]))
            db.set_submission_status(keys["name"], "failed")
            return

        # remove submission
        # TODO: will need a catch on this, maybe roll above into this
        if not CONFIG["testing"]:
            keys["subreddit"].send_message("removed a non-np submission",
                                           "this one: %s" % (keys["permalink"]))
            logging.info("Notified mods")
            new.remove()
            logging.info("Removed submission")

        db.set_submission_status(keys["name"], "complete")

def try_screenshot(db, new):
    keys = vars(new)

    # bail out if we already did this one
    if db.already_done(keys["name"]):
        logging.debug("Skip screenshot %s" % (keys["name"]))
        return False

    # don't bother if it's not a comment outside the sub
    if not should_screenshot(keys["url"]):
        logging.info("Don't need to screenshot %s" % keys["name"])
        db.set_submission_status(keys["name"], "complete")
        return False

    # take and save the screenshot
    try:
        screenie = take_screenshot(keys["url"], keys["name"])
    except:
        logging.exception("Error while taking screenshot of %s", (keys["url"]))
        return False

    # crop it, if required
    if os.path.getsize(screenie) > CONFIG["imgur_max_size"]:
        try:
            cropped = crop_screenshot(screenie)
            screenie = cropped
        except:
            logging.exception("Unable to crop screenshot %s" % (screenie))
            return False
        db.set_submission_status(keys["name"], "cropped")

    # upload to imgur
    try:
        imgur = upload_screenshot(screenie)
    except:
        logging.exception("Could not upload %s" % (screenie))
        return False
    db.set_submission_status(keys["name"], "uploaded")

    # post the link in the submission thread
    comment = "screenshot: %s" % (imgur)
    try:
        if not CONFIG["testing"]:
            new.add_comment(comment)
        logging.info(comment)
    except:
        logging.exception("Error adding comment to %s" % (keys["permalink"]))
        db.set_submission_status(keys["name"], "failed")
        return False

    # aaaand we're done
    db.set_submission_status(keys["name"], "complete")
    return True

def jerk_run():
    db = JerkDB()

    logging.info("jerkbot init")

    # get list of latest submissions and start tracking
    try:
        new_submissions = get_new_submissions(db)
    except:
        logging.exception("Unable to connect to reddit")
        return

    for submission in new_submissions:
        mod_submission(db, submission)
        try_screenshot(db, submission)

    logging.info("jerkbot run complete")

if __name__ == "__main__":
    jerk_run()
    sys.exit(0)
