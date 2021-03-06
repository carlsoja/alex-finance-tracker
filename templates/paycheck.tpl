{% extends "base.tpl" %}

{% block main %}
<p><a href="/">Home</a> > Manage paychecks</p>
<h2>Paychecks in datastore</h2>
{% for paycheck in paychecks %}
<p>{{ paycheck.date }}: {{ paycheck.gross }}<br />
Current: {{ paycheck.current }}<br />
Closed: {{ paycheck.closed }}</p>
{% endfor %}
{% endblock main %}

{% block form %}
<form action="" method="post">
  Date: <input type="text" name="date"><br />
  Gross: <input type="text" name="gross"><br />
  {% if accounts %}
  Account: <select name="account">
	         {% for account in accounts|dictsort:"name" %}
	           <option value="{{ account.key.name }}">{{ account.name }}</option>
	         {% endfor %}
	         </select><br />
	{% endif %}   
  Current: <select name="current">
	           <option value="True" selected="selected">True</option>
	           <option value="False">False</option>
	         </select><br />
  Closed: <select name="closed">
					  <option value="True">True</option>
					  <option value="False" selected="selected">False</option>
					</select><br />
	<input type="submit" value="send">
</form>
{% endblock form %}