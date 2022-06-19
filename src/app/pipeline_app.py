import streamlit as st
import json
import numpy as np


SAMPLE_FILE = 'deals_data.json'

st.markdown("# B2B Pipeline Analysis")
st.sidebar.markdown("# Analyzing deal data")

@st.cache
def load_data(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data

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

sample_data = load_data(SAMPLE_FILE)

st.write(
    """
    Now that the problem is well-understood with a toy dataset, it is time to scale up our intuition
    with more data and a more realistic use case.

    We create some simulated deals data for `ACME Inc.`, a B2B company selling {} products, say, a SaaS solution
    for different verticals: HR, healthcare, finance etc. (no worries: you can use _also your own data_ 
    at the end!).

    You can use the tab below to visualize how the distribution of ACV changes across products:
    """.format(3)
)

option = st.selectbox(
     'Which product deals you want to see?',
     list(sample_data.keys())
     )

st.write('Deals for {}'.format(option))
st.bar_chart(np.histogram(sample_data[option], bins=50)[0])

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

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
     # To read file as bytes:
     bytes_data = uploaded_file.getvalue()
     st.write(bytes_data)

     # To convert to a string based IO:
     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
     st.write(stringio)

     # To read file as string:
     string_data = stringio.read()
     st.write(string_data)

     # Can be used wherever a "file-like" object is accepted:
     dataframe = pd.read_csv(uploaded_file)
     st.write(dataframe)