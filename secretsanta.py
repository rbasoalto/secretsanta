#!/usr/bin/env python3

import argparse
import random
import smtplib
import json

class EmailSender(object):
    def __init__(self, server_hostname, server_port=25, user=None, password=None, use_starttls=True, from_address=None, from_name=None):
        self.server_hostname = server_hostname
        self.server_port = server_port
        self.user = user
        self.password = password
        self.use_starttls = use_starttls
        self.from_address = from_address or "%s@%s"%(self.user, self.server_hostname)
        self.from_name = from_name or self.from_address
        self.server = None
    def __enter__(self):
        self.server = self.open_smtp_connection()
    def __exit__(self, type, value, traceback):
        self.server = self.close_smtp_connection()
    def open_smtp_connection(self):
        server = smtplib.SMTP(self.server_hostname, self.server_port)
        server.ehlo()
        if self.use_starttls:
            server.starttls()
        if self.user:
            server.login(self.user, self.password)
        return server
    def close_smtp_connection(self):
        self.server.close()
        return None
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
        parser.add_argument("-c", "--config", help="JSON config file. Refer to README for help", default="config.json", type=argparse.FileType('r'))
        parser.add_argument("-p", "--participants", help="JSON participants file. Refer to README for help", default="participants.json", type=argparse.FileType('r'))
        parser.add_argument("-t", "--template", help="Email template file. Refer to README for help", default="template.txt", type=argparse.FileType('r'))
        self.args = parser.parse_args()
    def read_config(self):
        config = {}
        with self.args.config as configfile:
            config = json.load(configfile)
        server_hostname = config['server']['hostname']
        server_port = config['server']['port']
        user = config['server']['user']
        password = config['server']['password']
        use_starttls = config['server']['use_starttls']
        if use_starttls is None:
            use_starttls = True # crypto by default!
        from_address = config['from']['address']
        from_name = config['from']['name']
        self.email_sender = EmailSender(server_hostname, server_port=server_port, user=user, password=password, use_starttls=use_starttls, from_address=from_address, from_name=from_name)
    def read_participants(self):
        with self.args.participants as partyfile:
            self.participants = json.load(partyfile)
    def read_template(self):
        with self.args.template as templatefile:
            self.subject = templatefile.readLine().strip()
            self.body = '\n'.join(map(lambda s: s.strip(), templatefile.readLines()))
    def get_shuffling(self):
        pass
    def valid(self, p1, p2):
        for x in zip(p1, p2):
            if x[0][1] == x[1][1]:
                return False
        return True
    def run(self):
        self.read_config()
        self.read_participants()
        self.read_template()
        return
        p = map(lambda l: l.strip().split(','), open('participants.txt'))
        s = p[:]
        while not valid(p,s):
            random.shuffle(s)
        for pair in zip(p,s):
            send_mail(pair[0], pair[1])
        print(json.dumps(zip(p,s)))

if __name__ == '__main__':
    ss = SecretSanta()
    ss.run()