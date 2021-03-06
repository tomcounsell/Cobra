from apps.admin.utils.exception_handling import ExceptionHandler
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from settings import STAGE, DEBUG, DEMO
from apps.admin.utils.decorator import postpone

class Email(object):
  def __init__(self, template_dir=None, data={}, message=None, subject=None):
    #creates an email using the template and data provided
    if template_dir:

      subject_template = "email/%s/subject.txt" % template_dir
      text_body_template = "email/%s/text_body.txt" % template_dir
      html_body_template = "email/%s/html_body.html" % template_dir

      context = {'data':data}

      self.subject = render_to_string(subject_template, context)
      if subject:
        self.subject = "%s | %s" % (subject, self.subject)

      self.text_body = render_to_string(text_body_template, context)
      self.html_body = render_to_string(html_body_template, context)
      if message:
        self.text_body += "\n%s" % str(message)
        self.html_body += "<br><p>%s</p>" % str(message)

      #default from address
      self.from_email = "Anou <hello@theanou.com>"

    else:
      message = message if message else "test email body"
      self.subject = subject or "notification"
      self.text_body = str(message)
      self.html_body = "<p>%s</p>" % str(message)
      self.from_email = 'system@theanou.com'
      #self.attachment_url = None

  def sendFrom(self, from_email):
    self.from_email = from_email
    return self

  @postpone #cannot return a value, handle errors internally
  def sendTo(self, to): #sends the email object to the provided email or list of emails

    #allow the function to receive a string or a list
    self.to = [to] if isinstance(to, basestring) else to

    if STAGE or DEBUG or DEMO: #redirect non-production emails
      if DEMO:
        server_name = 'DEMO'
        self.from_email = "demo@theanou.com"
      elif STAGE:
        server_name = 'STAGE'
        self.from_email = "stage@theanou.com"
      else:
        server_name = 'LOCAL'
        self.from_email = "local@theanou.com"

      self.text_body = "*%s* To: %s\n %s" % (server_name,
                                             ','.join(self.to),
                                             self.text_body)
      self.html_body = "<h2>*%s* To: %s</h2> %s" % (server_name,
                                                    ','.join(self.to),
                                                    self.html_body)
      self.to = [('dev+test-%s@theanou.com' % server_name)]

    try:
      self.mail = EmailMultiAlternatives(
                    subject     = self.subject,
                    body        = self.text_body,
                    from_email  = self.from_email,
                    to          = self.to
                  )
      #sendgrid settings automatically bcc dump@theanou.com on every email
      self.mail.attach_alternative(self.html_body, "text/html")
      #if self.attachment_url:
      #  self.mail.attach_file(self.attachment_url)
      self.mail.send()
      self.save()

    except Exception as e:
      ExceptionHandler(e, "in email_class.sendTo", no_email=True)

  #def attach(self, url):
  #  self.attachment_url = url

  def save(self):
    from apps.communication.models.email import Email as EmailModel
    try:    self.order
    except: self.order = None

    try:
      email = EmailModel(
                from_address  = self.mail.from_email,
                to_address    = ','.join(self.mail.to),
                subject       = self.mail.subject,
                text_body     = self.mail.body,
                html_body     = self.mail.alternatives[0][0],
                order         = self.order
              )
    except Exception as e:
      ExceptionHandler(e, "in email_class.save")
    else:
      email.save()

  def assignToOrder(self, order):
    self.order = order
