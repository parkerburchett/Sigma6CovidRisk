from flask import Flask, jsonify, request, render_template, redirect, url_for
import pandas as pd
import os
# from flask_cors import CORS, cross_origin
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import figure
figure(figsize=(8, 6), dpi=80)

app = Flask(__name__,template_folder='templates')

path_to_new_pic = 'flask-backend/static/pic.png'

sns.set_style('darkgrid')
# load the data
df = pd.read_csv('flask-backend\cleaned_surveillance_data.csv') # 2.3M rows

# get validation options for the drop down. 
valid_month_year = set(df['month_year'].unique())
valid_sex = set(['Male', 'Female'])
valid_age_group = set(df['age_group'].unique())
valid_race_ethnicity_combined = set(df['race_ethnicity_combined'].unique())
valid_medcond_yn = set(['Yes', 'No'])


@app.route('/', methods=['GET','POST'])
def load_dropdowns():
    """
        Populates the dropdown with valid filtering options. 
    """
    return render_template('index.html',
    valid_month_year=valid_month_year,
    valid_sex =valid_sex,
    valid_age_group =valid_age_group,
    valid_race_ethnicity_combined=valid_race_ethnicity_combined,
    valid_medcond_yn =valid_medcond_yn
    )

# this gets the counts of people who died based on their features
def get_death_value_counts(month_year=None, sex=None, age_group=None, race_ethnicity_combined=None, medcond_yn=None):
    """
            Returns a value count of deaths based on the params passed. If a param is left empty then you don't filter based on it.
            Returns a dictionary of counts of deaths=True and deaths=False
            # super duper ugly code, but it works.
    """   
    if (month_year == '') | (month_year == 'None'):
        sub_set_condition = df['month_year'].notna() # this is just much faster than making an array of True vis np.Ones  
    else:
        sub_set_condition = df['month_year'] == month_year
    print(f'Your subset_condition only leaves {sub_set_condition.sum()} rows')

    if sex == '':
        pass
    else:
        sub_set_condition = sub_set_condition & (df['sex'] == sex)
    print(f'Your subset_condition only leaves {sub_set_condition.sum()} rows')

    if age_group == '':
        pass
    else:
        sub_set_condition = sub_set_condition & (df['age_group'] == age_group)

    print(f'Your subset_condition only leaves {sub_set_condition.sum()} rows')

    if race_ethnicity_combined == '':
        pass
    else:
        sub_set_condition = sub_set_condition & (df['race_ethnicity_combined'] == race_ethnicity_combined)

    print(f'Your subset_condition only leaves {sub_set_condition.sum()} rows')
    if medcond_yn == '':
        pass
    else:
        sub_set_condition = sub_set_condition & (df['medcond_yn'] == medcond_yn)

    print(f'Your subset_condition only leaves {sub_set_condition.sum()} rows')

    sub_set_df = df[sub_set_condition]['death_yn'].value_counts() # count the outcomes of those who met the conditions

    return sub_set_df.to_dict()


def make_simple_bar_chart(sub_group_counts):
    """
        Low tech. Make a bar chart and saves it as a .png 
    """
    fig, ax = plt.subplots()
    
    total_people = pd.Series(sub_group_counts).sum()
    
    ax.bar(sub_group_counts.keys(), sub_group_counts.values()) #

    plt.xticks(rotation=90)
    plt.title(f'Recovered vs Deaths amoung {total_people} \n who caught Covid19 based on your conditions \n that died in the USA')
    plt.ylabel("Count")
    plt.xlabel("Deceased")
    plt.savefig(path_to_new_pic)


@app.route('/picture', methods=['POST'])
def get_user_params():
    if request.method == 'POST':      
        month_year = request.form['valid_month_year']
        sex = request.form['valid_sex']
        age_group = request.form['valid_age_group']
        race_ethnicity_combined = request.form['valid_race_ethnicity_combined']
        medcond_yn = request.form['valid_medcond_yn'] # medical condition boolean.
        sub_group_counts = get_death_value_counts(month_year,sex,age_group,race_ethnicity_combined, medcond_yn)
        make_simple_bar_chart(sub_group_counts)
        return render_template('picture_viewer.html')


#  main thread of execution to start the server
if __name__ == '__main__':
    app.run(debug=True)

