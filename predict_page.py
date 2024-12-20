import streamlit as st
import pickle
import numpy as np

def load_model():
    with open('saved_steps.pkl', 'rb') as file:
        data = pickle.load(file)
    return data

data = load_model()

regressor = data['model']
le_country = data['le_country']
le_education = data['le_education']

def show_predict_page():
    st.title('Software Developer Salary Prediction')

    st.write("""### We need some information to predict the salary""")

    countries = ('United States of America', 
                 'Germany',
                 'United Kingdom of Great Britain and Northern Ireland', 
                 'Ukraine', 
                 'India',
                 'France',
                 'Canada',
                 'Brazil',
                 'Spain',
                 'Italy',
                 'Netherlands',
                 'Australia')
    
    education = ('Post grad',
                 "Master's degree",
                 "Less than a Bachelor's",
                 "Bachelor's degree")
    
    country = st.selectbox("Country", countries)
    edlevel = st.selectbox("Educational Qualification Level", education)
    experience = st.slider("Years of Experience", 0, 50, 3)

    ok = st.button("Calculate Salary")

    if ok:
        x = np.array([[country, edlevel, experience]])
        x[:, 0] = le_country.transform(x[:, 0])
        x[:, 1] = le_education.transform(x[:, 1])
        x = x.astype(float)

        salary = regressor.predict(x)
        st.subheader(f"The estimated salary is ${salary[0]:.2f}")
