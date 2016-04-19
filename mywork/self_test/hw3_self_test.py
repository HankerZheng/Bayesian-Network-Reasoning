import sys, os, random
sys.path.append('../../')
from file_compare import file_compare
# from game_space import gamespace

start_no = 0
end_no = 121
# start_no == end_no means that it only runs one case

fname = 'testcase'
test_names = ['HongtaiCao']
jump_cases = []
current_path = os.path.dirname(__file__)

def main():
	'''
	'''
	for test_num in xrange(start_no, end_no+1):
		if test_num in jump_cases:
			continue
		# run my code
		os.popen('python .\\HanZheng\\HW3.py -i .\\testcases\\%s%03d.txt' % (fname,test_num))
		my_output_file = '.\\output.txt'
		# run others code
		for name in test_names:
			os.chdir('.\\%s' % name)
			os.popen('python .\\hw3cs561s16.py -i ..\\testcases\\%s%03d.txt'% (fname,test_num))
			os.chdir('..')

		#compare my output with others
		for name in test_names:
			his_output_file = '%s\\output.txt' % name
		file_compare(my_output_file, his_output_file, '(%s%03d.txt) '% (fname,test_num) + ' -- Compare results with '+ name )

if __name__ == '__main__':
	main()
