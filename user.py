import webapp2
import jinja2
import os
import logging
import settings

#from utils import *
from database import Category,Product, Payment
from google.appengine.api import mail


template_dir = os.path.join(os.path.dirname(__file__), 'templatesuser')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class UserBaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params).encode('utf-8')
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
        
class UserStart(UserBaseHandler):
    def get(self):
        self.userrender("userstart.html")
        
class UserProduct(UserBaseHandler):
    def get(self, product_id_string):
        if product_id_string.isdigit():
            product_id = int(product_id_string)
            product = Product.getProductById(product_id)
            subproducts = Product.getSubProducts(product_id)
            self.userrender("userproduct.html", product = product, subproducts = subproducts)
        else:
            self.redirect('/')
            
class UserBuy(UserBaseHandler):
    def get(self, product_id_string):
        if product_id_string.isdigit():
            product_id = int(product_id_string)
            product = Product.getProductById(product_id)
            subproducts = Product.getAvailableSubProducts(product_id)
            self.userrender("userbuy.html", product = product, subproducts = subproducts, params = {})
        else:
            self.redirect('/')
    def post(self, product_id_string):
        params = dict()
        params['first_name'] = self.request.get("first_name")
        params['last_name'] = self.request.get("last_name")
        params['street'] = self.request.get("street")
        params['street_number'] = self.request.get("street_number")
        params['plz'] = self.request.get("plz")
        params['city'] = self.request.get("city")
        params['email'] = self.request.get("email")
        params['email2'] = self.request.get("email2")
        params['country'] = self.request.get("country")
        params['shipping_region'] = self.request.get("shipping_region")
        params['subproduct_name'] = self.request.get("subproduct_name")
        params['paymethod'] = self.request.get("paymethod")
        error = False
        if params['first_name'] == "":
            params['first_name_error'] = "Vorame fehlerhaft"
            error = True
        if params['last_name'] == "":
            params['last_name_error'] = "Nachname fehlerhaft"
            error = True
        if params['street'] == "":
            params['street_error'] = "Strasse fehlerhaft"
            error = True
        if params['street_number'] == "":
            params['street_number_error'] = "Hausnummer fehlerhaft"
            error = True
        if params['plz'] == "":
            params['plz_error'] = "PLZ fehlerhaft"
            error = True
        if params['city'] == "":
            params['city_error'] = "Stadt fehlerhaft"
            error = True
        if params['country'] == "":
            params['country_error'] = "Land fehlerhaft"
            error = True
        if params['email'] == "":
            params['email_error'] = "Email fehlerhaft"
            error = True
        if params['email2'] == "":
            params['email2_error'] = "Email Wiederholung fehlerhaft"
            error = True
        if params['email'] != params['email2']:
            params['email_error'] = "Emails stimmen nicht ueberein"
            error = True
        if params['subproduct_name'] == "":
            params['subproduct_name_error'] = "Version fehlerhaft"
            error = True
        if params['paymethod'] == "":
            params['paymethod_error'] = "Bezahlmethode fehlerhaft"
            error = True
        product_id = int(product_id_string)
        product = Product.getProductById(product_id)
        if error == True:
            subproducts = Product.getAvailableSubProducts(product_id)
            self.userrender("userbuy.html", product = product, subproducts = subproducts, params = params)
        else:
            paymentkey = Payment.addContactAndPayment(product_id, params)
            contact = Payment.getContact(paymentkey.id())
            product = Payment.getProduct(paymentkey.id())
            subproduct = Payment.getSubProduct(paymentkey.id())
            message = mail.EmailMessage(sender="madcatsclothing <madcatsclothing@gmail.com>",
                                        subject="Order %s" % paymentkey.id())
            message.to = "%s %s <%s>" % (contact.first_name, contact.last_name, contact.email)
            messagebody = u'''
            Hallo %s,
            Deine Bestellung von %s in %s ist bei uns eingegangen.
            Gratulation! Du hast einen fabelhaften Geschmack.
            Dein Bestellstatus kannst Du sehen unter: http://www.madcatsclothing.com/status/%s
            Wenn Du noch Fragen oder Anregungen hast, dann melde Dich doch einfach bei uns und schreib uns eine E-mail!
            Ganz viel Liebe
            
            Dein Madcats-Team
            ''' % (contact.first_name, product.name, subproduct.value, paymentkey.id())
            message.body = messagebody
            message.Send()
            if params['paymethod'] == "paypal":
                self.redirect('/paypal/%s' % paymentkey.id())
            if params['paymethod'] == "ueberweisung":
                self.redirect('/ueberweisung/%s' % paymentkey.id())
            if params['paymethod'] == "persoenlich":
                self.redirect('/abholung/%s' % paymentkey.id())
                
class UserPaypal(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        product = Payment.getProduct(payment_id)
        subproduct = Payment.getSubProduct(payment_id)
        contact = Payment.getContact(payment_id)
        paypal_url = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ext-enter&redirect_cmd=_xclick&business={email}&item_name={item_name}&item_number={item_number}&currency_code=EUR&amount={amount}&shipping={shipping}&tax=0&return={return_url}&cancel_return={cancel_url}&notify_url={ipn_url}".format(email = settings.ACCOUNT_EMAIL,
                                       item_name = ("%s Size: %s" % (product.name,subproduct.value)),
                                       item_number = product.key.id(),
                                       amount = product.price / 100.0,
                                       shipping = contact.shipping_cost / 100.0,
                                       return_url = "http://reddeshop.appspot.com/status/%s" % payment.key.id(),
                                       cancel_url = "http://www.google.de",
                                       ipn_url = "http://www.reddeshop.appspot.com/payment/ipn/%s" % payment.key.id())
        self.redirect(paypal_url)
        
class UserAbholung(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        product = Payment.getProduct(payment_id)
        subproduct = Payment.getSubProduct(payment_id)
        contact = Payment.getContact(payment_id)
        self.userrender("userabholung.html", payment = payment, product = product, subproduct = subproduct, contact = contact)
        
class UserUeberweisung(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        product = Payment.getProduct(payment_id)
        subproduct = Payment.getSubProduct(payment_id)
        contact = Payment.getContact(payment_id)
        self.userrender("userueberweisung.html", payment = payment, product = product, subproduct = subproduct, contact = contact)

class UserStatus(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        product = Payment.getProduct(payment_id)
        subproduct = Payment.getSubProduct(payment_id)
        contact = Payment.getContact(payment_id)
        self.userrender("userstatus.html", payment = payment, product = product, subproduct = subproduct, contact = contact)
            
app = webapp2.WSGIApplication([('/wadda', UserIndex),
                               ('/index', UserStart),
                               ('/', UserStart),
                               ('/product/(\d+)',UserProduct),
                               ('/abholung/(\d+)',UserAbholung),
                               ('/ueberweisung/(\d+)',UserUeberweisung),
                               ('/paypal/(\d+)',UserPaypal),
                               ('/status/(\d+)',UserStatus),
                               ('/buy/(\d+)',UserBuy)
                               ], debug=True)


