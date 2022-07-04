from lib.parser import get_variable_type, indent
from lib.validations import verify_query
from lib.helpers import print_output
import re
import sys
import requests


def stringify(text):
    '''
	Custom jinja filter used to wrap strings
    '''
    return '"{}"'.format(text)

def intify(text):
    '''
	Custom jinja filter used to assign integers
    '''
    return int(text)


def floatify(text):
    '''
	Custom jinja filter used to assign floats
    '''
    return float(text)

def inject_payload(operation, variables):
	for key in variables.keys():
		variable_type = get_variable_type(operation, key)
		regex = r'"\$' + re.escape(key) + r'\|'+ re.escape(variable_type) + r'\$"'
		if variable_type == 'str':
			filled_operation = re.sub(regex, '"'+re.escape(variables[key])+'"', operation)
		elif variable_type == 'int':
			filled_operation = re.sub(regex, ''+re.escape(variables[key])+'', operation)
		operation = filled_operation


	return operation

def generate_payload(batch_operations, root_type):
	'''
	Takes the total batch of alias operations and wraps it with the original root type
	'''
	operation_body = indent(batch_operations, 4)
	return root_type  + operation_body + '\n}'

def send_payload(url, payload, batches_sent, total_requests_to_send, verbose=False):
	'''
	Sends a packaged GraphQL query with populated payload in a single batch request
	'''

	print_output('[+] Payload {num}: \n{payload}'.format(payload=payload, num=batches_sent), verbose)

	print_output('[+] Verifying Payload Batch Operation...', verbose)
	if not verify_query(payload, query_format='String'):
		sys.exit(1)

	print('[+] Sending Alias Batch {batches_sent} of {total_requests_to_send} to {url}...'.format(
		batches_sent=batches_sent,
		total_requests_to_send=total_requests_to_send,
		url=url
	))
	
	try:
		response = requests.post(
			url,
			verify=False,
			timeout=360,
			json={'query':payload}
		)
		return response.json()

	except Exception as e:
		print('Error: {e}'.format(e=e))
		sys.exit(1)

