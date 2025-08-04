import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib as plt
import requests
import json
import os
import streamlit_option_menu
from streamlit_option_menu import option_menu


# establishing sql connection
from sqlalchemy import create_engine 
engine=create_engine('postgresql://neondb_owner:npg_6GTOUeWbmq3s@ep-late-bonus-a1sfwhzs-pooler.ap-southeast-1.aws.neon.tech/neondb')
query1='''select * from agg_ins'''
agg_ins=pd.read_sql(query1,engine)

query2='''select * from agg_trans'''
agg_trans=pd.read_sql(query2,engine)

query3='select * from agg_user'
agg_user=pd.read_sql(query3,engine)

query4='select * from map_ins'
map_ins=pd.read_sql(query4,engine)

query5='select * from map_trans'
map_trans=pd.read_sql(query5,engine)

query6='select * from map_user'
map_user=pd.read_sql(query6,engine)

query7='select * from top_ins'
top_ins=pd.read_sql(query7,engine)

query8='select * from top_trans'
top_trans=pd.read_sql(query8,engine)

query9='select * from top_user'
top_user=pd.read_sql(query9,engine)

query10='select * from grouped_df1'
grouped_df1=pd.read_sql(query10,engine)


#streamlit part

st.set_page_config(layout="wide")

st.title("PHONEPE TRANSACTION INSIGHTS")
st.write("**PHONEPE ANALYSIS**")
selected =option_menu(menu_title=None,
                   options=['Geolocation view of transaction','Analysis','Insights'],
                   orientation='horizontal',
                   menu_icon="cast",
                   default_index=0,)
if selected=='Geolocation view of transaction':
    
    df=grouped_df1[['standard_state','total_count']]
    
 

# Step 5: Plot the choropleth map
    fig = px.choropleth(
        df,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey="properties.ST_NM",
        locations="standard_state",
        color="total_count",
        color_continuous_scale='Reds',
        title= 'Phonepe transaction by state',
   
    )

    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

#TOP PAYMENT METHOD MOSTLY USED
    st.markdown("TOP PAYMENT METHOD")
    col1,col2=st.columns(2)
    with col1:
        year=st.selectbox( '',options=[2018,2019,2020,2021,2022,2023,2024],placeholder='Year',label_visibility="collapsed",key='year')
    with col2:
        quater=st.selectbox( '',options=[1,2,3,4],placeholder='Quater',label_visibility="collapsed",key='quater')
    query1 =f"""
        SELECT 
        payment_name, 
        SUM(payment_amount) AS total_amount, 
        SUM(payment_count) AS total_payment
    FROM agg_trans
    where "Year"=%s and "Quater"= %s
    GROUP BY payment_name
    ORDER BY payment_name;
    """
    payment_name= pd.read_sql(query1, engine, params=(str(year), str(quater)))

    fig=px.bar(payment_name,
            title='top payment method',
            x='payment_name',
            y='total_payment',
            orientation='v',
            color='total_amount',
            color_continuous_scale='plasma')
    st.plotly_chart(fig,use_container_width=False)
# state with highest transactions
    st.markdown('states with highest transactions') 

    col1,col2,col3=st.columns(3)

    with  col1:
        state = st.selectbox("Select State", agg_trans['State'].unique())
    with col2:
        year = st.selectbox("Select Year", sorted(agg_trans['Year'].unique()))
    with col3:
        quater = st.selectbox("Select Quarter", sorted(agg_trans['Quater'].unique()))

# 4. Main query using user inputs
    query2 = """
        SELECT 
            "State", "Year", "Quater", 
            SUM("payment_count") AS total_count,
            SUM("payment_amount") AS total_amount
        FROM agg_trans
        WHERE "Year" = %s AND "Quater" = %s AND "State" = %s
        GROUP BY "State", "Quater", "Year"
        ORDER BY "State","Quater", "Year"
    """
    params = (str(year), str(quater), state)


    top_states = pd.read_sql(query2, engine,params=params)
    fig = px.bar(
            top_states,
            x="State",
            y="total_count",
            color="total_amount",
            title="top state",
            color_continuous_scale='plasma',
            labels={"total_count": "Transaction count"},
            height=600
        )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    # quater which has highest payment 
    query='''with quaterly_total as (
    select "State", "Year", "Quater", sum(payment_amount) as total_payment
    from agg_trans
    group by "State", "Year", "Quater"
    ),
    ranked_quater as (
    select
        "State",
        "Year",
        "Quater",
        total_payment, 
        row_number() over (partition by "Year" order by total_payment desc) as rn
    from quaterly_total
    )
    select "State", "Year", "Quater", total_payment
    from ranked_quater
    where rn = 1;;'''
    quater=pd.read_sql(query,engine)
    fig=px.line(quater,
                x="total_payment",
                y="Quater",
                color="State",
                title="Quater with highest payment")
    st.plotly_chart(fig,use_container_width=True)

