import webapp2
import jinja2
import os
import logging
import settings

#from utils import *
from database import Category,Product, SubProduct,Payment


template_dir = os.path.join(os.path.dirname(__file__), 'templatesadmin')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


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
        if self.request.cookies.get('admin_secret') == settings.admin_secret:
            self.response.out.write(self.render_str(template, **kw))
        else:
            self.redirect("/admin/login")
    def checkAdminCookie(self):
        if self.request.cookies.get('admin_secret') == settings.admin_secret:
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
        if username == settings.right_admin_username and password == settings.right_admin_password:
            self.response.headers.add_header('Set-Cookie', 'admin_secret=%s; Path=/' % settings.admin_secret)
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
class AdminEditCategories(AdminBaseHandler):
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
            product_key = Product.addProduct(name, price, category)
            self.redirect("/admin/product/editproduct/%s" % product_key.id())
        else:
            self.redirect("/admin/login")
            
#todo
class AdminEditProduct(AdminBaseHandler):
    def get(self,product_id_string):
        if product_id_string.isdigit():
            product_id = int(product_id_string)
            product = Product.getProductById(product_id)
            category = Category.getCategoryById(product.category.id())
            categories = Category.getAllCategories()
            self.adminrender("admineditproduct.html",
                             product = product,
                             category = category,
                             categories = categories)
        else:
            self.redirect("/admin/index")
    def post(self,product_id_string):
        if product_id_string.isdigit() and self.checkAdminCookie():
            product_id = int(product_id_string)
            name = self.request.get("name")
            category = self.request.get("category")
            price = self.request.get("price")
            description = self.request.get("description")
            pictureurl = self.request.get("pictureurl")
            position = self.request.get("position")
            showcaseposition = self.request.get("showcaseposition")
            try:
                price = int(price)
                position = int(position)
                showcaseposition = int(showcaseposition)
            except ValueError:
                price = 0
                position = -1
                showcaseposition = -1
            Product.editProduct(product_id, name, price, category, description, pictureurl, position, showcaseposition)
            self.redirect("/admin/product/editproduct/%s" % product_id_string)
        else:
            self.redirect("/admin/index")
        
class AdminEditProducts(AdminBaseHandler):
    def get(self):
        products = Product.getAllProducts()
        self.adminrender("admineditproducts.html", products = products)
        
class AdminAddSubProduct(AdminBaseHandler):
    def get(self, product_id_string):
        if product_id_string.isdigit() and self.checkAdminCookie():
            product_id = int(product_id_string)
            product = Product.getProductById(product_id)
            subproducts = Product.getSubProducts(product_id)
            self.adminrender("adminaddsubproduct.html",
                             product = product,
                             subproducts = subproducts)
        else:
            self.redirect("/admin/index")
    def post(self, product_id_string):
        if product_id_string.isdigit() and self.checkAdminCookie():
            product_id = int(product_id_string)
            value = self.request.get("value")
            position = self.request.get("position")
            position = int(position)
            Product.addSubProduct(product_id, value, position)
            self.redirect("/admin/product/%s/addsubproduct" % product_id_string)
        else:
            self.redirect("/admin/index")
            
class AdminEditSubProducts(AdminBaseHandler):
    def get(self, product_id_string):
        if product_id_string.isdigit() and self.checkAdminCookie():
            product_id = int(product_id_string)
            product = Product.getProductById(product_id)
            subproducts = Product.getSubProducts(product_id)
            self.adminrender("admineditsubproduct.html",
                             product = product,
                             subproducts = subproducts)
        else:
            self.redirect("/admin/index")
            
class AdminEditSubProduct(AdminBaseHandler):
    def get(self, subproduct_id_string):
        if subproduct_id_string.isdigit() and self.checkAdminCookie():
            subproduct_id = int(subproduct_id_string)
            product = SubProduct.getProduct(subproduct_id)
            command = self.request.get("command")
            if command == "delete":
                SubProduct.deleteSubProduct(subproduct_id)
            elif command == "available":
                SubProduct.setAvailability(subproduct_id, True)
            elif command == "notavailable":
                SubProduct.setAvailability(subproduct_id, False)
        self.redirect("/admin/product/%s/editsubproducts" % product.key.id())
        
class AdminEditPayments(AdminBaseHandler):
    def get(self):
        paymentdicts = Payment.getActivePaymentDicts()
        self.adminrender("admineditpayments.html", paymentdicts = paymentdicts)
        
class AdminEditPayment(AdminBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        command = self.request.get("command")
        if command == "delete":
            Payment.deletePayment(payment_id)
        elif command == "payed":
            Payment.setPayed(payment_id, True)
        elif command == "notpayed":
            Payment.setPayed(payment_id, False)
        else:
            Payment.setPaymentState(payment_id, command)
        self.redirect("/admin/payments")
            
            
app = webapp2.WSGIApplication([('/admin/*', AdminPage),
                               ('/admin/login', AdminLogin),
                               ('/admin/index', AdminIndex),
                               ('/admin/newcategory', AdminNewCategory),
                               ('/admin/editcategory', AdminEditCategories),
                               ('/admin/product/newproduct', AdminNewProduct),
                               ('/admin/product/editproduct/(\d+)',AdminEditProduct),
                               ('/admin/product/editproduct', AdminEditProducts),
                               ('/admin/product/(\d+)/addsubproduct', AdminAddSubProduct),
                               ('/admin/product/(\d+)/editsubproducts', AdminEditSubProducts),
                               ('/admin/product/editsubproduct/(\d+)', AdminEditSubProduct),
                               ('/admin/payments',AdminEditPayments),
                               ('/admin/payment/(\d+)',AdminEditPayment)
                               ], debug=True)