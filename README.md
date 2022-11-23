# B2B Survival Analysis for Pipeline Forecasting

Code and data playground to better analyze pipeline data for "small-data" B2B sales pipelines.

## Overview

This repository contains the code to reproduce the analysis and the arguments of the [B2B sales 
pipeline Medium series](https://medium.com/@mllepatenaude/navigating-b2b-pipeline-data-distribution-uncertain-outcomes-bb906f2bfc02). If you are just interested in the interactive app and not so much
in the code behind it, you can enjoy directly the app [here](https://share.streamlit.io/audreypatenaude/b2b-survival-analysis/src/app/pipeline_app.py).

_Please note this repo is WIP. Come back often for updates_.

Project structure:

* `app`: code for the [streamlit](https://streamlit.io/) interactive app, available online [here](https://share.streamlit.io/audreypatenaude/b2b-survival-analysis/src/app/pipeline_app.py)
* `notebooks`: throw-away code used when developing and debugging the app.

## Setup

### Virtual env

Setup a virtual environment with the project dependencies:

* `python -m venv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

This will install the dependencies needed to run the app (and, if you wish to do so, run the playground notebooks as well).


## How to run the app

* cd into the `src/app` folder
* run the main streamlit script with `streamlit run pipeline_app.py`

## Acknowledgements

TBC

Contributors:

* [Jacopo Tagliabue](https://www.linkedin.com/in/jacopotagliabue/), code prototype.

## License

All the code in this repo is freely available under a MIT License, also included in the project.
