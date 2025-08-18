import os
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State

class UnclaimedBalancesDashboard:
    def __init__(self, csv_path:str, default_page_size=20):
        self.csv_path = csv_path
        self.default_page_size = default_page_size
        self.df = self.load_data()
        self.app = self.create_app()
        self.register_callbacks()

    def load_data(self) -> pd.DataFrame:
        """Load and clean the data from CSV"""
        df = pd.read_csv(self.csv_path, dtype=str)

        # Clean Balance to numeric
        df["Balance"] = (
            df["Balance"]
            .str.replace(",", "", regex=False)
            .astype(float)
        )

        # Parse Last Activity Date
        def parse_date(s):
            try:
                return pd.to_datetime(s, format="%d-%b-%Y", errors="raise")
            except Exception:
                return pd.to_datetime(s, errors="coerce")

        df["Last Activity Date"] = df["Last Activity Date"].apply(parse_date)

        # Convert columns to strings
        df["Account Type"] = df["Account Type"].astype(str)
        df["Account Number"] = df["Account Number"].astype(str)
        df["Customer Name"] = df["Customer Name"].astype(str)

        # Derive useful columns
        df["Last Activity Year"] = df["Last Activity Date"].dt.year
        today = pd.Timestamp.today().normalize()
        df["Years Inactive"] = ((today - df["Last Activity Date"]).dt.days / 365.25).round(1)

        # Drop rows with invalid dates or balances <= 0 if any
        df = df.dropna(subset=["Last Activity Date", "Balance"])
        
        return df

    def create_app(self) -> Dash:
        """Create and configure the Dash application"""
        app = Dash(__name__)
        app.title = "Unclaimed Balances Dashboard"
        
        # Precompute options and ranges
        account_type_options = sorted(
            [{"label": t, "value": t} for t in self.df["Account Type"].dropna().unique()],
            key=lambda x: x["value"]  # Sort by the value (account type string)
        )
        balance_min = float(max(0, np.nanmin(self.df["Balance"])))
        balance_max = float(np.nanmax(self.df["Balance"]))
        balance_marks = {int(balance_min): f"{balance_min:,.0f}", int(balance_max): f"{balance_max:,.0f}"}

        years_inactive_min = 0
        years_inactive_max = int(np.nanmax(self.df["Years Inactive"].fillna(0)))
        years_marks = {0: "0", years_inactive_max: str(years_inactive_max)}

        app.layout = self.create_layout(
            account_type_options,
            balance_min,
            balance_max,
            balance_marks,
            years_inactive_min,
            years_inactive_max,
            years_marks
        )
        
        return app

    def create_layout(self, account_type_options, balance_min, balance_max, balance_marks,
                     years_inactive_min, years_inactive_max, years_marks):
        """Create the application layout"""
        return html.Div(
            style={"fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif", 
                  "background": "#f7f7fb", "padding": "24px"},
            children=[
                html.H1("Unclaimed Balances Dashboard", style={"marginBottom": "8px"}),
                html.Div("Interactive analysis with filters for account type, balance range, and inactivity years.", 
                        style={"color": "#555", "marginBottom": "24px"}),

                # Filters
                self.create_filters_section(account_type_options, balance_min, balance_max, 
                                         balance_marks, years_inactive_min, years_inactive_max, years_marks),

                # KPI Row
                self.create_kpi_section(),

                # Charts
                self.create_charts_section(),

                # Data table with export options
                self.create_table_section(),

                html.Div(style={"height": "24px"}),
                html.Div("Tip: Use the filters at the top to explore specific segments. Export or screenshot charts as needed.", 
                        style={"color": "#666"}),
            ]
        )

    def create_filters_section(self, account_type_options, balance_min, balance_max, 
                             balance_marks, years_inactive_min, years_inactive_max, years_marks):
        """Create the filters section"""
        return html.Div(
            style={"display": "grid", "gridTemplateColumns": "3fr 3fr 2fr", "gap": "12px", "marginBottom": "16px"},
            children=[
                html.Div([
                    html.Label("Account Type"),
                    dcc.Dropdown(
                        id="account-type",
                        options=account_type_options,
                        value=[opt["value"] for opt in account_type_options],  # select all by default
                        multi=True,
                        placeholder="Select account types"
                    ),
                ]),
                html.Div([
                    html.Label("Balance Range"),
                    dcc.RangeSlider(
                        id="balance-range",
                        min=balance_min,
                        max=balance_max,
                        step=1,
                        value=[balance_min, balance_max],
                        tooltip={"placement": "bottom", "always_visible": False},
                        allowCross=False,
                        marks=balance_marks,
                    ),
                ], style={"padding": "8px 12px"}),
                html.Div([
                    html.Label("Minimum Years Inactive"),
                    dcc.Slider(
                        id="years-inactive",
                        min=years_inactive_min,
                        max=years_inactive_max,
                        step=1,
                        value=0,
                        marks=years_marks,
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ], style={"padding": "8px 12px"}),
            ],
        )

    def create_kpi_section(self):
        """Create the KPI cards section"""
        return html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(5, 1fr)", "gap": "12px", "marginBottom": "16px"},
            children=[
                self.create_kpi_card("Total Accounts", "—", "kpi-total-accounts"),
                self.create_kpi_card("Total Unclaimed Balance", "—", "kpi-total-balance"),
                self.create_kpi_card("Average Balance", "—", "kpi-avg-balance"),
                self.create_kpi_card("Oldest Last Activity", "—", "kpi-oldest"),
                self.create_kpi_card("Most Recent Activity", "—", "kpi-newest"),
            ],
        )

    def create_kpi_card(self, title, value, id=None):
        """Create a single KPI card"""
        return html.Div(
            className="kpi-card",
            children=[
                html.Div(title, className="kpi-title"),
                html.Div(value, className="kpi-value", id=id),
            ],
            style={"padding": "16px", "borderRadius": "16px", "boxShadow": "0 2px 10px rgba(0,0,0,0.08)", "background": "white"}
        )

    def create_charts_section(self):
        """Create the charts section with consistent heights"""
        chart_style = {
        'height': '60vh',  # 60% of viewport height
        'width': '100%'
     }
        
        return html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "16px"},
            children=[
                html.Div([
                    html.H3("Total Balance by Account Type"),
                    dcc.Graph(id="by-type", style=chart_style),
                ], style={"background": "white", "padding": "12px", "borderRadius": "16px", "boxShadow": "0 2px 10px rgba(0,0,0,0.08)"}),
                html.Div([
                    html.H3("Balance Distribution"),
                    dcc.Graph(id="balance-hist", style=chart_style),
                ], style={"background": "white", "padding": "12px", "borderRadius": "16px", "boxShadow": "0 2px 10px rgba(0,0,0,0.08)"}),
                html.Div([
                    html.H3("Total Unclaimed Balance by Last Activity Year"),
                    dcc.Graph(id="by-year", style=chart_style),
                ], style={"background": "white", "padding": "12px", "borderRadius": "16px", "boxShadow": "0 2px 10px rgba(0,0,0,0.08)"}),
                html.Div([
                    html.H3("Top 10 Accounts by Balance"),
                    dcc.Graph(id="top-accounts", style=chart_style),
                ], style={"background": "white", "padding": "12px", "borderRadius": "16px", "boxShadow": "0 2px 10px rgba(0,0,0,0.08)"}),
            ],
        )

    def create_table_section(self):
        """Create the data table section with export options"""
        return html.Div([
            html.Div([
                html.H3("Filtered Accounts (Table)"),
                html.Div([
                    dcc.Input(
                        id="page-size-input",
                        type="number",
                        min=1,
                        max=100,
                        value=self.default_page_size,
                        style={"width": "80px", "marginRight": "10px"}
                    ),
                    html.Button("Export to CSV", id="export-btn", style={
                        "marginLeft": "10px",
                        "padding": "8px 16px",
                        "background": "#4CAF50",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "4px",
                        "cursor": "pointer"
                    }),
                    dcc.Download(id="download-dataframe-csv"),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"}),
            ]),
            dash_table.DataTable(
                id="top-table",
                page_size=self.default_page_size,
                sort_action="native",
                filter_action="native",
                style_table={
                    "overflowX": "auto",
                    "maxHeight": "600px",
                    "overflowY": "auto"
                },
                style_cell={
                    "padding": "8px",
                    "whiteSpace": "normal",
                    "height": "auto",
                    "textAlign": "left",
                    "border": "1px solid #eee"
                },
                style_header={
                    "backgroundColor": "#f8f9fa",
                    "fontWeight": "bold",
                    "border": "1px solid #ddd"
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)"
                    }
                ],
                columns=[
                    {"name": "Customer Name", "id": "Customer Name"},
                    {"name": "Account Number", "id": "Account Number"},
                    {"name": "Account Type", "id": "Account Type"},
                    {"name": "Last Activity Date", "id": "Last Activity Date"},
                    {"name": "Balance", "id": "Balance", "type": "numeric", "format": {"specifier": "$.2f"}},
                    {"name": "Years Inactive", "id": "Years Inactive", "type": "numeric", "format": {"specifier": ".1f"}},
                ],
            ),
        ], style={"background": "white", "padding": "12px", "borderRadius": "16px", "boxShadow": "0 2px 10px rgba(0,0,0,0.08)"})

    def register_callbacks(self):
        """Register all Dash callbacks"""
        @self.app.callback(
            [
                Output("kpi-total-accounts", "children"),
                Output("kpi-total-balance", "children"),
                Output("kpi-avg-balance", "children"),
                Output("kpi-oldest", "children"),
                Output("kpi-newest", "children"),
                Output("by-type", "figure"),
                Output("balance-hist", "figure"),
                Output("by-year", "figure"),
                Output("top-accounts", "figure"),
                Output("top-table", "data"),
                Output("top-table", "page_size"),
            ],
            [
                Input("account-type", "value"),
                Input("balance-range", "value"),
                Input("years-inactive", "value"),
                Input("page-size-input", "value"),
            ],
        )
        def update_dashboard(account_types, balance_range, min_years_inactive, page_size):
            filtered = self.apply_filters(account_types, balance_range, min_years_inactive)

            # KPIs
            total_accounts = len(filtered)
            total_balance = filtered["Balance"].sum() if total_accounts else 0.0
            avg_balance = (filtered["Balance"].mean() if total_accounts else 0.0)
            oldest = filtered["Last Activity Date"].min() if total_accounts else None
            newest = filtered["Last Activity Date"].max() if total_accounts else None

            kpi_total_accounts = f"{total_accounts:,}"
            kpi_total_balance = self.fmt_currency(total_balance)
            kpi_avg_balance = self.fmt_currency(avg_balance)
            kpi_oldest = oldest.strftime("%d %b %Y") if pd.notnull(oldest) else "—"
            kpi_newest = newest.strftime("%d %b %Y") if pd.notnull(newest) else "—"

            # Figures
            fig_by_type = self.create_by_type_figure(filtered)
            fig_hist = self.create_balance_hist_figure(filtered)
            fig_by_year = self.create_by_year_figure(filtered)
            fig_top = self.create_top_accounts_figure(filtered)
            table_data = self.create_table_data(filtered)

            return (
                kpi_total_accounts,
                kpi_total_balance,
                kpi_avg_balance,
                kpi_oldest,
                kpi_newest,
                fig_by_type,
                fig_hist,
                fig_by_year,
                fig_top,
                table_data,
                page_size if page_size else self.default_page_size,
            )

        @self.app.callback(
            Output("download-dataframe-csv", "data"),
            Input("export-btn", "n_clicks"),
            State("account-type", "value"),
            State("balance-range", "value"),
            State("years-inactive", "value"),
            prevent_initial_call=True,
        )
        def export_data(n_clicks, account_types, balance_range, min_years_inactive):
            filtered = self.apply_filters(account_types, balance_range, min_years_inactive)
            
            # Format the Last Activity Date before exporting
            filtered = filtered.copy()
            filtered["Last Activity Date"] = filtered["Last Activity Date"].dt.strftime("%Y-%m-%d")
            
            return dcc.send_data_frame(
                filtered.to_csv,
                filename=f"unclaimed_balances_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                index=False
            )

    def apply_filters(self, account_types, balance_range, min_years_inactive):
        """Apply filters to the dataframe"""
        lo, hi = balance_range
        mask = (
            self.df["Account Type"].isin(account_types)
            & (self.df["Balance"] >= lo)
            & (self.df["Balance"] <= hi)
            & (self.df["Years Inactive"] >= min_years_inactive)
        )
        return self.df.loc[mask].copy()

    def fmt_currency(self, x: float) -> str:
        """Format a number as currency"""
        try:
            return f"${x:,.2f}"
        except Exception:
            return "—"

    def create_by_type_figure(self, filtered_df):
        """Create the 'by account type' bar chart with controlled scaling"""
        by_type = filtered_df.groupby("Account Type", as_index=False)["Balance"].sum().sort_values("Balance", ascending=False)
        fig = px.bar(
            by_type, 
            x="Account Type", 
            y="Balance", 
            title=None, 
            labels={"Balance": "Total Balance"}
        )
        fig.update_yaxes(rangemode="tozero")  # Ensure y-axis starts at zero
        return fig

    def create_balance_hist_figure(self, filtered_df):
        """Create the balance histogram with controlled bins and scaling"""
        max_balance = filtered_df["Balance"].max()
        fig = px.histogram(
            filtered_df, 
            x="Balance", 
            nbins=50, 
            title=None,
            range_x=[0, max_balance * 1.1]  # Add 10% padding
        )
        fig.update_yaxes(rangemode="tozero")
        return fig

    def create_by_year_figure(self, filtered_df):
        """Create the 'by year' line chart with consistent scaling"""
        by_year = filtered_df.dropna(subset=["Last Activity Year"]).groupby("Last Activity Year", as_index=False)["Balance"].sum()
        fig = px.line(
            by_year, 
            x="Last Activity Year", 
            y="Balance", 
            markers=True, 
            title=None, 
            labels={"Last Activity Year": "Year"}
        )
        fig.update_yaxes(rangemode="tozero")
        return fig

    def create_top_accounts_figure(self, filtered_df):
        """Create the top accounts horizontal bar chart with consistent scaling"""
        top10 = filtered_df.nlargest(10, "Balance")[["Customer Name", "Balance"]]
        fig = px.bar(
            top10[::-1], 
            x="Balance", 
            y="Customer Name", 
            orientation="h", 
            title=None, 
            labels={"Balance": "Balance", "Customer Name": "Customer"},
            range_x=[0, top10["Balance"].max() * 1.1]  # Add 10% padding
        )
        return fig

    def create_table_data(self, filtered_df):
        """Prepare data for the table"""
        top20 = filtered_df.nlargest(20, "Balance").copy()
        top20["Last Activity Date"] = top20["Last Activity Date"].dt.strftime("%d %b %Y")
        top20["Balance"] = top20["Balance"].round(2)
        return top20[[
            "Customer Name", "Account Number", "Account Type", "Last Activity Date", "Balance", "Years Inactive"
        ]].to_dict("records")

    def run(self, host="0.0.0.0", port=None, debug=False):
        """Run the Dash server"""
        port = port or int(os.environ.get("PORT", 8050))
        self.app.run(host=host, port=port, debug=debug)