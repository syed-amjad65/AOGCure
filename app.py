import streamlit as st
import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
import random
from streamlit_agraph import agraph, Node, Edge, Config
from groq import Groq
import os

st.set_page_config(page_title="AOGCure Command", layout="wide", page_icon="🧬")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.markdown("""
<style>
    .main, .stApp { background-color: #060a13; color: white; }
    [data-testid="stSidebar"] { background-color: #060a13; border-right: 1px solid #1e293b; }
    .block-container { padding-top: 1rem; }
    .header-box { background-color: #0f1629; padding: 20px 30px; border-radius: 10px; border-bottom: 2px solid #2563eb; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .header-title { color: white; font-size: 24px; font-weight: bold; margin: 0; }
    .header-sub { color: #94a3b8; font-size: 14px; margin: 0; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
    .kpi-card { background-color: #0f1629; border-radius: 8px; padding: 20px; border-top: 4px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
    .kpi-card.red { border-top-color: #ef4444; }
    .kpi-card.orange { border-top-color: #f97316; }
    .kpi-card.yellow { border-top-color: #eab308; }
    .kpi-card.green { border-top-color: #22c55e; }
    .kpi-card.purple { border-top-color: #a855f7; }
    .kpi-label { color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
    .kpi-value { color: white; font-size: 32px; font-weight: bold; margin: 0; }
    .kpi-delta { font-size: 13px; margin-top: 5px; }
    .kpi-delta.up { color: #ef4444; }
    .kpi-delta.down { color: #22c55e; }
    .graph-box { background-color: #0f1629; border-radius: 8px; padding: 20px; border: 1px solid #1e293b; margin-bottom: 20px; }
    .section-title { color: white; font-size: 18px; font-weight: bold; margin-top: 0; margin-bottom: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 10px;}
    .dataframe { color: white; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    data = []
    tails = [f"N{random.randint(100, 999)}UA" for _ in range(15)]
    airports = ['JFK', 'LAX', 'ORD', 'MIA', 'DFW', 'ATL', 'SFO', 'DEN']
    base = datetime(2023, 10, 15)
    for tail in tails:
        curr_time = base.replace(hour=6, minute=0)
        origin = random.choice(airports)
        for leg in range(4):
            dest = random.choice([a for a in airports if a != origin])
            delay = 0
            cause = "On Time"
            if leg == 0 and random.random() > 0.5:
                delay = random.randint(40, 120)
                cause = random.choice(["Gate Mismatch (B737 at A320 stand)", "Late Catering Arrival", "MEL Hold", "Ground Power Unit Failure"])
            elif leg > 0 and data[-1]['delay'] > 15:
                delay = data[-1]['delay'] + random.randint(-5, 20)
                cause = f"Late Arriving Aircraft (Inherited from {data[-1]['flight_id']})"
            elif random.random() > 0.85:
                delay = random.randint(20, 60)
                cause = "Crew Connection Delay"
            data.append({"flight_id": f"{tail[:4]}{leg+1}", "tail": tail, "origin": origin, "dest": dest, "scheduled_dep": curr_time, "delay": delay, "cause": cause})
            curr_time = curr_time + timedelta(hours=random.randint(2, 5)) + timedelta(minutes=delay) + timedelta(minutes=45)
            origin = dest
    return pd.DataFrame(data)

df = get_data()
delayed_df = df[df['delay'] > 15]

with st.sidebar:
    st.markdown("## 🧬 AOGCure")
    st.markdown("---")
    st.markdown("#### Command Center")
    selected = st.selectbox("Target Flight:", delayed_df['flight_id'].tolist())

header_html = """
<div class="header-box">
    <div>
        <h1 class="header-title">Executive Delay Intelligence</h1>
        <p class="header-sub">AOGCure Operations Command • Real-Time Cascade Tracking</p>
    </div>
    <div style="text-align: right;">
        <p class="header-sub" style="color: #3b82f6;">LIVE DATA • October 2023</p>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

total_flights = len(df)
critical_cascades = len(df[df['delay'] > 60])
active_delays = len(delayed_df)
aog_events = len(df[df['cause'].str.contains("MEL|Hold")])
recovery_rate = round(100 - (len(delayed_df) / total_flights * 100), 1)

kpi_html = f"""
<div class="kpi-grid">
    <div class="kpi-card red">
        <div class="kpi-label">Critical Cascades</div>
        <div class="kpi-value">{critical_cascades}</div>
        <div class="kpi-delta up">↑ 12 since last review</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-label">Active Delays</div>
        <div class="kpi-value">{active_delays}</div>
        <div class="kpi-delta up">↑ 24 this quarter</div>
    </div>
    <div class="kpi-card yellow">
        <div class="kpi-label">AOG / MEL Events</div>
        <div class="kpi-value">{aog_events}</div>
        <div class="kpi-delta up">↑ 8.3% MoM</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-label">AI Root Causes Found</div>
        <div class="kpi-value">{active_delays}</div>
        <div class="kpi-delta down" style="color: #a855f7;">100% AI Flagged</div>
    </div>
</div>
<div class="kpi-grid" style="margin-top: -10px;">
    <div class="kpi-card">
        <div class="kpi-label">Total Fleet Tracked</div>
        <div class="kpi-value" style="font-size: 24px;">{total_flights}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Threshold Breaches</div>
        <div class="kpi-value" style="font-size: 24px;">{critical_cascades + active_delays}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Unresolved Traces</div>
        <div class="kpi-value" style="font-size: 24px;">{active_delays}</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-label">On-Time Recovery Rate</div>
        <div class="kpi-value" style="font-size: 24px; color: #22c55e;">{recovery_rate}%</div>
        <div class="kpi-delta down">↑ 3.1% vs prior quarter</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

if selected:
    flight = df[df['flight_id'] == selected].iloc[0]
    tail = flight['tail']
    rotation = df[df['tail'] == tail].sort_values('scheduled_dep').reset_index(drop=True)
    
    graph_html = f"""
    <div class="graph-box">
        <h2 class="section-title">Target Investigation: {selected} ({tail}) • {flight['origin']} → {flight['dest']}</h2>
    """
    st.markdown(graph_html, unsafe_allow_html=True)

    nodes, edges, trace_data = [], [], []
    for idx, row in rotation.iterrows():
        color = "#ef4444" if row['delay'] > 60 else ("#f97316" if row['delay'] > 30 else ("#eab308" if row['delay'] > 15 else "#22c55e"))
        nodes.append(Node(id=row['flight_id'], label=f"{row['flight_id']} (+{row['delay']}m)\n{row['origin']}-{row['dest']}", size=25, color=color, shape="box"))
        if idx > 0:
            prev = rotation.iloc[idx-1]
            edges.append(Edge(source=prev['flight_id'], target=row['flight_id'], color="#ef4444" if prev['delay'] > 15 else "#64748b", width=3 if prev['delay'] > 15 else 1))
        if row['delay'] > 0:
            trace_data.append({"Flight ID": row['flight_id'], "Delay (Min)": row['delay'], "Root Cause": row['cause']})

    config = Config(width=1000, height=350, directed=True, physics=False, hierarchical=True)
    agraph(nodes=nodes, edges=edges, config=config)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='graph-box'><h2 class='section-title'>Root Cause Trace Log</h2>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(trace_data), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='graph-box'><h2 class='section-title'>AI Causal Analysis</h2>", unsafe_allow_html=True)
        with st.spinner("Analyzing cascade..."):
            try:
                prompt = f"You are an aviation VP. Read this delay cascade and write a 2-sentence brutal summary of what went wrong. Cascade: {trace_data}"
                resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], temperature=0.3)
                st.info(resp.choices[0].message.content)
            except Exception as e:
                st.error("AI Error - Check API Key")
        st.markdown("</div>", unsafe_allow_html=True)
