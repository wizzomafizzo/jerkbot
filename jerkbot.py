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

# notification templates
TEMPLATES = {
    "sketchy_subject": "sketchy user detected",
    "sketchy_body": """someone submitted with a sketchy account (low karma, newly created)

- username: %s
- info: %s
- submission: %s

[ban them](http://www.reddit.com/message/compose/?to=jerkbot-3hunna&subject=shadowban&message=ban%%20%s) | [show ban list](http://www.reddit.com/message/compose/?to=jerkbot-3hunna&subject=shadowban&message=showbans)
---|---
""",
    "non-np_subject": "removed a non-np submission",
    "non-np_body": "this one: %s",
    "non-np_comment": """fam, you need to submit this as an np link. this submission has been removed. you can read why [here](http://www.reddit.com/r/Hiphopcirclejerk/comments/297w9r/actually_serious_new_rule_enforcement_starting_on/).

you can resubmit with this link:

%s
""",
    "screenshot_comment": "screenshot: %s",
    "ban_subject": "shadowbans updated",
    "ban_body": "%s has been shadowbanned by %s",
    "unban_body": "%s had their shadowban removed by %s",
    "showbans_body": """shadowban list requested by %s

[ban new user](http://www.reddit.com/message/compose/?to=jerkbot-3hunna&subject=shadowban&message=ban%%20username) | [unban user](http://www.reddit.com/message/compose/?to=jerkbot-3hunna&subject=shadowban&message=unban%%20username)
---|---

---

%s
"""
}

# set up fancy logging shit
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
    logging.info("Created new image_dir: %s", CONFIG["image_dir"])

# this database keeps track of processed submissions/comments, so work is not doubled up
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
    def add_submission(self, submission):
        q = "insert into submissions values (?, ?, ?)"
        c = self.db.cursor()
        if not self.already_added(submission.name):
            c.execute(q, (submission.name, submission.url, "pending"))
            logging.info("Added new submission %s as pending", submission.name)
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
        logging.info("Update %s status to %s", name, status)
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
            logging.info("Adding user %s as %s", name, status)
            c.execute(q, (name, status, reason))
            self.db.commit()

    def set_user_status(self, name, status):
        self.add_user(name, status)
        q = "update users set status = ? where name = ?"
        c = self.db.cursor()
        logging.info("Set user %s status to %s", name, status)
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

    def get_banned_users(self):
        q = "select name from users where status = ?"
        c = self.db.cursor()
        c.execute(q, ("banned",))
        return [x[0] for x in c.fetchall()]

    # comment stuff
    def add_comment(self, name):
        q = "insert into comments values (?, ?)"
        c = self.db.cursor()
        if not self.comment_already_done(name):
            logging.info("Adding comment %s as complete", name)
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

def get_new_submissions(reddit, db):
    """Get newest submissions, add them as pending in database and return Submission objects."""
    new_submissions = reddit.get_subreddit(CONFIG["subreddit"]).get_new(limit=CONFIG["result_limit"])
    submissions = [x for x in new_submissions]
    [db.add_submission(x) for x in submissions]
    return submissions

def get_new_comments(reddit):
    """Get newest comments in subreddit."""
    subreddit = reddit.get_subreddit(CONFIG["subreddit"])
    return subreddit.get_comments(limit=CONFIG["result_limit"])

def take_screenshot(url, name):
    """Take screenshot of url and save to file, return path."""
    expand_comments = 'var el=$(".bylink");var ei=0;(function fe(){while(ei<el.length){var s=el[ei].innerHTML;var parent=s.indexOf("parent");if(parent==0){showcomment(el[ei]);}ei++;}})()'
    driver = webdriver.PhantomJS(executable_path=CONFIG["phantomjs_exe"])
    filename = os.path.join(CONFIG["image_dir"], "%s.png" % (name))
    driver.set_window_size(*CONFIG["viewport"])
    logging.info("Taking screenshot of %s (%s)", name, url)
    driver.get(url)
    driver.execute_script(expand_comments)
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

