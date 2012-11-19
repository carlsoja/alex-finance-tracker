<!DOCTYPE html>
<html>
  <head>
	<meta charset="utf-8">
	<title>{% block title %}{% endblock title %}</title>
	{% block headscript %}{% endblock headscript %}
	{% block headstyle %}{% endblock headstyle %}
  </head>
  <body>
	{% block main %}{% endblock main %}
	{% block form %}{% endblock form %}
	{% block javascript %}{% endblock javascript %}
  </body>
</html>