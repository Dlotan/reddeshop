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
        
    
class Product(ndb.Model):
    category = ndb.KeyProperty(required = True)
    name = ndb.StringProperty(required = True)
    price = ndb.IntegerProperty(required = True)
    description = ndb.TextProperty(required = False)
    pictureurl = ndb.StringProperty(required = False)
    published = ndb.BooleanProperty(default=False, required = False)
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
    def editProduct(cls, product_id, name, price, category, description = "", pictureurl = "", published = False):
        product = cls.get_by_id(product_id, ndb.Key(Category,'global'))
        category = Category.getCategoryByName(category)
        product.name = name
        product.price = price
        product.category = category.key
        product.description = description
        product.pictureurl = pictureurl
        product.published = published
        return product.put()
    @classmethod
    def getProductByName(cls,name):
        return cls.query(Product.name == name).get()
    @classmethod
    def getProductById(cls,product_id):
        return cls.get_by_id(product_id, ndb.Key(Category,'global'))
    
    
    