#ANALYSIS
elif selected == 'Analysis':
    st.subheader("Business case studies")
    option_menu=st.selectbox(" ",options=["Insurance analysis", "Transaction analysis","Device dominance","Fraud detection"])
    if option_menu== "Insurance analysis":
        col1,col2=st.columns(2)
        with col1:
        #Quartely growth of the Tamilnadu in insurance
         st.subheader("Total insurance transaction by state")
         query12 = """
                SELECT "State", SUM("Transaction_amount") AS total_Amount
                FROM agg_ins
                WHERE "Year"::integer = 2024
                GROUP BY "State"
                ORDER BY total_Amount DESC"""
        state_ins=pd.read_sql(query12,engine)
        st.bar_chart(state_ins.set_index("State"))
        col1,col2=st.columns(2)
        with col1:
            #Yealy transaction growth
            st.subheader("Yearly transaction growth")
            query13 = '''
                    SELECT "Year", SUM("Transaction_count") AS total_Transactions
                    FROM agg_ins
                    GROUP BY "Year"
                    ORDER BY "Year"'''
            yearly_growth=pd.read_sql(query13,engine)
            st.line_chart(yearly_growth.set_index("Year"))
            with col2:
                st.write(yearly_growth)
        col1,col2=st.columns(2)
        with col1:
            #Top districts in insurance transactions
            st.subheader("Top districts with insurance transactions")
            query14 = """
                    SELECT "District", SUM("Transaction_amount") AS total_Amount
                    FROM map_ins
                    GROUP BY "District"
                    ORDER BY total_Amount DESC
                    LIMIT 10"""
            top_district =pd.read_sql(query14,engine)
            
            st.bar_chart(top_district.set_index("District"),use_container_width=True)
            with col2:
                st.write(top_district)
        col1,col2=st.columns(2)
        with col1:
            #nation wide yearly growth
            st.subheader("Nations yearly growth")
            query = """
                    SELECT "Year", SUM("Transaction_count") AS total_Transactions
                    FROM agg_ins
                    GROUP BY "Year"
                    ORDER BY "Year"
                    """
            nation_year = pd.read_sql(query,engine)
            
            st.line_chart(nation_year.set_index("Year"),use_container_width=True)
            with col2:
                st.write(nation_year)
    elif option_menu=="Transaction analysis":
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Top districts")
            query15 = """
                    SELECT "State", "District", 
                    SUM("Transaction_amount") AS district_total
                    FROM map_trans
                    WHERE "State" IN (
                    SELECT "State" FROM map_trans
                    GROUP BY "State"
                    ORDER BY SUM("Transaction_amount") DESC
                    LIMIT 5)
                    GROUP BY "State", "District"
                    ORDER BY "State", district_total DESC;"""
        top_dist_trans= pd.read_sql(query15, engine)
        fig5 = px.bar(top_dist_trans, x='District', y='district_total', color='State',
              title='Top Districts in High-Performing States',
              labels={'District_Total': 'Transaction Amount (₹)'},
              barmode='group')
        st.plotly_chart(fig5)
        col1,col2=st.columns(2)
        with col1:
            st.markdown("Total transactions by state")
            query16 = """
                    SELECT "State", 
                    SUM("Transaction_count") AS total_transactions,
                    SUM("Transaction_amount") AS total_amount
                    FROM map_trans
                    GROUP BY "State"
                    ORDER BY total_amount DESC;"""
        top_trans_state = pd.read_sql(query16, engine)
        fig4 = px.bar(top_trans_state, x='State', y='total_amount', 
              title='Total Transaction Amount by State',
              labels={'total_amount': 'transaction amount (₹)'},
              text_auto='.2s')
        st.plotly_chart(fig4)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Yearly transaction trend")
            query17 = """
                    SELECT "State", "Year", 
                    SUM("Transaction_count") AS transactions
                    FROM map_trans
                    GROUP BY "State", "Year"
                    HAVING "State" IN (
                    SELECT "State" FROM map_trans
                    GROUP BY "State"
                    ORDER BY SUM("Transaction_amount") DESC
                    LIMIT 5)
                    ORDER BY "State", "Year";"""
            year_trans = pd.read_sql(query17, engine)
            fig2 = px.line(year_trans, x='Year', y='transactions', color='State',
               markers=True,
               title='Yearly Transaction Trends for Top 5 States')
            st.plotly_chart(fig2)
            with col2:
                st.write(year_trans)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Transaction heatmap")
            
            query18 = """
                        SELECT "State", "Year", 
                        SUM("Transaction_amount") AS total_amount
                        FROM map_trans
                        GROUP BY "State", "Year";"""
            heatmap_trans = pd.read_sql(query18, engine)
            pivot_df = heatmap_trans.pivot(index='State', columns='Year', values="total_amount")
            fig4 = px.imshow(pivot_df,
                 labels=dict(x="Year", y="State", color="total amount (₹)"),
                 title='Heatmap of Transaction Amounts by State and Year')
            st.plotly_chart(fig4)
        
    elif option_menu=="Device dominance":
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Geographical view of registered user")
            year1=st.selectbox("select the year",map_user['Year'].unique())
            query19='''select "State", sum(registered_user) as reg_user
                        from map_user
                        where "Year"=%s
                        group by "State";
            '''
            df1=pd.read_sql(query19,engine,params=(year1,))
            query30='''select * from df1;
                        '''
            df2=pd.read_sql(query30,engine)

            fig = px.choropleth(
                            df2,
                            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                            featureidkey='properties.ST_NM',
                            locations='State',
                            color="reg_user",
                            title=f'PhonePe India Transactions - {year1}',
                            color_continuous_scale='Rainbow',
                            width=900, height=800, 
                            hover_name='State')
            fig.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig)
            with col2:
                year2 = st.selectbox("select the year", map_user['Year'].unique(), key="year_selectbox_2")
                query31='''select "State", sum(registered_user) as reg_user
                        from map_user
                        where "Year"=%s
                        group by "State";
                    '''
                df3=pd.read_sql(query31,engine,params=(year2,))

                st.write(df3)
        col1,col2=st.columns(2)
