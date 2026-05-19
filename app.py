"""
采研智库 —— 原材料价格跟踪看板
"""
import streamlit as st
import sqlite3, os, io
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import pandas as pd

st.set_page_config(page_title="采研智库-原材料价格跟踪", page_icon="📊", layout="wide")

# === 嵌入式数据 (Streamlit Cloud 无 DB 时使用) ===
EMBEDDED_CSV = """date,product_name,product_id,category,unit,low,high,avg,change_val
2026-05-18,1#银,201102250392,贵金属,元/千克,18311,18331,18321,-1480
2026-05-15,1#银,201102250392,贵金属,元/千克,19786,19816,19801,-1595
2026-05-14,1#银,201102250392,贵金属,元/千克,21376,21416,21396,84
2026-05-13,1#银,201102250392,贵金属,元/千克,21302,21322,21312,150
2026-05-12,1#银,201102250392,贵金属,元/千克,21152,21172,21162,1267
2026-05-11,1#银,201102250392,贵金属,元/千克,19885,19905,19895,148
2026-05-08,1#银,201102250392,贵金属,元/千克,19737,19757,19747,387
2026-05-07,1#银,201102250392,贵金属,元/千克,19350,19370,19360,852.5
2026-05-06,1#银,201102250392,贵金属,元/千克,18500,18515,18507.5,477.5
2026-04-30,1#银,201102250392,贵金属,元/千克,18015,18045,18030,21
2026-04-29,1#银,201102250392,贵金属,元/千克,17994,18024,18009,-416
2026-04-28,1#银,201102250392,贵金属,元/千克,18410,18440,18425,-276
2026-04-27,1#银,201102250392,贵金属,元/千克,18686,18716,18701,-99
2026-04-24,1#银,201102250392,贵金属,元/千克,18785,18815,18800,-420
2026-04-23,1#银,201102250392,贵金属,元/千克,19200,19240,19220,-67
2026-04-22,1#银,201102250392,贵金属,元/千克,19267,19307,19287,-455
2026-04-21,1#银,201102250392,贵金属,元/千克,19722,19762,19742,-268
2026-04-20,1#银,201102250392,贵金属,元/千克,19995,20025,20010,527
2026-05-18,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-15,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-14,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-13,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-12,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-11,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-08,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-07,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-06,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-30,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-29,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-28,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-27,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-24,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-23,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-22,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-21,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-04-20,N型致密料,202501060001,光伏,元/千克,33,36,34.5,0
2026-05-18,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,190865,190865,190865,-894
2026-05-15,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,191759,191759,191759,-3345
2026-05-14,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,195104,195104,195104,-6222
2026-05-13,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,201326,201326,201326,936
2026-05-12,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,200390,200390,200390,5097
2026-05-11,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,195293,195293,195293,1219
2026-05-08,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,194074,194074,194074,5369
2026-05-07,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,188705,188705,188705,3360
2026-05-06,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,185345,185345,185345,9180
2026-04-30,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,176165,176165,176165,2865
2026-04-29,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,173300,173300,173300,237
2026-04-28,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,173063,173063,173063,-1689
2026-04-27,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,174752,174752,174752,3393
2026-04-24,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,171359,171359,171359,1018
2026-04-23,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,170341,170341,170341,505
2026-04-22,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,169836,169836,169836,-195
2026-04-21,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,170031,170031,170031,-608
2026-04-20,SMM电池级碳酸锂指数,202212050001,锂电,元/吨,170639,170639,170639,3947
2026-05-18,SMM A00铝,201102250311,基本金属,元/吨,24030,24070,24050,-320
2026-05-15,SMM A00铝,201102250311,基本金属,元/吨,24350,24390,24370,-240
2026-05-14,SMM A00铝,201102250311,基本金属,元/吨,24580,24640,24610,50
2026-05-13,SMM A00铝,201102250311,基本金属,元/吨,24540,24580,24560,180
2026-05-12,SMM A00铝,201102250311,基本金属,元/吨,24370,24390,24380,-10
2026-05-11,SMM A00铝,201102250311,基本金属,元/吨,24380,24400,24390,170
2026-05-08,SMM A00铝,201102250311,基本金属,元/吨,24210,24230,24220,170
2026-05-07,SMM A00铝,201102250311,基本金属,元/吨,24040,24060,24050,-480
2026-05-06,SMM A00铝,201102250311,基本金属,元/吨,24520,24540,24530,140
2026-04-30,SMM A00铝,201102250311,基本金属,元/吨,24370,24410,24390,-90
2026-04-29,SMM A00铝,201102250311,基本金属,元/吨,24460,24500,24480,10
2026-04-28,SMM A00铝,201102250311,基本金属,元/吨,24450,24490,24470,-340
2026-04-27,SMM A00铝,201102250311,基本金属,元/吨,24790,24830,24810,60
2026-04-24,SMM A00铝,201102250311,基本金属,元/吨,24740,24760,24750,-30
2026-04-23,SMM A00铝,201102250311,基本金属,元/吨,24770,24790,24780,10
2026-04-22,SMM A00铝,201102250311,基本金属,元/吨,24760,24780,24770,100
2026-04-21,SMM A00铝,201102250311,基本金属,元/吨,24650,24690,24670,-240
2026-04-20,SMM A00铝,201102250311,基本金属,元/吨,24900,24920,24910,-250
2026-05-18,SMM 1#电解铜,201102250376,基本金属,元/吨,103860,104400,104130,-1410
2026-05-15,SMM 1#电解铜,201102250376,基本金属,元/吨,105180,105900,105540,-1840
2026-05-14,SMM 1#电解铜,201102250376,基本金属,元/吨,107020,107740,107380,-1120
2026-05-13,SMM 1#电解铜,201102250376,基本金属,元/吨,108200,108800,108500,1785
2026-05-12,SMM 1#电解铜,201102250376,基本金属,元/吨,106310,107120,106715,2400
2026-05-11,SMM 1#电解铜,201102250376,基本金属,元/吨,104050,104580,104315,1555
2026-05-08,SMM 1#电解铜,201102250376,基本金属,元/吨,102640,102880,102760,-100
2026-05-07,SMM 1#电解铜,201102250376,基本金属,元/吨,102680,103040,102860,330
2026-05-06,SMM 1#电解铜,201102250376,基本金属,元/吨,102380,102680,102530,1170
2026-04-30,SMM 1#电解铜,201102250376,基本金属,元/吨,101200,101520,101360,-215
2026-04-29,SMM 1#电解铜,201102250376,基本金属,元/吨,101370,101780,101575,-485
2026-04-28,SMM 1#电解铜,201102250376,基本金属,元/吨,101860,102260,102060,-955
2026-04-27,SMM 1#电解铜,201102250376,基本金属,元/吨,102830,103200,103015,475
2026-04-24,SMM 1#电解铜,201102250376,基本金属,元/吨,102450,102630,102540,-245
2026-04-23,SMM 1#电解铜,201102250376,基本金属,元/吨,102280,103290,102785,605
2026-04-22,SMM 1#电解铜,201102250376,基本金属,元/吨,102070,102290,102180,65
2026-04-21,SMM 1#电解铜,201102250376,基本金属,元/吨,102000,102230,102115,-770
2026-04-20,SMM 1#电解铜,201102250376,基本金属,元/吨,102720,103050,102885,875"""

