'''
The purpose of this script is to read current day's emails in a specified mailbox and send a report to concerned parties

'''

import configparser
import imaplib
from pprint import pprint
import email
import datetime
import re



parser = configparser.ConfigParser()
parser.read("conf.ini")
# print(parser.get('auth','email_account'))

reminder = re.compile(r'Reminder: [3-9]]|\d{2}]')
bug_id   = re.compile(r'[A-Z]{3}\d{7}')


mail_account  = parser.get('auth','email_account')
mail_password = parser.get('auth','email_password')
mail_server   = parser.get('exchange','exchange_server')
mail_folder   = parser.get('exchange','email_folder')



def exch_authentication():

    '''This function initiates a SSL connection to IMAP server and
    authenticates user. It will prompt for password in terminal.'''

    print("Login to {} with user account {}".format(mail_server, mail_account))
    try:
        my_mail = imaplib.IMAP4_SSL(mail_server)
        '''All methods in IMAP class returns a tuple: (type, [data, ...]) where 'type'
        is usually 'OK' or 'NO', and 'data' is either the text from the
        tagged response, or untagged results from command. Each 'data'
        is either a string, or a tuple. If a tuple, then the first part
        is the header of the response, and the second part contains
        the data (ie: 'literal' value).
        Hence we should expect an OK as type for login method.'''

        my_mail.login(mail_account, mail_password)
        print("Connected to exchange server")
        # select returns "type" code and no of mails in the selected mailbox as data
        typ , data = my_mail.select(mail_folder)
        date = '17-Feb-2017'

        # date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
        result, data = my_mail.search(None, '(SENTON {date} HEADER Subject "[ACTION REQUIRED][Reminder:")'.format(date=date))
        # result, data = mail.search(None, '(SENTSINCE {date} HEADER Subject "My Subject" NOT FROM "sand@ggm.com")'.format(date=date))
        # result, data = mail.search(None, '(SENTON {date} HEADER Subject "[ACTION REQUIRED][Reminder:*")'.format(date=date))
        ids = data[0] # data is a list.
        id_list = ids.split() # ids is a space separated string
        subs = {}
        for id in id_list:
            result, data = my_mail.fetch(id, '(RFC822)')
            sub = email.message_from_bytes(data[0][1])["Subject"]
            if reminder.search(sub):
                subs[bug_id.findall(sub)[0]] = reminder.findall(sub)[0]

        print(subs)










        # result, data = my_mail.search(None, "ALL")
        # ids = data[0] # data is a list.
        # id_list = ids.split() # ids is a space separated string
        # latest_email_id = id_list[-1] # get the latest
        # result, data = my_mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
        # raw_email = data[0][1] # here's the body, which is raw text of the whole email
        # including headers and alternate payloads
        # print(data)





        my_mail.logout()
    except Exception as err_msg:
        print("LOGIN FAILED!!!", err_msg)

exch_authentication()
