import streamlit as st

st.set_page_config(
    page_title="محاكي طوابير السوبرماركت - Applied Probability",
    page_layout="wide"
)

import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt

st.title("🛒 محاكي طوابير السوبرماركت الكبير (Supermarket Checkout Queue Simulator)")
st.markdown("مشروع تطبيق لمادة **الاحتمالات التطبيقية والعمليات العشوائية** - محاكاة نظام طوابير متعدد الكاشيرات ($M/M/c$).")

st.sidebar.header("⚙️ إعدادات المحاكاة (Inputs)")
arrival_rate = st.sidebar.slider("معدل وصول الزبائن (عميل/دقيقة - $\lambda$)", 1.0, 50.0, 15.0, 1.0)
service_time = st.sidebar.slider("متوسط زمن خدمة العميل الواحد (دقائق - $1/\mu$)", 0.5, 5.0, 2.0, 0.25)
num_servers = st.sidebar.slider("عدد الكاشيرات المفتوحة ($c$)", 1, 15, 5, 1)
sim_duration = st.sidebar.slider("مدة المحاكاة (دقائق)", 60, 1440, 480, 60)

mu = 1.0 / service_time
lam = arrival_rate
rho = lam / (num_servers * mu)

st.sidebar.markdown("---")
st.sidebar.info(f"**معامل إشغال الكاشيرات النظري ($\rho$):** {rho:.2f}")
if rho >= 1.0:
    st.sidebar.error("⚠️ تحذير: معدل الوصول أعلى من قدرة الكاشيرات!")

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

if st.button("▶️ ابدأ تشغيل المحاكي"):
    with st.spinner("جاري محاكاة حركة العملاء..."):
        random.seed(42)
        waits, q_lens, t_stamps = run_simulation(sim_duration, arrival_rate, service_time, num_servers)
        
        if len(waits) > 0:
            avg_wait = sum(waits) / len(waits)
            max_wait = max(waits)
            total_customers = len(waits)
        else:
            avg_wait, max_wait, total_customers = 0, 0, 0

        st.markdown("### 📊 نتائج تحليل المحاكاة")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي العملاء", f"{total_customers} عميل")
        col2.metric("متوسط وقت الانتظار ($W_q$)", f"{avg_wait:.2f} دقيقة")
        col3.metric("أقصى وقت انتظار", f"{max_wait:.2f} دقيقة")
        col4.metric("عدد الكاشيرات ($c$)", f"{num_servers} كاشير")

        st.markdown("### 📈 تتبع طول الطابور بمرور الوقت")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(t_stamps, q_lens, color='#1f77b4', linewidth=1.5, label='عدد المنتظرين')
        ax.set_xlabel("زمن المحاكاة (بالدقائق)")
        ax.set_ylabel("عدد العملاء في قائمة الانتظار")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()
        st.pyplot(fig)
        
        st.success("✨ تم تنفيذ نموذج العمليات العشوائية بنجاح!")
else:
    st.info("👈 اضغط على زر **'ابدأ تشغيل المحاكي'** للأعلى لعرض النتائج.")
