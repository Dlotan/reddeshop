import webapp2
import jinja2
import os
#import logging

#from utils import *
#from database import *
#from admin import *


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

right_username = "admin"
right_password = "root"

class AdminBaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class AdminPage(AdminBaseHandler):
    def get(self):
        self.render("index.html")
        
        
class AdminLogin(AdminBaseHandler):
    def get(self):
        self.render("adminlogin.html")
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        if username == right_username and password == right_password:
            pass
        else:
            errortext = "user or password not correct"
            self.render("adminlogin.html",errortext = errortext, username = username)
        
class AdminIndex(AdminBaseHandler):
    def get(self):
        self.render("adminlogin.html")


            
app = webapp2.WSGIApplication([('/admin', AdminPage),
                               ('/admin/login', AdminLogin),
                               ('/admin/index', AdminIndex)
                               ], debug=True)