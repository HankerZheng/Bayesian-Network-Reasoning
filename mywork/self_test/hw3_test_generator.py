from parse import Table, Node, Task

table_file_name = 'table_model.txt'
outputname = "testcase"
queries_per_file = 100
queries_per_type = 10000
# file_no ~= q(ueries_per_type * 3 / queries_per_file) - 1



def parse_to_list(index, length, value_set):
	'''
	Given index, length, value_set, return a tuple with value in value_set
	the return tuple is the enumeration of the value_set

	>>> parse_to_list(0, 2, ['x','y','z']) # 00
	['x', 'x']
	>>> parse_to_list(1, 2, ['x','y','z']) # 01
	['x', 'y']
	>>> parse_to_list(2, 2, ['x','y','z']) # 02
	['x', 'z']
	>>> parse_to_list(3, 2, ['x','y','z']) # 10
	['y', 'x']
	>>> parse_to_list(4, 2, ['x','y','z']) # 11
	['y', 'y']
	>>> parse_to_list(5, 2, ['x','y','z']) # 12
	['y', 'z']
	>>> parse_to_list(6, 2, ['x','y','z']) # 20
	['z', 'x']
	>>> parse_to_list(7, 2, ['x','y','z']) # 21
	['z', 'y']
	>>> parse_to_list(8, 2, ['x','y','z']) # 22
	['z', 'z']
	>>> parse_to_list(9, 2, ['x','y','z'])
	[]

	'''
	base = len(value_set)
	if index >= (base**length):
		return []
	tmp, result = index, []
	for i in xrange(length):
		result.append(value_set[tmp%base])
		tmp = tmp / base
	result.reverse()
	return result


def parse_node(table):
	'''
	return a tuple (normal_nodes, decision_nodes)
	'''
	normal_nodes, decision_nodes = list(), list()
	for node_name in table.node_list:
		if table[node_name].decision:
			decision_nodes.append(node_name)
		else:
			normal_nodes.append(node_name)
	return normal_nodes, decision_nodes

def dict_to_string(in_dict):
	'''
	convert dict to string format.

	>>> dict_to_string({'A':'+', 'B':'x', 'C':'-'})
	'A = +, C = -'
	>>> dict_to_string({'A':'+', 'B':'-', 'C':'-'})
	'A = +, C = -, B = -'
	>>> dict_to_string({'A':'+'})
	'A = +'
	>>> dict_to_string({})
	''
	>>> dict_to_string({'A':'x', 'B':'x', 'D': 'x'})
	''
	'''
	new_dict = {key:in_dict[key] for key in in_dict.keys() if in_dict[key]!='x'}
	length, result = len(new_dict), ''
	if length == 0:
		return ''
	for i, key in enumerate(new_dict.keys()):
		result += key + ' = ' + new_dict[key]
		if i < (length - 1):
			result += ', '
	return result

def list_to_string(in_list):
	'''
	convert list to string format
	'''
	return ', '.join(in_list)

def same_value_dict(in_dict, value):
	'''
	whether all the value in in_dict has the same value as indecated in parameter
	'''
	if in_dict == {}:
		return True
	for key in in_dict.keys():
		if in_dict[key] != value:
			return False
	return True


def key_value_generator(in_list, decision, nullable):
	'''
	This is a generator. Given a list, yield key_value dict
	If decision is Ture, all items in list must have a key and a value
	If decision is False, not all items need a value 

	>>> a = key_value_generator(['A','B'], True, False)
	>>> a.next()
	{'A': '-', 'B': '-'}
	>>> a.next()
	{'A': '-', 'B': '+'}
	>>> a.next()
	{'A': '+', 'B': '-'}
	>>> a.next()
	{'A': '+', 'B': '+'}
	>>> a = key_value_generator(['A','B'], False, False)
	>>> a.next()
	{'A': 'x', 'B': '-'}
	>>> a.next()
	{'A': 'x', 'B': '+'}
	>>> a.next()
	{'A': '-', 'B': 'x'}
	>>> a.next()
	{'A': '-', 'B': '-'}
	>>> a.next()
	{'A': '-', 'B': '+'}
	>>> a.next()
	{'A': '+', 'B': 'x'}
	>>> a.next()
	{'A': '+', 'B': '-'}
	>>> a.next()
	{'A': '+', 'B': '+'}

	'''	
	if decision == True and in_list == []:
	# when there is no decision node in this table, we should handle it
		yield {}
	length = len(in_list)
	if length == 0:
		return

	value_set = ('-', '+') if decision else ('x', '-', '+')
	for index in xrange(len(value_set)**length):
		value_list = parse_to_list(index, length, value_set)
		this_dict = {in_list[i]:value_list[i] for i in xrange(length)}
		if nullable == False and decision == False and index == 0:
			continue
		else:
			yield this_dict


