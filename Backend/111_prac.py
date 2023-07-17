import hashlib
import string
import random

# s = "hello"
#
# ans = hashlib.blake2s(s.encode()).digest()
#
#
# print(type(str(ans)))
#
# loop_count = 10

# def method6():
#   return ''.join([`num` for num in xrange(loop_count)])


f = ""

x = string.ascii_lowercase
print(x)

for i in range(10):
  num = random.randint(0, 25)
  f += x[num]

print(f)


