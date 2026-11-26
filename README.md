📊 B2B Sales Pipeline Analytics

An interactive data analytics dashboard designed to analyze B2B sales performance, monitor pipeline health, identify sales opportunities, and support data-driven business decisions.

🚀 Project Overview

The B2B Sales Pipeline Analytics project provides insights into the sales pipeline by tracking revenue, deal performance, sales representatives, conversion rates, lead sources, and forecasting.

The dashboard helps sales teams and business stakeholders understand their pipeline performance, identify high-priority opportunities, and improve sales strategies through interactive visualizations and predictive analytics.

🎯 Objectives

- Analyze overall B2B sales performance.
- Track pipeline revenue and open opportunities.
- Monitor sales conversion and win rates.
- Identify factors influencing successful deal closures.
- Analyze sales representatives' performance.
- Predict deal closure probability using Machine Learning.
- Prioritize high-value deals.
- Forecast future sales performance.

✨ Features

📈 Sales KPI Dashboard

Monitor key performance indicators:

- Total Revenue
- Win Rate
- Average Deal Size
- Average Sales Cycle
- Open Pipeline Value

🔍 Interactive Filters

Filter sales data based on:

- Region
- Customer Segment
- Industry
- Lead Source
- Sales Representative
- Deal Stage

💰 Pipeline Analysis

Analyze deals across different sales stages:

- Lead
- Qualified
- Demo
- Negotiation
- Closed Won
- Closed Lost

🏆 Sales Performance Analysis

Evaluate sales representatives based on:

- Revenue generated
- Number of deals
- Conversion rate
- Average deal size
- Pipeline contribution

📊 Win Rate Analysis

Identify the factors that influence deal success, including:

- Lead source
- Industry
- Customer segment
- Deal amount
- Sales stage
- Sales representative performance

🔮 Sales Forecasting

Forecast future sales performance using historical pipeline data and sales trends.

🤖 Predictive Deal Scoring

A Machine Learning model predicts the probability of a deal being successfully closed.

This helps sales teams prioritize opportunities with a higher likelihood of conversion.

📋 Top Open Deals

Display high-priority opportunities based on deal value, sales stage, and predicted win probability.

---

📊 Dashboard Insights

The dashboard provides key business metrics, including:

KPI| Description
Total Revenue| Revenue generated from closed deals
Win Rate| Percentage of opportunities successfully converted
Average Deal Size| Average value of closed deals
Average Sales Cycle| Average time taken to close a deal
Open Pipeline| Total value of active sales opportunities

Example Dashboard Metrics

- Revenue: $7.69M
- Win Rate: 17.1%
- Average Deal Size: $20,610
- Average Sales Cycle: 63 Days
- Open Pipeline: $8.53M

Metrics shown are based on the dashboard screenshot and may change depending on dataset filters.

---

🛠️ Tech Stack

- Python – Data processing and analytics
- Pandas – Data manipulation
- NumPy – Numerical computations
- Plotly – Interactive visualizations
- Streamlit – Dashboard development
- Scikit-learn – Machine Learning and predictive modeling
- Matplotlib / Seaborn – Data visualization

---

🤖 Machine Learning

The project uses Logistic Regression to estimate the probability of a sales deal being successfully closed.

Model Workflow

1. Data preprocessing
2. Feature selection
3. Encoding categorical variables
4. Train-test split
5. Model training using Logistic Regression
6. Probability prediction
7. Model evaluation

Model Evaluation

The model is evaluated using metrics such as:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

The dashboard screenshot indicates a reported ROC-AUC score of approximately 0.82 for the deal prediction model.

---

📂 Project Structure

B2B-Sales-Pipeline-Analytics/
│
├── app.py
├── data/
│   └── sales_pipeline.csv
│
├── models/
│   └── deal_scoring_model.pkl
│
├── notebooks/
│   └── sales_analysis.ipynb
│
├── requirements.txt
├── README.md
└── .gitignore

Adjust the folder structure above according to your actual repository files.

---

⚙️ Installation & Setup

1. Clone the Repository

https://b2b-sales-pipeline-analytics-4eu2dejawdmzxkgxumcpmv.streamlit.app/

2. Navigate to the Project Folder

cd B2B-Sales-Pipeline-Analytics

3. Create a Virtual Environment

python -m venv venv

4. Activate the Environment

Windows:

venv\Scripts\activate

5. Install Dependencies

pip install -r requirements.txt

6. Run the Dashboard

streamlit run app.py

The dashboard will open in your browser at:

https://b2b-sales-pipeline-analytics-4eu2dejawdmzxkgxumcpmv.streamlit.app/

---

📦 Requirements

Example dependencies:

streamlit
pandas
numpy
plotly
scikit-learn
matplotlib
seaborn

---

📌 Business Impact

This project helps organizations:

- Improve sales visibility.
- Identify high-value opportunities.
- Optimize lead conversion strategies.
- Monitor sales team performance.
- Reduce time spent on low-probability deals.
- Improve sales forecasting.
- Make data-driven decisions.
- Identify bottlenecks in the sales process.

---

🔮 Future Improvements

- Real-time CRM integration.
- Automated sales alerts.
- Advanced forecasting using time-series models.
- Customer segmentation.
- Automated pipeline reports.
- Integration with Salesforce or HubSpot.
- Deployment using Streamlit Cloud.
- Advanced AI-powered sales recommendations.

---

👩‍💻 Author

Antra Roy

BCA – Data Science

Interested in Data Analytics, Machine Learning, Business Intelligence, and Data-Driven Decision Making.

---

⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

---
