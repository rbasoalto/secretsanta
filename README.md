# Secret Santa

Secret santa shuffler, with restrictions.

## Requirements

* Python (3.9ish should do?) and `pip install -r requirements.txt`
* You need a Google OAuth app to use the Gmail API. Put the `client_credentials.json` file in the root dir here.
* You need a participants file (see below).
* You need an email template (see below).
* You need a Google Account to send the email from. Note that the sent emails will be saved in the 'sent' folder, so it'd be ideal if it's not your primary account so you don't see the sent emails.

### Participants File

A JSON file with groups of people. People won't be assigned secret santas from their own group (ideal to avoid spouses having each other, etc).

Example:

```json
[
    [
        {
            "name": "John",
            "email": "johndoe@gmail.com"
        },
        {
            "name": "Jane",
            "email": "janedoe@gmail.com"
        }
    ],
    [
        {
            "name": "Foo",
            "email": "foobaz@gmail.com"
        },
        {
            "name": "Bar",
            "email": "barbaz@gmail.com"
        }
    ],
    [
        {
            "name": "Dog",
            "email": "dog@gmail.com"
        },
        {
            "name": "Cat",
            "email": "cat@gmail.com"
        },
        {
            "name": "Mouse",
            "email": "mouse@gmail.com"
        },
    ],
    [
        {
            "name": "Lone Wolf",
            "email": "lonewolf@gmail.com"
        }
    ]
]
```

### Email template

Just a text template for the email message, where the first line is the subject, and the rest of the file is the body. These tags will be replaced: `{FROM_NAME}`, `{TO_NAME}`, `{FROM_EMAIL}`, `{TO_EMAIL}`. Example:

```
Secret Santa!!!1
Hi {FROM_NAME},
You're {TO_NAME}'s Secret Santa.
```

## Usage

`python secretsanta.py -p participants.json -t template.txt`
