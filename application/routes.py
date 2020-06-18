from application import app, db
from datetime import datetime
from flask import render_template, request, json, Response, redirect, flash, url_for, session
from application.models import UserStore, Customer, Account,Transactions
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
    c_count = UserStore.objects(role='CASHIER').count()
    e_count = UserStore.objects(role='EXECUTIVE').count()
    customer_count = Customer.objects().count()
    account_count = Account.objects().count()
    return render_template("home.html",c_count=c_count,e_count=e_count,customer_count=customer_count,account_count=account_count )
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
        if len(str(ws_ssn)) !=9:
            flash("SSN length need to be 9 digits","danger")
            return redirect(url_for('create_customer'))
        customer = Customer.objects(ws_ssn=ws_ssn).first()
        if customer:
            flash("SSN Alreday exists with another Customer","danger")
            return redirect(url_for('create_customer'))
        ws_cust_id    =  '99899'+get_random_alphaNumeric_string(4)
        ws_name       =  request.form['ws_name'] 
        ws_adrs1       = request.form['ws_adrs1'] 
        if request.form['ws_adrs2']:
            ws_adrs2       = request.form['ws_adrs2']
        else:
            ws_adrs2 ='NULL'
        ws_city       = request.form['ws_city']
        ws_state       = request.form['ws_state']
        ws_age       = request.form['ws_age'] 
        ws_message       = 'JUST CREATED'
        ws_status = 'CREATED'
        ws_cust_update =   datetime.now()
        customer = Customer(ws_ssn=ws_ssn,ws_cust_id=ws_cust_id,ws_name=ws_name,ws_adrs1=ws_adrs1,ws_adrs2=ws_adrs2,ws_city=ws_city,ws_state=ws_state,ws_age=ws_age,ws_status=ws_status,ws_cust_update=ws_cust_update)
        customer.save()
        flash("Customer creation initiated successfully !","success")
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
        ws_adrs1       = request.form['ws_adrs1'] 
        if request.form['ws_adrs2']:
            ws_adrs2       = request.form['ws_adrs2']
        else:
            ws_adrs2 ='NULL'
        ws_city       = request.form['ws_city']
        ws_state       = request.form['ws_state']
        ws_age       = request.form['ws_age']
        ws_status       = 'UPDATED'
        ws_message       = request.form['ws_message']
        ws_cust_update =   datetime.now()
        Customer.objects(ws_cust_id=cid).update_one(ws_name=ws_name,ws_adrs1=ws_adrs1,ws_adrs2=ws_adrs2,ws_city=ws_city,ws_state=ws_state,ws_cust_update=ws_cust_update,ws_age=ws_age,ws_status=ws_status,ws_message=ws_message) 
        flash("Customer update initiated successfully !","success")
        url = '/customers/'+cid
        return redirect(url)
    customer = Customer.objects(ws_cust_id=cid).first()
    return render_template("customer_management/update_customer.html", customer=customer)

