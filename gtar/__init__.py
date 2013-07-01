#__init__.py

from Transport import Transport

def create_instance(c_instance):
	return Transport(c_instance)