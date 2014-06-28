#!/usr/bin/env python3

"""
Reddit bot for managing hhcj

It will:
- Take screenshots of comment submissions and post an imgur link as a comment
- Remove submissions without np subdomain links, notify user and mod mail
- Report users to mods who may be evading bans

You'll need:
- Python 3
- PRAW (in pip)
- pyimgur (in pip)
- Pillow (in pip)
- selenium (in pip)
- PhantomJS (you can download static builds off their site)
"""

import logging, logging.handlers, os, sys
import re, sqlite3, time
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

# this database keeps track of processed submissions, so work is not doubled up
# and also maintains a shitlist of users
class JerkDB():
    def __init__(self):
        self.db_filename = CONFIG["db_file"]

        if not os.path.isfile(self.db_filename):
            self.init_db()

        self.db = sqlite3.connect(self.db_filename)

    def init_db(self):
        tables = ("create table submissions (name text, url text, status text)",
                  "create table users (name text, status text, reason text)",
                  "create table comments (name text, status text)")
        db = sqlite3.connect(self.db_filename)
        c = db.cursor()
        for t in tables:
            c.execute(t)
        db.commit()
        db.close()

    # submission stuff
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

    # user stuff
    def add_user(self, name, status, reason=""):
        q = "insert into users values (?, ?, ?)"
        c = self.db.cursor()
        if not self.user_already_checked(name):
            logging.info("Adding user %s as %s" % (name, status))
            c.execute(q, (name, status, reason))
            self.db.commit()

    def set_user_status(self, name, status):
        q = "update users set status = ? where name = ?"
        c = self.db.cursor()
        logging.info("Set user %s status to %s" % (name, status))
        c.execute(q, (status, name))
        self.db.commit()

    def user_is_banned(self, name):
        q = "select name from users where name = ? and status = ?"
        c = self.db.cursor()
        c.execute(q, (name, "banned"))
        if c.fetchone() == None:
            return False
        else:
            return True

    def user_already_checked(self, name):
        q = "select name from users where name = ?"
        c = self.db.cursor()
        c.execute(q, (name,))
        if c.fetchone() == None:
            return False
        else:
            return True

    # comment stuff
    def add_comment(self, name):
        q = "insert into comments values (?, ?)"
        c = self.db.cursor()
        if not self.comment_already_done(name):
            logging.info("Adding comment %s as complete" % (name))
            c.execute(q, (name, "complete"))
            self.db.commit()

    def comment_already_done(self, name):
        q = "select name from comments where name = ?"
        c = self.db.cursor()
        c.execute(q, (name,))
        if c.fetchone() == None:
            return False
        else:
            return True

def should_screenshot(url):
    """Return true if submission is a comment link not in the same sub."""
    comment_pattern = "reddit.com/r/\w+/comments/\w+"
    subreddit_pattern = "/%s/" % (CONFIG["subreddit"])

    # we're only interested in comments and self posts
    if re.search(comment_pattern, url, re.I) != None:
        # but not from the subreddit we're submitting to
        if re.search(subreddit_pattern, url, re.I) == None:
            return True

    return False

def is_np(url):
    """Return true if url is a no participate link."""
    if re.match("https*://np\.", url):
        return True
    else:
        return False

def to_np(url):
    """Return a comment url converted to the np subdomain."""
    return re.sub("https*://.*reddit.com", "https://np.reddit.com", url)

def get_new_submissions(db):
    """Get newest submissions, add them as pending in database and return Submission objects."""
    reddit = praw.Reddit(user_agent=CONFIG["user_agent"])
    reddit.login(CONFIG["reddit_username"], CONFIG["reddit_password"])
    new_submissions = reddit.get_subreddit(CONFIG["subreddit"]).get_new(limit=CONFIG["result_limit"])
    submissions = [x for x in new_submissions]

    [db.add_submission(vars(x)) for x in submissions]

    return submissions

def get_new_comments():
    """Get newest comments in subreddit."""
    reddit = praw.Reddit(user_agent=CONFIG["user_agent"])
    reddit.login(CONFIG["reddit_username"], CONFIG["reddit_password"])
    subreddit = reddit.get_subreddit(CONFIG["subreddit"])
    return subreddit.get_comments(limit=CONFIG["result_limit"])

def take_screenshot(url, name):
    """Take screenshot of url and save to file, return path."""
    driver = webdriver.PhantomJS(executable_path=CONFIG["phantomjs_exe"])
    filename = os.path.join(CONFIG["image_dir"], "%s.png" % (name))
    driver.set_window_size(*CONFIG["viewport"])
    logging.info("Taking screenshot of %s (%s)" % (name, url))
    driver.get(url)
    driver.get_screenshot_as_file(filename)
    driver.quit()
    return filename

def upload_screenshot(filename):
    """Upload image file to imgur, return url."""
    imgur = pyimgur.Imgur(client_id=CONFIG["imgur_api_key"])
    uploaded = imgur.upload_image(filename)
    return uploaded.link

