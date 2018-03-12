tests:
	# TODO - Include in install.
	pip install -r requirements.txt
	python setup.py install
	pytest

# [Dummy dependency to force a make command to always run.]
FORCE:
