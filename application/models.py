import flask
from application import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserStore(db.Document):
    user_id     =   db.StringField( unique=True )
    password    =   db.StringField( )
    timestamp    =   db.DateTimeField( )
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)    

class Customer(db.Document):
    TYPE = (('ACTIVE', 'ACTIVE'),('IN_ACTIVE', 'IN ACTIVE'))
    ws_ssn   =   db.IntField(  unique=True )
    ws_cust_id  =   db.StringField(  )
    ws_name  =   db.StringField( max_length=255 )
    ws_adrs  =   db.StringField()
    ws_age   =   db.IntField(  )
    ws_status   =   db.StringField(max_length=10, choices=TYPE)
    ws_cust_update   =   db.DateTimeField(  )
    ws_message = db.StringField()
class Account(db.Document):
    TYPE = (('S', 'Savings'),('C', 'Current'))
    ws_cust_id   =   db.StringField(   )
    ws_acct_id  =   db.StringField(unique=True  )
    ws_acct_type  =   db.StringField(max_length=3, choices=TYPE)
    ws_acct_balance  =   db.IntField(min_value=0)
    ws_acct_crdate   =   db.DateTimeField(  )
    ws_acct_lasttrdate   =   db.DateTimeField(  )
    ws_acct_duration   =   db.IntField( min_value=0 )
class Transactions(db.Document):
    TYPE = (('S', 'Savings'),('C', 'Current'))
    ws_tnsc_id   =   db.StringField(   )
    ws_acct_id   =   db.StringField(  )
    ws_accnt_type  =   db.StringField(max_length=3, choices=TYPE)
    ws_desc  =   db.StringField()
    ws_amt  =   db.IntField( min_value=1 )
    ws_trxn_date  =   db.DateTimeField()
    ws_src_typ   =   db.StringField(max_length=3, choices=TYPE)
    ws_tgt_typ   =   db.StringField(max_length=3, choices=TYPE)

