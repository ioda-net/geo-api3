import cgi
import json
import datetime
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPInternalServerError
from smtplib import SMTPException


@view_config(route_name='feedback', renderer='json', request_method='POST')
def feedback(self, request):
    defaultRecipient = request.registry.settings['feedback.default_recipient']
    defaultSubject = request.registry.settings['feedback.default_subject']

    def getParam(param, defaultValue):
        val = request.params.get(param, defaultValue)
        val = val if val != '' else defaultValue
        return val

    def mail(to, subject, text, attachement, kml, kmlfilename, jsonToAttach):
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email import encoders
#        import unicodedata
        import smtplib

        msg = MIMEMultipart()

        msg['To'] = to
        msg['From'] = to
        msg['Subject'] = subject

        msg.attach(MIMEText(text, _charset='utf-8'))
        # Attach meta information
        part = MIMEBase('application', 'json')
        part.set_payload(json.dumps(jsonToAttach))
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename=' + jsonfilename)
        msg.attach(part)

        # Attach file if there
        if isinstance(attachement, cgi.FieldStorage):
            types = attachement.type.split('/')
            if len(types) != 2:
                raise HTTPInternalServerError('File type could not be determined')
            part = MIMEBase(types[0], types[1])
            filePart = attachement.file.read()
            part.set_payload(filePart)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % attachement.filename)
            msg.attach(part)

        # Attach kml if there
        if kml is not None and kml is not '':
            part = MIMEBase('application', 'vnd.google-earth.kml+xml')
            part.set_payload(kml)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename=' + kmlfilename)
            msg.attach(part)

        mailServer = smtplib.SMTP(
            request.registry.settings['feedback.mail_host_name'],
            request.registry.settings['feedback.mail_host_port'])
        err = mailServer.send_message(msg)
        if err:
            print(err)
        mailServer.quit()

    ua = getParam('ua', 'no user-agent found')
    permalink = getParam('permalink', 'No permalink provided')
    feedback = getParam('feedback', 'No feedback provided')
    email = getParam('email', 'Anonymous')
    text = u'%s sent a feedback:\n %s. \nPermalink: %s. \n\nUser-Agent: %s'
    attachement = getParam('attachement', None)
    kml = getParam('kml', None)
    now = datetime.datetime.now()
    timeID = now.strftime('%Y%m%d%H%M%S%f')[0:16]
    defaultSubject = defaultSubject + ' ID : ' + timeID
    kmlfilename = 'Drawing-' + timeID + '.kml'
    jsonfilename = 'Meta-' + timeID + '.json'
    attachfilename = ''
    if isinstance(attachement, cgi.FieldStorage):
        attachfilename = attachement.filename

    jsonAtt = {
        'emailAddress': email,
        'body': feedback,
        'permalink': permalink,
        'kml': kmlfilename if (kml is not None and kml is not '') else '',
        'attachement': attachfilename,
        'userAgent': ua,
        'ID': timeID
    }

    try:
        mail(
            defaultRecipient,
            defaultSubject,
            text % (email, feedback, permalink, ua),
            attachement,
            kml,
            kmlfilename,
            jsonAtt
        )
    except SMTPException as e:
        print(e)
        raise HTTPInternalServerError()

    return {'success': True}
