ping: pyats_example_job.py default_testbed.yaml
	pyats run job pyats_example_job.py --testbed-file default_testbed.yaml
bgp: BGP_check_job.py default_testbed.yaml
	pyats run job BGP_check_job.py -t default_testbed.yaml --html-logs ./html_logs
env: requirements.txt
	virtualenv .venv -p python3
	.venv/bin/pip install -r requirements.txt
clean: clean-pyc clean-env clean-pyats clean-virlutils
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
clean-env:
	rm -rf .venv/
	rm -rf venv/
clean-pyats:
	rm -rf archive/
	rm -rf runinfo/
	rm -rf html_logs/
clean-virlutils:
	rm -f default_testbed.yaml
	rm -f default_inventory.yaml
	rm -rf .virl/
