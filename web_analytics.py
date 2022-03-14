#!/usr/bin/env python
# coding: utf-8

# In[1]:
import collections
import pandas as pd
import random
import time
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from plotly import graph_objects as go


# In[2]:

# Here are some code to get you started, ^V^

# Creates all dictionary for evert row of excel entry passed, creates the counts of each pages visited in the row as occurences and
# all the pages as clickstream
def turn_line_of_file_into_dict(line_of_file):
    line_of_file = line_of_file.rstrip("\n")
    data_items = line_of_file.split(",")
    clickstream = data_items[2:]
    occurences = dict((x, clickstream.count(x)) for x in set(clickstream))

    return {'source': data_items[0],
            'platform': data_items[1],
            'occurences': [occurences],
            'clickstream': [data_items[2:]],
            }


# Get all the necessray counts for bouce/purchase_success/purchase_started
def get_counts(index,index_source, total):
    listl=[]
    pages_visited=0
    bounce=0
    purchase_success=0
    purchase_started_not_purchased=0
    purchase_started=0

    occurences  = index_source['occurences']
    for occurence in occurences:
        # Purchase Rate is number of successful purchases per total visits
        if "purchase_success" in occurence.keys():
            purchase_success += 1

        # Purchase Started but not completed counts
        if "purchase_start" in occurence.keys() and "purchase_success" not in occurence.keys():
            purchase_started_not_purchased += 1

        # Just Purchase Started counts
        if "purchase_start" in occurence.keys():
            purchase_started += 1

       # Bounce Rate is calculated bassed on single visit per total visit
        page_depth = sum(occurence.values())
        pages_visited+=page_depth
        if page_depth == 1:
            bounce += 1

    # List appends all the values to store and display in the DF
    listl.append(index)
    listl.append(total)
    listl.append(pages_visited)
    listl.append(bounce)
    listl.append((bounce/total)*100)
    listl.append(purchase_success)
    listl.append(total-purchase_success)
    listl.append((purchase_success/total)*100)
    listl.append(purchase_started_not_purchased)
    listl.append(purchase_started)
    return listl

