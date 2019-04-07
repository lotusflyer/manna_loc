#!/usr/bin/python

import sys

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

arg_list = sys.argv

print(arg_list)
print(arg_list[0])
print(arg_list[1])

targ_addr = arg_list[1]
print(targ_addr)

if len(sys.argv) == 2:
    print("target address is: {}".format(targ_addr))
else:
    print("something went wrong")

