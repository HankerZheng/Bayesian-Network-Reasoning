import re

_START_6 = re.compile(r'^\*{6}$')
_START_3 = re.compile(r'^\*{3}$')
_FUNC = re.compile(r'^([PMEU]{1,3})\((.+)\)$')

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

if __name__ == '__main__':
	filename = '../HW3_samples/sample05.txt'
	tasks,table,utility = parse_file(filename)
	print utility
	print tasks
	for node_name in table.node_list:
		print table[node_name]