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

right_username = "admin"
right_password = "root"
admin_secret = "5e4r6t7zughkjftzguzuhijonbkhjzgqwe2190u98iokml"

class AdminBaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    #check for admin coockie
    def adminrender(self, template, **kw):
        if self.request.cookies.get('admin_secret') == admin_secret:
            self.response.out.write(self.render_str(template, **kw))
        else:
            self.redirect("/admin/login")
    def checkAdminCookie(self):
        if self.request.cookies.get('admin_secret') == admin_secret:
            return True
            

class AdminPage(AdminBaseHandler):
    def get(self):
        self.redirect("/admin/index")
               
class AdminLogin(AdminBaseHandler):
    def get(self):
        self.render("adminlogin.html")
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        if username == right_username and password == right_password:
            self.response.headers.add_header('Set-Cookie', 'admin_secret=%s; Path=/' % admin_secret)
            self.redirect("/admin/index") 
        else:
            errortext = "user or password not correct"
            self.render("adminlogin.html", errortext = errortext, username = username)
 
#Admin main site           
class AdminIndex(AdminBaseHandler):
    def get(self):
        self.adminrender("adminindex.html")
      
class AdminNewCategory(AdminBaseHandler):
    def get(self):
        self.adminrender("adminnewcategory.html")
    def post(self):
        if self.checkAdminCookie():
            categoryname = self.request.get("name")
            Category.addCategory(categoryname)
            self.redirect("/admin/index")
        else:
            self.redirect("/admin/login")
        
#todo
class AdminEditCategory(AdminBaseHandler):
    def get(self):
        self.adminrender("adminindex.html")        
class AdminNewProduct(AdminBaseHandler):
    def get(self):
        categories = Category.getAllCategories()
        self.adminrender("adminnewproduct.html", categories = categories)
    def post(self):
        if self.checkAdminCookie():
            name = self.request.get("name")
            category = self.request.get("category")
            price = self.request.get("price")
            try:
                price = int(price)
            except ValueError:
                price = 0
            description = self.request.get("description")
            pictureurl = self.request.get("pictureurl")
            Product.addProduct(name, price, category, description, pictureurl)
            self.redirect("/admin/index")
        else:
            self.redirect("/admin/login")
#todo
class AdminEditProduct(AdminBaseHandler):
    def get(self):
        self.adminrender("adminindex.html")
            
app = webapp2.WSGIApplication([('/admin/*', AdminPage),
                               ('/admin/login', AdminLogin),
                               ('/admin/index', AdminIndex),
                               ('/admin/newcategory', AdminNewCategory),
                               ('/admin/editcategory', AdminEditCategory),
                               ('/admin/newproduct', AdminNewProduct),
                               ('/admin/editproduct', AdminEditProduct)
                               ], debug=True)