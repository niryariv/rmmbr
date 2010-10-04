import cgi
import urllib
import re
import uuid
import os


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.ext.webapp import template


class Phone(db.Model):
  number = db.StringProperty(required = True)
  email  = db.StringProperty(required = True)
  status = db.StringProperty(required = True)
  verify_code = db.StringProperty(required = True)
  updated = db.DateTimeProperty(auto_now_add=True)
  
  
  
class ProcessSMS(webapp.RequestHandler):
  
  def get(self):
    number = cgi.escape(self.request.get('p').strip())
    text  = cgi.escape(self.request.get('t').strip())
    
    signup = re.compile('signup (.*)')
    #signup = s.match(text)
    
    if number == '' or text == '':
      return
    
    else:
      if signup.match(text):
        r = self.send_signup(signup.match(text).group(1), number)
      else:
        r = self.send_reminder(text, number)
    
    self.response.out.write(r)
    
      
  def send_reminder(self, text, number):
    body = "http://google.com/search?q=" + urllib.quote(text)
    subject = '[rmmbr] ' + text
    email = Phone.get_by_key_name('p_' + number).email
    mail.send_mail('rmmbr.mail@gmail.com', email, subject, body)


  def send_signup(self, email, number):
    p = Phone(
      key_name = 'p_'+number,
      number = number,
      email  = email,
      status = 'signup',
      verify_code = str(uuid.uuid1())
    )
    Phone.put(p)
    
    body = '''
      Welcome to rmmbr! 
      
      You're signed up now for phone# ''' + number + '''
      
      Whenever you want to send yourself a reminder, just send the following text to 41411: "rmmbr <message>".
      
      Enjoy!
    '''
    subject = '[rmmbr] Welcome to rmmbr!'
    mail.send_mail('rmmbr.mail@gmail.com', email, subject, body)
    
    
    
class MainPage(webapp.RequestHandler):
  def get(self):
    template_values = { 'sitename' : 'rmmbr'}
    
    path = os.path.join(os.path.dirname(__file__), 'views/index.html')

    # handle rmbr -> rmmbr (TODO: something cleaner, with WSGI framework)
    url = self.request.url
    rmmbr_url = url.replace('http://rmbr.appspot.com', 'http://rmmbr.appspot.com')
    if rmmbr_url != url:
      self.redirect(rmmbr_url)
    else:
      self.response.out.write(template.render(path, template_values))
      
    
    
application = webapp.WSGIApplication(
                                     [
                                     ('/send', ProcessSMS),
                                     ('/', MainPage)
                                     ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
