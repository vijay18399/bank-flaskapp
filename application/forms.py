from flask_wtf import FlaskForm
from wtforms import DateTimeField,SelectField,  PasswordField, SubmitField,IntegerField, BooleanField,StringField,TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from application.models import UserStore

class LoginForm(FlaskForm):
    user_id   = StringField("User Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6,max=15)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    user_id   = StringField("User Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(),Length(min=6,max=15)])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(),Length(min=6,max=15), EqualTo('password')])
    submit = SubmitField("Register Now")

    def validate_user_id(self,user_id):
        user = UserStore.objects(user_id=user_id.data).first()
        if user:
            raise ValidationError("user_id is already in use. Pick another one.")
class CustomerForm(FlaskForm):
    ws_ssn   =   IntegerField( "SSN", validators=[DataRequired()] )
    # ws_cust_id  =  IntegerField("Customer id ", validators=[DataRequired()] )
    ws_name  =   StringField( "Name", validators=[DataRequired()] )
    ws_adrs  =   TextAreaField("Address", validators=[DataRequired()])
    ws_age   =   IntegerField("Age", validators=[DataRequired()]  )
    submit = SubmitField("Create Customer")
class AccountForm(FlaskForm):
    ws_cust_id   =   IntegerField(   "Customer id ", validators=[DataRequired()] )
    ws_acct_id  =   IntegerField(  "Account id", validators=[DataRequired()] )
    ws_acct_type  =   SelectField("Account type",choices=[('S', 'Savings'), ('C', 'Current')])
    ws_acct_balance  =   IntegerField( "Balance", validators=[DataRequired()])
    ws_acct_crdate   =   DateTimeField(   "CR data", validators=[DataRequired()])
    ws_acct_lasttrdate   =   DateTimeField(  "CR last date", validators=[DataRequired()] )
    ws_acct_duration   =   IntegerField( "Duration", validators=[DataRequired()])
    submit = SubmitField("Create Account")