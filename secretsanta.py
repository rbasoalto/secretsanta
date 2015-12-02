#!/usr/bin/env python3

import argparse
import random
import smtplib
import json

class EmailSender(object):
    def __init__(self):
        pass
    def send_mail(self, p1, p2):
        FROM = '"Secret Santa" <secretsanta@basoalto.cl>'
        TO = ['"%s" <%s>' % (p1[0], p1[2])]
        SUBJECT = 'Basoalto\'s Secret Santa!'
        TXT = '''Hola %s,\nEres el Secret Santa de %s, para que le hagas un regalo.\n\nHello %s,\nYou are %s\'s Secret Santa. Get him/her a present.''' % (p1[0], p2[0], p1[0], p2[0])
        MSG = "From: %s\nTo: %s\nSubject: %s\n\n%s\n"%(FROM, ', '.join(TO), SUBJECT, TXT)
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        # server.ehlo()
        # server.starttls()
        # server.login(USER, PASS)
        # server.sendmail(FROM, TO, MSG)
        # server.close()

class SecretSanta(object):
    def __init__(self):
        self.parse_args()
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("config", help="JSON config file. Refer to README for help")
        parser.add_argument("participants", help="JSON participants file. Refer to README for help")
        self.args = parser.parse_args()
    def read_config(self):
        pass
    def read_participants(self):
        pass
    def get_shuffling(self):
        pass
    def valid(p1, p2):
        for x in zip(p1, p2):
            if x[0][1] == x[1][1]:
                return False
        return True
    def run(self):
        p = map(lambda l: l.strip().split(','), open('participants.txt'))
        s = p[:]
        while not valid(p,s):
            random.shuffle(s)
        for pair in zip(p,s):
            send_mail(pair[0], pair[1])
        print json.dumps(zip(p,s))

if __name__ == '__main__':
    ss = SecretSanta()
    ss.run()