import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# load dataset
bike_sharing = pd.read_csv("dashboard/all_data.csv")
bike_sharing['date'] = pd.to_datetime(bike_sharing['date'])

# set title
st.set_page_config(page_title="Bike-Sharing Dashboard",
                   page_icon="bar_chart:",
                   layout="wide")


# monthly data
def create_monthly_data(bike_sharing):
    monthly_data = bike_sharing.resample(rule='M', on='date').agg({
        "nonmember_hourly": "sum",
        "member_hourly": "sum",
        "total_count_hourly": "sum"
    })
    monthly_data.index = monthly_data.index.strftime('%b-%y')
    monthly_data = monthly_data.reset_index()
    monthly_data.rename(columns={
        "date": "date_day",
        "total_count_hourly": "total_rides",
        "nonmember_hourly": "nonmember_rides",
        "member_hourly": "member_rides"
    }, inplace=True)
    
    return monthly_data
# monthly data

# seasonly total
def create_seasonly_total(bike_sharing):
    seasonly_total = bike_sharing.groupby("season_daily").agg({
        "total_count_hourly": "sum"
    })
    seasonly_total = seasonly_total.reset_index()
    seasonly_total.rename(columns={
        "total_count_hourly": "total_rides",
    }, inplace=True)

    seasonly_total['season_daily'] = pd.Categorical(seasonly_total['season_daily'],
                                             categories=['Spring', 'Summer', 'Fall', 'Winter'])  
    seasonly_total = seasonly_total.sort_values('season_daily')

    return seasonly_total
# seasonly total

# seasonly data
def create_seasonly_data(bike_sharing):
    seasonly_data = bike_sharing.groupby("season_daily").agg({
        "nonmember_hourly": "sum",
        "member_hourly": "sum",
        "total_count_hourly": "sum"
    })
    seasonly_data = seasonly_data.reset_index()
    seasonly_data.rename(columns={
        "nonmember_hourly": "nonmember_rides",
        "member_hourly": "member_rides",
        "total_count_hourly": "total_rides"
    }, inplace=True)
    
    seasonly_data = pd.melt(seasonly_data,
                                      id_vars=['season_daily'],
                                      value_vars=['nonmember_rides', 'member_rides'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')

    seasonly_data = seasonly_data.sort_values('season_daily')
    
    return seasonly_data
# seasonly data

# weekday data
def create_weekday_data(bike_sharing):
    weekday_data = bike_sharing.groupby("weekday_daily").agg({
        "nonmember_hourly": "sum",
        "member_hourly": "sum",
        "total_count_hourly": "sum"
    }).reset_index()

    weekday_data.rename(columns={
        "nonmember_hourly": "nonmember_rides",
        "member_hourly": "member_rides",
        "total_count_hourly": "total_rides"
    }, inplace=True)

    weekday_data = pd.melt(weekday_data,
                           id_vars=['weekday_daily'],
                           value_vars=['nonmember_rides', 'member_rides'],
                           var_name='type_of_rides',
                           value_name='count_rides')

    weekday_data['weekday_daily'] = pd.Categorical(weekday_data['weekday_daily'],
                                                   categories=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

    weekday_data = weekday_data.sort_values('weekday_daily')

    return weekday_data
# weekday data

# filter date

min_date = bike_sharing["date"].min()
max_date = bike_sharing["date"].max()

# sidebar
with st.sidebar:
    # add capital bikeshare logo
    st.image("dashboard/bike.jpg")

    # get start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label="Date Filter", min_value=min_date.date(),
        max_value=max_date.date(),
        value=[min_date.date(), max_date.date()]
    )

# sidebar

# connect filter & main_df

main_df = bike_sharing[
    (bike_sharing["date"] >= pd.Timestamp(start_date)) &
    (bike_sharing["date"] <= pd.Timestamp(end_date))
]

monthly_data = create_monthly_data(main_df)
seasonly_total = create_seasonly_total(main_df)
seasonly_data = create_seasonly_data(main_df)
weekday_data = create_weekday_data(main_df)

# mainpage
st.title("Bike-Sharing Dashboard :bar_chart:")
st.markdown("##")

col1, col2, col3 = st.columns(3)

with col1:
    total_all_rides = main_df['total_count_hourly'].sum()
    st.metric("Total Rides", value=total_all_rides)
with col2:
    total_nonmember_hourly_rides = main_df['nonmember_hourly'].sum()
    st.metric("Total Non Member Rides", value=total_nonmember_hourly_rides)
with col3:
    total_member_hourly_rides = main_df['member_hourly'].sum()
    st.metric("Total Member Rides", value=total_member_hourly_rides)

st.markdown("---")
# mainpage


# CHART1
fig = px.line(monthly_data,
              x='date_day',
              y=['nonmember_rides', 'member_rides', 'total_rides'],
              color_discrete_sequence=["blue", "red", "purple"],
              markers=True,
              title="Monthly Count of Bikeshare Rides").update_layout(xaxis_title='', yaxis_title='Total Rides')

st.plotly_chart(fig, use_container_width=True)
# CHART1

# CHART2 3
fig1 = px.bar(seasonly_total,
              x='season_daily',
              y='total_rides',
            #   color='type_of_rides',
              color_discrete_sequence=["orange"],
              title='Count of bikeshare rides by season').update_layout(xaxis_title='Season', yaxis_title='Total Rides')

fig2 = px.pie(seasonly_data,
              names='type_of_rides',
              values='count_rides',
              color='type_of_rides',
              color_discrete_sequence=["red", "yellow"],
              title='Count of bikeshare rides by customer category',
              hole=0.4,
              labels={'type_of_rides': 'Ride Type', 'count_rides': 'Total Rides'})

fig2.update_layout(showlegend=True, legend=dict(title='Customer Category'))

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig1, use_container_width=True)
right_column.plotly_chart(fig2, use_container_width=True)
# CHART2 3

# CHART4
fig4 = px.bar(weekday_data,
              x='weekday_daily',
              y='count_rides',
              color='type_of_rides',
              barmode='group',
              color_discrete_sequence=["blue", "green"],
              title='Count of bikeshare rides by weekday').update_layout(xaxis_title='Day', yaxis_title='Total Rides')

st.plotly_chart(fig4, use_container_width=True)
# CHART4

st.caption('Copyright ©, created by Javi Akbar Prabowo')
