#!/usr/bin/env python3

import json
import random
from pathlib import Path

import typer

from gmail import GMailAPIEmailSender

app = typer.Typer(help="Secret Santa email shuffler and sender")


class DummyEmailSender(object):
    def __init__(self):
        print("Building dummy email sender")

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def send_mail(self, recipient, subject, body):
        print("Sending mail to %s with subject %s and body %s" % (recipient, subject, body))


class SecretSanta(object):
    def __init__(self, participants_file: Path, template_file: Path, dry_run: bool):
        self.email_sender = DummyEmailSender() if dry_run else GMailAPIEmailSender()
        self.participants = {}
        self.restrictions = {}
        self.read_participants(participants_file)
        self.read_template(template_file)

    def read_participants(self, participants_file: Path):
        raw_participants = json.loads(participants_file.read_text())
        for group in raw_participants:
            for person in group:
                self.participants[person['email']] = person
                self.restrictions[person['email']] = [p['email'] for p in group]

    def read_template(self, template_file: Path):
        lines = template_file.read_text().splitlines()
        self.subject = lines[0].strip()
        self.body = '\n'.join(s.strip() for s in lines[1:])

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
        return (self.subject
                .replace("{FROM_NAME}", self.participants[pair[0]]['name'])
                .replace("{FROM_EMAIL}", self.participants[pair[0]]['email'])
                .replace("{TO_NAME}", self.participants[pair[1]]['name'])
                .replace("{TO_EMAIL}", self.participants[pair[1]]['email']))

    def render_body(self, pair):
        return (self.body
                .replace("{FROM_NAME}", self.participants[pair[0]]['name'])
                .replace("{FROM_EMAIL}", self.participants[pair[0]]['email'])
                .replace("{TO_NAME}", self.participants[pair[1]]['name'])
                .replace("{TO_EMAIL}", self.participants[pair[1]]['email']))

    def run(self):
        pairs = self.get_shuffling()
        with self.email_sender:
            for pair in pairs:
                self.email_sender.send_mail(self.participants[pair[0]],
                                            self.render_subject(pair),
                                            self.render_body(pair))


@app.command()
def main(
    participants: Path = typer.Option("participants.json", "--participants", "-p",
                                      help="JSON participants file. Refer to README for help",
                                      exists=True, dir_okay=False),
    template: Path = typer.Option("template.txt", "--template", "-t",
                                  help="Email template file. Refer to README for help",
                                  exists=True, dir_okay=False),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Dry run (no emails sent)"),
):
    SecretSanta(participants, template, dry_run).run()


if __name__ == '__main__':
    app()
