# Bayesian Network Reasoning
This is the 3rd course project with the test-case generator for CSCI 561 in USC. The purpose of this project is to analyze probabilities, suggest the best decision with the Maximum Expected Utility.

# Input File Format
1. The first few lines are queries (one query per line). The query can have three forms:
    - Starting with 'P', asking for specific joint probabilities, marginal probabilities, or conditional probabilities, when there is either no decision node, or the decision node, or the decision node has a set value (for conditional probabilities): e.g. `P(NightDefense = +, Infiltration = )`, `P(Demoralize = + | LeakIdea = +, Infiltration = +)`
    - Starting with 'EU', asking for expected utility, conditioned on other observed evidence, when there is one or more than one unset decision nodes (expected utility will always): e.g. `EU(Infiltration = + | LeakIdea = +)`
    - Starting with "MEU", asking for maximum expected utility, conditioned on other observed evidence, when there is one or more than one unset decision nodes: e.g. `MEU(Infiltration | LeakIdea = +)`
2. The line after all queries will have six "*" as the seperator.
3. The following lines represent a Bayesian network by showing the tables of probabilities / conditional probabilities for each event / node. The tables are seperated by three "*", and will have the following format:
```  
Demoralize | NightDefense Infiltration  
0.3 + +  
0.6 + -  
0.9 - +  
0.05 - -
```
4. The first line contains the nodes's name, followed by the names of its parents, separated by a "|" sign (or no "|" sign when there's no parent).
5. All node names begin with an uppercase letter and contain letters only.
6. The following lines show the probabilities for all combinations of parent node values.
7. All nodes can only have two values, "+" (event occurred) or "-" (event did not occurred).
8. The probability will range from 0 to 1 (but not 0 or 1 exactly), and is always for occurrence only.
9. The parent node values always follow the order in which they appear in the first line.
10. There won't be any directed cycles in the given networks.

An example input is showed as blow:
```
P(Demoralize = + | LeakIdea = -, Infiltration = +)
EU(Infiltration = +)
EU(Infiltration = + | LeakIdea = +)
MEU(Infiltration)
MEU(Infiltration | LeakIdea = +)
******
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
```

# Test-case Generator
Source code in `/mywork/self_test/hw3_test_generator.py`. Given a basic knowledge base, the test-case generator would randomly generate certain number of possible queries in `/mywork/self_test/testcases/`.

# Usage
This program should be called as `$python .\file_name.py -i input_file_name.txt`
