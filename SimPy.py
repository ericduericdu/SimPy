"""Problem B Homework 2 ECS145
Group Members:
    John Nguyen 998808398
    Eric Du 913327304
    Joanne Wang 9133360523
    Jeffrey Tai 998935915
"""

from SimPy.Simulation import *
from random import Random, gammavariate

class Inventory(Level):
    def __init__(self,time):
        Level.__init__(self,monitored=True)
        self.start_time = time

class G:
    TotalWaitTime = 0.0  # total wait time for all customers with pending orders
    NImmedServ = 0  # number of customers that were served immediately
    NOrders = 0  # total customers
    NDelivered = 0 # Total Deliveries
    NImmedDeli = 0 # number of deliveries that were shippped immedately upon arriving
    Rnd = Random(12345)
    inventory = Inventory(now())

class Delivery(Process):
    def __init__(self,alphai, betai):
        Process.__init__(self)
        self.alphai = alphai
        self.betai = betai
        self.start_time = 0.0
    def run(self):
        while True:
            yield (hold, self, G.Rnd.gammavariate(alpha=self.alphai, beta=self.betai))
            G.inventory.start_time = now()
            yield (put, self, G.inventory,1)
            G.NDelivered += 1

class CustomerGenerator(Process):
    def __init__(self, alpha_c, beta_c):
        Process.__init__(self)
        self.alpha_c = alpha_c
        self.beta_c = beta_c

    def run(self):
        while 1:
            """Wait for a customer to come in"""
            yield (hold, self, G.Rnd.gammavariate(alpha=self.alpha_c,beta=self.beta_c))
            customer = Customer(now())
            activate(customer, customer.run())
            G.NOrders += 1

class Customer(Process):
    def __init__(self,time):
        Process.__init__(self)
        self.start_time = time

    def run(self):
        if G.inventory.amount > 0:
            G.NImmedServ += 1
            if G.inventory.start_time == self.start_time:
                G.NImmedDeli += 1
            yield (get, self, G.inventory, 1)

        else:
            self.start_time = now()
            yield (get, self, G.inventory, 1)
            G.NImmedDeli += 1
            G.TotalWaitTime += now() - self.start_time

def storesim(maxsimtime, alphac, betac, alphai, betai):
    initialize()  # required SimPy statement
    # set up the customer and inventory processes
    customerGenerator = CustomerGenerator(alphac, betac)
    activate(customerGenerator, customerGenerator.run())
    deliver = Delivery(alphai,betai)
    activate(deliver,deliver.run())
    simulate(until=maxsimtime)
    mean = G.TotalWaitTime / G.NOrders
    CustImmed = float(G.NImmedServ) / G.NOrders
    InvImmed = float(G.NImmedDeli) / G.NDelivered
    print "the mean time it takes for a customer's order to be filled:", \
        mean
    print "proportion of customer orders filled immediately:", \
        CustImmed
    print "the proportion of inventory deliveries that are immediately used to fill a customer order upon arrival of the delivery:", \
        InvImmed
    return (mean,CustImmed,InvImmed)
