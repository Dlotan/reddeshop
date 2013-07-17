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
    def userrender(self, template, **kw):
        categories = Category.getAllCategories()
        self.render(template, categories = categories, **kw)

class UserIndex(UserBaseHandler):
    def get(self):
        products = Product.getAllProductsOrderShowcaseposition()
        self.userrender("userindex.html", products = products)
        
class UserProduct(UserBaseHandler):
    def get(self, product_id_string):
        if product_id_string.isdigit():
            product_id = int(product_id_string)
            product = Product.getProductById(product_id)
            category = Category.getCategoryById(product.category.id())
            self.userrender("userproduct.html", product = product, category = category)
        else:
            self.redirect('/')


            
app = webapp2.WSGIApplication([('/', UserIndex),
                               ('/product/(\d+)',UserProduct)
                               ], debug=True)


