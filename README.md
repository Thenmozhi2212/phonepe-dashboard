# phonepe-dashboard

PHONEPE INSIGHTS:
Data Extraction: In this phase, the project initiates with a scripted process to clone the GitHub repository containing PhonePe Pulse data. Utilizing scripting ensures a seamless and automated extraction process. The extracted data is then stored in a structured format, either CSV or JSON, facilitating ease of use in subsequent steps.

Data Transformation: Python, along with the Pandas library, is employed for data manipulation and transformation. This step involves comprehensive data cleaning, addressing missing values, and structuring the dataset to meet the requirements of analysis and visualization. By leveraging Python's powerful data processing capabilities, the dataset is refined and prepared for the next stages.

Database Insertion: Connecting to a POSTGRES database using the "psycopg2" library, the transformed data is efficiently inserted into the database. Utilizing SQL commands, the data is stored securely, ensuring a streamlined approach for storage and retrieval. This step enhances data management capabilities and supports the scalability of the solution.

Dashboard Creation: The visualization aspect is crafted using Streamlit and Plotly libraries in Python. Plotly's geo-map functions are integrated to provide geographical insights visually. The user interface is designed to be intuitive and user-friendly, featuring dropdown options for users to select different metrics and figures. This ensures an interactive and engaging experience for users exploring the PhonePe Pulse data.

Data Retrieval: Connecting back to the POSTGRES database with the "sqlalchemy" library, the project retrieves the stored data into a Pandas dataframe. This dynamic retrieval ensures that the dashboard is consistently updated with the latest information, maintaining its relevance and usefulness over time.

INSIGHTS:
Aggregated transaction geographical view
Transaction insgiths
Insurance insights
Fraud detection
Device dominance


SKILLS TAKE AWAY:
GitHub Cloning
Python
Pandas
POSTGRES
SQLAlchemy
Streamlit
Plotly


