a = 10 ** 9
i = 0
n = 10 ** 6

while i <= n:
    a += 10 ** (-6)
    i += 1
    
a -= 10 ** 9
print (str(a))
