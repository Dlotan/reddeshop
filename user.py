import webapp2
import jinja2
import os
import logging
import settings

#from utils import *
from database import Category,Product, Payment,SubProduct,getShippingCost
from google.appengine.api import mail
from webapp2_extras import sessions


template_dir = os.path.join(os.path.dirname(__file__), 'templatesuser')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class UserBaseHandler(webapp2.RequestHandler):
    def dispatch(self):                                 # override dispatch
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)       # dispatch the main handler
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params).encode('utf-8')
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def userrender(self, template, **kw):
        categories = Category.getAllCategories()
        cart = self.session.get('cart')
        iconnumber = 0
        if cart:
            for position in cart:
                iconnumber = iconnumber + position[1]
        self.render(template, categories = categories, iconnumber = iconnumber, **kw)

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
            
class UserAddSingle(UserBaseHandler):
    def get(self, subproduct_id_string, amount_string):
        subproduct_id = int(subproduct_id_string)
        amount = int(amount_string)
        self.session['cart'] = [(subproduct_id,amount)]
        self.redirect('/checkout')
            
class UserCheckout(UserBaseHandler):
    def get(self,):
        cart = self.session.get('cart')
        newcart = []
        sumprice = 0.0
        for position in cart:
            subproduct = SubProduct.getSubProductById(position[0])
            product = SubProduct.getProduct(position[0])
            newcart.append((product,subproduct,position[1]))
            sumprice = sumprice + (product.price * position[1])
        sumprice = sumprice / 100.0
        self.userrender("usercheckout.html", cart = newcart, sumprice = sumprice, params = {})
    def post(self):
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
        params['shipping_cost'] = getShippingCost(params['shipping_region']) / 100.0
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
        if params['paymethod'] == "":
            params['paymethod_error'] = "Bezahlmethode fehlerhaft"
            error = True
        cart = self.session.get('cart')
        newcart = []
        sumprice = 0
        for position in cart:
            subproduct = SubProduct.getSubProductById(position[0])
            product = SubProduct.getProduct(position[0])
            newcart.append((product,subproduct,position[1]))
            sumprice = sumprice + (product.price * position[1])
        sumprice = sumprice / 100.
        if error == True:
            self.userrender("usercheckout.html", cart = newcart, sumprice = sumprice, params = params)
        else:
            self.userrender("userconfirm.html", cart = newcart, sumprice = sumprice, params = params)
            

class UserConfirm(UserBaseHandler):
    def post(self):
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
        params['shipping_cost'] = getShippingCost(params['shipping_region']) / 100.0
        params['paymethod'] = self.request.get("paymethod")
        error = False
        if params['first_name'] == "":
            error = True
        if params['last_name'] == "":
            error = True
        if params['street'] == "":
            error = True
        if params['street_number'] == "":
            error = True
        if params['plz'] == "":
            error = True
        if params['city'] == "":
            error = True
        if params['country'] == "":
            error = True
        if params['email'] == "":
            error = True
        if params['email2'] == "":
            error = True
        if params['email'] != params['email2']:
            error = True
        if params['paymethod'] == "":
            error = True
        if not error:
            cart = self.session.get('cart')
            paymentkey = Payment.addContactAndPayment(cart ,params)
            contact = Payment.getContact(paymentkey.id())
            extendedpositions = Payment.getExtendedPositions(paymentkey.id())
            message = mail.EmailMessage(sender="madcatsclothing <madcatsclothing@gmail.com>",
                                        subject="Order %s" % paymentkey.id())
            message.to = "%s %s <%s>" % (contact.first_name, contact.last_name, contact.email)
            messagebody = u'''
            Hallo %s,
            Deine Bestellung ist bei uns eingegangen.
            Gratulation! Du hast einen fabelhaften Geschmack.
            Dein Bestellstatus kannst Du sehen unter: http://www.madcatsclothing.com/status/%s
            Wenn Du noch Fragen oder Anregungen hast, dann melde Dich doch einfach bei uns und schreib uns eine E-mail!
            Ganz viel Liebe
            
            Dein Madcats-Team
            
            Hier nochmal eine auflistung deiner gekauften Produkte:
            ''' % (contact.first_name, paymentkey.id())
            for extendedposition in extendedpositions:
                messagebody = "%s Product: %s Size: %s Menge: %s\n" % (messagebody,extendedposition[0].name,extendedposition[1].value,extendedposition[2])
            message.body = messagebody
            message.Send()
            message = mail.EmailMessage(sender="madcatsclothing <madcatsclothing@gmail.com>",
                                        subject="New Order on madcatsclothing")
            message.to = "Lari <larissagoeb@gmail.com>"
            message.body = "Neue Bestellung"
            message.Send()
            self.session['cart'] = []
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
        sumprice = Payment.getSumWithoutShippingPrice(payment_id)
        contact = Payment.getContact(payment_id)
        paypal_url = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ext-enter&redirect_cmd=_xclick&business={email}&item_name={item_name}&item_number={item_number}&currency_code=EUR&amount={amount}&shipping={shipping}&tax=0&return={return_url}&cancel_return={cancel_url}&notify_url={ipn_url}".format(email = settings.ACCOUNT_EMAIL,
                                       item_name = ("Order %s" % payment.key.id()),
                                       item_number = payment.key.id(),
                                       amount = sumprice / 100.0,
                                       shipping = contact.shipping_cost / 100.0,
                                       return_url = "http://reddeshop.appspot.com/status/%s" % payment.key.id(),
                                       cancel_url = "http://www.google.de",
                                       ipn_url = "http://www.reddeshop.appspot.com/payment/ipn/%s" % payment.key.id())
        self.redirect(paypal_url)
        
