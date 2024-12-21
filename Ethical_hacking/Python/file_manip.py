#!/bin/python

months = open("months.txt")
print(months.read())

months.seek(0)
print(months.readlines())
months.seek(0)
print(months.readline())
months.seek(0)
for month in months:
	print(month)
months.seek(0)
for month in months:
	print(month.strip())

months.close()

days = open("days.txt",'a')
days.write(input("Insert some text: "))
days.close()