def check_messages(reddit, db):
    """Get unread bot messages/commands and process."""
    # get unread messages and mark read/clear notice
    messages = reddit.get_unread(True, True)
    subreddit = reddit.get_subreddit(CONFIG["subreddit"])
    mod_list = [x.name for x in subreddit.get_moderators()]

    for message in messages:
        # don't process non-direct pm or already processed ones
        if not db.comment_already_done("pm_" + message.name) and message.context == "":
            # check user is privileged, ignore if not
            if not message.author.name in mod_list:
                logging.warning("Unauthorised user %s tried to run command", message.author.name)
                db.add_comment("pm_" + message.name)
                continue

            # process command
            # NOTE: if this needs to expand it must be split up
            try:
                msg = message.body.split()
                if msg[0] == "ban":
                    # ban specified user
                    db.set_user_status(msg[1], "banned")
                    logging.info("%s has been shadowbanned", msg[1])
                    subreddit.send_message(TEMPLATES["ban_subject"],
                                           TEMPLATES["ban_body"] % (msg[1], message.author.name))
                elif msg[0] == "unban":
                    # unban specified user
                    db.set_user_status(msg[1], "pass")
                    logging.info("%s has been unshadowbanned", msg[1])
                    subreddit.send_message(TEMPLATES["ban_subject"],
                                           TEMPLATES["ban_body"] % (msg[1], message.author.name))
                elif msg[0] == "showbans":
                    # send list of all bans to modmail
                    user_list = ""
                    for user in db.get_banned_users():
                        user_list += "- %s\n" % user
                    if user_list == "":
                        user_list = "no bans"

                    logging.info("Posting ban list")
                    subreddit.send_message(TEMPLATES["ban_subject"],
                                           TEMPLATES["showbans_body"] % (message.author.name, user_list))
            except:
                # not really fatal if this happens, can simply be logged and skipped
                logging.exception("Error occurred when process command list")
            finally:
                db.add_comment("pm_" + message.name)

def check_user(db, session, name, subreddit, url=""):
    """Index a new user and report to mods if suspicious."""
    # lookup account, warn mods if an author's account is sketchy lookin
    # only warns once
    if not db.user_already_checked(name):
        redditor = session.get_redditor(name)
        limit_seconds = CONFIG["sketchy_days"] * 24 * 60 * 60

        # check if sketchy
        if (time.time() - redditor.created) < limit_seconds:
            karma = CONFIG["sketchy_karma"]
            # check for low karma
            if redditor.link_karma < karma and redditor.comment_karma < karma:
                logging.info("%s is sketchy", redditor.name)
                # add to database sketchy
                db.add_user(redditor.name, "sketchy")
                # send mod mail
                subreddit.send_message(TEMPLATES["sketchy_subject"],
                                       TEMPLATES["sketchy_body"] % (redditor.name, redditor._url,
                                                                    url, redditor.name))
                logging.info("Notified mods")
        else:
            logging.info("%s is cool", redditor.name)
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

    # bail out if we already did this one
    if db.already_done(new.name):
        logging.debug("Skip modding %s", new.name)
        return

    # lookup and index account, warn mods if account is suspicious
    check_user(db, new.reddit_session, new.author.name, new.subreddit, new.permalink)

    # remove submission silently if user is shadowbanned
    if db.user_is_banned(new.author.name):
        if not CONFIG["testing"]:
            new.remove()
        logging.info("Removed submission, %s is shadowbanned", new.author.name)
        db.set_submission_status(new.name, "complete")
        return

    # check it is an np link for comment subs
    # if it is, remove it and notify user, modmail
    if should_screenshot(new.url) and not is_np(new.url):
        logging.info("%s is not an np link", new.name)

        try:
            # notify user
            if not CONFIG["testing"]:
                new.add_comment(TEMPLATES["non-np_comment"] % to_np(new.url))
            logging.info("Notified user of non-np link")

            # send mod mail
            # NOTE: disabled for now, don't really care
            #new.subreddit.send_message(TEMPLATES["non-np_subject"],
            #                           TEMPLATES["non-np_body"] % (new.permalink))
            #logging.info("Notified mods")

            # remove the submission
            if not CONFIG["testing"]:
                new.remove()
            logging.info("Removed submission")

            db.set_submission_status(new.name, "complete")
            return
        except:
            logging.exception("Error modding submission: %s", new.permalink)
            db.set_submission_status(new.name, "failed")
            return

    # don't bother with anything else if no screenie required
    if not should_screenshot(new.url):
        db.set_submission_status(new.name, "complete")

