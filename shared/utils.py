import re
import threading

import phonenumbers
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

regex_phone = re.compile(r'^[+]998([0-9][012345789]|[0-9][125679]|7[01234569])[0-9]{7}$')


def check_phone(phone):
    try:
        parse_number = phonenumbers.parse(phone)
        return phonenumbers.is_valid_number(parse_number)

    except phonenumbers.NumberParseException:
        return False


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
            EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'phone/authentication/code.html',
        {'code': code}
    )
    Email.send_email(
        {
            'subject': "Ro'yxatdan o'tish",
            'to_email': email,
            'body': html_content,
            'content_type': "html",
        }
    )
