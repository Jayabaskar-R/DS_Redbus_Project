import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
from PIL import Image

# MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="JabasR@2001",
    database="Red_Bus"  # Add your actual database name here 
)

# Function to fetch route names based on search input, ignoring case sensitivity
def fetch_route_names(connector, search_term):
    query = f"SELECT DISTINCT Route_Name FROM RedBus_details WHERE Route_Name LIKE '%{search_term}%' COLLATE utf8mb4_general_ci ORDER BY Route_Name"
    route_names = pd.read_sql(query, con=connector)
    return route_names['Route_Name'].tolist()

# Function to fetch data from MySQL based on selected Route_Name, price sort order, and departing time filter
def fetch_data(connector, route_name, price_sort_order, departing_time_start):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    
    # Convert time objects to string format for MySQL
    departing_time_start_str = departing_time_start.strftime("%H:%M:%S")

    # Adjust the query to filter by departing time
    query = f"""
    SELECT * FROM RedBus_details
    WHERE Route_Name = %s 
    AND Departing_time >= %s
    ORDER BY Star_rating DESC, Price {price_sort_order_sql}
    """
    df = pd.read_sql(query, con=connector, params=(route_name, departing_time_start_str))
    return df

# Function to filter data based on Star_Rating and Bus_Type
def filter_data(df, star_ratings, bus_types):
    filtered_df = df[df['Star_rating'].isin(star_ratings) & df['Bus_type'].isin(bus_types)]
    return filtered_df

# Main Streamlit app
def main():
    # Load the image (ensure the path is correct)
    logo_path = "redbus_logo.png"
    logo = Image.open(logo_path)

    # Create a layout with two columns
    col1, col2 = st.columns([1, 5])  # Adjust the width ratios of the columns

    with col1:
     # Display the logo on the left side
        st.image(logo, use_column_width=True)

    with col2:
     # Display the heading text on the right side
     st.markdown("""
         <h1 style='text-align: left; color: red;'>RedBus - Secure Online Bus Tickets Booking</h1>
         """, unsafe_allow_html=True)

    # Additional content can go below as needed


    try:
        # Create layout with columns
        col1, col2, col3 = st.columns([1, 1, 1])  # Equal width columns

        # Column 1: Route name search bar (left-aligned)
        with col1:
            search_term = st.text_input('Search for Route Name')
        
        # Column 2: Departing Time input
        with col2:
            departing_time_start = st.time_input('Departing Time Start')

        # Column 3: Price sort order
        with col3:
            price_sort_order = st.selectbox('Sort by Price', ['Low to High', 'High to Low'])

        # Fetch route names dynamically as the user types
        if search_term:
            route_names = fetch_route_names(mydb, search_term)

            if route_names:
                # Display a selectbox with the matching routes
                selected_route = st.selectbox('Select Route Name', route_names)

                if selected_route:
                    # Fetch data based on selected Route_Name, price sort order, and departing time
                    if departing_time_start:
                        data = fetch_data(mydb, selected_route, price_sort_order, departing_time_start)

                        if not data.empty:
                            # Display data table with a subheader
                            st.write(f"### Data for Route: {selected_route}")
                            st.write(data)

                            # Filter by Star_Rating (1-5 with 0.5 increments) and Bus_Type on the main page
                            star_ratings = [i/2 for i in range(2, 11)]  # Creates [1, 1.5, 2, ..., 5]
                            selected_ratings = st.multiselect('Filter by Star Rating', star_ratings)

                            bus_types = data['Bus_type'].unique().tolist()
                            selected_bus_types = st.multiselect('Filter by Bus Type', bus_types)

                            if selected_ratings and selected_bus_types:
                                filtered_data = filter_data(data, selected_ratings, selected_bus_types)
                                # Display filtered data table with a subheader
                                st.write(f"### Filtered Data for Star Rating: {selected_ratings} and Bus Type: {selected_bus_types}")
                                st.write(filtered_data)
                        else:
                            st.write(f"No data found for Route: {selected_route} with the specified filters.")
            else:
                st.write("No routes found matching your search.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if mydb.is_connected():
            mydb.close()

if __name__ == '__main__':
    main()
   

    