# Get all the necessray counts for blog1 vs blog2 comparison
def get_counts_blogs(index,index_source,value):
    listl=[]
    pages_visited = 0
    blog_1_only_visited=0
    blog_2_only_visited=0
    bounce_blog_1_landing=0
    bounce_blog_2_landing=0
    purchase_success_blog_1=0
    purchase_success_blog_2=0
    purchase_success_blog_1_landing=0
    purchase_success_blog_2_landing=0
    bounce_blog_1=0
    bounce_blog_2=0
    total = len(index_source)

    # exit=0

    clickstreams  = index_source['clickstream']
    landing_page = {"blog_1":0,"blog_2":0,"contact_us":0,"home":0,
                    "special_advert_deal":0,"pricing":0,"purchase_start":0,"purchase_enter_address":0,"purchase_success":0}

    # Calculates the information for creating Funnel
    # Calculates Landing Page and then sorts and takes the largest value
    landing_pge = [clickstream[0] for clickstream in clickstreams]
    landing = collections.Counter(landing_pge)
    sorted_landing = sorted(landing.items(), key=lambda kv: kv[1],reverse=True)
    click_stream_landing = [clickstream for clickstream in clickstreams if clickstream[0] == sorted_landing[0][0]]

    # Calculates First Iteration Values by generating next higrst visits from the top visit of landing page
    first_pge = [clickstream[1] for clickstream in click_stream_landing if len(clickstream)>1]
    sorted_first = sorted(collections.Counter(first_pge).items(), key=lambda kv: kv[1],reverse=True)

    # Calculates Second Iteration Values by generating next higrst visits from the top visit of landing page and top first page
    second_pge = [clickstream[2] for clickstream in click_stream_landing
                   if len(clickstream)>2 and clickstream[1] == sorted_first[0][0] ]
    sorted_second = sorted(collections.Counter(second_pge).items(), key=lambda kv: kv[1],reverse=True)

    # Keeps iterating till 5th one...
    third_pge = [clickstream[3] for clickstream in click_stream_landing
                   if len(clickstream) > 3 and clickstream[1] == sorted_first[0][0]  and
                   clickstream[2] == sorted_second[0][0] ]
    sorted_third = sorted(collections.Counter(third_pge).items(), key=lambda kv: kv[1], reverse=True)
    third_page_clickstream = [clickstream for clickstream in click_stream_landing
                  if len(clickstream)>3 and clickstream[1] == sorted_first[0][0] and
                  clickstream[2] == sorted_second[0][0] and clickstream[3] == sorted_third[0][0]]
    fourth_pge = [clickstream[4] for clickstream in third_page_clickstream
                  if len(clickstream) > 4 ]
    sorted_fourth = sorted(collections.Counter(fourth_pge).items(), key=lambda kv: kv[1], reverse=True)

    fifth_pge = [clickstream[5] for clickstream in third_page_clickstream
                   if len(clickstream) > 5 and clickstream[4] == sorted_fourth[0][0]]
    sorted_fifth = sorted(collections.Counter(fifth_pge).items(), key=lambda kv: kv[1], reverse=True)


    counter_1=0
    counter_2=0
    counter_3=0
    counter_4=0
    
    # Generates the values for conversion rate when blog1 or blog2 is landing page vs blog1 only visited and blog2 only visited
    for clickstream in clickstreams:
        landing_page[clickstream[0]] = landing_page.get(clickstream[0]) + 1
        if "blog_1" == clickstream[0]:
            counter_1+=1
            collections.Counter(clickstream).values()
            if len(clickstream) == 1:
                bounce_blog_1_landing += 1
            if "purchase_success" in clickstream:
                purchase_success_blog_1_landing += 1
        if "blog_2" == clickstream[0]:
            counter_2 += 1
            if len(clickstream) == 1:
                bounce_blog_2_landing += 1
            if "purchase_success" in clickstream:
                purchase_success_blog_2_landing += 1
        if "blog_1" in clickstream and "blog_2" not in clickstream:
            counter_3 += 1
            if "purchase_success" in clickstream:
                purchase_success_blog_1 += 1
            if len(clickstream) == 1:
                bounce_blog_1 += 1
            blog_1_only_visited+=1
        if "blog_2" in clickstream and "blog_1" not in clickstream:
            counter_4 += 1
            if "purchase_success" in clickstream:
                purchase_success_blog_2 += 1
            if len(clickstream) == 1:
                bounce_blog_2 += 1
            blog_2_only_visited+=1
        page_depth = len(clickstream)
        pages_visited += page_depth



    page_iteration={}
    page_iteration[0]=sorted_landing
    page_iteration[1]=sorted_first
    page_iteration[2]=sorted_second
    page_iteration[3]=sorted_third
    page_iteration[4]=sorted_fourth
    page_iteration[5]=sorted_fifth

    
    # Generates a DF to fill the misisng values with 0 handles excetion and missing values
    sorted_landing_df = pd.DataFrame(sorted_landing)
    sorted_landing_df = sorted_landing_df.reindex(list(range(0, 7)), fill_value=0)
    sorted_first_df = pd.DataFrame(sorted_first)
    sorted_first_df = sorted_first_df.reindex(list(range(0, 7)), fill_value=0)
    sorted_second_df = pd.DataFrame(sorted_second)
    sorted_second_df = sorted_second_df.reindex(list(range(0, 7)), fill_value=0)
    sorted_third_df = pd.DataFrame(sorted_third)
    sorted_third_df = sorted_third_df.reindex(list(range(0, 7)), fill_value=0)
    sorted_fourth_df = pd.DataFrame(sorted_fourth)
    sorted_fourth_df = sorted_fourth_df.reindex(list(range(0, 7)), fill_value=0)
    sorted_fifth_df = pd.DataFrame(sorted_fifth)
    sorted_fifth_df = sorted_fifth_df.reindex(list(range(0, 7)), fill_value=0)

    # Generates Funnel Chart
    fig = go.Figure()

    fig.update_layout(
        title = 'Funnel ClickStream for ' + index,
        title_x=0.5
    )

    # sorted_landing = sorted_landing + list(sorted_landing(0, 3))
    fig.add_trace(go.Funnel(
        name='max inflow users',
        # marker={"colorbar": ["dodgerblue"], "line": {"color": ["dodgerblue"]},"connector":{"fillcolor": ["dodgerblue"]}},
        # color= ["deepskyblue", "lightsalmon", "tan", "teal", "silver"],
        y=["Landing", "Iteration 1", "Iteration 2", "Iteration 3", "Iteration 4", "Iteration 5"],
        text=[str(sorted_landing_df[0][0]), str(sorted_first_df[0][0]), str(sorted_second_df[0][0]),
              str(sorted_third_df[0][0]), str(sorted_fourth_df[0][0]), str(sorted_fifth_df[0][0])],
        x=[sorted_landing_df[1][0], sorted_first_df[1][0], sorted_second_df[1][0],
           sorted_third_df[1][0], sorted_fourth_df[1][0], sorted_fifth_df[1][0]],
        textinfo="text+value+percent initial+text"))
    fig.show()

    # Appends all the metrics for blog comparison and stores in DF for pretty printing
    listl.append(index)
    listl.append(total)
    listl.append(pages_visited)
    listl.append(blog_1_only_visited)
    listl.append(landing_page.get("blog_1"))
    listl.append(blog_2_only_visited)
    listl.append(landing_page.get("blog_2"))
    if counter_1==0:
        listl.append(0)
        listl.append(0)
    else:
        listl.append((purchase_success_blog_1_landing / counter_1) * 100)
        listl.append((bounce_blog_1_landing / counter_1) * 100)

    if counter_2 == 0:
        listl.append(0)
        listl.append(0)
    else:
        listl.append((purchase_success_blog_2_landing / counter_2) * 100)
        listl.append((bounce_blog_2_landing / counter_2) * 100)

    if counter_3 == 0:
        listl.append(0)
        listl.append(0)
    else:
        listl.append((purchase_success_blog_1 / counter_3) * 100)
        listl.append((bounce_blog_1 / counter_3) * 100)
    if counter_4 == 0:
        listl.append(0)
        listl.append(0)
    else:
        listl.append((purchase_success_blog_2 / counter_4) * 100)
        listl.append((bounce_blog_2 / counter_4) * 100)
    listl.append(page_iteration)

    return listl

