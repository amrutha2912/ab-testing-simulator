# A/B Testing Simulator

An interactive Streamlit dashboard for analysing A/B test results. Upload experiment data or enter values manually to compute statistical significance, confidence intervals, and lift estimates.

## What it does

- Accepts either manual input (sample sizes and conversions) or a CSV upload with group and outcome columns
- Runs a two-proportion Z-test and independent samples t-test
- Computes absolute and relative lift, confidence intervals, and p-values
- Displays a significance verdict with clear reasoning
- Generates a visual summary: conversion rate bar chart, confidence interval plot, p-value vs alpha comparison
- Exports results as a CSV and chart PNG

## Usage

```bash
git clone https://github.com/amrutha2912/ab-testing-simulator.git
cd ab-testing-simulator
pip install -r requirements.txt
streamlit run app.py
```

The app runs locally in your browser at `http://localhost:8501`.

## CSV format (upload mode)

Your CSV should have at minimum:
- A group column with values like `control` and `treatment`
- A binary outcome column (1 = converted, 0 = not converted)

## Project structure

```
ab-testing-simulator/
├── app.py
├── requirements.txt
└── README.md
```

## Tech stack

Python, Streamlit, SciPy, Pandas, NumPy, Matplotlib

## Author

Amrutha Satyamoorthy - [Portfolio](https://amrutha-satyamoorthy.vercel.app) | [LinkedIn](https://linkedin.com/in/amruthasatyamoorthy)