from parse import parse_file, Table, Task, Node, parse_seq

def my_round(data, precise):
	'''
	round data number to ndigit after the decimal point

	>>> my_round(13,2) == 13
	True
	>>> my_round(0.25,1) == 0.3
	True
	>>> my_round(13.523123,2) == 13.52
	True
	>>> my_round(130,2) == 130
	True
	>>> my_round(1.309,2) == 1.31
	True
	>>> my_round(1.308,2) == 1.31
	True
	>>> my_round(1.307,2) == 1.31
	True
	>>> my_round(1.306,2) == 1.31
	True
	>>> my_round(1.305,2) == 1.31
	True
	>>> my_round(1.304,2) == 1.3
	True
	>>> my_round(-1.309,2) == -1.31
	True
	>>> my_round(-1.308,2) == -1.31
	True
	>>> my_round(-1.307,2) == -1.31
	True
	>>> my_round(-1.306,2) == -1.31
	True
	>>> my_round(-1.305,2) == -1.31
	True
	>>> my_round(-1.304,2) == -1.3
	True

	'''
	sign = True if data < 0 else False
	updated_data = -data if sign else data
	updated_data = updated_data + 1e-8
	decimal = updated_data - int(updated_data)
	num = int (decimal* (10**(precise+1)))
	if num % 10 >= 5:
		num += 10
	num = num/10
	result = num/(10.0**(precise)) + int(updated_data)
	return -result if sign else result


def contra_check(queries, conditions):
	'''
	check whether queries are contradict to conditions
	'''	
	for key in queries.keys():
		if key in conditions.keys():
			if conditions[key] != queries[key]:
				return True
	return False

def parse_to_list(index, length):
	'''
	given an index and length, return a list of {'+','-'}

	>>> parse_to_list(2,3)
	['-', '+', '-']
	>>> parse_to_list(2,1)
	>>> parse_to_list(3,3)
	['-', '+', '+']
	>>> parse_to_list(5,5)
	['-', '-', '+', '-', '+']

	'''
	if index > (2**length-1):
		return None
	result, tmp = list(), index
	for i in xrange(length-1, -1, -1):
		flag = tmp >> i
		result.append('+' if flag else '-')
		tmp = tmp - flag* 2**i
	return result 


def parse_to_dict(in_list, index):
	'''
	create a dict, which takes in_list as key and index as value

	>>> parse_to_dict(['a','b'], 3)
	{'a': 1, 'b': 1}
	>>> parse_to_dict(['a','b'], 7)
	>>> parse_to_dict(['a','b','x'], 4)
	{'a': 1, 'x': 0, 'b': 0}

	'''
	length, re_list = len(in_list), list(in_list)
	temp = index
	re_list.reverse()
	if (2**length-1) < index:
		return None
	result = dict()
	for key in re_list:
		result[key] = temp%2
		temp = temp /2
	return result



def answer_p(queries, table):
	'''
	return the probability of queries in Bayes Network table
	Same as calculating P(A=+,B=-), where queries={'A':1, 'B':0}

	>>> table_sentences = ['LeakIdea', '0.4', '***', 'NightDefense | LeakIdea', '0.8 +', '0.3 -', '***', 'Infiltration', '0.5', '***', 'Demoralize | NightDefense Infiltration', '0.3 + +', '0.6 + -', '0.95 - +', '0.05 - -']
	>>> table = Table.parse(table_sentences)
	>>> answer_p({}, table) == 1.0
	True
	>>> answer_p({'NightDefense':1, 'Infiltration':0}, table) == 0.25
	True
	>>> answer_p({'LeakIdea':1}, table) == 0.4
	True
	>>> answer_p({'LeakIdea':0}, table) == 0.6
	True

	'''
	if not queries:
		# queries is empty, just return 1
		return 1.0
	
	# recursion terminating condition
	# the parents of the node in queries are in queries == terminate
	termi = True
	for key in queries.iterkeys():
		for parent_node in table[key].parents:
			if not parent_node in queries.keys():
				termi = False
				break
		if termi == False:
			break
	# things to do when terminating condition holds
	if termi:
		result = 1
		for node_name in queries.iterkeys():
			if table[node_name].decision:
			# jump to next loop if this node is a decision node
				continue
			index = 0
			for parent_name in table[node_name].parents:
				index = (index<<1) + queries[parent_name]
			result *= table[node_name].prob_table[index] if queries[node_name] else (1 - table[node_name].prob_table[index])
		return result

	# things to do when terminating condition doesn't hold
	for node_name in queries.iterkeys():
		index = 0
		for parent_name in table[node_name].parents:
			if not parent_name in queries.keys():
				new_queries0 = dict(queries)
				new_queries0.update(**{parent_name:0})
				new_queries1 = dict(queries)
				new_queries1.update(**{parent_name:1})
				result = answer_p(new_queries0, table) + answer_p(new_queries1, table)
	return result


def ask_p(queries, conditions, table):
	'''
	queries and conditions are dict with node_name and node value
	calculate the conditional probability
	'''
	if contra_check(queries, conditions):
		return 0.0
	new_queries = dict(queries)
	new_queries.update(**conditions)
	prob0 = answer_p(new_queries, table)
	prob1 = answer_p(conditions, table)
	return prob0/prob1

def ask_eu(queries, conditions, utility, table):
	'''
	return the expected utility
	'''
	eu = 0
	# new_queries = dict(queries)
	for i in xrange(2**len(utility.parents)):
		new_query = parse_to_dict(utility.parents, i)
		# if the condition in new_condition is contradict to the condition in new_queries
		# jump to next loop
		# if contra_check(new_queries, new_condition):
		#	continue
		# two conditions are consistent with each other
		new_condition = dict(queries)
		new_condition.update(**conditions)
		eu += utility.prob_table[i]*ask_p(new_query, new_condition, table)
	return eu

def ask_meu(queries, conditions, utility, table):
	'''
	'''
	meu = (-100000.0, 0)
	for i in xrange(2**len(queries)):
		new_queries = parse_to_dict(queries, i)
		this_eu = ask_eu(new_queries, conditions, utility, table)
		if this_eu > meu[0]:
			meu = (this_eu, i)
	result = parse_to_list(meu[1], len(queries))
	return ' '.join(result), meu[0]


if __name__ == '__main__':
	import doctest, decimal
	doctest.testmod()
	filename = './self_test/testcases/testcase104.txt'
	tasks,table,utility = parse_file(filename)
	for task in tasks:
		if task.type == 'P':
			result = ask_p(task.query, task.condition, table)
			print my_round(result, 2)
		elif task.type == 'EU':
			print ask_eu(task.query, task.condition, utility, table)
		elif task.type == 'MEU':
			result = ask_meu(task.query, task.condition, utility, table)
			print result[0], result[1]