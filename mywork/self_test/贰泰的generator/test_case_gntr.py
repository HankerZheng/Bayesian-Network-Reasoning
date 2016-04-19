from query_gntr import *
import re

_EMPTY_CATCH = re.compile(r"\(\)")
itest=12
input_file="./testcases/sample002.txt" # 6561 P questions
outputname = "testcases"
append = \
'''******
LeakIdea
0.4
***
NightDefense | LeakIdea
0.8 +
0.3 -
***
Infiltration
decision
***
Demoralize | NightDefense Infiltration
0.3 + +
0.6 + -
0.95 - +
0.05 - -
******
utility | Demoralize 
100 +
-10 -
'''

count, file_no = 1, 0
get_query = query_gntr(input_file,"")

while count < 13000:
	with open('./testcases/%s%03d.txt' % (outputname, file_no), 'w') as f:
		while count % 100:
			this_query = get_query.next()
			if _EMPTY_CATCH.search(this_query):
				this_query = get_query.next()
			f.write('%s\n' % this_query)
			count += 1
		f.write(append)
		count += 1
	file_no += 1

print count