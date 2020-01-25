from jinja2 import Template


def build_from_template(jinja_template, queries):
	file = open(jinja_template).read()
	res = Template(file).render(queries=queries)

	res = res.replace('\n', '')
	with open('/Users/mzakany/Desktop/x.html', 'w') as file:
		file.write(res)

	return res
