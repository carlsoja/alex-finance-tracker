{% extends "base.tpl" %}

{% block main %}
<h2>Expenses in datastore</h2>
{% for expense in expenses %}
<p>{{ expense.date }}: {{ expense.name }}<br />
${{ expense.amount }}, {{ expense.frequency }}</p>
{% endfor %}
{% endblock main %}

{% block form %}
<form action="" method="post">
  Date: <input type="text" name="date"><br />
  Name: <input type="text" name="name"><br />
  Description: <input type="text" name="description"><br />
  Amount: <input type="text" name="amount"><br />
  Frequency: <input type="text" name="freq"><br />
  Category: <input type="text" name="category"><br />
  <input type="submit" value="send">
</form>
{% endblock form %}