# Bar chart-Total users - State
        with col1:
            st.subheader("Top brand")
            query20 = """
                    SELECT brand,
                    SUM(user_count) AS total_users
                    FROM agg_user
                    GROUP BY brand
                    ORDER BY total_users DESC
                    LIMIT 10;"""
            top_brand = pd.read_sql(query20, engine)
            fig1 = px.bar(top_brand, x='brand', y='total_users', text_auto='.2s',
              title='Top 10 Brands by Total User Count (All India)')
            st.plotly_chart(fig1)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Brand dominance over year")
            query21 = """
                    SELECT "Year", "Quater", "State", brand,
                    SUM(user_count) AS total_users,
                    ROUND((AVG(user_percentage) * 100)::numeric, 2) AS avg_percentage FROM agg_user
                    WHERE brand IN (
                    SELECT brand FROM agg_user
                    GROUP BY brand
                    ORDER BY SUM(user_count) DESC
                    LIMIT 5)
                    GROUP BY "Year", "Quater", "State", brand
                    ORDER BY "Year", "Quater";"""
        brand_share = pd.read_sql(query21, engine)
        brand_share['YearQuarter'] = brand_share['Year'].astype(str) + ' Q' + brand_share['Quater'].astype(str)
        fig3 = px.line(brand_share, x='YearQuarter', y='avg_percentage', color='brand',
               title='Top 5 Brands - Average Share Over Time by State',
               markers=True)
        st.plotly_chart(fig3)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Most dominant device per state")
            query22='''
                        WITH filtered AS (
                        SELECT "State", brand, user_percentage
                        FROM agg_user
                        WHERE "Year"::integer = 2022 AND "Quater"::integer = 1
                        ),
                        ranked AS (
                        SELECT *,
                        RANK() OVER(PARTITION BY "State" ORDER BY user_percentage DESC) AS rnk
                        FROM filtered)
                        SELECT "State", brand, user_percentage
                        FROM ranked
                        WHERE rnk = 1
                        ORDER BY "State";'''

            dominant_device=pd.read_sql(query22,engine)
            fig_dominant_device = px.bar(dominant_device,
                             x='State', 
                             y='user_percentage', 
                             color='brand',       
                             title='Dominant Device by State',
                             hover_data=['user_percentage']) 
            st.plotly_chart(fig_dominant_device,use_container_width=True)
            col1,col2=st.columns(2)
            with col1:
                    st.subheader("Brand presence across states")
                    query23 = """
                        SELECT "State", brand,
                        ROUND((AVG(user_percentage) * 100)::numeric, 2) AS avg_share
                        FROM agg_user
                        GROUP BY "State", brand;"""
                    brand_presence = pd.read_sql(query23, engine)
                    pivot_df = brand_presence.pivot(index='State', columns='brand', values='avg_share').fillna(0)
                    fig5 = px.imshow(pivot_df,
                    labels=dict(x="brand", y="State", color="Avg Share (%)"),
                    title="Heatmap of Brand Share Across States")
                    st.plotly_chart(fig5)
                    with col2:
                        st.write(brand_presence)
    elif option_menu=='Fraud detection':
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Unusual transactions")
            query24='''SELECT "State", "Year", "Quater", 
                    MAX("Transaction_amount") AS max_txn, 
                    MIN("Transaction_amount") AS min_txn,
                    AVG("Transaction_amount") AS avg_txn
                    FROM map_trans
                    GROUP BY "State", "Year", "Quater"
                    ORDER BY max_txn DESC;'''
            abnormal_tran=pd.read_sql(query24,engine)
            fig1 = px.bar(abnormal_tran, x='State', y='max_txn', color='Year',
              title='States with Maximum Transaction Amounts',
              labels={'max_txn': 'Max Transaction (₹)'})
            st.plotly_chart(fig1)
            with col2:
                st.write(abnormal_tran)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Low value with high transaction count")
            st.write("this indicates micro fraud or spamming transactions")
            query25='''SELECT "State", "Year", "Quater", txn_count, txn_value, avg_value
                    FROM (
                    SELECT "State", "Year", "Quater",
                    SUM("Transaction_count") AS txn_count,
                    SUM("Transaction_amount") AS txn_value,
                    ROUND((SUM("Transaction_amount") / NULLIF(SUM("Transaction_count"), 0))::NUMERIC, 2) AS avg_value
                    FROM map_trans
                    GROUP BY "State", "Year", "Quater") AS subquery
                    
                    ORDER BY avg_value;'''
            micro_trans=pd.read_sql(query25,engine)
            fig3 = px.scatter(micro_trans, x='txn_count', y='avg_value', color='State',
                  title='Low Average Transaction Value vs Count',
                  size='txn_count', hover_name='State')
            st.plotly_chart(fig3)
            with col2:
                st.write(micro_trans)

        col1,col2=st.columns(2)
        with col1:
            st.subheader("Districts with high count but low registered users")
            query26='''SELECT m."State", m."District", m."Year", m."Quater", m."Transaction_count", u."registered_user"
                        FROM map_trans m
                        JOIN map_user u
                        ON m."State" = u."State" AND m."District" = u."District" AND m."Year" = u."Year" AND m."Quater" = u."Quater" 
                        WHERE u."registered_user" < 1000 AND m."Transaction_count" > 50000
                        ORDER BY m."Transaction_count" DESC;'''
            low_user_high_trans=pd.read_sql(query26,engine)
            fig5 = px.bar(low_user_high_trans, x='District', y='Transaction_count', color='State',
              title='Suspicious Districts: High Txns, Low Users',
              hover_data=['registered_user'])
            st.plotly_chart(fig5)
            st.write(low_user_high_trans)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Sudden transaction spike")
            query27='''WITH q_change AS (
                        SELECT "State", "Year", "Quater",
                        SUM("Transaction_amount") AS total_txn
                        FROM map_trans
                        GROUP BY "State", "Year", "Quater"),
                        growth_calc AS (
                        SELECT a."State", a."Year", a."Quater",
                        a.total_txn AS current,
                        b.total_txn AS previous,
                        ROUND((100.0 * (a.total_txn - b.total_txn) / NULLIF(b.total_txn, 0))::NUMERIC, 2) AS growth_rate
                        FROM q_change a
                        JOIN q_change b
                        ON a."State" = b."State"
                        AND a."Year" = b."Year"
                        AND a."Quater" = b."Quater" + 1)
                        SELECT * FROM growth_calc
                        WHERE growth_rate > 200         
                        ORDER BY growth_rate DESC;'''
            trans_spike=pd.read_sql(query27,engine)
            
            fig2 = px.bar(trans_spike, x='State', y='growth_rate', color='Quater',
              title='States with Sudden Transaction Spikes',
              labels={'growth_rate': 'Growth Rate (%)'})
            st.plotly_chart(fig2)
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Transaction count deviations")
            st.write("Detect unusually high counts compared to state average")
            query28='''WITH state_avg AS (
                    SELECT "State", AVG("Transaction_count") AS avg_count
                    FROM map_trans
                    GROUP BY "State"
                    ),
                    anomalies AS (
                    SELECT m."State", m."Year", m."Quater", m."Transaction_count", s.avg_count
                    FROM map_trans m
                    JOIN state_avg s ON m."State" = s."State" -- Corrected: m."State" and s."State"
                    WHERE m."Transaction_count" > 2 * s.avg_count)
                    SELECT * FROM anomalies ORDER BY "Transaction_count" DESC;'''
            trans_dev=pd.read_sql(query28,engine)
            fig4 = px.bar(trans_dev, x='State', y='Transaction_count', color='Year',
              title='Transaction Count Anomalies by State',
              labels={'Transaction_count': 'Txn Count'})
            st.plotly_chart(fig4)
            with col2:
              st.write(trans_dev)
