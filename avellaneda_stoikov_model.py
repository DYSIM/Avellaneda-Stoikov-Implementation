import math
import numpy as np
import matplotlib.pyplot as plt
import random
from brownian_motion import brownian_motion



# Parameters

# Initial Price
s_0 = 100
# Time. normalized to 1
T = 1.0
# Volatility
sigma = 2
# number of time steps
N = 200
# single time step. time fraction
dt = T / N
# inventory Risk aversion
gamma = 0.1
# order book liquidity
k = 1.5


number_of_simulation = 1000

pnl_of_simulation = np.zeros((number_of_simulation))
final_inventory = np.zeros((number_of_simulation))

M = s_0/200
A = 1./dt/np.exp(k*M/2)

# begin monte carlo simulation
for mode in ['symmetric', 'inventory']:

    for simulation in range(number_of_simulation):
        prices = brownian_motion(s_0, N, sigma, dt) # mid-price
        time = np.linspace(0.0, T, N)

        pnl = np.zeros((N))
        cash = np.zeros((N))
        inventory = np.zeros((N))
        reserve_price = np.zeros((N))
        r_optimal_ask = np.zeros((N))
        r_optimal_bid = np.zeros((N))

        for step in range(N-1):

            # limited time horizon
            reserve_price[step] = prices[step] - inventory[step] * gamma * (sigma ** 2) * (T-dt*step)
            reserve_spread = (2/gamma) * np.log(1 + gamma/k)

            if mode == 'symmetric':
                # symmetric strategy (fixed around mid-price)
                r_optimal_ask[step] = prices[step] + reserve_spread / 2
                r_optimal_bid[step] = prices[step] - reserve_spread / 2
                optimal_distance_ask = r_optimal_ask[step] - prices[step]
                optimal_distance_bid = prices[step] - r_optimal_bid[step]
            elif mode == 'inventory':
                #i nventory strategy (fixed around reservation price)
                r_optimal_ask[step] = reserve_price[step] + reserve_spread / 2
                r_optimal_bid[step] = reserve_price[step] - reserve_spread / 2
                optimal_distance_ask = -gamma*inventory[step]*(sigma**2) + (1/gamma)*np.log(1 + (gamma/k))
                optimal_distance_bid = gamma*inventory[step]*(sigma**2) + (1/gamma)*np.log(1 + (gamma/k))
            # print(optimal_distance_ask,optimal_distance_bid)

            # A_ask =  1./dt/np.exp(k*optimal_distance_ask)
            # A_bid =  1./dt/np.exp(k*optimal_distance_bid)


            # exponential arrival rates
            lambda_ask = A * np.exp(-k*optimal_distance_ask)
            lambda_bid = A * np.exp(-k*optimal_distance_bid)

            # probability of bid and ask
            ask_probability = 1 - math.exp(-lambda_ask*dt)
            bid_probability = 1 - math.exp(-lambda_bid*dt)

            ask_amount = 0
            bid_amount = 0
            if random.random() < ask_probability:
                ask_amount = 1
            if random.random() < bid_probability:
                bid_amount = 1

            # Transact. change inventory, cash, and pnl
            inventory[step+1] = inventory[step] - ask_amount + bid_amount
            cash[step+1] = cash[step] + r_optimal_ask[step]*ask_amount - r_optimal_bid[step]*bid_amount
            pnl[step+1] = cash[step+1] + inventory[step+1]*prices[step]

        #store final pnl and inventory
        pnl_of_simulation[simulation] = pnl[-1]
        final_inventory[simulation] = inventory[-1]


    # calculate statistics
    print(f'Statistics over: {number_of_simulation} simulations for {mode} mode\n')

    print("Average PnL: %.2f"% np.mean(pnl_of_simulation))
    print("Std Profit: %.2f"% np.std(pnl_of_simulation))
    print("Average inventory: %.2f"% np.mean(final_inventory))
    print("Std inventory: %.2f\n\n"% np.std(final_inventory))

    # save plot
    f = plt.figure(figsize=(15, 5))
    f.add_subplot(1,3, 1)
    plt.plot(time[:-1], prices[:-1], color='black', label='Mid-market price')
    plt.plot(time[:-1], reserve_price[:-1], color='green', linestyle='dashed', label='Reservation price')
    plt.plot(time[:-1], r_optimal_ask[:-1], color='red', linestyle='', marker='.', label='Price asked', markersize='3')
    plt.plot(time[:-1], r_optimal_bid[:-1], color='red', linestyle='', marker='o', markerfacecolor = 'none',label='Price bid', markersize='3')
    plt.xlabel('Time', fontsize=16)
    plt.ylabel('Stock Price', fontsize=16)
    plt.grid(True)
    plt.legend()

    f.add_subplot(1,3, 2)
    plt.plot(time[:-1], pnl[:-1], color='green', label='P&L')
    plt.xlabel('Time', fontsize=16)
    plt.ylabel('PnL', fontsize=16)
    plt.grid(True)
    plt.legend()

    f.add_subplot(1,3, 3)
    plt.plot(time[:-1], inventory[:-1], color='red', label='Qty of Inventory')
    plt.xlabel('Time', fontsize=16)
    plt.ylabel('Inventory', fontsize=16)
    plt.grid(True)
    plt.legend()

    f.savefig(f'result_{mode}.png')
