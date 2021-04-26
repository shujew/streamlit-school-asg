import pandas as pd
import streamlit as st
import plotly.express as px


st.title('DS-620 Activity 6')
st.text('By Nishil Asnani and Mohammad Shuaib Jewon')

st.header('Data Processing')
st.markdown("""We have data in 2 csv files:
- hospital_general_information.csv
  - Hospital information by state
- us_populaton_by_state.csv
  - population count by state

We merge these 2 files to create a dataframe to work with
""")

@st.cache
def get_data():
    hospital_general_information_fname = 'hospital_general_information.csv'
    us_pop_by_state_fname = 'us_populaton_by_state.csv'
    
    # renaming column State to ST to match the column name
    # inside us_pop_by_state
    hospital_general_information_df = pd.read_csv(
        hospital_general_information_fname
    ).rename(columns={
        'State':'ST',
    })
    us_pop_by_state_df = pd.read_csv(us_pop_by_state_fname)

    # we want to be working with population / hospital
    # so we'll merge these 2 dataframes and filter by
    # the values we need

    map_hos_pop_data = hospital_general_information_df.groupby(
        # first group the data by 2-letter state code
        'ST'
    )[
        # calculate the count of hospitals (per state since
        # we first grouped by state)
        'Hospital Name',
    ].count().rename(columns={
        # rename Hospital Name to Hospital Count
        # since that's what the column has become
        'Hospital Name':'Hospital Count'
    }).reset_index().merge(
        # merge population dataframe into this dataframe
        # to get population data by state
        us_pop_by_state_df,
        left_on='ST', 
        right_on='ST',
    ).set_index('State')
    
    # calculate Population / Hospital Count
    map_hos_pop_data['Population / Hospital Count'] =  map_hos_pop_data['Population'] / map_hos_pop_data['Hospital Count']

    return map_hos_pop_data


df = get_data()
st.dataframe(df)

st.header('Filters')
st.text('By default, all states are included in the visualizations')

states_choice = st.multiselect(
    'State Selection', 
    df['ST'].to_list(), 
    default=df['ST'].to_list(),
    help='Select which states to use in Visualizations below'
)

st.header('Visualizations')

st.subheader('Population per Hospital')
st.text('Interactive map of USA showing Population / Hospital by State')

fig_map = px.choropleth(
    df[df['ST'].isin(states_choice)], # filter df by states selected
    locations="ST",  # column with locations
    color="Population / Hospital Count",  # column to use for heatmap color
    hover_name="ST", # column to use for title
    hover_data=['Hospital Count', 'Population'], # columns to include while hovering
    locationmode = 'USA-states', # plot as us states
)
fig_map.update_layout(
    geo_scope='usa',  # set scope of map to usa only
)
st.plotly_chart(fig_map)

st.subheader('Population v/s Hospital Count')
st.text('''Scatter plot with trendline. See below graph for correlation 
coefficient if more than one state selected''')

fig_scatter = px.scatter(
    df[df['ST'].isin(states_choice)], 
    x="Population", 
    y="Hospital Count", 
    text="ST", 
    trendline="ols"
)
st.plotly_chart(fig_scatter)

if len(states_choice) > 1:
    r2_value = px.get_trendline_results(
        fig_scatter
    ).px_fit_results.iloc[0].rsquared
    st.text(f'Correlation Coefficient (R^2 value): {r2_value:.5f}')

st.subheader('Hospital Count by State')
st.text('Bar chart showing number of Hospitals by State')

fig_bar = px.bar(
    df[df['ST'].isin(states_choice)],
    x='ST', 
    y='Hospital Count',
    text='Hospital Count',
    labels={
        'ST':'State'
    },
)
st.plotly_chart(fig_bar)

