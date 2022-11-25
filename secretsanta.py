#!/usr/bin/env python3

import argparse
import random
import smtplib
import json


class DummyEmailSender(object):
    def __init__(self):
        print("Building dummy email sender")

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def send_mail(self, recipient, subject, body):
        print(("Sending mail to %s with subject %s and body %s")%(recipient, subject, body))

class EmailSender(object):
    def __init__(self, server_hostname, server_port=25, user=None, password=None, use_starttls=True, from_email=None, from_name=None):
        self.server_hostname = server_hostname
        self.server_port = server_port
        self.user = user
        self.password = password
        self.use_starttls = use_starttls
        self.from_email = from_email or "%s@%s"%(self.user, self.server_hostname)
        self.from_name = from_name or self.from_email
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

    def send_mail(self, recipient, subject, body):
        from_line = '"%s" <%s>' % (self.from_name, self.from_email)
        recipient_list = ['"%s" <%s>' % (recipient['name'], recipient['email'])]
        msg = "From: %s\nTo: %s\nSubject: %s\n\n%s\n"%(from_line, ', '.join(recipient_list), subject, body)
        self.server.sendmail(from_line, recipient_list, msg)


class SecretSanta(object):
    def __init__(self):
        self.email_sender = None
        self.participants = {}
        self.restrictions = {}
        self.subject = None
        self.body = None
        self.args = self.parse_args()
        self.read_config()
        self.read_participants()

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", help="JSON config file. Refer to README for help",
                            default="config.json")
        parser.add_argument("-p", "--participants", help="JSON participants file. Refer to README for help",
                            default="participants.json")
        parser.add_argument("-t", "--template", help="Email template file. Refer to README for help",
                            default="template.txt")
        parser.add_argument("-n", "--dry_run", help="Dry run", default=False)
        return parser.parse_args()

    def read_config(self):
        with open(self.args.config) as configfile:
            config = json.load(configfile)
        server_hostname = config['server']['hostname']
        server_port = config['server']['port']
        user = config['server']['user']
        password = config['server']['password']
        use_starttls = config['server']['use_starttls']
        if use_starttls is None:
            use_starttls = True # crypto by default!
        from_email = config['from']['email']
        from_name = config['from']['name']
        if self.args.dry_run:
            self.email_sender = DummyEmailSender()
        else:
            self.email_sender = EmailSender(server_hostname, server_port=server_port, user=user, password=password,
                                            use_starttls=use_starttls, from_email=from_email, from_name=from_name)

    def read_participants(self):
        with open(self.args.participants) as participants_file:
            raw_participants = json.load(participants_file)
        for group in raw_participants:
            for person in group:
                self.participants[person['email']] = person
                self.restrictions[person['email']] = list(map(lambda p: p['email'], group))

    def read_template(self):
        with open(self.args.template) as templatefile:
            self.subject = templatefile.readline().strip()
            self.body = '\n'.join(map(lambda s: s.strip(), templatefile.readlines()))

    def get_shuffling(self):
        froms = list(self.participants.keys())
        tos = list(self.participants.keys())
        while not self.valid(zip(froms, tos)):
            random.shuffle(tos)
        return zip(froms, tos)

    def valid(self, s):
        for x in s:
            if x[1] in self.restrictions[x[0]]:
                return False
        return True

    def render_subject(self, pair):
        subject = self.subject
        subject = subject.replace("{FROM_NAME}", self.participants[pair[0]]['name']) 
        subject = subject.replace("{FROM_EMAIL}", self.participants[pair[0]]['email']) 
        subject = subject.replace("{TO_NAME}", self.participants[pair[1]]['name']) 
        subject = subject.replace("{TO_EMAIL}", self.participants[pair[1]]['email']) 
        return subject

    def render_body(self, pair):
        body = self.body
        body = body.replace("{FROM_NAME}", self.participants[pair[0]]['name']) 
        body = body.replace("{FROM_EMAIL}", self.participants[pair[0]]['email']) 
        body = body.replace("{TO_NAME}", self.participants[pair[1]]['name']) 
        body = body.replace("{TO_EMAIL}", self.participants[pair[1]]['email']) 
        return body

    def run(self):
        self.read_config()
        self.read_participants()
        self.read_template()
        pairs = self.get_shuffling()
        with self.email_sender:
            for pair in pairs:
                self.email_sender.send_mail(self.participants[pair[0]], self.render_subject(pair), self.render_body(pair))
        print(json.dumps(list(pairs)))

if __name__ == '__main__':
    ss = SecretSanta()
    ss.run()
