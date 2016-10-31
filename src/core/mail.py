# classes to send mails to users
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Oct.31

# TODO: exceptions handlers, sending mails with attachments

import smtplib
from email.mime.text import MIMEText
from settings import MAIL_SETTINGS as ms
from settings import NOTIFY_MAIL_SETTINGS as nms
from settings import logger

class BaseMailSender(object):
	"""sends mails with text only"""
	def __init__(self, smtphost=None, smtpport=None, smtpuser=None, smtppass=None):
		super(BaseMailSender, self).__init__()
		self.smtphost = smtphost
		self.smtpport = smtpport
		self.smtpuser = smtpuser
		self.smtppass = smtppass

		self.smtp = smtplib.SMTP(self.smtphost, self.smtpport)
		logger.info("connected to smtp server {0}".format(self.smtphost))

	def __del__(self):
		self.smtp.quit()

	def send(self, from_addr, to_addrs, subj, content):
		msg = MIMEText(content)

		msg['Subject'] = subj
		msg['From'] = from_addr
		msg['To'] = to_addrs
		logger.info("sending messages to {0}".format(to_addrs))
		self.smtp.sendmail(from_addr, to_addrs, msg.as_string())



class NotifyMailSender(BaseMailSender):
	"""notifies users if tasks was done"""
	def __init__(self, recipients, sender=ms.get("sender")):
		super(NotifyMailSender, self).__init__(smtphost=ms.get("smtp_server"), smtpport=ms.get("smtp_port"))
		self.recipients = recipients
		self.sender = sender
	
	def notify(self, title):
		self.send(self.sender, self.recipients, nms['subject'].format(**locals()), nms['content'].format(**locals()))