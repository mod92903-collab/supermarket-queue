import streamlit as st

st.set_page_config(page_title="Supermarket Queue Simulator")

import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt

st.title("🛒 Supermarket Checkout Queue Simulator")
st.markdown("Applied Probability and Random Processes Project - $M/M/c$ Queueing Model Simulation.")

st.sidebar.header("⚙️ Simulation Settings")
arrival_rate = st.sidebar.slider("Arrival Rate (lambda)", 1.0, 50.0, 15.0, 1.0)
service_time = st.sidebar.slider("Average Service Time (minutes)", 0.5, 5.0, 2.0, 0.25)
num_servers = st.sidebar.slider("Number of Open Cashiers (c)", 1, 15, 5, 1)
sim_duration = st.sidebar.slider("Simulation Duration (minutes)", 60, 1440, 480, 60)

mu = 1.0 / service_time
lam = arrival_rate
rho = lam / (num_servers * mu)

st.sidebar.markdown("---")
st.sidebar.info(f"**Theoretical Server Utilization (rho):** {rho:.2f}")
if rho >= 1.0:
    st.sidebar.error("⚠️ Warning: Arrival rate exceeds capacity!")

def run_simulation(sim_time, arrival_rate, service_time, c):
    env = simpy.Environment()
    checkout_counters = simpy.Resource(env, capacity=c)
    
    wait_times = []
    queue_lengths = []
    time_stamps = []
    
    def customer(env, name, counters, wait_times):
        arrival_time = env.now
        with counters.request() as req:
            yield req
            wait = env.now - arrival_time
            wait_times.append(wait)
            serv_duration = random.expovariate(1.0 / service_time)
            yield env.timeout(serv_duration)

    def customer_generator(env, counters, arrival_rate, wait_times):
        i = 0
        while True:
            interarrival = random.expovariate(arrival_rate)
            yield env.timeout(interarrival)
            i += 1
            env.process(customer(env, f'Customer {i}', counters, wait_times))
            queue_lengths.append(len(counters.queue))
            time_stamps.append(env.now)

    env.process(customer_generator(env, checkout_counters, arrival_rate, wait_times))
    env.run(until=sim_time)
    
    return wait_times, queue_lengths, time_stamps

if st.button("▶️ Run Simulation"):
    with st.spinner("Simulating customer queue behaviors..."):
        random.seed(42)
        waits, q_lens, t_stamps = run_simulation(sim_duration, arrival_rate, service_time, num_servers)
        
        if len(waits) > 0:
            avg_wait = sum(waits) / len(waits)
            max_wait = max(waits)
            total_customers = len(waits)
        else:
            avg_wait, max_wait, total_customers = 0, 0, 0

        st.markdown("### 📊 Simulation Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers Served", f"{total_customers}")
        col2.metric("Avg Waiting Time", f"{avg_wait:.2f} min")
        col3.metric("Max Waiting Time", f"{max_wait:.2f} min")
        col4.metric("Active Cashiers", f"{num_servers}")

        st.markdown("### 📈 Queue Length Over Time")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(t_stamps, q_lens, color='#1f77b4', linewidth=1.5, label='Queue Length')
        ax.set_xlabel("Simulation Time (Minutes)")
        ax.set_ylabel("Number of Customers Waiting")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()
        st.pyplot(fig)
        
        st.success("✨ Stochastic queue simulation completed successfully!")
else:
    st.info("👈 Click on **'Run Simulation'** above to generate results.")
