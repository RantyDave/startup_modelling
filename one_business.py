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
import matplotlib.pyplot as plt
from startup_modelling.company import Personality, Market, State
from startup_modelling.single_founder import single_founder_saas

figure, money_axes = plt.subplots()
money_axes.set_xlabel("months")
money_axes.set_ylabel("thousands")
money_axes.set_ylim(-400000, 600000)
money_axes.grid(True)
alpha = 1

for events in range(10, 100, 10):
    personality = Personality()
    market = Market(events=events, monthly=250, ctrct_len=48, acq=1500)
    state = State()

    results, factors = single_founder_saas(personality, market, state)
    money_axes.plot([r.salaries * 12 for r in results], label='salary (year)', color='blue', alpha=alpha)
    money_axes.plot([r.cash for r in results], label='cash', color='red', alpha=alpha)
    money_axes.plot([r.revenue for r in results], label='revenue', color='purple', alpha=alpha)
    money_axes.plot([r.overall for r in results], label='overall', color='green', alpha=alpha)
    money_axes.plot([r.pipeline for r in results], label='pipeline', color='orange', alpha=alpha)

    if alpha == 1:
        money_axes.legend()

    alpha = 0.1

plt.show()
