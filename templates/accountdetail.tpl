{% extends "base.tpl" %}

{% block main %}
<p><a href="/">Home</a> > {{ account.name }}</p>
<h2>{{ account.name }}</h2>
<p><strong>Verified Balance:</strong> ${{ account.ver_balance|floatformat:"2" }}</p>
<p><strong>Unverified Balance:</strong> ${{ account.unv_balance|floatformat:"2" }}</p>
<h3>Unverified transactions:</h3>
<ul>
{% for t in unv_transactions %}
<li>{{ t.0.date }}: {{ t.0.GetClassName }} - {{ t.0.name }} - ${{ t.0.amount|floatformat:"2" }}<br />
UNV_BALANCE: ${{ t.1|floatformat:"2" }}</li>
{% empty %}
<li><em>No unverified transactions.</em></li>
{% endfor %}
</ul>
<h3>Verified transactions:</h3>
<ul>
{% for t in ver_transactions %}
<li>{{ t.0.date }}: {{ t.0.GetClassName }} - {{ t.0.name }} - ${{ t.0.amount|floatformat:"2" }}<br />
VER_BALANCE: ${{ t.1|floatformat:"2" }}</li>
{% endfor %}
</ul>
<p><strong>Starting balance:</strong> ${{ starting|floatformat:"2" }}
{% endblock main %}