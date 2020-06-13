from application import app, db
from datetime import datetime
from flask import render_template, request, json, Response, redirect, flash, url_for, session
from application.models import UserStore, Customer, Account,Transactions
from application.forms import LoginForm, RegisterForm ,CustomerForm, AccountForm
courseData = [{"courseID":"1111","title":"PHP 111","description":"Intro to PHP","credits":"3","term":"Fall, Spring"}, {"courseID":"2222","title":"Java 1","description":"Intro to Java Programming","credits":"4","term":"Spring"}, {"courseID":"3333","title":"Adv PHP 201","description":"Advanced PHP Programming","credits":"3","term":"Fall"}, {"courseID":"4444","title":"Angular 1","description":"Intro to Angular","credits":"3","term":"Fall, Spring"}, {"courseID":"5555","title":"Java 2","description":"Advanced Java Programming","credits":"4","term":"Fall"}]
import random
import string
from mongoengine.queryset.visitor import Q
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True )

@app.route("/login", methods=['GET','POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_id       = form.user_id.data
        password    = form.password.data

        user = UserStore.objects(user_id=user_id).first()
        if user and user.get_password(password):
            flash(f"{user.user_id}, you are successfully logged in!", "success")
            session['user_id'] = user.user_id
            return redirect("/index")
        else:
            flash("Sorry, something went wrong.","danger")
    return render_template("login.html", title="Login", form=form, login=True )

@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('user_id',None)
    return redirect(url_for('index'))


@app.route("/register", methods=['POST','GET'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id       = form.user_id.data
        password    = form.password.data
        user = UserStore(user_id=user_id)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form, register=True)

@app.route("/create_account", methods=['POST','GET'])
def create_account():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        ws_cust_id       = request.form['ws_cust_id']
        ws_acct_id       = get_random_alphaNumeric_string(8)
        ws_acct_type       = request.form['ws_acct_type']
        ws_acct_balance       = request.form['ws_acct_balance']
        ws_acct_crdate       =  datetime.now()
        ws_acct_lasttrdate       =  datetime.now()
        ws_acct_duration       = 0
        account = Account(ws_cust_id=ws_cust_id,ws_acct_id=ws_acct_id,ws_acct_type=ws_acct_type,ws_acct_balance=ws_acct_balance,ws_acct_crdate=ws_acct_crdate,ws_acct_lasttrdate=ws_acct_lasttrdate,ws_acct_duration=ws_acct_duration)
        account.save()
        flash("Account Created successfully !","success")
        return redirect(url_for('index'))
    return render_template("account_form.html" )
def get_random_alphaNumeric_string(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
@app.route("/create_customer", methods=['POST','GET'])
def create_customer():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    form =CustomerForm()
    if form.validate_on_submit():
        ws_ssn       = form.ws_ssn.data
        ws_cust_id       = get_random_alphaNumeric_string(8)
        ws_name       = form.ws_name.data
        ws_adrs       = form.ws_adrs.data
        ws_age       = form.ws_age.data
        ws_status = 'ACTIVE'
        ws_cust_update =   datetime.now()
        customer = Customer(ws_ssn=ws_ssn,ws_cust_id=ws_cust_id,ws_name=ws_name,ws_adrs=ws_adrs,ws_age=ws_age,ws_status=ws_status,ws_cust_update=ws_cust_update)
        customer.save()
        flash("Customer Created successfully !","success")
        return redirect(url_for('index'))
    return render_template("customer_form.html", form=form)
@app.route("/customers/")
@app.route("/customers/<cid>")
def customers(cid = False):
    customers = Customer.objects.order_by("-ws_cust_id")
    if cid :
        customers = Customer.objects(ws_cust_id=cid)
    return render_template("customers.html", customers=customers, courses = True, term=cid )
@app.route("/accounts/")
@app.route("/accounts/<aid>")
def accounts(aid = False):
    accounts = Account.objects.order_by("-ws_acct_id")
    if aid :
        accounts = Account.objects(ws_acct_id=aid)
    return render_template("accounts.html", accounts=accounts, courses = True, term=aid )
@app.route("/update_customer/<cid>", methods=['POST','GET'])
def update_customer(cid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        ws_name       = request.form['ws_name']
        ws_adrs       = request.form['ws_adrs']
        ws_age       = request.form['ws_age']
        ws_status       = request.form['ws_status']
        ws_message       = request.form['ws_message']
        ws_cust_update =   datetime.now()
        Customer.objects(ws_cust_id=cid).update_one(ws_name=ws_name,ws_adrs=ws_adrs,ws_cust_update=ws_cust_update,ws_age=ws_age,ws_status=ws_status,ws_message=ws_message) 
        flash("Customer Updated successfully !","success")
        return redirect(url_for('index'))
    else:
        customers = Customer.objects(ws_cust_id=cid)
        return render_template("customer_update.html", datas=customers)

@app.route("/delete_customer/<cid>")
def delete_customer(cid):
    print(cid,flush=True)
    Customer.objects(ws_cust_id=cid).delete()
    flash("Customer Deleted successfully !","success")
    return redirect(url_for('customers'))

@app.route("/withdraw/<aid>", methods=["GET","POST"])
def withdraw(aid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount=request.form['amount']
        previous_amount=request.form['ws_acct_balance']
        ws_acct_id = request.form['ws_acct_id']
        ws_acct_balance=int(previous_amount)-int(amount)
        if ws_acct_balance<=0:
            flash("With draw  failure insuffiecient funds !","fail")
            url='/withdraw/'+ws_acct_id
            return redirect(url)
        Account.objects(ws_acct_id=ws_acct_id).update_one(ws_acct_balance=ws_acct_balance)
        # transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Withdraw',ws_amt=amount,ws_trxn_date=datetime.now())
        # transactions.save()
        url='/accounts/'+ws_acct_id
        return redirect(url)
    account = Account.objects(ws_acct_id=aid).first()
    return render_template("withdraw.html",account=account)

@app.route("/deposit/<aid>", methods=["GET","POST"])
def deposit(aid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount=request.form['amount']
        previous_amount=request.form['ws_acct_balance']
        ws_acct_id = request.form['ws_acct_id']
        ws_acct_balance=int(previous_amount)+int(amount)
        Account.objects(ws_acct_id=ws_acct_id).update_one(ws_acct_balance=ws_acct_balance)
        # transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Deposit',ws_amt=amount,ws_trxn_date=datetime.now())
        # transactions.save()
        url='/accounts/'+ws_acct_id
        return redirect(url)
    account = Account.objects(ws_acct_id=aid).first()
    return render_template("deposit.html",account=account)
@app.route("/transfer/<cid>", methods=["GET","POST"])
def transfer(cid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        pass
    account = Account.objects(ws_cust_id=cid)
    count = Account.objects(ws_cust_id=cid).count()
    return render_template("transfer.html",account=account,ws_cust_id=cid,count=count)
@app.route("/delete_account/<aid>")
def delete_account(aid):
    print(aid,flush=True)
    Account.objects(ws_acct_id=aid).delete()
    flash("Customer Deleted successfully !","success")
    return redirect(url_for('accounts'))
@app.route("/search_account", methods=["GET","POST"])
def search_account():
    if request.method == 'POST':
        ws_cust_id=request.form['cid']
        ws_acct_id=request.form['aid']
        if ws_acct_id:
            url= 'accounts/'+ws_acct_id
            return redirect(url)
        else:
            account = Account.objects(ws_cust_id=ws_cust_id).first()
            print(account,flush=True)
            ws_acct_id=account.ws_acct_id
            url= 'accounts/'+ws_acct_id
            return redirect(url)
    return render_template("search_account.html")
@app.route("/search_customer", methods=["GET","POST"])
def search_customer():
    if request.method == 'POST':
        ws_cust_id=request.form['cid']
        ws_ssn=request.form['ssn']
        if ws_cust_id:
            url= 'customers/'+ws_cust_id
            return redirect(url)
        else:
            customer = Customer.objects(ws_ssn=ws_ssn).first()
            print(customer,flush=True)
            ws_cust_id=customer.ws_cust_id
            url= 'customers/'+ws_cust_id
            return redirect(url)
    return render_template("search_customer.html")
@app.route("/tnxs", methods=["GET","POST"])
def tnxs():
    if request.method == 'POST':
        ws_acct_id=request.form['ws_acct_id']
        transactions = Transactions.objects(ws_acct_id=ws_acct_id)
        if request.form['from_date'] and request.form['to_date']:
            start = request.form['from_date']
            end=request.form['to_date']
            transactions = Transactions.objects((Q(ws_acct_id=ws_acct_id) & Q(ws_trxn_date__gte=start)) & Q(ws_trxn_date__lte=end))
        return render_template("transactions.html", transactions=transactions )
    return render_template("transactions.html")