# === 字体路径 (Streamlit Cloud 可能没有中文字体) ===
import platform
if platform.system() == "Darwin":
    ZH_FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
else:
    ZH_FONT_PATH = None  # Cloud: use default

# === CSS ===
st.markdown("""
<style>
    [data-testid="stToolbar"], header[data-testid="stHeader"],
    [data-testid="stDecoration"], #MainMenu, footer,
    .stDeployButton { display: none !important; }
    .metric-card {
        background: white; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 8px;
    }
    .metric-value { font-size: 26px; font-weight: 700; color: #111827; }
    .metric-label { font-size: 12px; color: #6B7280; margin-top: 2px; }
    .metric-change-up { color: #EF4444; font-size: 13px; font-weight: 600; }
    .metric-change-down { color: #10B981; font-size: 13px; font-weight: 600; }
    .main-header { font-size: 22px; font-weight: 700; color: #111827; margin-bottom: 4px; }
    .main-subtitle { font-size: 13px; color: #6B7280; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# === 数据加载 ===
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(io.StringIO(EMBEDDED_CSV))
    return df

def get_products():
    df = load_data()
    return list(df[['product_name', 'category', 'unit']].drop_duplicates().itertuples(index=False, name=None))

def get_date_range():
    df = load_data()
    return df['date'].min(), df['date'].max()

# === 图表生成 ===
def make_chart(df_filtered, product_name, unit):
    if df_filtered.empty:
        return None
    df = df_filtered.sort_values('date')
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in df['date']]
    fig, ax = plt.subplots(figsize=(10, 4))
    color = "#3B82F6"
    ax.fill_between(dates, df['low'], df['high'], alpha=0.15, color=color)
    ax.plot(dates, df['avg'], color=color, linewidth=2.2, marker='o', markersize=4,
            markerfacecolor='white', markeredgewidth=1.5, markeredgecolor=color)
    ax.set_title(f'{product_name} 价格走势', fontsize=14, pad=12)
    ax.set_ylabel(f'价格 ({unit})', fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if len(dates) >= 1:
        last_val = df['avg'].iloc[-1]
        ax.annotate(f'{last_val:,.0f}', (dates[-1], last_val),
                   textcoords="offset points", xytext=(0, 12), ha='center',
                   fontsize=9, color=color, fontweight='bold')
    plt.tight_layout()
    return fig

# === 主界面 ===
st.markdown('<div class="main-header">📊 采研智库 —— 原材料价格跟踪</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">数据来源：SMM 上海有色网 | 每日更新</div>', unsafe_allow_html=True)

df = load_data()
products = get_products()
date_range = get_date_range()

if df.empty:
    st.warning("暂无数据")
    st.stop()

# === 概览指标卡 ===
st.markdown("### 最新价格快照")
latest_date = df['date'].max()
cols = st.columns(len(products))
for i, (name, cat, unit) in enumerate(products):
    row = df[(df['product_name'] == name) & (df['date'] == latest_date)]
    if not row.empty:
        price = row['avg'].iloc[0]
        change = row['change_val'].iloc[0]
        change_class = "metric-change-up" if change and change > 0 else "metric-change-down"
        change_sign = "↑" if change and change > 0 else "↓" if change and change < 0 else ""
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{name}</div>
                <div class="metric-value">{price:,.0f}</div>
                <div class="metric-label">{unit}</div>
                <span class="{change_class}">{change_sign}{abs(change or 0):,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# === 筛选器 ===
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    selected_products = st.multiselect("选择品种", [p[0] for p in products], default=[p[0] for p in products])
with col2:
    d0 = datetime.strptime(date_range[0], "%Y-%m-%d")
    d1 = datetime.strptime(date_range[1], "%Y-%m-%d")
    date_filter = st.date_input("日期范围", value=(d0, d1), min_value=d0, max_value=d1)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Streamlit Cloud 版")

# === 图表区 ===
st.markdown("### 价格走势")
if isinstance(date_filter, tuple) and len(date_filter) == 2:
    start_d, end_d = date_filter
    start_s = start_d.strftime("%Y-%m-%d") if hasattr(start_d, 'strftime') else start_d
    end_s = end_d.strftime("%Y-%m-%d") if hasattr(end_d, 'strftime') else end_d
else:
    start_s, end_s = date_range

chart_cols = st.columns(min(len(selected_products), 2))
for i, pname in enumerate(selected_products):
    col_idx = i % 2
    with chart_cols[col_idx]:
        p_info = next((p for p in products if p[0] == pname), None)
        if p_info:
            unit = p_info[2]
            df_p = df[(df['product_name'] == pname) & (df['date'] >= start_s) & (df['date'] <= end_s)]
            fig = make_chart(df_p, pname, unit)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
        st.markdown("---")

# === 数据表格 ===
st.markdown("### 原始数据")
st.dataframe(
    df[df['product_name'].isin(selected_products)][['date', 'product_name', 'low', 'high', 'avg', 'change_val', 'unit']]
    .rename(columns={'date': '日期', 'product_name': '品种', 'low': '最低价', 'high': '最高价', 'avg': '均价', 'change_val': '涨跌', 'unit': '单位'})
    .sort_values(['日期', '品种'], ascending=[False, True]),
    use_container_width=True, hide_index=True
)
st.caption(f"数据更新: {latest_date} | 来源: SMM 上海有色网 | Streamlit Cloud 版")
