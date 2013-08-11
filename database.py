from google.appengine.ext import ndb
from datetime import datetime
import logging

class Category(ndb.Model):
    name = ndb.StringProperty(required = True)
    position = ndb.IntegerProperty(default = 1)
    created = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def getAllCategories(cls):
        return cls.query()
    @classmethod
    def getAllCategoriesOrderPosition(cls):
        return cls.query().order(Category.position)
    @classmethod
    def getCategoryByName(cls,name):
        return cls.query(Category.name == name).get()
    @classmethod
    def getCategoryById(cls,category_id):
        return cls.get_by_id(category_id, ndb.Key(Category,'global'))
    @classmethod
    def addCategory(cls,name):
        # already exist check ??!
        category = Category(name = name, 
                            parent = ndb.Key(Category,'global'))
        category.put()
    @classmethod
    def getAllProducts(cls,categoryname):
        category = Category.getCategoryByName(categoryname)
        return Product.query(Product.category == category.key)
    @classmethod
    def getAllProductsOrderPosition(cls,categoryname):
        category = Category.getCategoryByName(categoryname)
        return Product.query(Product.category == category.key).filter(Product.position > -1).order(Product.position) #ndb.and ??!
        
class Product(ndb.Model):
    category = ndb.KeyProperty(required = True)
    name = ndb.StringProperty(required = True)
    price = ndb.IntegerProperty(required = True)
    description = ndb.TextProperty(required = False)
    pictureurl = ndb.TextProperty(required = False)
    position = ndb.IntegerProperty(default = -1) #position in category. -1 if not shown
    showcaseposition = ndb.IntegerProperty(default = -1) #position on frontpage. -1 if not on frontpage
    last_edited = ndb.DateTimeProperty(auto_now=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def addProduct(cls,name,price,category,description = "", pictureurl = ""):
        category = Category.getCategoryByName(category)
        product = Product(name = name, price = price, 
                          description = description, 
                          pictureurl = pictureurl, 
                          category = category.key, 
                          parent = ndb.Key(Category,'global'))
        return product.put()
    @classmethod
    def editProduct(cls, product_id, name, price, category, description = "", pictureurl = "", position = -1, showcaseposition = -1):
        product = cls.get_by_id(product_id, ndb.Key(Category,'global'))
        category = Category.getCategoryByName(category)
        product.name = name
        product.price = price
        product.category = category.key
        product.description = description
        product.pictureurl = pictureurl
        product.position = position
        product.showcaseposition = showcaseposition
        return product.put()
    @classmethod
    def getProductByName(cls,name):
        return cls.query(Product.name == name).get()
    @classmethod
    def getProductById(cls,product_id):
        return cls.get_by_id(product_id, ndb.Key(Category,'global'))
    @classmethod
    def getAllProducts(cls):
        return cls.query()
    @classmethod
    def getAllProductsOrderShowcaseposition(cls):
        return cls.query(Product.showcaseposition > -1).order(Product.showcaseposition)
    @classmethod
    def addSubProduct(cls, product_id, value, position):
        product = cls.get_by_id(product_id, ndb.Key(Category,'global'))
        subproduct = SubProduct(product = product.key,
                                value = value,
                                position = position,
                                parent = ndb.Key(Category,'global'))
        return subproduct.put()
    @classmethod
    def getSubProducts(cls, product_id):
        product = cls.get_by_id(product_id, ndb.Key(Category,'global'))
        subproducts = SubProduct.query(SubProduct.product == product.key)
        subproducts = [subproduct for subproduct in subproducts if subproduct.position >= 0]
        subproducts = sorted(subproducts, key = lambda subproduct: subproduct.position)
        return subproducts
    @classmethod
    def getAvailableSubProducts(cls, product_id):
        product = cls.get_by_id(product_id, ndb.Key(Category,'global'))
        subproducts = SubProduct.query(SubProduct.product == product.key, SubProduct.available == True)
        subproducts = [subproduct for subproduct in subproducts if subproduct.position >= 0]
        subproducts = sorted(subproducts, key = lambda subproduct: subproduct.position)
        return subproducts
    @classmethod
    def getSubProductByName(cls, product_id, subproduct_value):
        return [subproduct for subproduct in cls.getSubProducts(product_id) if subproduct.value == subproduct_value and subproduct.position >= 0][0]
    
class SubProduct(ndb.Model):
    product = ndb.KeyProperty(kind = 'Product',required = True)
    value = ndb.StringProperty(required = True)
    position = ndb.IntegerProperty(required = True)
    available = ndb.BooleanProperty(default = True)
    @classmethod
    def getSubProductById(cls, subproduct_id):
        subproduct = cls.get_by_id(subproduct_id, ndb.Key(Category,'global'))
        return subproduct
    @classmethod
    def deleteSubProduct(cls, subproduct_id):
        subproduct = cls.getSubProductById(subproduct_id)
        subproduct.position = -1
        subproduct.put()
    @classmethod
    def setAvailability(cls, subproduct_id, availability):
        subproduct = cls.getSubProductById(subproduct_id)
        subproduct.available = availability
        return subproduct.put()
    @classmethod
    def getProduct(cls, subproduct_id):
        subproduct = cls.get_by_id(subproduct_id, ndb.Key(Category,'global'))
        product = Product.getProductById(subproduct.product.id())
        return product
    
class Contact(ndb.Model):
    first_name = ndb.StringProperty(required = True)
    last_name = ndb.StringProperty(required = True)
    street = ndb.StringProperty(required = True)
    street_number = ndb.StringProperty(required = True)
    plz = ndb.StringProperty(required = True)
    city = ndb.StringProperty(required = True)
    country = ndb.StringProperty(required = True)
    shipping_region = ndb.StringProperty(choices = ["germany","eu","worldwide"],default = "germany")
    email = ndb.StringProperty(required = True)
    shipping_cost = ndb.ComputedProperty(lambda self: getShippingCost(self.shipping_region))
    @classmethod
    def addContact(cls, params):
        contact = Contact(first_name = params['first_name'],
                          last_name = params['last_name'],
                          street = params['street'],
                          street_number = params['street_number'],
                          plz = params['plz'],
                          city = params['city'],
                          shipping_region = params['shipping_region'],
                          email = params['email'],
                          country = params['country'],
                          parent = ndb.Key(Category,'global'))
        return contact.put()
    @classmethod
    def getContactById(cls, contact_id):
        return cls.get_by_id(contact_id, ndb.Key(Category,'global'))
    @classmethod
    def deleteContact(cls, contact_id):
        contact = cls.getContactById(contact_id)
        contact.key.delete()
def getShippingCost(shipping_region):
    if shipping_region == "germany":
        return 0
    elif shipping_region == "eu":
        return 700
    else:
        return 1500
    
        
#class Cart(ndb.Model):
#    subproducts = ndb.KeyProperty(kind = 'SubProduct', required = True)
    
    
class Payment(ndb.Model):
    subproduct = ndb.KeyProperty(kind = 'SubProduct',required = True)
    contact = ndb.KeyProperty(kind = 'Contact',required = True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    paymethod = ndb.StringProperty(choices = ["paypal", "persoenlich", "ueberweisung"], required = True)
    state = ndb.StringProperty(choices = ["processing","transit","finished","canceled"], default = "processing")
    payed = ndb.BooleanProperty(default = False)
    @classmethod
    def getPaymentById(cls, payment_id):
        return cls.get_by_id(payment_id, ndb.Key(Category,'global'))
    @classmethod
    def addContactAndPayment(cls, product_id, params):
        contact = Contact.addContact(params)
        subproduct = Product.getSubProductByName(product_id, params['subproduct_name'])
        payment = Payment(subproduct = subproduct.key,
                          contact = contact,
                          paymethod = params['paymethod'],
                          parent = ndb.Key(Category,'global'))
        return payment.put()
    @classmethod
    def getContact(cls, payment_id):
        payment = cls.getPaymentById(payment_id)
        return Contact.getContactById(payment.contact.id())
    @classmethod
    def getSubProduct(cls, payment_id):
        payment = cls.getPaymentById(payment_id)
        return SubProduct.getSubProductById(payment.subproduct.id())
    @classmethod
    def getProduct(cls, payment_id):
        payment = cls.getPaymentById(payment_id)
        subproduct = SubProduct.getSubProductById(payment.subproduct.id())
        return SubProduct.getProduct(subproduct.key.id())
    @classmethod
    def getActivePaymentDicts(cls):
        mylist = []
        payments = cls.query(Payment.state != "finished")
        payments = sorted(payments, key = lambda payment: payment.date)
        for payment in payments:
            params = {}
            params['payment'] = payment
            params['contact'] = cls.getContact(payment.key.id())
            params['product'] = cls.getProduct(payment.key.id())
            params['subproduct'] = cls.getSubProduct(payment.key.id())
            mylist.append(params)
        return mylist
    @classmethod
    def setPaymentState(cls, payment_id, state):
        payment = cls.getPaymentById(payment_id)
        payment.state = state
        return payment.put()
    @classmethod
    def deletePayment(cls, payment_id):
        payment = cls.getPaymentById(payment_id)
        Contact.deleteContact(payment.contact.id())
        payment.key.delete()
    @classmethod
    def setPayed(cls, payment_id, payed):
        payment = cls.getPaymentById(payment_id)
        payment.payed = payed
        payment.put()
    @classmethod
    def getSumPrice(cls, payment_id):
        payment = cls.getPaymentById(payment_id)
        contact = cls.getContact(payment_id)
        shipping_cost = contact.shipping_cost
        product_price = SubProduct.getProduct(payment.subproduct.id()).price
        return shipping_cost + product_price
    @classmethod
    def getShippingCost(cls, payment_id):
        payment = cls.getPaymentById(payment_id)
        contact = cls.getContact(payment_id)
        return contact.shipping_cost
        
class TXNStore(ndb.Model):
    txn_id = ndb.StringProperty(required = True)
    @classmethod
    def addTXN_ID(cls,txn_id):
        txnstore = TXNStore(txn_id = txn_id ,parent = ndb.Key(Category,'global'))
        return txnstore.put()
    @classmethod
    def checkTXN_ID(cls, txn_id):
        return cls.query(TXNStore.txn_id == txn_id).get()
        

    