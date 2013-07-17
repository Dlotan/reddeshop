from google.appengine.ext import ndb

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
    pictureurl = ndb.StringProperty(required = False)
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
    
    
    