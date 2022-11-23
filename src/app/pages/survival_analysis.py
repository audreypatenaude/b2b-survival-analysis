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
    """Note: this is the web app accompanying our [blog post series](https://medium.com/@mllepatenaude/navigating-b2b-pipeline-data-distribution-uncertain-outcomes-bb906f2bfc02) on survival analysis for B2B pipelines.
    We suggest that you read the posts and play with the app in tandem.""")

st.header("Part 1: The Problem with Conversion Analysis")

st.write("""
    When considering desired outcomes in some relatively distant future - for example, closing deals in a B2B software company,
    a common trick is establishing a threshold of interest, say, 3 months, and then calculate the average closing rate at 3 months after the opportunity was created.

    By turning the conversion problem into a binary classification with a fixed time horizon, however, we are now:
    
    * incapable of making considerations for deals that are younger than the threshold. Should I wait two quarters to know how THIS quarter is going?
    * incapable of adapting our closing estimates as deals age: what does deal age tell us about closing probability?
    
    To overcome this limitation, we will use a different approach here, borrowed by what is called survival analysis (SA). In SA, the typical questions we want to answer are:

    * are people that took treament A dying faster than those who took treatment B? (We certainly would like to know as fast as possible the answer to this!)
    * given that somebody survived 5 years after getting diagnosed X, how likely are they to be alive in the next 3 years? (We certainly would like to incorporate the knowledge we have at years 5 into our current estimate)

    SA, like deal closing, has to deal with an event in the future that may occur at any point in time. But at any given moment, we only know what happened to deals (or patients) that have had an outcome already, 
    but have no idea what's going to happen to the others (NOTE: the similarity breaks down as everybody dies eventually, but not every deal closes, but the general idea will serve as a 
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
    # create a df to store the final values
    values_dfs = []
    # for each product plot the line
    for product in products:
        p_df = pd.DataFrame()
        cnt_df = df.loc[df['ProductId'] == product]
        T, E = datetimes_to_durations(cnt_df["SQLDate"], cnt_df["WonDate"], freq='W')
        kmf = KaplanMeierFitter().fit(T, E, label='Prod {}'.format(product))
        y = [1 - _[0] for _ in kmf.survival_function_.values]
        y_min = [1 - _[0] for _ in kmf.confidence_interval_.values]
        y_max = [1 - _[1] for _ in kmf.confidence_interval_.values]
        x = range(0, len(y))
        # plot
        ax.plot(x, y, label='Prod {}'.format(product))
        ax.set_xlabel('Weeks from SQL opening date')
        ax.set_ylabel('Probability of winning')
        ax.fill_between(x, y_min, y_max, alpha=.1)
        # fill df
        p_df['x'] = x
        p_df['y'] = y
        p_df['y_mix'] = y_min
        p_df['y_max'] = y_max
        p_df['product'] = [product for _ in range(len(y))]
        values_dfs.append(p_df)
    # plot the legend
    plt.legend()

    return plt, pd.concat(values_dfs, ignore_index=True)

_fig, values_df = plot_winning_rate(sample_survival_data)
st.pyplot(_fig)
st.caption("""
    Closing rate by product line as time goes by (with confidence intervals)
    Y: Winning probability, X: Weeks from SQL date.
""")

st.write("""
    The plot above give us immediately two benefits compared to a traditional, binary conversion analysis:

    * first, by plotting by cohorts (that is, considering for each deal week 0 the opportunity creation date), we can immediately compare product lines even in the early days: for example, even if `Prod 1` was a new line with only 10 weeks of data, we would still be able to make some partial judgment and comparison with `Prod 2` (in particular, `Prod 2` seems to be much better in the early weeks!);
    * second, by using a [statistical estimator from the lifelines package](https://lifelines.readthedocs.io/en/latest/fitters/univariate/KaplanMeierFitter.html) we also get confidence intervals around our closing rate. 
""")

st.write("""
    Now that we have a better answer to our first challenge above, we turn our attention to the second open question:
    certainly, if a deal is 20 weeks old, its probability of closing may be different than if it is only 10 weeks old.

    How can we incorporate this insight into our calculations? Enter the conditional version of the Kaplan-Meier estimator!

""")

st.header("Part 2: Conditional Probabilities")

st.write("""
It turns out, we already have most of what we need in place! Recall our problem: given `t` weeks has passed in this opportunity, what
is the probability of a success in `k + t` weeks?

The [conditional survival estimate](https://aacrjournals.org/clincancerres/article/21/7/1530/248476/Conditional-Survival-A-Useful-Concept-to-Provide) 
given Kaplan-Meier (unconditional) estimates is just the ratio `KM (k + t) / KM (t)`.

""")


k_weeks = st.text_input('Pick a future look-ahead window (weeks, integer)', '8')

def plot_conditional_winning_rate(
    df,
    k_weeks: int
):
    # setup the plot
    f = plt.figure(figsize=(16,9))
    ax = f.add_subplot(111)
    products = list(df['ProductId'].unique())
    print("Products detected: {}".format(products))
    # create a df to store the final values
    values_dfs = []
    # for each product plot the line
    for product in products:
        p_df = pd.DataFrame()
        cnt_df = df.loc[df['ProductId'] == product]
        T, E = datetimes_to_durations(cnt_df["SQLDate"], cnt_df["WonDate"], freq='W')
        kmf = KaplanMeierFitter().fit(T, E, label='Prod {}'.format(product))
        all_vals = [_[0] for _ in kmf.survival_function_.values]
        max_weeks = len(all_vals)
        y = [all_vals[min(idx + k_weeks, max_weeks - 1)] / all_vals[idx] for idx in range(max_weeks)]
        y = [1 - _ for _ in y]
        x = range(0, len(y))
        ax.plot(x, y, label='Prod {}'.format(product))
        ax.set_xlabel('Weeks from SQL opening date')
        ax.set_ylabel('Probability of winning')
        # fill df
        p_df['x'] = x
        p_df['y'] = y
        p_df['look_ahead'] = [min(idx + k_weeks, max_weeks - 1) for idx in x]
        p_df['product'] = [product for _ in range(len(y))]
        values_dfs.append(p_df)
    # plot the legend
    plt.legend()

    return plt, pd.concat(values_dfs, ignore_index=True)

# calculate and plot the lines
c_fig, cond_value_df = plot_conditional_winning_rate(sample_survival_data, int(k_weeks))
st.pyplot(c_fig)
st.caption("""
    Conditional winning rate (k={}) by product line.
    Y: Conditional winning probability, X: Weeks from SQL date.
""".format(k_weeks))

st.write("""
Not bad! If you run the above with the default `8` as look-ahead window, you see that, given a `10 weeks` opportunity (X-axis), the probability of closing in the next `8` is different for the two products. 

Of course, once you get the intuition, try experiment with different values! Keep in mind that we are using the values Product and Age for this example, but "Product" could be replaced by any other variable that distinguishes the different types of deals you have in your pipeline (i.e. other texture attributes which could be account type, deal size, etc).

While this is certainly looking like progress, and a (somehow) principled way to look at the challenge, this is _only the beginning_ of a proper analysis: 

* first, no other specific feature of our opportunities is used to provide insights (except partionining by products and age); if we want to also consider, say, sales reps or industry, we need to move to a [full regression model](https://lifelines.readthedocs.io/en/latest/Survival%20Regression.html);
* second, we have been cheating (a bit) by setting our prediction as a binary problem (win in business=death in survival): in B2B SaaS, outcome is more commonly conceptualized as non-binary, `win`, `loss`, `still open`; also consider that while eventually everybody dies, not everybody buys;
* third, we have only scratched the surface when using non-parametric estimates for mostly descriptive purposes, but there is a world of [parametric models](https://lifelines.readthedocs.io/en/latest/Survival%20analysis%20with%20lifelines.html#fitting-to-a-weibull-model) out there for more advanced use cases.

In other words, while we know this is likely _not_ where you want to end your analysis, we do hope it provides a good intuitive _start_!

""")


st.header("Use your own data!")

st.write("""
        Upload a csv file with three columns (ProductId,SQLDate,WonDate), where the first column is 
        a integer ID (0, for product_0 for example), the second is a date representing the creation of the opportunity,
        the third is the winning date of the opportunity (if winning date is there, a row would look like `1,3/13/2020,3/22/2020`, otherwise the third column will be empty, e.g. `1,3/13/2020,`).
        
        For an explicit example, _see also the sample raw data above_.

        Once data is uploaded, you will see the same analysis on your data 
        (NOTE: _no data is stored on our side!_)! If you want to see the actual numbers, you can use the checkbox to display the table generating the chart!
    """
)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
     # check if this is a csv -> should be more robust ;-)
    if not uploaded_file.name.endswith('.csv'):
        st.write("Please upload a csv file")
    else:
        user_survival_data = load_survivals_data(uploaded_file)
        user_fig, user_values_df = plot_winning_rate(user_survival_data)
        st.pyplot(user_fig)
        st.caption("""
            Analysis on your data, by product line (with confidence intervals).
            Y: Winning probability, X: Weeks from SQL date.
        """)
        if st.checkbox('Show values'):
            st.write(user_values_df)
        # conditional estimates
        st.write("Now plotting the conditional estimates")
        user_c_fig, user_cond_value_df = plot_conditional_winning_rate(user_survival_data, int(k_weeks))
        st.pyplot(user_c_fig)
        st.caption("""
            Conditional winning rate (k={}).
            Y: Conditional winning probability, X: Weeks from SQL date.
        """.format(k_weeks))
        if st.checkbox('Show conditional values'):
            st.write(user_cond_value_df)
