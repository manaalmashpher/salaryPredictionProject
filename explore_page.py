import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = None

def shorten_categories(categories, cutoff):
    categorical_map = {}
    for i in range(len(categories)):
        if categories.values[i] >= cutoff:
            categorical_map[categories.index[i]] = categories.index[i]
        else:
            categorical_map[categories.index[i]] = 'Other'
    return categorical_map

def clean_experience(x):
    if x == 'More than 50 years':
        return 50
    if x == 'Less than 1 year':
        return 0.5
    return float(x)

def clean_education(x):
    if "Bachelor’s degree" in x:
        return "Bachelor's degree"
    if "Master’s degree" in x:
        return "Master's degree"
    if "Professional degree" in x:
        return "Post grad"
    return "Less than a Bachelor's"


host = os.getenv("NEONDB_HOST")
database = os.getenv("NEONDB_DATABASE")
user = os.getenv("NEONDB_USER")
password = os.getenv("NEONDB_PASSWORD")
port = os.getenv("NEONDB_PORT")
#print("Database Host:", host)
try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    print("Connection successful!")
    if conn:
        cursor = conn.cursor()
except Exception as e:
    print("Connection failed:", e)
query = "SELECT * FROM survey_results_public;"

@st.cache_data
def load_data():
    df = pd.read_sql_query(query, conn)

    df = df[["country", "edlevel", "yearscodepro", "employment", "convertedcompyearly"]]
    df = df.rename({"convertedcompyearly": "salary"}, axis = 1) 
    df = df[df["salary"].notnull()]
    df = df.dropna()
    df = df[df["employment"] == "Employed, full-time"]
    df = df.drop("employment", axis = 1)

    country_map = shorten_categories(df.country.value_counts(), 400)
    df['country'] = df['country'].map(country_map)
    df = df[df['salary'] <= 250000]
    df = df[df['salary'] >= 10000]
    df = df[df['country'] != 'Other']

    df['yearscodepro'] = df['yearscodepro'].apply(clean_experience)
    df['edlevel'] = df['edlevel'].apply(clean_education)
    return df

df = load_data()

def show_explore_page():
    st.title("Explore Recent Trends in Salary of Software Engineers")

    st.write("""### Stack Overflow Developer Salaries""")

    data = df["country"].value_counts()

    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels = data.index, autopct = "%1.1f%%", shadow = True, startangle = 90)
    ax1.axis("equal") 

    st.write("""#### Survey data from different countries""")

    st.pyplot(fig1)

    st.write("""#### Mean Salary based on Country""")

    data = df.groupby(["country"])["salary"].mean().sort_values(ascending=True)
    st.bar_chart(data)

    st.write("""#### Mean Salary based on Experience""")

    data = df.groupby(["yearscodepro"])["salary"].mean().sort_values(ascending=True)
    st.line_chart(data)