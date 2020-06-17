import flask
from application import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserStore(db.Document):
    user_id     =   db.StringField( unique=True )
    password    =   db.StringField( )
    timestamp    =   db.DateTimeField( )
    role = db.StringField( )
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)    

class Customer(db.Document):
    STATUS = (('UPDATED', 'UPDATED'),('CREATED', 'CREATED'),('DELETED', 'DELETED'))
    ws_ssn   =   db.IntField(  unique=True )
    ws_cust_id  =   db.StringField(  )
    ws_name  =   db.StringField( max_length=255 )
    ws_adrs1  =   db.StringField()
    ws_adrs2  =   db.StringField()
    ws_city =   db.StringField()
    ws_state =   db.StringField()
    ws_age   =   db.IntField(  )
    ws_status   =   db.StringField(max_length=10, choices=STATUS)
    ws_cust_update   =   db.DateTimeField(  )
    ws_message = db.StringField()

class Account(db.Document):
    TYPE = (('S', 'Savings'),('C', 'Current'))
    STATUS = (('UPDATED', 'UPDATED'),('CREATED', 'CREATED'),('DELETED', 'DELETED'))
    ws_cust_id   =   db.StringField(   )
    ws_acct_id  =   db.StringField(unique=True  )
    ws_acct_type  =   db.StringField(max_length=3, choices=TYPE)
    ws_status   =   db.StringField(max_length=10, choices=STATUS)
    ws_message = db.StringField(   )
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