@app.route("/delete_customer/<cid>")
def delete_customer(cid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    Customer.objects(ws_cust_id=cid).update_one(ws_status='DELETED')
    flash("Customer  with ID- "+cid+" deletion initiated successfully !","success")
    return redirect(url_for('index'))

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
        ws_acct_id       = get_random_alphaNumeric_string(9)
        ws_acct_type       = request.form['ws_acct_type']
        ws_acct_balance       = int(request.form['ws_acct_balance'])
        if ws_acct_balance <= 0:
            flash("Account creation Failed due to negative amount!","danger")
            return redirect(url_for('create_account'))
        ws_acct_crdate       =  datetime.now()
        ws_acct_lasttrdate       =  datetime.now()
        ws_acct_duration       = 0
        ws_status = 'CREATED'
        account= Account.objects(ws_cust_id=ws_cust_id,ws_acct_type=ws_acct_type)
        if account:
            flash("Current User already have this type of account please try other","danger")
            return redirect(url_for('create_account'))
        account = Account(ws_cust_id=ws_cust_id,ws_acct_id=ws_acct_id,ws_acct_type=ws_acct_type,ws_acct_balance=ws_acct_balance,ws_acct_crdate=ws_acct_crdate,ws_message='CREATED',ws_acct_lasttrdate=ws_acct_lasttrdate,ws_acct_duration=ws_acct_duration,ws_status=ws_status)
        account.save()
        transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Deposit',ws_amt=ws_acct_balance,ws_trxn_date=datetime.now())
        transactions.save()
        flash("Account creation initiated successfully!","success")
        return redirect('/accounts/'+ws_acct_id)
    return render_template("account_management/create_account.html")

@app.route('/delete-account', methods=['POST','GET'])
def delete_account():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        ws_acct_id       = request.form['ws_acct_id']
        ws_acct_type       = request.form['ws_acct_type']
        account= Account.objects(ws_acct_id=ws_acct_id,ws_acct_type=ws_acct_type).update_one(ws_status='DELETED')
        if account ==0:
            flash("No Account  Available with Given Information !","danger")
        else:
            flash("Account deletion initiated successfully","success")
        return redirect(url_for('delete_account'))
    return render_template("account_management/delete_account.html")
@app.route("/deleteaccount/<aid>")
def deleteaccount(aid):
    Account.objects(ws_acct_id=aid).update_one(ws_status='DELETED')
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
        elif ws_cust_id:
            account = Account.objects(ws_cust_id=ws_cust_id).first()
            if account:
                ws_acct_id=account.ws_acct_id
                url= 'accounts/'+ws_acct_id
                return redirect(url)
            else:
                flash("No account exists with given Account Id !","danger")
        else:
            flash("Search possible only by filling either  Account Id or Customer ID !","danger")
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
        elif ws_ssn :
            customer = Customer.objects(ws_ssn=ws_ssn).first()
            if customer:
                ws_cust_id=customer.ws_cust_id
                url= 'customers/'+ws_cust_id
                return redirect(url)
            else:
                flash("No Customer exists with given SSN !","danger")
        else:
            flash("Fill Either Customer ID OR SSN ID to search","danger")
    return render_template("status_detail/customer_search.html")

@app.route('/account-status')
def account_status():
    count = Account.objects().count()
    if count ==0:
        flash("Currently No Accounts Created Untill Now","danger")
        return redirect(url_for(index))
    accounts = Account.objects()
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
        Account.objects(ws_acct_id=ws_acct_id).update_one(ws_acct_balance=ws_acct_balance,ws_message='DEPOSIT',ws_acct_lasttrdate=datetime.now())
        transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Deposit',ws_amt=amount,ws_trxn_date=datetime.now())
        transactions.save()
        url='/accounts/'+ws_acct_id
        flash("Amount deposited successfully","success")
        return redirect(url)
    if aid:
        account = Account.objects(ws_acct_id=aid).first()
        return render_template("account_operations/deposit.html",account=account,info=True)
    return render_template("account_operations/deposit.html",info=False)


@app.route('/transfer', methods=["GET","POST"])
def transfer():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        print(request.form,flush=True)
        sr_acct_id=request.form['sr_acct_id']
        tr_acct_id=request.form['tr_acct_id']
        if sr_acct_id == tr_acct_id:
            flash("Source and Target cannot be  same !","danger")
            return redirect('/transfer')
        amount = int(request.form['amount'])
        account1 = Account.objects(ws_acct_id=sr_acct_id).first()
        account2 = Account.objects(ws_acct_id=tr_acct_id).first()
        if account1 and account2:
            if account1.ws_acct_balance >= amount:
                sr_acct_balance = account1.ws_acct_balance - amount
                tr_acct_balance = account2.ws_acct_balance + amount
                Account.objects(ws_acct_id=sr_acct_id).update_one(ws_acct_balance=sr_acct_balance,ws_message='TRANSFER',ws_acct_lasttrdate=datetime.now())
                Account.objects(ws_acct_id=tr_acct_id).update_one(ws_acct_balance=tr_acct_balance,ws_message='TRANSFER',ws_acct_lasttrdate=datetime.now())
                transactions1 = Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=sr_acct_id,ws_desc='Transfer from here',ws_amt=amount,ws_trxn_date=datetime.now(),ws_src_typ=account1.ws_acct_type,ws_tgt_typ=account2.ws_acct_type)
                transactions1.save()
                transactions2 = Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=tr_acct_id,ws_desc='Transfer to here',ws_amt=amount,ws_trxn_date=datetime.now(),ws_src_typ=account1.ws_acct_type,ws_tgt_typ=account2.ws_acct_type)
                transactions2.save()
                flash("Amount transfer completed successfully !","success")
                return redirect('/transfer')
            else:
                flash("Transfer not allowed, please choose smaller amount !","danger")
                return redirect('/transfer')
        else:
            if account1:
                flash("Destination Account Doest exists !","danger")
                return redirect('/transfer')
            else:
                flash("Source Account Doest exists !","danger")
                return redirect('/transfer')
    return render_template("account_operations/transfer_money.html")
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
            flash("Withdraw not allowed, please choose smaller amount","danger")
            url='/withdraw/'+ws_acct_id
            return redirect(url)
        Account.objects(ws_acct_id=ws_acct_id).update_one(ws_acct_balance=ws_acct_balance,ws_message='WITHDRAW',ws_acct_lasttrdate=datetime.now())
        transactions= Transactions(ws_tnsc_id=get_random_alphaNumeric_string(8),ws_acct_id=ws_acct_id,ws_desc='Withdraw',ws_amt=amount,ws_trxn_date=datetime.now())
        transactions.save()
        flash("Amount withdrawn successfully","success")
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
@app.route("/get_account/<aid>")
def getaccounts(aid):
    accounts = Account.objects(ws_acct_id=aid).first()
    return Response(json.dumps(accounts), mimetype="application/json")
@app.route("/get_customer/<cid>")
def getcustomer(cid):
    customers = Customer.objects(ws_cust_id=cid)
    return Response(json.dumps(customers), mimetype="application/json")



