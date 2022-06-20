import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

# needed for streamlit cloud
script_path = Path(__file__).parents[0] 
SAMPLE_FILE = script_path / 'deals_data.csv'


st.markdown("# B2B Pipeline Analysis")
st.sidebar.markdown("# Analyzing deal data")


@st.cache
def load_deals_data(file_name):
    return pd.read_csv(file_name)


st.write(
    """Note: this is the web app accompanying our blog post series on survival analysis for B2B pipelines (_fortcoming_).
    We suggest that you read the posts and play with the app in tandem.""")
    
st.header("Part 1: Distribution and Common Errors")

st.write(
    """While we explain some (mildly) fancy methods in the series, we have often found confusing 
    practices even in some very basic reasoning around marketing and pipeline analysis. So we decided to kick things off with 
    some basic but important principles that may help you avoid common forecasting mistakes.
    """)

st.write("""
    At the cost of being obvious, our interactive app goes over the perils of skewed distributions and
    what we should know when making simple considerations about future goals. 
    """)

st.header("Distributions and why they matter")

st.write(
    """
    Consider the deal history of (the imaginary) `Company A` and `Company B` below
    (each won deal value is in thousands of USD). `Company A` and `Company B` make the same
    revenue at the end of the year, their [average](https://en.wikipedia.org/wiki/Mean) ACV (Annual Contract Value) is the same, 
    but the [median](https://en.wikipedia.org/wiki/Median) is very different.

    You can play around with the numbers yourself to build up your intuition.
    """
)

company_A = st.text_input('Deals for Company A (thousands of USD)', '60,40,55,45,50')
company_B = st.text_input('Deals for Company B (thousands of USD)', '10,20,30,150,40')

st.write('`Company A` total revenues is {} k USD, avg. ACV is {} K USD, median is {}; `Company B` total revenues is {} k USD, avg. ACV is {} K USD, median is {}'.format(
    sum([float(_) for _ in company_A.split(',')]), 
    np.mean([float(_) for _ in company_A.split(',')]),
    np.median([float(_) for _ in company_A.split(',')]),
    sum([float(_) for _ in company_B.split(',')]), 
    np.mean([float(_) for _ in company_B.split(',')]),
    np.median([float(_) for _ in company_B.split(',')])
))

st.write(
    """
    Should Alice - head of marketing at `Company A`, and Bob - head of marketing at `Company B` -
    both reason with their avg. ACV to make forecasting and strategy? As a first experiment, we remove the biggest deal from past history and recompute the avg. ACV and
    the median:
    """
)

company_A_redux = st.text_input('Deals for Company A (thousands of USD)', '60,40,45,50')
company_B_redux = st.text_input('Deals for Company B (thousands of USD)', '10,20,30,40')

st.write('`Company A` avg. ACV is now {} K USD, median is {}; `Company B` avg. ACV is now {} K USD, median is {}'.format(
    np.mean([float(_) for _ in company_A_redux.split(',')]),
    np.median([float(_) for _ in company_A_redux.split(',')]),
    np.mean([float(_) for _ in company_B_redux.split(',')]),
    np.median([float(_) for _ in company_B_redux.split(',')])
))

st.write(
    """
    `Company A`'s deal values are mostly the same, while `Company B`'s outlook is completely different. 
    The lesson for Bob is clear: when there are few very large deals influencing revenues, the avg. ACV
    alone may be an unreliable indicator of the state of the business:

    * if your deals look like `Company B` (you can upload your data below and try!), and your mean and your median deal values differ by a large margin, using the mean may overstate the health of your business, which now relies on few large outliers to reach its goals;
    * if your deals look like `Company B`, it may happen that your ACV is also not representative of _any_ real customer: `Company B` ACV of {} k USD represents a price _nobody_ may ever pay, as it is higher than the smaller deals, and lower than the big fat ones - as such, it is bad indicator of your customers' willingness to pay, and an unreliable figure for business development.
    """.format(np.mean([float(_) for _ in company_B.split(',')]))
)

st.write(
    """
    As a less simplistic example, consider the above points in the context of the deal size distribution below 
    (blue, median, ~50k, purple, mean, ~100k): the median clearly captures the low-end of the deal spectrum 
    (leaving open the question on how to treat outliers on the right), while the mean is capturing neither the low-end
    or the high-end, and ends up representing a small minority of deals. 
    """
    )


image = Image.open(script_path / 'example.jpg')
st.image(image, caption='Mean and median for another deal size distribution', width=300)

st.subheader("'[When will then be now](https://www.youtube.com/watch?v=5drjr9PmTMA)?' - or, a glimpse into a thousand futures")

# load and cache the sample deal data
sample_deal_data = load_deals_data(SAMPLE_FILE)

