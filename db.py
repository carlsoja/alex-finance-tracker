#usr/bin/python2.7

from google.appengine.ext import db

class Account(db.Model):
	name = db.StringProperty()
	a_type = db.StringProperty(
	  choices = set(['Checking', 'Savings', 'Investment', 'Credit Card']))
	unv_balance = db.FloatProperty()
	ver_balance = db.FloatProperty()
	last_verified = db.DateProperty()

class Paycheck(db.Model):
	date = db.DateProperty()
	gross = db.FloatProperty()
	deductions = db.ListProperty(db.Key)
	ins_deductions = db.ListProperty(db.Key)
	after_deduction_pay = db.FloatProperty()
	deposits = db.ListProperty(db.Key)
	after_deposit_balance = db.FloatProperty()
	expenses = db.ListProperty(db.Key)
	final_balance = db.FloatProperty()
	current = db.BooleanProperty()
	closed = db.BooleanProperty()

class Transaction(db.Model):
	date = db.DateProperty()
	name = db.StringProperty()
	description = db.TextProperty()
	amount = db.FloatProperty()
	account = db.ReferenceProperty(collection_name='accounts')
	paycheck = db.ReferenceProperty(collection_name='paychecks')
	frequency = db.StringProperty(
	  choices = set(['Core', 'Regular', 'One-Time']),
	  default = 'One-Time')
	recurring_date = db.DateProperty()
	verified = db.BooleanProperty()

class Expense(Transaction):
	paid = db.BooleanProperty()
	e_category = db.StringProperty()

class Deposit(Transaction):
	d_type = db.StringProperty(
	  choices = set(['Savings', 'Investment', 'Retirement']),
	  default = 'Savings')