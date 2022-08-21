import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from lifelines.utils import datetimes_to_durations
from lifelines import KaplanMeierFitter


st.markdown("# Conversion as Survival analysis")
st.sidebar.markdown("# Survival analysis")

# needed for streamlit cloud
script_path = Path(__file__).parents[0] 
SAMPLE_SURVIVAL_FILE = script_path / 'survival_data.csv'


st.write(
    """Note: this is the web app accompanying our blog post series on survival analysis for B2B pipelines (_fortcoming_).
    We suggest that you read the posts and play with the app in tandem.""")

st.header("Part 1: The Problem with Conversion Analysis")

st.write("""
    When considering desired outcomes in some relatively distant future - for example, closing deals in B2B -,
    a common trick is establishing a threshold of interest, say, 3 months, and then calculate / predict the closing rate at 3 months after the SQL was created.

    By turning the conversion problem into a binary classification with a fixed time horizon, however, we are now:
    
    * incapable of making considerations for deal that are younger than the threshold. Should I wait two quarters to know how THIS quarter is going?
    * incapable of adapting our closing estimates as deals age: what does deal age tell us about closing probability?
    
    To overcome this limitation, we will use a different approach here, borrowed by what is called survival analysis (SA). In SA, the typical questions we want to answer are:

    * are people that took treament A vs B dying faster? (We certainly would like to know as fast as possible the answer to this!)
    * given somebody survived 5 years after getting diagnosed X, how likely is he/she to be alive in the next 3? (We certainly would like to incorporate the knowledge we have at years 5 into our current estimate)

    SA, like deal closing, has to deal with an event in the future that may occur at any point in time: at any given moment, we only know what happened to deals / patients with one outcome, 
    but have no idea about the others (NOTE: the similarity breaks down as everybody dies eventually, but not every deal closes, but the general idea will serve as a 
    good metaphor to the introductory treatment we propose here).
""")


@st.cache
def load_survivals_data(file_name):
    return pd.read_csv(file_name)

# load and cache the sample deal data
sample_survival_data = load_survivals_data(SAMPLE_SURVIVAL_FILE)

st.subheader("Comparing products conversion rates")
st.write("""
    As usual, we created some realistic but fake data for `ACME Inc.`: we have {} products, 
    and a list of sales conversations - some of them closed successfully (in the date shown in the file),
    some of them are still open.
""".format(len(sample_survival_data['ProductId'].unique())))

if st.checkbox('Show raw data format'):
    st.write(sample_survival_data[:5])

def plot_winning_rate(
    df 
):
    # setup the plot
    f = plt.figure(figsize=(16,9))
    ax = f.add_subplot(111)
    products = list(df['ProductId'].unique())
    print("Products detected: {}".format(products))
    # for each product plot the line
    for product in products:
        cnt_df = df.loc[df['ProductId'] == product]
        T, E = datetimes_to_durations(cnt_df["SQLDate"], cnt_df["WonDate"], freq='W')
        kmf = KaplanMeierFitter().fit(T, E, label='Prod {}'.format(product))
        y = [1 - _[0] for _ in kmf.survival_function_.values]
        y_min = [1 - _[0] for _ in kmf.confidence_interval_.values]
        y_max = [1 - _[1] for _ in kmf.confidence_interval_.values]
        x = range(0, len(y))
        ax.plot(x, y, label='Prod {}'.format(product))
        ax.set_xlabel('Weeks from SQL opening date')
        ax.set_ylabel('Probability of closing')
        ax.fill_between(x, y_min, y_max, alpha=.1)
    # plot the legend
    plt.legend()

    return plt

_fig = plot_winning_rate(sample_survival_data)
st.pyplot(_fig)
st.caption("""
    Closing rate by product line as time goes by (with confidence intervals)
    X: Winning probability, Y: Weeks from SQL date.
""")

st.write("""
    The plot above give us immediately two benefits compared to a traditional, binary conversion analysis:

    * first, by plotting by cohorts (that is, considering for each deal week 0 the SQL opening date), we can immediately compare product lines even in the early days: for example, even if `Prod 1` was a new line with only 10 weeks of data, we would still be able to make some partial judgment and comparison with `Prod 2`;
    * second, by using a [statistical estimator from the lifelines package](https://lifelines.readthedocs.io/en/latest/fitters/univariate/KaplanMeierFitter.html) we also get confidence interval around our closing rate. 
""")

st.write("""
    Now that we have a better answer to our first challenge above, we turn our attention to the second open question:
    certainly, if a deal is 20 weeks long, its probability of closing may be different than if it is only 10 weeks long.

    How can we incorporate this insight into our calculations? Enter the conditional version of the Kaplan-Meier estimator!

""")

st.header("Part 2: Conditional Probabilities")

st.write("""
It turns out, we already have most of what we need in place! Recall our problem: given `t` weeks has passed in this opportunity, what
is the probability of a success in `k + t` weeks?

The [conditional survival estimate](https://aacrjournals.org/clincancerres/article/21/7/1530/248476/Conditional-Survival-A-Useful-Concept-to-Provide) 
given Kaplan-Meier (unconditional) estimates is just the ratio `KM (k + t) / KM (t)`.

""")


st.header("Use your own data!")

st.write("""
        Upload a csv file with three columns (ProductId,SQLDate,WonDate), where the first column is 
        a integer ID (0, for product_0 for example), the second is a date representing the creation of the opportunity,
        the third (if present) is the winning date of the opportunity.
        
        For an explicit example, _see also the sample raw data above_.

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
        user_survival_data = load_survivals_data(uploaded_file)
        user_fig = plot_winning_rate(user_survival_data)
        st.pyplot(user_fig)
        st.caption("""
            Analysis on your data, by product line (with confidence intervals).
            X: Winning probability, Y: Weeks from SQL date.
        """)
