from django_plotly_dash import DjangoDash
from dash import dcc, html
from dash.dependencies import Input, Output
from accounts.models import Order
import pandas as pd
import plotly.express as px

app = DjangoDash('OrderStats')

def get_order_data():
    qs = Order.objects.all().values('payment_method', 'is_paid', 'is_verified')
    return pd.DataFrame(qs)

app.layout = html.Div([
    html.H3("Orders Overview"),
    dcc.Graph(id='order-chart'),
])

@app.callback(
    Output('order-chart', 'figure'),
    Input('order-chart', 'id')  # Dummy input to trigger on load
)
def update_chart(_):
    df = get_order_data()
    if df.empty:
        return px.bar(title="No order data available.")
    return px.histogram(df, x='payment_method', color='is_paid', barmode='group', title="Orders by Payment Method")