st.write(
    """
    Now that the problem is well-understood with a toy dataset, it is time to scale up our intuition
    with more data and a more realistic use case. We created some simulated deals data for `ACME Inc.`,
     a B2B company selling {} products, e.g. a SaaS solution
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

def build_product_select(df: pd.DataFrame, key: str):
    unique_products = list(df['product'].unique())
    s = st.multiselect(
     'Select products:',
     unique_products,
     unique_products, key=key)

    return s

def build_product_plot(df: pd.DataFrame, options: list, id: int):
    plt.figure(id)
    # just loop over here (but could be better!)
    for o in options:
        cnt_dists = df.loc[df['product'] == o].groupby('product')['deal_size'].apply(list)[0]
        st.write("{}: mean is {:.1f}. median is: {:.1f}".format(
            o, np.mean(cnt_dists), np.median(cnt_dists) 
            ))
        plt.hist(cnt_dists, 50, alpha=0.2, density=True, label=o)
    # add legend
    plt.legend()

    return plt

# display products based on selection
product_options = build_product_select(sample_deal_data, key='default_options')
_fig = build_product_plot(sample_deal_data, product_options, id=0)
st.pyplot(_fig)
st.caption("""
    Historical distribution of deal size by selected product.
    X: Deal ACV, Y: Normalized counts.
""")


def simulate_futures(
    df: pd.DataFrame, 
    options: list, 
    id: int, # id for the plot
    deals_we_close: int, # deal we expect to close
    n_futures: int, # futures to simulate
):
    plt.figure(id)
    # just loop over here (but could be better!)
    for o in options:
        cnt_dists = list(df.loc[df['product'] == o]['deal_size'])
        s = [sum(np.random.choice(cnt_dists, size=deals_we_close, replace=True)) for n in range(n_futures)]
        st.write("{}: mean is {:.1f}, 10th percentile outcome {:.1f}, 90th percentile outcome {:.1f}".format(
            o, np.mean(s), np.percentile(s, 10), np.percentile(s, 90)
            ))
        plt.hist(s, 50, alpha=0.2, density=True, label=o) 
    # add legend
    plt.legend()

    return plt

n_futures = 10000

st.write(
    """
    An interesting question for practictioners like Bob and Alice is setting (and then reaching) a pipeline goal
    for the next time period (say, a quarter, a month etc.): assuming for now we know our opportunity conversion rates (more on that in
    the `Survival Analysis` tab), we can estimate closing 20 new deals in our next period - our expected generated revenue
    is therefore avg. ACV * 20.

    If you followed so far, you have reasons to be skeptical of this "point-wise" estimate: certainly the future is a bit more
    complex than a single number! Since real-world deal distribution may be hard to model without fancy math, we will
    drive our point home through _simulations_. 
    
    Imagine - like [Doctor Strange](https://en.wikipedia.org/wiki/Doctor_Strange_(2016_film)), if you will - to be able to see
    all of the different possible ways the future quarter may unfold: in one future, things go in a very conservative way and you sell mostly
    small deals; in another version of the future, a personal connection with a C-level speeds up an enterprise negotation - and so on. To get a sense of 
    what is a realistic estimate of your next quarter's revenues, you can plot the total revenues you get in each of these potential futures (well, 
    you can't really plot _all_ of them, so we simulate {}).

    The key point about these future scenarios is that you don't know which one will be the _actual one_: when setting goals and making
    forecasts, it is important to fully understand how spread out the possible outcomes can be: when playing around with different products, we 
    will also compute exceedingly bad and good scenarios to give you a sense of the distribution (NOTE: 
    in our careers, we have seen real-world deal distributions significantly more skewed than this synthentic one - in those cases, explicitely
    addressing this issue is even more important!). 
    """.format(n_futures)
)

product_revenue_options = build_product_select(sample_deal_data, key='default_options_revenues')
n_deals = st.number_input('Deals we expect to close', min_value=5, max_value=50, value=20, step=5, key='default_deals')
_future_fig = simulate_futures(
    sample_deal_data, 
    product_revenue_options, 
    id=1, 
    deals_we_close=n_deals, 
    n_futures=n_futures
)
st.pyplot(_future_fig)
st.caption("""
    Potential future revenues for selected products by probability density.
    X: Total Revenues, Y: Probability of outcome
""")


st.header("Use your own data!")

st.write("""
        Upload a csv file with two columns (product,deal_size), where the first column is a string ID
        (product_0), and the second is a number representing deal size (see also the sample data above
        as an example).

        Once data is uploaded, you will see the same analysis on your data 
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
        st.write("Data uploaded. First {} lines are:".format(k))
        st.write(user_dataframe[:k])
        st.write("Deal size distribution, by product:")
        user_product_options = build_product_select(user_dataframe, key='user_options')
        user_fig = build_product_plot(user_dataframe, user_product_options, id=2)
        st.pyplot(user_fig)
        st.write("Simulation of {} futures".format(n_futures))
        user_n_deals = st.number_input('Deals we expect to close', min_value=5, max_value=50, value=20, step=5, key='user_deals')
        user_future_fig = simulate_futures(
            user_dataframe, 
            user_product_options, 
            id=3, 
            deals_we_close=user_n_deals, 
            n_futures=n_futures
        )
        st.pyplot(user_future_fig)