class UserAbholung(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        extendedpositions = Payment.getExtendedPositions(payment_id)
        sumprice = Payment.getSumPrice(payment_id)
        contact = Payment.getContact(payment_id)
        cart = Payment.getExtendedPositions(payment_id)
        self.userrender("userabholung.html", payment = payment, 
                        extendedpositions = extendedpositions, 
                        contact = contact, 
                        cart = cart,
                        sumprice = sumprice / 100.0)
        
class UserUeberweisung(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        extendedpositions = Payment.getExtendedPositions(payment_id)
        sumprice = Payment.getSumPrice(payment_id)
        contact = Payment.getContact(payment_id)
        cart = Payment.getExtendedPositions(payment_id)
        self.userrender("userueberweisung.html", payment = payment, 
                        extendedpositions = extendedpositions, 
                        contact = contact, 
                        cart = cart,
                        sumprice = sumprice / 100.0)

class UserStatus(UserBaseHandler):
    def get(self, payment_id_string):
        payment_id = int(payment_id_string)
        payment = Payment.getPaymentById(payment_id)
        cart = Payment.getExtendedPositions(payment_id)
        contact = Payment.getContact(payment_id)
        sumprice = Payment.getSumPrice(payment_id)
        self.userrender("userstatus.html", payment = payment, 
                        cart = cart, 
                        contact = contact,
                        sumprice = sumprice / 100.0)

class UserCartAdd(UserBaseHandler):
    def get(self,subproduct_id_string,amount_string):
        subproduct_id = int(subproduct_id_string)
        amount = int(amount_string)
        cart = self.session.get('cart')
        summ = 0
        if cart:
            found = False
            for i,productposition in enumerate(cart):
                if productposition[0] == subproduct_id:
                    newamount = productposition[1] + amount
                    productposition[1] = newamount
                    cart[i] = productposition
                    found = True
                summ = summ + productposition[1]
            if not found:
                cart.append((subproduct_id,amount))
                summ = summ + amount
            self.session['cart'] = cart
            self.write("%s" % summ)
        else:
            self.session['cart'] = [(subproduct_id,amount)]
            self.write("%s" % amount)
            
class UserCartDelete(UserBaseHandler):
    def get(self,subproduct_id_string):
        subproduct_id = int(subproduct_id_string)
        cart = self.session.get('cart')
        for i,productposition in enumerate(cart):
            if productposition[0] == subproduct_id:
                cart.pop(i)
        self.session['cart'] = cart
        self.write("0")

class UserCartGetAmount(UserBaseHandler):
    def get(self):
        cart = self.session.get('cart')
        if cart:
            summ = 0
            for productposition in cart:
                summ = summ + productposition[1]
            self.write("%s" % summ)
        else:
            self.write("0")
            
class UserShowCart(UserBaseHandler):
    def get(self):
        cart = self.session.get('cart')
        newcart = []
        sumprice = 0
        if cart:
            for position in cart:
                subproduct = SubProduct.getSubProductById(position[0])
                product = SubProduct.getProduct(position[0])
                newcart.append((product,subproduct,position[1]))
                sumprice = sumprice + (product.price * position[1])
            sumprice = sumprice / 100.
        else:
            cart = []
        self.userrender("usercart.html", cart = newcart, sumprice = sumprice)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'qwertsdfcvb585',
}         
app = webapp2.WSGIApplication([('/', UserStart),
                               ('/index', UserIndex),
                               ('/product/(\d+)',UserProduct),
                               ('/addsingle/(\d+)/(\d+)',UserAddSingle),
                               ('/abholung/(\d+)',UserAbholung),
                               ('/ueberweisung/(\d+)',UserUeberweisung),
                               ('/paypal/(\d+)',UserPaypal),
                               ('/status/(\d+)',UserStatus),
                               ('/checkout',UserCheckout),
                               ('/confirm',UserConfirm),
                               ('/cart/add/(\d+)/(\d+)',UserCartAdd),
                               ('/cart/delete/(\d+)',UserCartDelete),
                               ('/cart/getamount',UserCartGetAmount),
                               ('/cart/show',UserShowCart)
                               ], debug=True, config = config)


