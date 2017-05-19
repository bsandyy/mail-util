'''
The purpose of this script is to read current day's emails in a specified mailbox and send a report to concerned parties

'''

import configparser
import imaplib
from pprint import pprint
import email
import datetime
import re
import smtplib
import json


parser = configparser.ConfigParser()
parser.read("conf.ini")
# print(parser.get('auth','email_account'))

# regex to match the reminder string  in the subject line
reminder = re.compile(r'Reminder: ([3-9]|\d{2})')

# regex to match the bugid string in the subject line
bug_id = re.compile(r'[A-Z]{3}\d{7}')


mail_account = parser.get('auth', 'email_account')
mail_password = parser.get('auth', 'email_password')
mail_server = parser.get('exchange', 'exchange_server')
mail_folder = parser.get('exchange', 'email_folder')
mail_sender = parser.get('receivers', 'from')
mail_to = parser.get('receivers', 'to')
mail_cc = parser.get('receivers', 'cc')


def exch_extract():
    '''Method to extract bug id's with remider count greater than x.'''
    print("Login to {} with user account {}".format(mail_server, mail_account))
    try:
        my_mail = imaplib.IMAP4_SSL(mail_server)
        '''This function initiates a SSL connection to IMAP server and
        authenticates user. It will prompt for password in terminal.'''
        my_mail.login(mail_account, mail_password)
        '''All methods in IMAP class returns a tuple: (type, [data, ...]) where 'type'
        is usually 'OK' or 'NO', and 'data' is either the text from the
        tagged response, or untagged results from command. Each 'data'
        is either a string, or a tuple. If a tuple, then the first part
        is the header of the response, and the second part contains
        the data (ie: 'literal' value).
        Hence we should expect an OK as type for login method.'''

        print("Connected to exchange server")
        # select returns "type" code and no of mails in the selected mailbox as data
        typ, data = my_mail.select(mail_folder)
        #  Format date = '17-Feb-2017'
        # date = datetime.date.today().strftime("%d-%b-%Y")
        date = '17-Feb-2017'  # For Testing comment the below line
        # date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
        date = datetime.date.today().strftime("%d-%b-%Y")
        result, data = my_mail.search(
            None, '(SENTON {date} HEADER Subject "[ACTION REQUIRED][Reminder:")'.format(date=date))
        # result, data = mail.search(None, '(SENTSINCE {date} HEADER Subject "My Subject" NOT FROM "sand@ggm.com")'.format(date=date))
        ids = data[0]  # data is a list.
        id_list = ids.split()  # ids is a space separated string
        subs = {}
        for id in id_list:
            result, data = my_mail.fetch(id, '(RFC822)')
            sub = email.message_from_bytes(data[0][1])["Subject"]
            if reminder.search(sub):
                subs[bug_id.findall(sub)[0]] = reminder.findall(sub)[0]
        # Check to handle empty bug dictionary
        if len(subs):
            mailer(json.dumps(subs))
            my_mail.logout()
        else:
            print("Not sending any mails today as the reminder count for all mails is under control")
    except Exception as err_msg:
        print("LOGIN FAILED!!!", err_msg)


def mailer(message):
    '''Function to send emails'''
    sub = "Bugs with high reminder count"
    sender = mail_sender
    receivers = [mail_to, mail_cc]
    msg = '''From: XMS BUG TRACKING <{}>
To:{}
Cc:{}
MIME-Version: 1.0
Content-type: text
Subject:{}

Hi Shimpi,

Please follow up on the below bugs and request the respective owners to keep the bug updated.

{}

Thanks,
Sandeep
'''.format(sender, ';'.join(receivers), mail_cc, sub, message)
    print(msg)
    try:
        smtpObj = smtplib.SMTP(mail_server, 25)
        smtpObj.sendmail(sender, receivers, msg)
        print("Successfully sent email")
    except Exception as error:
        print("some mail error", error)


if __name__ == '__main__':
    exch_extract()
