# Copyright (c) 2018 David Preece, All rights reserved.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
from random import random


class Personality:
    """The personality of someone involved in the company, all numbers per month:

    :param development: months to get to 100% development or product/market fit
    :param marketing: months to get to 100% channel
    :param salary: survival salary in dollars
    :param op_cost: opportunity cost salary in dollars
    """
    def __init__(self, *, development=18, marketing=48, salary=4000, op_cost=8000):
        self.development = 1/development
        self.marketing = 1/marketing
        self.salary = salary
        self.op_cost = op_cost


class Person:
    """A single person.

    :param personality: their assumed fixed personality
    """
    def __init__(self, personality):
        self.personality = personality
        self.op_cost = 0
        self.returned = 0

    def one_month(self):
        self.op_cost += self.personality.op_cost
        self.returned += self.personality.salary


class Market:
    """The market the company is operating in

    :param events: the number of potential sale events per month
    :param flake: the fraction of these sales that may become unavailable just because
    :param monthly: the monthly subscription cost
    :param ctrct_len: length of contract
    :param variance: the variance in length of contract as a fraction
    :param acq: acquisition cost
    """
    def __init__(self, *, events=1000, flake=0.5, monthly=10, ctrct_len=24, variance=0.5, acq=10):
        self.events = events
        self.flake = flake
        self.monthly = monthly
        self.ctrct_len = ctrct_len
        self.variance = variance
        self.acq = acq

    def sales_pool_this_month(self):
        return int(self.events * (1 - (random() * self.flake)))

    def generate_sale(self):
        return Sale(self.monthly, self.ctrct_len + (-0.5 + random()) * self.variance)


class Sale:
    """A single sale or subscriber.

    :param spend: monthly price
    :param length: the number of months over which the spend it spent
    """
    def __init__(self, spend, months):
        self.spend = spend
        self.months = months

    def revenue_this_month(self):
        if self.months > 0:
            self.months -= 1
        return self.spend if self.months >= 0 else 0

    def remaining_revenue(self):
        return self.months * self.spend


class State:
    """The current state of the company assets - a balance sheet, I guess:

    :param capital: a startup capital injection
    :param channel: an initial marketing channel as a fraction of potential market
    :param pmf: an initial product/market fit as a fraction
    """
    def __init__(self, *, capital=150000, channel=0, pmf=0.5):
        self.age = 0
        self.initial = capital
        self.cash = capital
        self.ip = 0  # a multiplier on the number of sales
        self.channel = channel
        self.pmf = pmf
        self.subscribers = set()

    def development_effect(self):
        overall = self.ip * self.pmf
        return overall if overall > 0.75 else 0

    def pmf_enough(self):
        return self.pmf > 0.75

    def ip_enough(self):
        return self.ip > 0.75

    def pipeline(self):
        return sum(s.remaining_revenue() for s in self.subscribers)

    def as_string(self):
        return ("age=%d cash=%d pipeline=%f ip=%f pmf=%f channel=%f subscribers=%d" %
                (self.age, int(self.cash), self.pipeline(), self.ip, self.pmf, self.channel, len(self.subscribers)))


class Result(object):
    """One months' result"""
    pass


class Factors(object):
    """One month's factors"""
    pass


class Company:
    """The company itself

    :param state: an initial state
    :param people: the people involved
    :param market: the market in which they operate
    :param fixed_overhead: monthly fixed overhead
    :param cost_of_sale: as a fraction
    """
    def __init__(self, state, people, market, fixed_overhead):
        self.state = state
        self.people = people
        self.market = market
        self.overhead = fixed_overhead

    def month(self, market_fit_emphasis):
        """Iterate through one months' business

        :param market_emphasis: The fraction of emphasis placed on product/market fit as opposed to development"""
        self.state.age += 1

        # pay the people
        salaries = sum(p.personality.salary for p in self.people)
        self.state.cash -= (salaries + self.overhead)

        # pay the tax man
        self.state.cash -= salaries * 0.3

        # iterate their state of mind
        for person in self.people:
            person.one_month()

        # develop ip
        self.state.ip += sum(p.personality.development * (1 - market_fit_emphasis) for p in self.people)
        if self.state.ip > 1:
            self.state.ip = 1

        # improve product/market fit
        self.state.pmf += sum(p.personality.development * market_fit_emphasis for p in self.people)
        if self.state.pmf > 1:
            self.state.pmf = 1

        # grow the sales channel if product/market fit and ip development are enough
        if not self.state.development_effect() > 0:
            self.state.channel = 0
        else:
            self.state.channel += sum(p.personality.marketing for p in self.people)
            if self.state.channel > 1:
                self.state.channel = 1

        # maybe make some sales
        pool = self.market.sales_pool_this_month()
        sales_this_month = pool * self.state.development_effect() * self.state.channel
        for n in range(0, int(sales_this_month)):
            self.state.subscribers.add(self.market.generate_sale())
        self.state.cash -= self.market.acq * sales_this_month

        # calculate revenue
        revenue = sum(s.revenue_this_month() for s in self.state.subscribers)
        self.state.cash += revenue

        # scores on the doors
        returned = sum(p.returned for p in self.people)
        op_cost = sum(p.op_cost for p in self.people)
        result = Result()
        result.revenue = revenue
        result.sales = int(sales_this_month)
        result.pipeline = self.state.pipeline()
        result.cash = self.state.cash
        result.salaries = salaries
        result.overall = ((self.state.cash + returned) - (self.state.initial + op_cost))

        factors = Factors()
        factors.ip = self.state.ip
        factors.pmf = self.state.pmf
        factors.channel = self.state.channel
        factors.pool = pool
        factors.sales = sales_this_month

        return result, factors

    def capital_injection(self, amount):
        """Inject capital into the company"""
        self.state.cash += amount

