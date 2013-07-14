import random
import string
import hashlib

secret_word = "pw4dlotanwiki"
def make_salt(length = 5):
    return ''.join(random.choice(string.letters) for x in xrange(length))

def make_joint_hash(text, salt):
    h = make_hash(text,salt)
    return '%s|%s' % (text, h) 
 
def make_hash(text, salt):
    return hashlib.sha256(text + salt + secret_word).hexdigest()

def verify_hash(hashtext, salt):
    texts = hashtext.split("|")
    if make_hash(texts[0],salt) == texts[1]:
        return True
    
def split_hash(hashtext):
    texts = hashtext.split("|")
    return texts