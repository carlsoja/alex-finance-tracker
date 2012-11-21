#usr/bin/python2.7

from google.appengine.ext import db

class Transaction(db.Model):
	date = db.DateProperty()
	name = db.StringProperty()
	description = db.TextProperty()
	amount = db.FloatProperty()
	account = db.StringProperty()
	paycheck = db.ReferenceProperty()
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

class Paycheck(db.Model):
	date = db.DateProperty()
	gross = db.FloatProperty()
	deductions = db.ListProperty(db.Key)
	ins_deductions = db.ListProperty(db.Key)
	deposits = db.ListProperty(db.Key)
	expenses = db.ListProperty(db.Key)
	current = db.BooleanProperty()
	closed = db.BooleanProperty()