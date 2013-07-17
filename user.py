import webapp2
import jinja2
import os
#import logging

#from utils import *
from database import Category,Product
#from admin import *


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class UserBaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class UserIndex(UserBaseHandler):
    def get(self):
        categories = Category.getAllCategories()
        products = Product.getAllProductsOrderShowcaseposition()
        self.render("userindex.html", categories = categories, products = products)


            
app = webapp2.WSGIApplication([('/', UserIndex),
                               ], debug=True)


