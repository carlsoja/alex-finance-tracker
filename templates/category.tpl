{% extends "base.tpl" %}

{% block main %}
<p><a href="/">Home</a> > Manage categories</p>
<h2>Categories in datastore</h2>
<h3>Parent Categories</h3>
<ul>
{% for cat in parent_cats %}
<li>{{ cat.name }}</li>
{% empty %}
<li><em>No parent categories entered</em></li>
{% endfor %}
</ul>
<h3>Child Categories</h3>
<ul>
{% for cat in sub_cats %}
<li>{{ cat.name }} <em>({{ cat.parent_cat.name }})</em></li>
{% empty %}
<li><em>No child categories entered</em></li>
{% endfor %}
</ul>
{% endblock main %}

{% block form %}
<form action="" method="post">
  Name: <input type="text" name="name"><br />
  {% if parent_cats|length == 0 %}
  {% else %}
  Parent/Child: <select name="p-c">
	                <option value="parent" selected="selected">Parent</option>
	                <option value="child">Child</option>
	              </select><br />
  Parent Category: <select name="parent-cat">
	                   {% for cat in parent_cats %}
				             <option value="{{ cat.key }}">{{ cat.name }}</option>
				             {% endfor %}
				           </select><br />
	{% endif %}
  Type: <select name="type">
	        <option value="Expense" selected="selected">Expense</option>
	        <option value="Deposit">Deposit</option>
	      </select><br />
	<input type="submit" value="send">
</form>
{% endblock form %}