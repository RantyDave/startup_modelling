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

# simulating a single founder company
from startup_modelling.company import Person, Company


def single_founder_saas(personality, market, state):
    founder = Person(personality)
    initial_state = state
    overhead = 1000
    company = Company(initial_state, [founder], market, overhead)
    results = []
    factors = []

    while not company.state.age == 60:
        market_fit_emphasis = 0 if not company.state.ip_enough() else 0.75
        result, factor = company.month(market_fit_emphasis)
        results.append(result)
        factors.append(factor)
        # print("Month %d sales=%d revenue=%f" % (company.state.age, factor.sales, result.revenue))

        # founder pays themselves 1/2 revenue if not owing anything and
        # that's more than minimum, capped at 20k/mo
        salary = (0.5 * result.revenue if 0.5 * result.revenue > personality.salary else personality.salary)
        if salary > 20000:
            salary = 20000
        if company.state.cash < 0:
            salary = personality.salary
        company.people[0].personality.salary = salary

    return results, factors

