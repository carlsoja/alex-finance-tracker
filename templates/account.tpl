{% extends "base.tpl" %}

{% block main %}
<p><a href="/">Home</a> > Manage accounts</p>
<h2>Accounts in datastore</h2>
{% for account in accounts %}
<p>{{ account.a_type }}: {{ account.name }}<br />
Balance: ${{ account.unv_balance|floatformat:"2" }}</p>
{% endfor %}
{% endblock main %}

{% block form %}
<form action="" method="post">
  Name: <input type="text" name="name"><br />
  Type: <select name="type">
	        <option value="Checking" selected="selected">Checking</option>
	        <option value="Savings">Savings</option>
	        <option value="Investment">Investment</option>
	        <option value="Credit Card">Credit Card</option>
	      </select><br />
  Starting Balance: <input type="text" name="starting"><br />
  Start Date: <input type="text" name="start_date"><br />
  Last Verified: <input type="text" name="last_verified"><br />
	<input type="submit" value="send">
</form>
{% endblock form %}