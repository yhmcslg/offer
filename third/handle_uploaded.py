#coding:utf8
	
import os
def	handle_uploaded_file(dirname,f):
	with open(dirname,'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)