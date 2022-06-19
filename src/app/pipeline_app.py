import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



SAMPLE_FILE = 'deals_data.csv'

st.markdown("# B2B Pipeline Analysis")
st.sidebar.markdown("# Analyzing deal data")

@st.cache
def load_deals_data(file_name):
    return pd.read_csv(file_name)

st.write(
    """While we explain some (mildly) fancy methods in our blog posts, we have often found confusing 
    remarks even in some very basic reasoning around marketing, business development, pipeline analysis, etc.
    """)

st.write("""
    At the cost of being obvious, our (interactive) app goes over the perils of skewed distributions and
    what we should know when making simple considerations about future goals. 
    """)

st.header("Distributions and why they matters")


st.write(
    """
    Consider the deal history of (the imaginary) `Company A` and `Company B` below
    (each won deal value is in thousands of USD). `Company A` and `Company B` makes the same
    revenues at the end of the year, their average ACV (Annual Contract Value) is the same, 
    but the median is very different.

    You can play around with the numbers yourself to build up your intuition.
    """
)

company_A = st.text_input('Deals for Company A (thousands of USD)', '60,40,55,45,50')
company_B = st.text_input('Deals for Company B (thousands of USD)', '10,20,30,150,40')

st.write('`Company A` total revenues is {} k USD, avg. ACV is {} K USD, median is {}'.format(
    sum([float(_) for _ in company_A.split(',')]), 
    np.mean([float(_) for _ in company_A.split(',')]),
    np.median([float(_) for _ in company_A.split(',')])
))
st.write('`Company B` total revenues is {} k USD, avg. ACV is {} K USD, median is {}'.format(
    sum([float(_) for _ in company_B.split(',')]), 
    np.mean([float(_) for _ in company_B.split(',')]),
    np.median([float(_) for _ in company_B.split(',')])
))

st.write(
    """
    Should Alice - head of marketing at `Company A`, and Bob - head of marketing at `Company B` -
    both reason with avg. ACV to make forecasting and strategy?

    As a first experiment, we remove the biggest deal from past history and recompute the avg. ACV and
    the median:
    """
)

company_A_redux = st.text_input('Deals for Company A (thousands of USD)', '60,40,45,50')
company_B_redux = st.text_input('Deals for Company B (thousands of USD)', '10,20,30,40')

st.write('`Company A` avg. ACV is now {} K USD, median is {}'.format(
    np.mean([float(_) for _ in company_A_redux.split(',')]),
    np.median([float(_) for _ in company_A_redux.split(',')])
))
st.write('`Company B` avg. ACV is now {} K USD, median is {}'.format(
    np.mean([float(_) for _ in company_B_redux.split(',')]),
    np.median([float(_) for _ in company_B_redux.split(',')])
))

st.write(
    """
    `Company A` values are mostly the same, while `Company B` outlook is completely different. 
    The lesson for Bob is clear: when there are few very large deals influencing revenues, the avg. ACV
    alone may be an unreliable indicator of the state of the business:

    * if your deals look like `Company B` (you can upload your data below and try!), and your mean and your median deal values differ by a large margin, using the mean by overstate the health of your business, which now relies on few large outliers to reach its goals;
    * if your deals look like `Company B`, it may happen that your ACV is also not representative of _any_ real customer: `Company B` ACV of {} k USD represents a price _nobody_ may ever pay, as it is higher than the smaller deals, and lower than the big fat ones - as such, it is bad indicator of your customers' willing to pay, and an unreliable figure for business development.
    """.format(np.mean([float(_) for _ in company_B.split(',')]))
)

st.subheader("'When will then be now?' - or, a glimpse into a thousand futures")

# load and cache the sample deal data
sample_deal_data = load_deals_data(SAMPLE_FILE)

st.write(
    """
    Now that the problem is well-understood with a toy dataset, it is time to scale up our intuition
    with more data and a more realistic use case.

    We created some simulated deals data for `ACME Inc.`, a B2B company selling {} products, say, a SaaS solution
    for different verticals: HR, healthcare, finance etc. (no worries: you can use _also your own data_ 
    at the end!).
    """.format(len(list(sample_deal_data['product'].unique())))
)

if st.checkbox('Show raw data format'):
    st.write(sample_deal_data[:10])

st.write(
    """
    You can use the tab below to visualize how the distribution of ACV changes across products:
    """
)

def build_product_select(df: pd.DataFrame):
    unique_products = list(df['product'].unique())
    s = st.multiselect(
     'Select the products you want to display:',
     unique_products,
     unique_products)

    return s

def build_product_plot(df: pd.DataFrame, options: list):
    for o in options:
        cnt_dists = df.loc[df['product'] == o].groupby('product')['deal_size'].apply(list)[0]
        plt.hist(cnt_dists, 50, alpha=0.2, density=True, label=o)

    plt.legend()

    return plt

# display products based on selection
product_options = build_product_select(sample_deal_data)
_fig = build_product_plot(sample_deal_data, product_options)
st.pyplot(_fig)

st.write(
    """
    An interesting question for people like bob and alice
    """
)

def simulate_future_revenues(
    dist, # historical distribution
    deals_we_close: int = 10, # deal we expect to close
    possible_futures: int = 100000, # future to simulate
    with_plot: bool=True,
    is_debug: bool=True
):
    # Store sum in a list. Repeat k times. Calculate mean and std of list.
    s = [sum(np.random.choice(dist, size=deals_we_close, replace=True)) for n in range(possible_futures)]
    if is_debug:
        print("Mean {:.1f}, Median {:.1f}, Sum {:.1f}, Std {:.1f}".format(
                    np.mean(s),
                    np.median(s),
                    np.sum(s),
                    np.std(s)
                ))
    
    if with_plot:
        plt.hist(s, 50, alpha=0.5, density=True) 
        plt.show()
    
    return


st.header("Use your own data!")

st.write("""
        Upload a csv file with two columns (product,deal_size), where the first column is a string ID
        (product_0), and the second is a number representing deal size (see also the sample data above
        as an example).

        Once data is uploaded, you will see a button to run the same analysis on your data 
        (NOTE: _no data is stored on our side!_)!
    """
)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
     # check if this is a csv -> should be more robust ;-)
    if not uploaded_file.name.endswith('.csv'):
        st.write("Please upload a csv file")
    else:
        user_dataframe = pd.read_csv(uploaded_file)
        k = 3
        st.write("Data uploaded: first {} lines are:".format(k))
        st.write( user_dataframe[:k])
        if st.button('Compute my future!'):
            pass
