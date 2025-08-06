# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# === Configuration ===
st.set_page_config(
    page_title="Mortgage Calculator Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Data Preparation ===
COUNTRIES = {
    "United States": {
        "currency": "USD",
        "default_rate": 7.0,
        "flag": "🇺🇸"
    },
    "Morocco": {
        "currency": "MAD",
        "default_rate": 6.5,
        "flag": "🇲🇦"
    },
    "Eurozone": {
        "currency": "EUR",
        "default_rate": 4.5,
        "flag": "🇪🇺"
    },
    "United Kingdom": {
        "currency": "GBP",
        "default_rate": 6.0,
        "flag": "🇬🇧"
    },
    "Canada": {
        "currency": "CAD",
        "default_rate": 6.5,
        "flag": "🇨🇦"
    },
    "Australia": {
        "currency": "AUD",
        "default_rate": 6.0,
        "flag": "🇦🇺"
    },
    "South Africa": {
        "currency": "ZAR",
        "default_rate": 8.0,
        "flag": "🇿🇦"
    },
    "India": {
        "currency": "INR",
        "default_rate": 7.5,
        "flag": "🇮🇳"
    },
    "Brazil": {
        "currency": "BRL",
        "default_rate": 9.0,
        "flag": "🇧🇷"
    },
    "Japan": {
         "currency": "JPY",
         "default_rate": 3.5,
         "flag": "🇯🇵"
    },
    "Switzerland": {
         "currency": "CHF",
         "default_rate": 2.5,
         "flag": "🇨🇭"
    },
    "Mexico": {
         "currency": "MXN",
         "default_rate": 11.0,
         "flag": "🇲🇽"
    }
}

# === Functions ===
def calculate_mortgage(
    home_value,
    down_payment,
    interest_rate,
    loan_term_years,
    start_date,
    property_tax,
    pmi_rate,
    home_insurance,
    hoa_fee,
    override_rate=None,
    override_term=None
):
    """
    Calculate mortgage details.
    """
    try:
        home_value = float(home_value)
        down_payment = float(down_payment)
        interest_rate_decimal = float(interest_rate) / 100
        loan_term_years = int(loan_term_years)

        if override_term and override_term > 0:
            loan_term_years = int(override_term)

        if override_rate is not None and override_rate > 0:
            interest_rate_decimal = float(override_rate) / 100

        loan_term_months = loan_term_years * 12

        property_tax = float(property_tax)
        pmi_rate_decimal = float(pmi_rate) / 100
        home_insurance = float(home_insurance)
        hoa_fee = float(hoa_fee)

        loan_amount = home_value - down_payment
        monthly_interest_rate = interest_rate_decimal / 12

        if monthly_interest_rate > 0:
            monthly_payment_principal_interest = (
                loan_amount *
                (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) /
                ((1 + monthly_interest_rate) ** loan_term_months - 1)
            )
        else:
            monthly_payment_principal_interest = loan_amount / loan_term_months

        pmi_monthly = loan_amount * pmi_rate_decimal / 12 if loan_amount > 0 else 0.0
        property_tax_monthly = property_tax / 12 if property_tax > 0 else 0.0
        home_insurance_monthly = home_insurance / 12 if home_insurance > 0 else 0.0

        total_monthly_payment = (monthly_payment_principal_interest +
                                property_tax_monthly + pmi_monthly +
                                home_insurance_monthly + hoa_fee)

        total_payments = total_monthly_payment * loan_term_months
        total_interest_paid = (monthly_payment_principal_interest * loan_term_months) - loan_amount
        annual_payment = total_monthly_payment * 12

        loan_payoff_date = start_date.replace(year=start_date.year + loan_term_years)
        if start_date.month == 2 and start_date.day == 29:
            try:
                loan_payoff_date = loan_payoff_date.replace(day=28)
            except ValueError:
                pass

        results = {
            "Loan Amount": loan_amount,
            "Monthly Payment (P&I)": monthly_payment_principal_interest,
            "Total Monthly Payment": total_monthly_payment,
            "Total Interest Paid": total_interest_paid,
            "Loan Payoff Date": loan_payoff_date.strftime("%b %Y"),
            "Annual Payment Amount": annual_payment,
            "Total Payments": total_payments,
            "Property Tax Per Month": property_tax_monthly,
            "PMI Per Month": pmi_monthly,
            "Home Insurance Per Month": home_insurance_monthly,
            "HOA Fee Per Month": hoa_fee,
        }

        return results
    except Exception as e:
        st.error(f"An error occurred during calculation: {e}")
        return None

def generate_yearly_schedule(
    home_value,
    down_payment,
    interest_rate,
    loan_term_years,
    start_date,
    property_tax,
    pmi_rate,
    home_insurance,
    hoa_fee,
    override_rate=None,
    override_term=None
):
    """
    Generate a yearly amortization schedule.
    """
    try:
        results = calculate_mortgage(
            home_value, down_payment, interest_rate, loan_term_years, start_date,
            property_tax, pmi_rate, home_insurance, hoa_fee,
            override_rate=override_rate, override_term=override_term
        )

        if not results:
            return pd.DataFrame()

        loan_amount = float(home_value) - float(down_payment)
        annual_interest_rate = float(interest_rate) / 100
        if override_rate is not None and override_rate > 0:
             annual_interest_rate = float(override_rate) / 100

        loan_term_years = int(loan_term_years)
        if override_term and override_term > 0:
            loan_term_years = int(override_term)

        monthly_rate = annual_interest_rate / 12
        loan_term_months = loan_term_years * 12

        if monthly_rate > 0:
            monthly_payment_pi = (
                loan_amount *
                (monthly_rate * (1 + monthly_rate) ** loan_term_months) /
                ((1 + monthly_rate) ** loan_term_months - 1)
            )
        else:
            monthly_payment_pi = loan_amount / loan_term_months

        schedule_data = []
        balance = loan_amount

        for year in range(1, loan_term_years + 1):
            yearly_interest = 0.0
            yearly_principal = 0.0

            for month in range(12):
                if balance <= 0:
                    break
                interest_payment = balance * monthly_rate
                principal_payment = monthly_payment_pi - interest_payment
                balance -= principal_payment

                if balance < 0:
                    principal_payment += balance
                    balance = 0.0

                yearly_interest += interest_payment
                yearly_principal += principal_payment

            schedule_data.append({
                "Year": year,
                "Date": start_date.replace(year=start_date.year + year - 1).strftime("%Y"),
                "Principal": yearly_principal,
                "Interest": yearly_interest,
                "Ending Balance": balance
            })

            if balance <= 0:
                # If loan is paid off, fill remaining years with zeros
                for remaining_year in range(year + 1, loan_term_years + 1):
                    schedule_data.append({
                        "Year": remaining_year,
                        "Date": start_date.replace(year=start_date.year + remaining_year - 1).strftime("%Y"),
                        "Principal": 0.0,
                        "Interest": 0.0,
                        "Ending Balance": 0.0
                    })
                break

        df_schedule = pd.DataFrame(schedule_data)
        return df_schedule
    except Exception as e:
        st.error(f"An error occurred while generating the yearly schedule: {e}")
        return pd.DataFrame()

def generate_monthly_schedule(
    home_value,
    down_payment,
    interest_rate,
    loan_term_years,
    start_date,
    property_tax,
    pmi_rate,
    home_insurance,
    hoa_fee,
    override_rate=None,
    override_term=None
):
    """
    Generate a monthly amortization schedule (first year + last year).
    """
    try:
        results = calculate_mortgage(
            home_value, down_payment, interest_rate, loan_term_years, start_date,
            property_tax, pmi_rate, home_insurance, hoa_fee,
            override_rate=override_rate, override_term=override_term
        )

        if not results:
            return pd.DataFrame()

        loan_amount = float(home_value) - float(down_payment)
        annual_interest_rate = float(interest_rate) / 100
        if override_rate is not None and override_rate > 0:
             annual_interest_rate = float(override_rate) / 100

        loan_term_years = int(loan_term_years)
        if override_term and override_term > 0:
            loan_term_years = int(override_term)

        monthly_rate = annual_interest_rate / 12
        loan_term_months = loan_term_years * 12

        if monthly_rate > 0:
            monthly_payment_pi = (
                loan_amount *
                (monthly_rate * (1 + monthly_rate) ** loan_term_months) /
                ((1 + monthly_rate) ** loan_term_months - 1)
            )
        else:
            monthly_payment_pi = loan_amount / loan_term_months

        schedule_data = []
        balance = loan_amount
        current_date = start_date

        total_months = loan_term_months

        # Generate data for the first 12 months and the last 12 months
        months_to_show = list(range(1, min(13, total_months + 1))) # First 12 months
        if total_months > 12:
            months_to_show.extend(range(max(total_months - 11, 13), total_months + 1)) # Last 12 months

        for month in range(1, total_months + 1):
            if month not in months_to_show:
                # Skip months not in our display range
                interest_payment = balance * monthly_rate
                principal_payment = monthly_payment_pi - interest_payment
                balance -= principal_payment
                if balance < 0:
                    balance = 0.0
                continue

            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment_pi - interest_payment
            ending_balance = balance - principal_payment

            # Ensure balance doesn't go negative
            if ending_balance < 0:
                principal_payment += ending_balance # Adjust last payment
                ending_balance = 0.0

            schedule_data.append({
                "Month": month,
                "Date": current_date.strftime("%b %Y"),
                "Principal": principal_payment,
                "Interest": interest_payment,
                "Ending Balance": ending_balance
            })

            balance = ending_balance
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

            if balance <= 0:
                break

        df_schedule = pd.DataFrame(schedule_data)
        return df_schedule
    except Exception as e:
        st.error(f"An error occurred while generating the monthly schedule: {e}")
        return pd.DataFrame()

def plot_yearly_schedule(df_schedule, currency, selected_country):
    """Plot the improved yearly amortization schedule."""
    if df_schedule.empty:
        st.warning("No data to display for the yearly schedule.")
        return

    # Create a line chart for Principal, Interest, and Balance
    fig = go.Figure()

    # Add Principal payments (positive values)
    fig.add_trace(go.Scatter(
        x=df_schedule['Year'],
        y=df_schedule['Principal'],
        mode='lines+markers',
        name='Principal',
        line=dict(color='#2E8B57', width=2),
        marker=dict(size=6),
        hovertemplate='<b>Year %{x}</b><br>Principal: %{y:,.2f} ' + currency + '<extra></extra>'
    ))

    # Add Interest payments (positive values)
    fig.add_trace(go.Scatter(
        x=df_schedule['Year'],
        y=df_schedule['Interest'],
        mode='lines+markers',
        name='Interest',
        line=dict(color='#DC143C', width=2),
        marker=dict(size=6),
        hovertemplate='<b>Year %{x}</b><br>Interest: %{y:,.2f} ' + currency + '<extra></extra>'
    ))

    # Add Balance (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df_schedule['Year'],
        y=df_schedule['Ending Balance'],
        mode='lines',
        name='Balance',
        line=dict(color='#1E90FF', width=3, dash='dot'),
        yaxis='y2',
        hovertemplate='<b>Year %{x}</b><br>Balance: %{y:,.2f} ' + currency + '<extra></extra>'
    ))

    # Update layout with secondary y-axis
    fig.update_layout(
        title=f"Yearly Loan Amortization ({selected_country})",
        xaxis_title="Year",
        yaxis_title=f"Amount ({currency})",
        yaxis2=dict(
            title=f"Loan Balance ({currency})",
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_monthly_schedule(df_schedule, currency, selected_country):
    """Plot the monthly amortization schedule."""
    if df_schedule.empty:
        st.warning("No data to display for the monthly schedule.")
        return

    # Create a stacked area chart for Principal and Interest
    # Melt the DataFrame for easier plotting
    df_plot = df_schedule.melt(id_vars=['Month', 'Date'], value_vars=['Principal', 'Interest'],
                               var_name='Component', value_name='Amount')

    fig = px.area(
        df_plot,
        x='Month',
        y='Amount',
        color='Component',
        title=f"Monthly Loan Amortization (Sample Months) ({selected_country})",
        labels={'Amount': f'Amount ({currency})', 'Month': 'Payment Number'},
        color_discrete_map={'Principal': '#2E8B57', 'Interest': '#DC143C'}
    )

    # Improve hover data to show the date
    fig.update_traces(
        hovertemplate='<b>Month %{x}</b><br>' +
                      '<b>%{meta}</b>: %{y:,.2f} ' + currency + '<br>' +
                      '<b>Date</b>: %{customdata}<extra></extra>',
        customdata=df_schedule['Date']
    )

    fig.update_layout(
        xaxis_title="Payment Number (Month)",
        yaxis_title=f"Amount ({currency})",
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# === Main App Logic ===
st.title("Mortgage Calculator Dashboard")

with st.sidebar:
    st.header("Configuration")
    selected_country = st.selectbox("Select Country", list(COUNTRIES.keys()))
    currency = COUNTRIES[selected_country]["currency"]
    default_rate = COUNTRIES[selected_country]["default_rate"]
    flag = COUNTRIES[selected_country]["flag"]

    st.markdown(f"**Selected Country:** {flag} {selected_country}")

    st.subheader("Override Options")
    override_rate = st.number_input(
        "Override Interest Rate (%)",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        help="Enter 0.0 to use the default rate for the selected country"
    )
    override_term = st.number_input(
        "Override Loan Term (Years)",
        min_value=0,
        value=0,
        step=1,
        help="Enter 0 to use the term from the main input field"
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("Loan Details")
    home_value = st.number_input("Home Value", min_value=0.0, value=400000.0, step=1000.0, format="%.2f")
    down_payment = st.number_input("Down Payment", min_value=0.0, value=80000.0, step=1000.0, format="%.2f")
    display_rate = override_rate if override_rate > 0 else default_rate
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=display_rate, step=0.01, format="%.2f")
    loan_term_years = st.number_input("Loan Term (Years)", min_value=1, value=30, step=1)

with col2:
    st.subheader("Additional Costs & Start Date")
    today = date.today()
    start_date = st.date_input("Start Date", value=today, format="MM/DD/YYYY")
    property_tax = st.number_input(f"Property Tax (Annual, {currency})", min_value=0.0, value=3000.0, step=100.0, format="%.2f")
    st.markdown("**Private Mortgage Insurance (PMI):** Required if down payment is less than 20%.")
    pmi_rate = st.number_input("PMI Rate (%)", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Typically 0.3% to 1.5% of the loan amount annually.")
    home_insurance = st.number_input(f"Home Insurance (Annual, {currency})", min_value=0.0, value=1500.0, step=100.0, format="%.2f")
    st.markdown("**Homeowners Association (HOA) Fee:** Monthly fee for community maintenance.")
    hoa_fee = st.number_input(f"Monthly HOA Fee ({currency})", min_value=0.0, value=0.0, step=10.0, format="%.2f")

if st.button("Calculate", type="primary"):
    final_override_rate = override_rate if override_rate > 0 else None
    final_override_term = override_term if override_term > 0 else None

    results = calculate_mortgage(
        home_value,
        down_payment,
        interest_rate,
        loan_term_years,
        start_date,
        property_tax,
        pmi_rate,
        home_insurance,
        hoa_fee,
        override_rate=final_override_rate,
        override_term=final_override_term
    )

    if results:
        st.subheader("Loan Summary")
        st.markdown(f"Here's a breakdown of your estimated {selected_country} mortgage:")

        sum_col1, sum_col2, sum_col3 = st.columns(3)
        with sum_col1:
            st.metric(label="🏠 Loan Amount", value=f"{results['Loan Amount']:,.2f} {currency}")
            st.metric(label="💰 Monthly Payment (P&I)", value=f"{results['Monthly Payment (P&I)']:.2f} {currency}")
        with sum_col2:
            st.metric(label="📉 Total Interest Paid", value=f"{results['Total Interest Paid']:,.2f} {currency}")
            st.metric(label="📅 Loan Payoff Date", value=results['Loan Payoff Date'])
        with sum_col3:
            st.metric(label="📊 Total Payments", value=f"{results['Total Payments']:,.2f} {currency}")
            st.metric(label="📈 Annual Payment", value=f"{results['Annual Payment Amount']:,.2f} {currency}")

        # --- Amortization Schedules ---
        # Yearly Schedule
        df_yearly_schedule = generate_yearly_schedule(
            home_value,
            down_payment,
            interest_rate,
            loan_term_years,
            start_date,
            property_tax,
            pmi_rate,
            home_insurance,
            hoa_fee,
            override_rate=final_override_rate,
            override_term=final_override_term
        )

        # Monthly Schedule (Sample)
        df_monthly_schedule = generate_monthly_schedule(
            home_value,
            down_payment,
            interest_rate,
            loan_term_years,
            start_date,
            property_tax,
            pmi_rate,
            home_insurance,
            hoa_fee,
            override_rate=final_override_rate,
            override_term=final_override_term
        )

        if not df_yearly_schedule.empty or not df_monthly_schedule.empty:
            st.subheader("Loan Amortization Schedule")

            # Tabs for Yearly and Monthly
            tab_yearly, tab_monthly = st.tabs(["Yearly Breakdown", "Monthly Breakdown (Sample)"])

            with tab_yearly:
                if not df_yearly_schedule.empty:
                    st.markdown("This chart shows the yearly breakdown of principal, interest, and remaining loan balance.")
                    plot_yearly_schedule(df_yearly_schedule, currency, selected_country)

                    with st.expander("See detailed yearly schedule data"):
                        formatted_yearly_df = df_yearly_schedule.copy()
                        for col in formatted_yearly_df.select_dtypes(include=['number']).columns:
                            if col != 'Year': # Don't add currency to 'Year'
                                formatted_yearly_df[col] = formatted_yearly_df[col].apply(lambda x: f"{x:,.2f} {currency}")
                        # Drop the 'Year' column for display as requested previously, but it's useful for plotting
                        display_yearly_df = formatted_yearly_df.drop(columns=['Year'])
                        st.dataframe(display_yearly_df, use_container_width=True)
                else:
                    st.warning("Yearly schedule could not be generated.")

            with tab_monthly:
                if not df_monthly_schedule.empty:
                    st.markdown("This chart shows the monthly breakdown of principal and interest for the first and last year of the loan.")
                    plot_monthly_schedule(df_monthly_schedule, currency, selected_country)

                    with st.expander("See detailed monthly schedule data (Sample)"):
                        formatted_monthly_df = df_monthly_schedule.copy()
                        for col in formatted_monthly_df.select_dtypes(include=['number']).columns:
                            if col != 'Month': # Don't add currency to 'Month'
                                formatted_monthly_df[col] = formatted_monthly_df[col].apply(lambda x: f"{x:,.2f} {currency}")
                        # Drop the 'Month' column for display as it's less critical in the table view
                        display_monthly_df = formatted_monthly_df.drop(columns=['Month'])
                        st.dataframe(display_monthly_df, use_container_width=True)
                else:
                    st.warning("Monthly schedule could not be generated.")


        # --- Monthly Payment Breakdown ---
        st.subheader("Monthly Payment Breakdown")
        st.markdown("Here's how your total monthly payment is calculated:")
        breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
        with breakdown_col1:
            st.metric(label="Principal & Interest", value=f"{results['Monthly Payment (P&I)']:.2f} {currency}")
        with breakdown_col2:
            st.metric(label="Property Tax", value=f"{results['Property Tax Per Month']:.2f} {currency}")
            st.metric(label="PMI", value=f"{results['PMI Per Month']:.2f} {currency}")
        with breakdown_col3:
            st.metric(label="Home Insurance", value=f"{results['Home Insurance Per Month']:.2f} {currency}")
            st.metric(label="HOA Fee", value=f"{results['HOA Fee Per Month']:.2f} {currency}")

        st.markdown("---")
        st.markdown(f"**Total Monthly Payment:** **{results['Total Monthly Payment']:.2f} {currency}**")
        st.markdown("*This estimate includes principal, interest, taxes, insurance, and HOA fees.*")

st.markdown("---")
st.caption("© 2025 Mortgage Calculator Dashboard")
st.caption("Note: Default interest rates and financial rules are sourced from official central bank websites and financial institutions. "
           "These are placeholders. Please verify current rates before making decisions. "
           "You can override default values with the most up-to-date information as needed.")
