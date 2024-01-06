import json

def pp(content):
	for i in range(len(str(content))+4):
		print("#",end="")
	print('\n# ',end="")
	print(content,end='')
	print(' #')
	for i in range(len(str(content))+4):
		print("#",end="")
	print()

def dict2json(d):
    j=json.dumps(d)
    pp(j)
    return j
def pline(s):
	for i in s:
		print("#",end='')
def fm(source,msg):
	data="# from: "+source+", msg: "+msg+" #"
	pline(data)
	print()
	print(data)
	pline(data)
	print()

