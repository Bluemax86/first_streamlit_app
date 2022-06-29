import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError

streamlit.title('My Parents New Healthy Diner')

streamlit.header('Breakfast Favorites')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥬 Kale, Spinach & Rocket Smoothie')
streamlit.text('🥚 Hard-Boiled Free-Range Egg')
streamlit.text('🥑 🍞 Avocado Toast')

streamlit.header('🍌 🍓 Build Your Own Fruit Smoothie 🥝 🍇')
my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Let's put a pick list here so the user can pick the fruit they want to include
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Avocado','Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page
streamlit.dataframe(fruits_to_show)

# Create a repeatable code block, normally called a function
def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
  # Normalize the json data into a flat table format 
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  return fruityvice_normalized

# New section to display Fruityvice API response
streamlit.header('Fruityvice Fruit Advice')
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error("please select a fruit to get information")
  else:
    returned_fruit = get_fruityvice_data(fruit_choice)
    streamlit.dataframe(returned_fruit)
except URLError as e:
  streamlit.error()
  
streamlit.header("View Our Fruit List - Add Your Favorites!")
# Snowflake related functions
def get_fruit_load_list():
  with my_cnx.cursor() as my_cur:
    my_cur.execute("SELECT * FROM FRUIT_LOAD_LIST")
    return my_cur.fetchall()
  
# Add a button to return the fruit list
if streamlit.button('Get Fruit List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  streamlit.dataframe(my_data_rows)


# Allow user to add fruit
def add_fruit_to_snowflake(new_fruit):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("INSERT INTO FRUIT_LOAD_LIST (FRUIT_NAME) VALUES('" + new_fruit + "')")
    return "Thank you for adding " + new_fruit

fruit_add = streamlit.text_input('What fruit would you like to add?')
if streamlit.button('Add New Fruit'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  added_fruit = add_fruit_to_snowflake(fruit_add)
  my_cnx.close()
  streamlit.text(added_fruit)
