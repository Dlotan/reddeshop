import logging
import webapp2
from database import Payment, TXNStore

import urllib
#from google.appengine.api import mail
from google.appengine.api import urlfetch
PP_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"
ACCOUNT_EMAIL= "florianseller@gmail.com"
#PP_URL = "https://www.paypal.com/cgi-bin/webscr"
#ACCOUNT_EMAIL = "my_email_for_real-paypal_acct@good.com"

class IPNHandler(webapp2.RequestHandler):
    def post(self, payment_id_string):   
        payment_id = int(payment_id_string) 
        parameters = None
        # Check payment is completed, not Pending or Failed.
        if self.request.get('payment_status') == 'Completed':
            if self.request.POST:
                parameters = self.request.POST.copy()
            if self.request.GET:
                parameters = self.request.GET.copy()
            logging.debug('IPN 1, or your own message for yourself to read in log.')
        else:
            self.response.out.write('Error, sorry. The parameter payment_status was not Completed.')
        if parameters:
            logging.debug('Hat Parameter erhalten')
            parameters['cmd']='_notify-validate'
            params = urllib.urlencode(parameters)
            status = urlfetch.fetch(
                         url = PP_URL,
                         method = urlfetch.POST,  
                         payload = params,
                        ).content
            if not status == "VERIFIED":
                self.response.out.write('Error. The request could not be verified, check for fraud.')
                parameters['homemadeParameterValidity']=False 
            if parameters['receiver_email'] == ACCOUNT_EMAIL:
                logging.debug('receiver mail stimmt')
                transaction_id = parameters['txn_id']
                if not TXNStore.checkTXN_ID(transaction_id):
                    logging.debug('transaction_id noch nicht benutzt')
                    TXNStore.addTXN_ID(transaction_id)
                    logging.debug('IPN 100. All OK.')
                    logging.debug(parameters['txn_id'])
                    logging.debug(parameters['payer_email'])
                    logging.debug(parameters['mc_gross'])
                    Payment.setPayed(payment_id, True)
            
            
app = webapp2.WSGIApplication([('/payment/ipn/(\d+)', IPNHandler)
                               ], debug=True)