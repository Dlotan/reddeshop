from google.appengine.ext import ndb

class Category(ndb.Model):
    name = ndb.StringProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def getAllCategories(cls):
        return cls.query()
    @classmethod
    def getCategoryByName(cls,name):
        return cls.query(Category.name == name).get()
    @classmethod
    def addCategory(cls,name):
        # already exist check ??!
        category = Category(name = name)
        category.put()
    @classmethod
    def getAllProducts(cls,name):
        category = Category.getCategoryByName(name)
        categorykey = category.key()
        return Product.query(ancestor = categorykey)
        
    
class Product(ndb.Model):
    name = ndb.StringProperty(required = True)
    price = ndb.IntegerProperty(required = True)
    description = ndb.TextProperty(required = False)
    pictureurl = ndb.StringProperty(required = False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def addProduct(cls,name,price,category,description = "", pictureurl = ""):
        category = Category.getCategoryByName(category)
        product = Product(name = name, price = price, description = description, pictureurl = pictureurl, parent = category.key)
        product.put()
    @classmethod
    def getProductByName(cls,name):
        return cls.query(Product.name == name).get()
    
    
    