def p_query_generator(table):
	'''
	generate query for P question
	'''
	normal_nodes, decision_nodes = parse_node(table)
	for query in key_value_generator(normal_nodes,False, False):
		for condition in key_value_generator(decision_nodes, True, False):
			for add_condition in key_value_generator(normal_nodes, False, True):
				new_condition = dict(**condition)
				new_condition.update(**add_condition)
				if same_value_dict(new_condition, 'x'):
					yield 'P(' + dict_to_string(query) + ')'
				else:
					yield 'P(' + dict_to_string(query) + ' | ' + dict_to_string(new_condition) + ')'

def eu_query_generator(table):
	'''
	generate query for P question
	'''
	normal_nodes, decision_nodes = parse_node(table)
	if decision_nodes == []:
		return
	for query in key_value_generator(decision_nodes, True, False):
		#for condition in key_value_generator(decision_nodes, False, True):
		for add_condition in key_value_generator(normal_nodes, False, True):
			#new_condition = dict(**condition)
			#new_condition.update(**add_condition)
			new_condition = dict(**add_condition)
			if same_value_dict(new_condition, 'x'):
				yield 'EU(' + dict_to_string(query) + ')'
			else:
				yield 'EU(' + dict_to_string(query) + ' | ' + dict_to_string(new_condition) + ')'


def meu_query_generator(table):
	'''
	generate query for P question
	'''
	normal_nodes, decision_nodes = parse_node(table)
	if decision_nodes == []:
		return
	query = decision_nodes
	#for condition in key_value_generator(decision_nodes, False, True):
	for add_condition in key_value_generator(normal_nodes, False, True):
		#new_condition = dict(**condition)
		#new_condition.update(**add_condition)
		new_condition = dict(**add_condition)
		if same_value_dict(new_condition, 'x'):
			yield 'MEU(' + list_to_string(query) + ')'
		else:
			yield 'MEU(' + list_to_string(query) + ' | ' + dict_to_string(new_condition) + ')'



def type_filter(table, in_type):
	if in_type == 'P':
		return p_query_generator(table)
	elif in_type == 'EU':
		return eu_query_generator(table)
	elif in_type == 'MEU':
		return meu_query_generator(table)


def query_generator(table_file_name, total_num_each, in_types=['P','EU','MEU']):
	'''
	final generator
	generate one query each time
	'''

	with open(table_file_name, 'r') as f:
		raw_data = f.read()

	table_data = raw_data.split('\n******')[0]
	sentences = table_data.split('\n')
	model_table = Table.parse(sentences)
	# first thing yield is append data
	yield raw_data

	for in_type in in_types:
		queries = type_filter(model_table, in_type)
		count = 0
		for query in queries:
			count += 1
			yield query
			if count > total_num_each:
				break



if __name__ == '__main__':

	import doctest
	doctest.testmod()

	file_no, loop = 0, True
	get_query = query_generator(table_file_name, queries_per_type, in_types=['P','EU', 'MEU'])
	append_data = get_query.next()

	while loop:
		with open('./testcases/%s%03d.txt' % (outputname, file_no), 'w') as f:
			count = 0
			while count < queries_per_file:
				try:
					this_query = get_query.next()
				except StopIteration:
					loop = False
					break
				f.write('%s\n' % this_query)
				count += 1
			f.write('******\n')
			f.write(append_data)
			file_no += 1