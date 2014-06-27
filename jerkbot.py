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

import logging, os, re, sqlite3
import praw, pyimgur
from PIL import Image
from selenium import webdriver

from config import CONFIG

logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO,
                    format="%(asctime)s: %(message)s")

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
        tables = ("create table submissions (name text, url text, status text)",)
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
        q = "select name from submissions where name = ? and status = ?"
        c = self.db.cursor()
        c.execute(q, (name, "complete"))
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

def get_new_submissions():
    reddit = praw.Reddit(user_agent=CONFIG["user_agent"])
    reddit.login(CONFIG["reddit_username"], CONFIG["reddit_password"])
    new_submissions = reddit.get_subreddit(CONFIG["subreddit"]).get_new(limit=CONFIG["result_limit"])
    valid_submissions = []
    db = JerkDB()

    for new in new_submissions:
        comment_pattern = "reddit.com/r/\w+/comments/\w+"
        subreddit_pattern = "/%s/" % (CONFIG["subreddit"])
        submission = vars(new)
        url = submission["url"]

        # we're only interested in comments and self posts
        if re.search(comment_pattern, url, re.I) != None:
            # but not from the subreddit we're submitting to
            if re.search(subreddit_pattern, url, re.I) == None:
                valid_submissions.append((new, submission))

    for valid in valid_submissions:
        db.add_submission(valid[1])

    return [x[0] for x in valid_submissions]

def take_screenshot(url, name):
    driver = webdriver.PhantomJS(executable_path=CONFIG["phantomjs_exe"])
    filename = os.path.join(CONFIG["image_dir"], "%s.png" % (name))
    driver.set_window_size(CONFIG["viewport"]*)
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

def submission_run(db, submissions):


    # this is where the magic happens
    for new in new_submissions:
        keys = vars(new)

        # bail out if we already did this one
        if db.already_done(keys["name"]):
            logging.info("Already done %s" % (keys["name"]))
            continue

        # take and save the screenshot
        try:
            screenie = take_screenshot(keys["url"], keys["name"])
        except:
            logging.exception("Error while taking screenshot of %s", (keys["url"]))
            continue

        # crop it, if required
        if os.path.getsize(screenie) > CONFIG["imgur_max_size"]:
            try:
                cropped = crop_screenshot(screenie)
                screenie = cropped
            except:
                logging.exception("Unable to crop screenshot %s" % (screenie))
                continue
            db.set_submission_status(keys["name"], "cropped")

        # upload to imgur
        try:
            imgur = upload_screenshot(screenie)
        except:
            logging.exception("Could not upload %s" % (screenie))
            continue
        db.set_submission_status(keys["name"], "uploaded")

        # post the link in the submission thread
        comment = CONFIG["comment_text"] % (imgur)
        try:
            if not CONFIG["disable_comment"]:
                new.add_comment(comment)
            logging.info(comment)
        except praw.errors.RateLimitExceeded:
            logging.info("You probably need more link karma on your reddit account")
            logging.exception("Not allowed to post comment")
        except:
            logging.exception("Error adding comment to %s" % (keys["permalink"]))
            continue

        # aaaand we're done
        db.set_submission_status(keys["name"], "complete")

def jerk_run():
    db = JerkDB()

    logging.info("jerkbot init")

    # get list of latest submissions
    try:
        new_submissions = get_new_submissions()
    except:
        logging.exception("Unable to connect to reddit")
        return

    submission_run(db, new_submissions)

    logging.info("jerkbot run complete")

if __name__ == "__main__":
    jerk_run()