def mod_comment(db, comment):
    """Report suspicious users and remove shadowbanned comments."""
    # bail out if we already checked
    if db.comment_already_done(comment.name):
        logging.debug("Already done %s", comment.name)
        return

    # check if user is suspicious
    check_user(db, comment.reddit_session, comment.author.name,
               comment.subreddit, comment.link_url)

    # shadowban
    if db.user_is_banned(comment.author.name):
        if not CONFIG["testing"]:
            comment.remove()
        logging.info("Removed comment, %s is shadowbanned", comment.author.name)

    db.add_comment(comment.name)

def try_screenshot(db, new):
    """If required, take a screenshot of submission link and post comment to uploaded image."""
    # bail out if we already did this one
    if db.already_done(new.name):
        logging.debug("Skip screenshot %s", new.name)
        return

    # don't bother if it's not a comment outside the sub
    if not should_screenshot(new.url):
        logging.info("Don't need to screenshot %s", new.name)
        db.set_submission_status(new.name, "complete")
        return

    # take and save the screenshot
    try:
        screenie = take_screenshot(new.url, new.name)
    except:
        logging.exception("Error while taking screenshot of %s", new.url)
        return

    # crop it, if required
    if os.path.getsize(screenie) > CONFIG["imgur_max_size"]:
        # TODO: this method of cropping is not totally reliable and can result
        # in a screenshot being cropped larger than it was, filled with white
        # space. this happens on subs that have complex themes
        try:
            cropped = crop_screenshot(screenie)
            screenie = cropped
        except:
            logging.exception("Unable to crop screenshot %s", screenie)
            return
        db.set_submission_status(new.name, "cropped")

    # upload to imgur
    try:
        imgur = upload_screenshot(screenie)
    except:
        logging.exception("Could not upload %s", screenie)
        return
    db.set_submission_status(new.name, "uploaded")

    # post the link in the submission thread
    try:
        if not CONFIG["testing"]:
            new.add_comment(TEMPLATES["screenshot_comment"] % imgur)
        logging.info("Linked screenshot in submission")
    except:
        logging.exception("Error adding comment to %s", new.permalink)
        db.set_submission_status(new.name, "failed")
        return

    # aaaand we're done
    db.set_submission_status(new.name, "complete")

def jerk_run():
    """Main function for app, completes one full scan of subreddit."""
    db = JerkDB()

    logging.info("=== jerkbot init ===")

    if CONFIG["testing"]:
        logging.warning("!!! Testing mode is enabled, nothing much will happen !!!")

    # start new reddit session
    logging.info("*** Init reddit session")
    try:
        reddit = praw.Reddit(user_agent=CONFIG["user_agent"])
        reddit.login(CONFIG["reddit_username"], CONFIG["reddit_password"])
    except:
        logging.exception("Unable to connect to reddit")
        return

    # NOTE: these are sorted newest first
    # check PMs and process any commands as needed
    logging.info("*** Checking messages...")
    check_messages(reddit, db)

    # get list of latest submissions/comments and start tracking
    logging.info("*** Finding new submissions/comments...")
    new_submissions = get_new_submissions(reddit, db)
    new_comments = get_new_comments(reddit)

    # attempt to mod and snap all new submissions
    logging.info("*** Checking submissions...")
    for submission in new_submissions:
        # this just hides the logging, functions already check for this
        if not db.already_done(submission.name):
            logging.info(">>> Starting submission %s...", submission.name)
            mod_submission(db, submission)
            try_screenshot(db, submission)
            logging.info("<<< Finished submission %s", submission.name)

    # mod new comments
    logging.info("*** Checking comments...")
    for comment in new_comments:
        # same here
        if not db.comment_already_done(comment.name):
            mod_comment(db, comment)

    logging.info("=== jerkbot run complete ===")

if __name__ == "__main__":
    jerk_run()
    sys.exit(0)
