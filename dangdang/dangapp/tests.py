import datetime
import random

from django.test import TestCase

# Create your tests here.
def getNum():
    cur=datetime.datetime.now()
    numStr=cur.year+cur.day+cur.month+cur.hour+cur.minute+cur.second
    ran=random.randint(1000,9999)
    print(numStr,ran)

if __name__ == '__main__':
    getNum()
