{% extends "base.tpl" %}

{% block headscript %}
<script>
function nameDisplay(fieldid, selectid) {
	var namefield = document.getElementById(fieldid);
	var typeselect = document.getElementById(selectid);
	var selection = typeselect.options[typeselect.selectedIndex].value;
	if (selection == "other") {
		namefield.style.display = "block";
	}
	else {
		namefield.style.display = "none";
	}
}
function subcatSelectionDisplay() {
	var parentselect = document.getElementById("expense-parent-cat");
	var parent_selection = parentselect.options[parentselect.selectedIndex].value;
	var parentcatids = Array({% for group in child_cat_groups %}"{{ group.0.parent_cat.key.name }}"{% if forloop.counter != child_cat_groups|length %}, {% endif %}{% endfor %});
	for(i=0; i < parentcatids.length; i++){
		selector = document.getElementById(parentcatids[i]);
		if (parent_selection == parentcatids[i]) {
			selector.style.display = "block";
		}
		else {
			selector.style.display = "none";
			selector.options[selector.selectedIndex].value = null;
		}
	}
}
</script>
{% endblock headscript %}

{% block main %}
<p><a href="/">Home</a> > {{ paycheck.date }} Paycheck</p>
<h2>{{ paycheck.date}} Paycheck</h2>
<p><strong>GROSS</strong>: ${{ paycheck.gross|floatformat:"2" }}</p>
<p>Taxes:</p>
<ul>
	<li><strong>FEDERAL:</strong> {% if federal_tax %}${{ federal_tax.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
  <li><strong>STATE:</strong> {% if state_tax %}${{ state_tax.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
  {% if other_taxes %}
  {% for tax in other_taxes %}
	<li>{{ tax.name }}: ${{ tax.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li><em>No other taxes entered</em></li>
	{% endif %}
</ul>
<p><strong>Total taxes:</strong> ${{ tax_total|floatformat:"2" }}</p>
<form action="" method="post">
  Type: <select name="tax-type" id="taxtypeselect" onchange="a='taxname';b='taxtypeselect';nameDisplay(a,b);">
	        {% if federal_tax %}{% else %}<option value="federal">Federal</option>{% endif %}
	        {% if state_tax %}{% else %}<option value="state">State</option>{% endif %}
	        <option value="other">Other</option>
	      </select><br />
	<div id="taxname" style="display:none">Name: <input type="text" name="tax-name"><br /></div>
  Amount: <input type="text" name="tax-amount">
  <input type="submit" value="Submit">
</form>
<p>Deductions:</p>
<ul>
	<li><strong>MEDICAL:</strong> {% if med_insurance %}${{ med_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>DENTAL:</strong> {% if dental_insurance %}${{ dental_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>LIFE:</strong> {% if life_insurance %}${{ life_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>VISION:</strong> {% if vision_insurance %}${{ vision_insurance.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
	<li><strong>401k:</strong> {% if 401k %}${{ 401k.amount|floatformat:"2" }}{% else %}<em>Not entered</em>{% endif %}
  {% if deductions %}
  {% for d in deductions %}
	<li>{{ d.name }}: ${{ d.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li><em>No other deductions entered</em></li>
	{% endif %}
</ul>
<p><strong>Total deductions:</strong> ${{ deductions_total|floatformat:"2" }}</p>
<form action="" method="post">
  Type: <select name="deduction-type" id="deducttypeselect" onchange="a='deductname';b='deducttypeselect';nameDisplay(a,b);">
	        {% if med_insurance %}{% else %}<option value="Medical">Medical</option>{% endif %}
	        {% if dental_insurance %}{% else %}<option value="Dental">Dental</option>{% endif %}
	        {% if life_insurance %}{% else %}<option value="Life">Life</option>{% endif %}
	        {% if vision_insurance %}{% else %}<option value="Vision">Vision</option>{% endif %}
	        {% if 401k %}{% else %}<option value="401k">401k</option>{% endif %}
	        <option value="other">Other</option>
	      </select><br />
	<div id="deductname" style="display:none">Name: <input type="text" id="dname" name="deduction-name"><br /></div>
  Amount: <input type="text" name="deduction-amount">
  <input type="submit" value="Submit">
</form>
<p><strong>AFTER DEDUCTIONS</strong>: ${{ paycheck.after_deduction_balance|floatformat:"2" }}</p>
<p>Deposits:</p>
<ul>
  {% for d in deposits %}
	<li><strong>{{ d.receiving_account.name }}:</strong> ${{ d.amount|floatformat:"2"}} - {{ d.description }}</li>
	{% empty %}
	<li>No deposits entered</li>
	{% endfor %}
</ul>
<p><strong>Total deposits:</strong> ${{ deposits_total|floatformat:"2" }}</p>
<form action="" method="post">
  Account: <select name="deposit-account" id="depositaccountselect">
	           {% for account in accounts|dictsort:"name" %}
	           <option value="{{ account.key.name }}">{{ account.name }}</option>
	           {% endfor %}
	         </select><br />
  Amount: <input type="text" name="deposit-amount"><br />
  Date: <input type="text" name="deposit-date"><br />
  Description: <input type="text" name="deposit-description"><br />
	<input type="submit" value="Submit">
</form>
<p><strong>AFTER DEPOSITS</strong>: ${{ paycheck.after_deposit_balance|floatformat:"2" }}</p>
<p>Expenses:</p>
<ul>
  {% if expenses %}
  {% for expense in expenses %}
	<li>{{ expense.name }}: ${{ expense.amount|floatformat:"2"}}</li>
	{% endfor %}
	{% else %}
	<li>No expenses entered</li>
	{% endif %}
</ul>
<p><strong>Total expenses:</strong> ${{ expenses_total|floatformat:"2" }}</p>
<form action="" method="post">
  Vendor: <input type="text" name="expense-vendor"><br />
  Amount: <input type="text" name="expense-amount"><br />
  Date: <input type="text" name="expense-date"><br />
  Description: <input type="text" name="expense-description"><br />
  Category: <select name="parent-cat" id="expense-parent-cat" onchange="subcatSelectionDisplay()">
	            {% for cat in parent_cats %}
	            <option value="{{ cat.key.name }}">{{ cat.name }}</option>
	            {% endfor %}
	          </select><br />
	          {% for group in child_cat_groups %}
	            <select name="child-cat" id="{{ group.0.parent_cat.key.name }}">
		          {% for cat in group %}
		            <option value="{{ cat.key.name }}">{{ cat.name }}</option>
		          {% endfor %}
		          </select>
		        {% endfor %}<br />
  <input type="submit" value="Submit">
</form>
<p><strong>FINAL PAYCHECK BALANCE</strong>: ${{ paycheck.final_balance|floatformat:"2" }}</p>
{% endblock main %}

{% block javascript %}
<script>
  var namefields = new Array('taxname', 'deductname');
  var selectfields = new Array('taxtypeselect', 'deducttypeselect');
  for (i=0; i < namefields.length; i++) {
	  nameDisplay(namefields[i], selectfields[i]);
  }
  subcatSelectionDisplay();
</script>
{% endblock javascript %}