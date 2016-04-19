import re, sys

_START_6 = re.compile(r'^\*{6}$')
_START_3 = re.compile(r'^\*{3}$')
_FUNC = re.compile(r'^([PMEU]{1,3})\((.+)\)$')


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



def parse_seq(mark_list):
	'''
	convert ['+','-','+'] into seq number

	>>> parse_seq(['+'])
	1
	>>> parse_seq(['+','-','+'])
	5
	>>> parse_seq(['-','-'])
	0
	>>> parse_seq(['-'])
	0
	'''
	seq = 0
	for mark in mark_list:
		seq = (seq<<1) + (1 if mark.strip() =='+' else 0)
	return seq


class Node(object):
	def __init__(self, name, parents=[], prob_table=None, decision=False):
		'''
		name: 		String, indecating the name of this node
		parents: 	List, the names of its parent nodes
		prob_table: List, organized in ACC order, --00 -+01 +-10 ++11
		decision: 	Bool, decide whether this node is a decision node
		utility: 	Bool, decide whether this node is a utility node
		'''
		self.name = name
		if isinstance(parents, list):
			self.parents = list(parents)
		else:
			self.parents = [parents]
		if decision==True:
			self.decision = True
			self.prob_table = None
		else:
			self.decision = False
			self.prob_table = list(prob_table)

	@classmethod
	def parse(cls, sentences):
		'''
		this should be called by Table.parse
		return one Node instance - return cls.__init__(...)
		sentences would be lines between '***'s
		'''
		if len(sentences) == 0:
			return None
		# parse name
		name = sentences[0].split(' | ')[0].strip()
		# parse parents
		if ' | ' in sentences[0]:
			parents = sentences[0].split(' | ')[1].split()
		else:
			parents = []
		if sentences[1].strip() == 'decision':
			return cls(name=name, parents=parents, prob_table=None, decision=True) 
		
		# parse prob_table
		prob_table = [0 for x in xrange(2**len(parents))]
		if len(parents) == 0:
			# if len == 0, there would only be one probability
			prob_table = [float(sentences[1])]
		else:
			# if len >= 1, it would be in '0.4 + - +' format
			for sentence in sentences[1:]:
				prob = sentence.split()
				prob_table[parse_seq(prob[1:])] = float(prob[0])
		# init Node instance
		return cls(name=name, parents=parents, prob_table=prob_table)

	def __str__(self):
		string = 'Name = %s, Parents = %s, Prob_table = %s, Decision = %s' % (self.name, self.parents, self.prob_table, self.decision)
		return string
	__repr__ = __str__


class Task(object):
	def __init__(self, task_type, queries, conditions):
		'''
		queries:	List of sentences. format - ['A = +', 'B = -'] or ['A', 'B']
		conditions:	List of sentences. format - ['A = +', 'B = -']
		'''
		self.type = task_type.strip()
		self.query = {}
		if task_type == 'MEU':
			self.query = queries
		else:
			for query in queries:
				equation = query.split(' = ')
				self.query[equation[0]] = 1 if equation[1]=='+' else 0
		self.condition = {}
		for condition in conditions:
			equation = condition.split(' = ')
			self.condition[equation[0]] = 1 if equation[1]=='+' else 0

	@classmethod
	def parse(cls, sentence):
		'''
		return one Task instance - return cls.__init__(...)
		sentence would be lines before first '******'
		'''
		re_result = _FUNC.match(sentence)
		# parse type
		if re_result:
			task_type = re_result.group(1)
		else:	return None
		# parse query
		paras = re_result.group(2)
		if ' | ' in paras:
			# there is condition
			query = paras.split(' | ')[0].split(', ')
			condition = paras.split(' | ')[1].split(', ')
		else:
			# there is no condition
			query = paras.split(', ')
			condition = []
		return cls(task_type=task_type,queries=query, conditions=condition)

	def __str__(self):
		string = 'Type = %s, Query = %s, Condition = %s' % (self.task, self.query, self.condition)
		return string
	__repr__ = __str__


class Table(dict):
	'''
	get access to Node fron node name. 
	table1['Infiltration'] returns the Node instance whose name is 'Infiltration'
	'''
	def __init__(self, node_list, node_dict):
		self.node_list = node_list
		super(Table,self).__init__(**node_dict)

	@classmethod
	def parse(cls, sentences):
		'''
		return one Table instance - return cls.__init__(...)
		sentence would be lines between first '******' and second '******'
		'''
		info = []
		node_dict = {}
		node_list = []
		for sentence in sentences:
			if _START_3.match(sentence):
				this_node = Node.parse(info)
				node_list.append(this_node.name)
				node_dict[this_node.name] = this_node
				info = []
			else:
				info.append(sentence)
		this_node = Node.parse(info)
		node_list.append(this_node.name)
		node_dict[this_node.name] = this_node
		return cls(node_list,node_dict)

	def __str__(self):
		string = 'Nodes are %s' % (self.node_list)
		return string
	__repr__ = __str__


def parse_file(file_name):
	tasks, table = [], None
	table_sentences, utility_sentences = [], []
	start_count = 0
	with open(file_name) as f:
		for line in f:
			if _START_6.match(line):
				start_count +=1
				continue
			if start_count == 0:
				# parse task sentences
				tasks.append(Task.parse(line))
			elif start_count == 1:
				# parse table sentences
				table_sentences.append(line)
			elif start_count == 2:
				# parse utility sentences
				utility_sentences.append(line)
	# start parsing
	table = Table.parse(table_sentences)
	utility = Node.parse(utility_sentences)
	return (tasks,table,utility)


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
	# import doctest
	# doctest.testmod()
	input_file_name = sys.argv[2]
	tasks,table,utility = parse_file(input_file_name)
	with open('output.txt', 'w') as f:
		for i, task in enumerate(tasks):
			if i > 1:
				f.write('\n')
			if task.type == 'P':
				result = ask_p(task.query, task.condition, table)
				f.write( '%.2f' % my_round(result,2))
			elif task.type == 'EU':
				result = ask_eu(task.query, task.condition, utility, table)
				f.write( '%d' % my_round(result,0))
			elif task.type == 'MEU':
				result = ask_meu(task.query, task.condition, utility, table)
				f.write('%s ' % result[0])
				f.write('%d' % my_round(result[1],0))
			if i == 0:
				f.write('\n')