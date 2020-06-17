from application import app, db
from datetime import datetime
from flask import render_template, request, json, Response, redirect, flash, url_for, session
from application.models import UserStore, Customer, Account,Transactions
from application.forms import LoginForm, RegisterForm ,CustomerForm, AccountForm
import random
import string
from mongoengine.queryset.visitor import Q
def get_random_alphaNumeric_string(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("home.html", index=True )
@app.route("/login", methods=['POST','GET'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        user_id       = request.form['user_id']
        password    = request.form['password']
        user = UserStore.objects(user_id=user_id).first()
        if user and user.get_password(password):
            UserStore.objects(user_id=user_id).update_one(timestamp=datetime.now())
            flash(f"{user.user_id}, you are successfully logged in!", "success")
            session['user_id'] = user.user_id
            session['role'] = user.role
            return redirect("/index")
        else:
            flash("Sorry, something went wrong.","danger")
    return render_template("login.html")
@app.route("/register", methods=['POST','GET'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        user_id       = request.form['user_id']
        password    = request.form['password']
        role    = request.form['role']
        user = UserStore.objects(user_id=user_id).first()
        if user:
            flash("Account Alreday exists with current ID!","danger")
            return redirect(url_for('register'))
        user = UserStore(user_id=user_id,role=role)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('user_id',None)
    return redirect(url_for('index'))
@app.route('/create-customer', methods=['POST','GET'])
def create_customer():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        ws_ssn       = request.form['ws_ssn']
        customer = Customer.objects(ws_ssn=ws_ssn).first()
        if customer:
            flash("SSN Alreday exists with another Customer","danger")
            return redirect(url_for('create_customer'))
        ws_cust_id    =  '998998'+get_random_alphaNumeric_string(4)
        ws_name       =  request.form['ws_name'] 
        ws_adrs       = request.form['ws_adrs'] 
        ws_age       = request.form['ws_age'] 
        ws_status = 'ACTIVE'
        ws_cust_update =   datetime.now()
        customer = Customer(ws_ssn=ws_ssn,ws_cust_id=ws_cust_id,ws_name=ws_name,ws_adrs=ws_adrs,ws_age=ws_age,ws_status=ws_status,ws_cust_update=ws_cust_update)
        customer.save()
        flash("Customer Created successfully !","success")
        return redirect('/customers/'+ws_cust_id)
    return render_template("customer_management/create_customer.html")
@app.route("/customers/<cid>")
def customers(cid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if cid :
        customers = Customer.objects(ws_cust_id=cid)
        if  customers:
            return render_template("customer_management/customers.html", customers=customers)
        else:
            flash("User with ID "+cid+" Doesn't exists","danger")
            return redirect(url_for(index))
    else:
        flash("URL Doesn't exists","danger")
        return redirect(url_for(index))
@app.route('/update-customer/<cid>', methods=['POST','GET'])
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
        url = '/customers/'+cid
        return redirect(url)
    customer = Customer.objects(ws_cust_id=cid).first()
    return render_template("customer_management/update_customer.html", customer=customer)

@app.route("/delete_customer/<cid>")
def delete_customer(cid):
    print(cid,flush=True)
    Customer.objects(ws_cust_id=cid).delete()
    flash("Customer  with ID "+cid+" Deleted successfully !","success")
    return redirect(url_for('customer_status'))

@app.route('/customer-status')
def customer_status():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    customers = Customer.objects.order_by("-ws_cust_id")
    return render_template("customer_management/customer_status.html", customers=customers)

@app.route('/create-account', methods=['POST','GET'])
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
        return redirect('/accounts/'+ws_acct_id)
    return render_template("account_management/create_account.html")

@app.route('/delete-account', methods=['POST','GET'])
def delete_account():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        ws_acct_id       = request.form['ws_acct_id']
        ws_acct_type       = request.form['ws_acct_type']
        account= Account.objects(ws_acct_id=ws_acct_id,ws_acct_type=ws_acct_type).delete()
        if account ==0:
            flash("No Account  Available with Given Information !","danger")
        else:
            flash("Account Deleted  successfully !","success")
        return redirect(url_for('delete_account'))
    return render_template("account_management/delete_account.html")
@app.route("/deleteaccount/<aid>")
def deleteaccount(aid):
    Account.objects(ws_acct_id=aid).delete()
    flash("Account Deleted successfully !","success")
    return redirect(url_for('index'))

@app.route('/account-search', methods=["GET","POST"])
def account_search():
    if request.method == 'POST':
        ws_cust_id=request.form['cid']
        ws_acct_id=request.form['aid']
        if ws_acct_id:
            account = Account.objects(ws_acct_id=ws_acct_id).first()
            if account:
                url= 'accounts/'+ws_acct_id
                return redirect(url)
            else:
                flash("No account exists with given Account Id !","danger")
        else:
            account = Account.objects(ws_cust_id=ws_cust_id).first()
            if account:
                ws_acct_id=account.ws_acct_id
                url= 'accounts/'+ws_acct_id
                return redirect(url)
            else:
                flash("No account exists with given Account Id !","danger")
    return render_template("status_detail/account_search.html")

@app.route('/customer-search', methods=["GET","POST"])
def customer_search():
    if request.method == 'POST':
        ws_cust_id=request.form['cid']
        ws_ssn=request.form['ssn']
        if ws_cust_id:
            customer = Customer.objects(ws_cust_id=ws_cust_id).first()
            if customer:
                url= 'customers/'+ws_cust_id
                return redirect(url)
            else:
                flash("No Customer exists with given Customer Id !","danger")
        else:
            customer = Customer.objects(ws_ssn=ws_ssn).first()
            if customer:
                ws_cust_id=customer.ws_cust_id
                url= 'customers/'+ws_cust_id
                return redirect(url)
            else:
                flash("No Customer exists with given SSN !","danger")
    return render_template("status_detail/customer_search.html")

@app.route('/account-status')
def account_status():
    count = Account.objects().count()
    if count ==0:
        flash("Currently No Accounts Created Untill Now","danger")
        return redirect(url_for(index))
    accounts =  list( Account.objects.aggregate(*[{
        '$lookup': {
            'from': 'customer', 
            'localField': 'ws_cust_id', 
            'foreignField': 'ws_cust_id', 
            'as': 'r1'}}]))
    return render_template("status_detail/account_status.html",accounts=accounts)
@app.route('/deposit', methods=["GET","POST"])
@app.route('/deposit/<aid>', methods=["GET","POST"])
def deposit(aid=False):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount=request.form['amount']
        previous_amount=request.form['ws_acct_balance']
        ws_acct_id = request.form['ws_acct_id']
        ws_acct_balance=int(previous_amount)+int(amount)
        Account.objects(ws_acct_id=ws_acct_id).update_one(ws_acct_balance=ws_acct_balance)
        transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Deposit',ws_amt=amount,ws_trxn_date=datetime.now())
        transactions.save()
        url='/accounts/'+ws_acct_id
        return redirect(url)
    if aid:
        account = Account.objects(ws_acct_id=aid).first()
        return render_template("account_operations/deposit.html",account=account,info=True)
    return render_template("account_operations/deposit.html",info=False)


@app.route('/transfer/<cid>', methods=["GET","POST"])
def transfer(cid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        print(request.form,flush=True)
        sr_acct_id=request.form['sr_acct_id']
        tr_acct_id=request.form['tr_acct_id']
        cid = request.form['cid']
        if sr_acct_id == tr_acct_id:
            flash("Source and Target cannot be  same !","success")
            return redirect('/transfer/'+cid)
        amount = int(request.form['amount'])
        account1 = Account.objects(ws_acct_id=sr_acct_id).first()
        account2 = Account.objects(ws_acct_id=tr_acct_id).first()
        if account1.ws_acct_balance >= amount:
            sr_acct_balance = account1.ws_acct_balance - amount
            tr_acct_balance = account2.ws_acct_balance + amount
            Account.objects(ws_acct_id=sr_acct_id).update_one(ws_acct_balance=sr_acct_balance)
            Account.objects(ws_acct_id=tr_acct_id).update_one(ws_acct_balance=tr_acct_balance)
            transactions1 = Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=sr_acct_id,ws_desc='Transfer from here',ws_amt=amount,ws_trxn_date=datetime.now(),ws_src_typ=account1.ws_acct_type,ws_tgt_typ=account2.ws_acct_type)
            transactions1.save()
            transactions2 = Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=tr_acct_id,ws_desc='Transfer to here',ws_amt=amount,ws_trxn_date=datetime.now(),ws_src_typ=account1.ws_acct_type,ws_tgt_typ=account2.ws_acct_type)
            transactions2.save()
            flash("Tranfer Successful !","success")
            return redirect('/transfer/'+cid)
        else:
            flash("Tranfer Failur due to insuffiecient funds !","fail")
            return redirect('/transfer/'+cid)
    account = Account.objects(ws_cust_id=cid)
    count = Account.objects(ws_cust_id=cid).count()
    return render_template("account_operations/transfer_money.html",account=account,ws_cust_id=cid,count=count)
@app.route('/withdraw', methods=["GET","POST"])
@app.route('/withdraw/<aid>', methods=["GET","POST"])
def withdraw(aid=False):
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
        Account.objects(ws_acct_id=ws_acct_id).update_one(ws_acct_balance=ws_acct_balance,ws_acct_lasttrdate=datetime.now())
        transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Withdraw',ws_amt=amount,ws_trxn_date=datetime.now())
        transactions.save()
        url='/accounts/'+ws_acct_id
        return redirect(url)
    if aid:
        account = Account.objects(ws_acct_id=aid).first()
        return render_template("account_operations/withdraw_money.html",account=account,info=True)
    return render_template("account_operations/withdraw_money.html",info=False)

@app.route('/account-statement', methods=["GET","POST"])
def account_statement():
    if request.method == 'POST':
        ws_acct_id=request.form['ws_acct_id']
        transactions = Transactions.objects(ws_acct_id=ws_acct_id)
        n = request.form['limit']
        if n:
            n = int(request.form['limit'])
            transactions = Transactions.objects(ws_acct_id=ws_acct_id).limit(n)
        if request.form['from_date'] and request.form['to_date']:
            start = request.form['from_date']
            end=request.form['to_date'] 
            if n:
                n = int(request.form['limit'])
                transactions = Transactions.objects((  Q(ws_trxn_date__lte=end) & Q(ws_trxn_date__gte=start)   ) &  Q(ws_acct_id=ws_acct_id)   ).limit(n)
            transactions = Transactions.objects((  Q(ws_trxn_date__lte=end) & Q(ws_trxn_date__gte=start)   ) &  Q(ws_acct_id=ws_acct_id) )
        return render_template("account_operations/account_statement.html", transactions=transactions ,ws_acct_id=ws_acct_id)
    return render_template("account_operations/account_statement.html")
@app.route("/accounts/<aid>")
def accounts(aid):
    print(aid,flush=True)
    if aid :
        accounts = Account.objects(ws_acct_id=aid)
    else:
        return redirect(url_for(index))
    return render_template("account_operations/accounts.html", accounts=accounts )



