import cgi
import json
import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from smtplib import SMTPException
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


class Feedback:
    def __init__(self, request):
        self.request = request
        self.default_recipient = \
            request.registry.settings['feedback.default_recipient']
        self.default_subject = \
            request.registry.settings['feedback.default_subject']
        self.mail_host_name = \
            request.registry.settings['feedback.mail_host_name']
        self.mail_host_port = \
            request.registry.settings['feedback.mail_host_port']

    @view_config(route_name='feedback', renderer='json', request_method='POST')
    def feedback(self):
        self.parse_params()
        msg = self.prepare_message()
        success = self.send(msg)
        return {'success': success}

    def parse_params(self):
        ua = self.get_param('ua', 'no user-agent found')
        permalink = self.get_param('permalink', 'No permalink provided')
        feedback = self.get_param('feedback', 'No feedback provided')
        self.user_email = self.get_param('email', None)
        self.recipient = self.get_param('to', None)
        self.subject = self.get_param('subject', None)
        text_format = {
            'user': self.user_email,
            'feedback': feedback,
            'permalink': permalink,
            'ua': ua,
        }
        self.text = '''{user} sent a feedback:
\t{feedback}.
Permalink: {permalink}.

User-Agent: {ua}'''.format(**text_format)
        self.attachment = self.get_param('attachment', None)
        self.kml = self.get_param('kml', None)
        now = datetime.datetime.now()
        time_id = now.strftime('%Y%m%d%H%M%S%f')[0:16]
        self.default_subject += ' ID: {}'.format(time_id)
        self.kmlfilename = 'Drawing-{}.kml'.format(time_id)
        self.jsonfilename = 'Meta-{}.json'.format(time_id)
        attachfilename = ''
        if isinstance(self.attachment, cgi.FieldStorage):
            attachfilename = self.attachment.filename

        self.metadata = json.dumps({
            'emailAddress': self.user_email,
            'body': feedback,
            'permalink': permalink,
            'kml': self.kmlfilename if (self.kml is not None and self.kml != '') else '',
            'attachment': attachfilename,
            'userAgent': ua,
            'ID': time_id
        })

    def get_param(self, param, default_value):
        val = self.request.params.get(param, default_value)
        # Note: attachment (cgi.FieldStorage) cannot be converted to bool
        return val if val != '' else default_value

    def prepare_message(self):
        msg = MIMEMultipart()
        msg['To'] = self.recipient if self.recipient else self.default_recipient
        msg['From'] = self.user_email if self.user_email else self.default_recipient
        msg['Subject'] = self.subject if self.subject else self.default_subject
        msg.attach(MIMEText(self.text, _charset='utf-8'))
        self.add_attachment(msg, self.attachment)
        self.add_attachment(
            msg,
            self.metadata,
            mime_base=('application', 'json'),
            filename=self.jsonfilename)
        self.add_attachment(
            msg,
            self.kml,
            mime_base=('application', 'vnd.google-earth.kml+xml'),
            filename=self.kmlfilename)

        return msg

    def add_attachment(self, msg, attachment, mime_base=('application', 'json'), filename=''):
        payload = None
        if isinstance(attachment, cgi.FieldStorage):
            types = attachment.type.split('/')
            if len(types) != 2:  # pragma: no cover
                raise HTTPInternalServerError('File type could not be determined')
            part = MIMEBase(types[0], types[1])
            payload = attachment.file.read()
            filename = attachment.filename
        elif attachment:
            part = MIMEBase(mime_base[0], mime_base[1])
            payload = attachment

        if payload is not None:
            part.set_payload(payload)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename={}'.format(filename))
            msg.attach(part)

    def send(self, msg):
        try:
            with SMTP(host=self.mail_host_name, port=self.mail_host_port) as smtp:
                    smtp.send_message(msg)
        except SMTPException as e:  # pragma: no cover
            print('*** SMTPException', e)
            raise HTTPInternalServerError()
        except Exception:  # pragma: no cover
            return False
        else:
            return True