elif selected=="Insights":
    tab1,tab2,tab3,tab4=st.tabs(["Transaction insights","Insurance insights","User device insights","Fraud detectant insights"])
    with tab1:
        st.subheader("Potential Insights")
        st.write("The queries analysis provide the comprehensive view of payment trends at both a nation wide and region wide, allowing" \
        " for identification of popukar payment method,high performing areas, temporal shifts in digital transaction")
        st.write("Telgana is the top state with highest transaction amount")
        st.write("The transactions can be increased by marketing and tailoring campaigns and improving the connectivity")
        st.write("The most commonly used payment method in the last year and quater is the Merchant payment/ The other payment" \
        " has shown slight decline in the recent year.")
    with tab2:
        st.subheader("Insurance insights")
        st.write("The dashboard provides a multi-faceted view of transaction and insurance trends. " \
        " For insurance, it highlights that total insurance transaction amounts in 2024 are unevenly distributed across states, " \
        " with specific districts emerging as high-value hubs.") 
        st.write("Furthermore, a clear national and state-level upward trend "
        " in transaction counts over the years suggests growing digital adoption in the insurance sector. Separately, "
        " in general transactions, the analysis pinpoints top-performing states and their leading districts, " \
        "showing how transaction amounts are concentrated geographically.") 
        st.write("The yearly transaction trends for these " \
        "top states indicate varying growth trajectories, while a heatmap offers a quick visual of state-wise " \
        "transaction volume evolution over time, allowing for rapid identification of high-activity periods and regions.")
    with tab3:
        st.subheader("Device dominance")
        st.write("The analysis reveals a clear hierarchy among device brands in terms of total user count across India," \
        " with the top 10 brands collectively holding significant sway.") 
        st.write("Examining the top 5 brands over time shows " \
        " varying degrees of market share stability and growth across different states and quarters, indicating dynamic " \
        " competition or shifting user preferences.") 
        st.write("Furthermore, the data pinpoints the single most dominant device " \
        " brand within each state for a specific period, highlighting regional preferences or market penetration strategies." \
        " Finally, a heatmap effectively visualizes the average market share of various brands across different states," \
        " allowing for quick identification of a brand's strongholds and weaker areas nationally.")
    with tab4:
        st.subheader("Fraud detectant")
        st.write("The fraud detection module built using the PhonePe transaction dataset uncovers several key insights " \
        " into potentially suspicious behaviors across states and districts.") 
        st.write("Firstly, states with unusually high maximum " \
        " transaction amounts could either be genuine economic hubs or indicate possible laundering or high-value fraud."\
        " Secondly, regions with extremely low average transaction values but very high transaction counts point toward " \
        " micro-transactions, often a sign of spamming or bot-driven activity. Thirdly, districts that show high " \
        " transaction volumes despite having very few registered users may reflect account farming or device-level " \
        " automation, both of which are red flags for fraudulent behavior.") 
        st.write("Additionally, the detection of sudden " \
        " spikes in transaction growth (over 200% between quarters) highlights irregular usage patterns, possibly linked " \
        " to promotional abuse or manipulation. Finally, by comparing transaction counts to state-level averages, the " \
        " system reveals anomalies where activity far exceeds the norm, suggesting intensified or suspicious user behavior. " \
        " Together, these insights help identify regions and behaviors that merit closer inspection for fraud prevention.")


    
        




            

            






            








        
















    

    