def crop_screenshot(filename):
    """Crop a screenshot to configured height, save to file and return path."""
    screenshot = Image.open(filename)
    cropped = screenshot.crop((0, 0, CONFIG["viewport"][0], CONFIG["cropped_height"]))
    cropped_filename = re.sub("\.png$", "-cropped.png", filename)
    cropped.save(cropped_filename)
    return cropped_filename

def check_user(db, session, name, subreddit, url=""):
    # lookup account, warn mods if an author's account is less than N days old
    # only warns once
    if not db.user_already_checked(name):
        redditor = session.get_redditor(name)
        limit_seconds = CONFIG["sketchy_days"] * 24 * 60 * 60

        # comment sent to modmail
        msg = "someone submitted with a recently created account (<%i days)\n\n" % (CONFIG["sketchy_days"])
        msg += "username: %s\n\ninfo: %s\n\nsubmission: %s" % (redditor.name, redditor._url, url)

        if (time.time() - redditor.created) < limit_seconds:
            logging.info("%s is sketchy" % (redditor.name))
            # add to database sketchy
            db.add_user(redditor.name, "sketchy")
            # send mod mail
            if not CONFIG["testing"]:
                subreddit.send_message("fresher detected", msg)
            logging.info("Notified mods")
        else:
            logging.info("%s is cool" % (redditor.name))
            # add to database pass
            db.add_user(redditor.name, "pass")

        return True
    else:
        return False

def mod_submission(db, new):
    """Make sure a submission follows the rules.

    - Linked comments must use np subdomain, remove and notify bad submissions
    - Lookup and report suspicious users (evading bans)
    - Remove submissions posted by banned users silently"""
    keys = vars(new)

    # bail out if we already did this one
    if db.already_done(keys["name"]):
        logging.debug("Skip modding %s" % (keys["name"]))
        return

    # lookup and index account, warn mods if account is suspicious
    check_user(db, keys["reddit_session"], keys["author"].name,
               keys["subreddit"], keys["permalink"])

    # check it is an np link for comment subs
    # if it is, remove it and notify user, modmail
    if should_screenshot(keys["url"]) and not is_np(keys["url"]):
        logging.info("%s is not an np link" % keys["name"])

        # submission comment
        comment = "fam, you need to submit this as an np link. this submission has been removed."
        comment += " you can read why [here](http://www.reddit.com/r/Hiphopcirclejerk/comments/297w9r/actually_serious_new_rule_enforcement_starting_on/).\n\n"
        comment += "you can resubmit with this link:\n\n%s" % (to_np(keys["url"]))

        try:
            # notify user
            if not CONFIG["testing"]:
                new.add_comment(comment)
            logging.info("COMMENT: " + comment)

            # send mod mail
            if not CONFIG["testing"]:
                keys["subreddit"].send_message("removed a non-np submission",
                                               "this one: %s" % (keys["permalink"]))
            logging.info("Notified mods")

            # remove the submission
            if not CONFIG["testing"]:
                new.remove()
            logging.info("Removed submission")

            db.set_submission_status(keys["name"], "complete")
        except:
            logging.exception("Error modding submission: %s" % (keys["permalink"]))
            db.set_submission_status(keys["name"], "failed")
            return

    # remove submission silently if user is shadowbanned
    if db.user_is_banned(new.author.name):
        if not CONFIG["testing"]:
            new.remove()
        logging.info("Removed submission, %s is shadowbanned" % new.author.name)
        db.set_submission_status(new.name, "complete")

def mod_comment(db, comment):
    # bail out if we already checked
    if db.comment_already_done(comment.name):
        logging.debug("Already done %s" % (comment.name))
        return

    # check if user is suspicious
    check_user(db, comment.reddit_session, comment.author.name,
               comment.subreddit, comment.link_url)

    # shadowban
    if db.user_is_banned(comment.author.name):
        if not CONFIG["testing"]:
            comment.remove()
        logging.info("Removed comment, %s is shadowbanned" % comment.author.name)

    db.add_comment(comment.name)

def try_screenshot(db, new):
    """If required, take a screenshot of submission link and post comment to uploaded image."""
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
    """Main function for app, completes one full scan of subreddit."""
    db = JerkDB()

    logging.info("=== jerkbot init ===")

    if CONFIG["testing"]:
        logging.warning("Testing mode is enabled, nothing much will happen")

    # get list of latest submissions/comments and start tracking
    logging.info("*** Finding new submissions/comments...")
    try:
        new_submissions = get_new_submissions(db)
        new_comments = get_new_comments()
    except:
        logging.exception("Unable to connect to reddit")
        return

    # attempt to mod and snap all new submissions
    logging.info("*** Checking submissions...")
    for submission in new_submissions:
        # this just hides the logging, functions already check for this
        if not db.already_done(submission.name):
            logging.info(">>> Starting submission %s..." % (submission.name))
            mod_submission(db, submission)
            try_screenshot(db, submission)
            logging.info("<<< Finished submission %s" % (submission.name))

    # mod new comments
    logging.info("*** Checking comments...")
    for comment in new_comments:
        mod_comment(db, comment)

    logging.info("=== jerkbot run complete ===")

if __name__ == "__main__":
    jerk_run()
    sys.exit(0)
