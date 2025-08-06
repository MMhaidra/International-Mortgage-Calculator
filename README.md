# International Mortgage Calculator

A Streamlit web application to calculate and visualize mortgage payments for various countries, featuring dynamic currency selection, adjustable parameters, and amortization schedules.

## Features

*   **International Support:** Select from a list of countries. The currency and default interest rate update automatically.
*   **Dynamic Inputs:** Input fields adapt labels and currency symbols based on the selected country.
*   **Override Options:** Easily override default interest rates and loan terms with custom values.
*   **Comprehensive Calculation:** Calculates monthly payment (Principal & Interest), total interest paid, total payments, loan payoff date, and annual payment.
*   **Detailed Breakdown:** Shows the breakdown of the total monthly payment, including Property Tax, PMI, Home Insurance, and HOA Fees.
*   **Visualizations:**
    *   **Yearly Amortization Chart:** Interactive line chart showing yearly Principal, Interest, and Loan Balance over the loan term.
    *   **Monthly Amortization Chart (Sample):** Area chart showing the monthly Principal vs. Interest for the first and last year of the loan.
*   **Data Tables:** View detailed yearly and monthly amortization schedules.

## How to Use

1.  **Select Country:** Choose a country from the dropdown menu in the sidebar. The currency and default interest rate will update.
2.  **Enter Loan Details:** Fill in the home value, down payment, interest rate, loan term, and start date in the main panel.
3.  **Enter Additional Costs:** Input annual property tax, PMI rate, annual home insurance, and monthly HOA fees.
4.  **Override (Optional):** Use the 'Override Options' in the sidebar to enter specific interest rates or loan terms if needed.
5.  **Calculate:** Click the 'Calculate' button.
6.  **View Results:** Explore the calculated summary, visualizations, and detailed breakdown.

## Technologies Used

*   [Streamlit](https://streamlit.io/) - For creating the web application.
*   [Plotly Express / Graph Objects](https://plotly.com/python/) - For interactive data visualizations.
*   [Pandas](https://pandas.pydata.org/) - For data manipulation and display.

## Running Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/international-mortgage-calculator.git
    cd international-mortgage-calculator
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the app:**
    ```bash
    streamlit run App.py
    ```

## Deployment

This app is designed to be easily deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).

## Note

Default interest rates and financial rules are placeholders based on general information. Please verify current rates with official sources. You can override default values with the most up-to-date information as needed.
