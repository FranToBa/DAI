import random
import re



def burbuja(n):
	for i in range(len(n)-1,0,-1):
		for j in range(i):
			if (n[j] > n[j+1]):
				tmp = n[j]
				n[j] = n[j + 1]
				n[j + 1] = tmp


def burbujaCorto(m):
	intercambio = True
	i = len(m)-1
	while i > 0 and intercambio:
		intercambio = False
		for j in range(i):
           		if m[j]>m[j+1]:
               			intercambio = True
               			tmp = m[j]
               			m[j] = m[j+1]
               			m[j+1] = tmp
		i = i-1

def fibonacci_f(n):
	if n<=0:
		return 0
	elif n==1:
		return 1
	elif n==2:
		return 1
	else:
		return fibonacci_f(n-1)+fibonacci_f(n-2)

def palabraYMayuscula(string):
	a = re.compile(r'([A-Za-z]+) ([A-Z])')
	return a.match(string)

def email(string):
	a = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b')
	return a.match(string)

def tarjetaCredito(string):
	a = re.compile(r'([0-9]{4}) ([0-9]{4}) ([0-9]{4}) ([0-9]{4})|([0-9]{4})-([0-9]{4})-([0-9]{4})-([0-9]{4})')
	return a.match(string)
