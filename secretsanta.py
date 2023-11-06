#!/usr/bin/env python3

import argparse
import random
import smtplib
import json

from gmail import GMailAPIEmailSender


class DummyEmailSender(object):
    def __init__(self):
        print("Building dummy email sender")

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def send_mail(self, recipient, subject, body):
        print(("Sending mail to %s with subject %s and body %s")%(recipient, subject, body))


class SecretSanta(object):
    def __init__(self):
        self.email_sender = None
        self.participants = {}
        self.restrictions = {}
        self.subject = None
        self.body = None
        self.args = self.parse_args()
        self.init_email()
        self.read_participants()
        self.read_template()

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--participants", help="JSON participants file. Refer to README for help",
                            default="participants.json")
        parser.add_argument("-t", "--template", help="Email template file. Refer to README for help",
                            default="template.txt")
        parser.add_argument("-n", "--dry_run", help="Dry run", default=False)
        return parser.parse_args()

    def init_email(self):
        if self.args.dry_run:
            self.email_sender = DummyEmailSender()
        else:
            self.email_sender = GMailAPIEmailSender()

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
        pairs = self.get_shuffling()
        with self.email_sender:
            for pair in pairs:
                self.email_sender.send_mail(self.participants[pair[0]], self.render_subject(pair), self.render_body(pair))


if __name__ == '__main__':
    ss = SecretSanta()
    ss.run()
