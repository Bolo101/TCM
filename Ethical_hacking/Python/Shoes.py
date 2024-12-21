#!/bin/python
class Shoes:
    def __init__(self,name,price):
        self.name = name
        self.price = float(price)

    def budget_check(self,budget):
        if not isinstance(budget,(int,float)): #close application if type is not matched
                print('Invalid entry. Please enter a number')
                exit()

    def change(self, budget):
         return(budget - self.price)
    
    def buy(self, budget):
         self.budget_check(budget)

         if budget >= self.price:
            print(f'You can cop some {self.name}')
            if budget == self.price:
                 print('You have exactly enough money for this item')
            else:
                 print(f'You can have these shoes and {self.change(budget)}$')
            exit('Thanks for you purchase')