# Generated Table based on Data frams per groupings value passed
def generate_table(grouping, data_click_stream):
    data_dict = dict(data_click_stream[grouping].value_counts())
    list_append=[]
    list_append_blogs=[]

    # coloumn for the final df based on performance metrics for printing and ease of visualization
    column_names =["Source", "Total", "pages_visited", "bounce", "bounce_rate", "purchased", "not_purchased",
                   "conversion_rate", "purchase_started_not_success","purchase_started"]

    # coloumn for the final df based on blog1 vs blog2 evaluation for printing and ease of visualization
    column_names_blog = ["Source", "Total","pages_visited","blog_1_only_visit", "blog_1_landing", "blog_2_only_visit", "blog_2_landing",
                     "blog_1_landing_purchase_rate","blog_1_landing_bounce_rate","blog_2_landing_purchase_rate","blog_2_landing_bounce_rate",
                     "blog_1_purchase_rate","blog_1_bounce_rate","blog_2_purchase_rate","blog_2_bounce_rate", "pages_interaction"]
    for index, value in data_dict.items():
        index_source = data_click_stream[data_click_stream[grouping] == index]
       # Get the metric measures and then stores in the  list of dictiory for forming DF
        dict_data = get_counts(index, index_source, value)
        list_append.append(dict_data)
        # Get the metric measures for blog1 vs blog2 then stores in the  list of dictiory for forming DF
        page_data = get_counts_blogs(index, index_source, value)
        list_append_blogs.append(page_data)

    # Creates DF based on the perf metrics
    data_df = pd.DataFrame(list_append)
    data_df.columns = column_names

    # Creates seperate DF forblog comparison based on the perf metrics
    data_df_blogs = pd.DataFrame(list_append_blogs)
    data_df_blogs.columns = column_names_blog

    # Captures Drop out rate and stores in main DF
    data_df['dropout_Rate'] = 100 - data_df['purchased'] / data_df['purchase_started'] * 100
    print(data_df.to_string())
    data_df_mean = data_df.mean()
    print(data_df_mean.to_string())
    print(data_df_blogs.to_string())

    return data_df

# Reads the Excel Files and creates a dictionary per line
with open('visitor_data_clickstream.csv') as file:
    frames = []
    for line in file:
        data_item_dict = turn_line_of_file_into_dict(line)
        data_fd = pd.DataFrame(data_item_dict)
        frames.append(data_fd)
data_click_stream = pd.concat(frames)

source_grouped = generate_table('source',data_click_stream)
platform_grouped = generate_table('platform',data_click_stream)
