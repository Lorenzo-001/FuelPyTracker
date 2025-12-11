import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def build_price_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Genera il grafico lineare per l'andamento del prezzo carburante."""
    avg_p = df["Prezzo"].mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Data"], y=df["Prezzo"], 
        mode='lines+markers', name='Prezzo', 
        line=dict(color='#EF553B', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df["Data"], y=[avg_p]*len(df), 
        mode='lines', name='Media', 
        line=dict(color='gray', dash='dash')
    ))
    
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=10, b=10), 
        yaxis_title="€ / Litro",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x"
    )
    return fig

def build_efficiency_chart(df: pd.DataFrame) -> go.Figure:
    """Genera il grafico area per l'efficienza (Km/L)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Data"], y=df["Efficienza"], 
        mode='lines+markers', name='Km/L', 
        fill='tozeroy', 
        line=dict(color='#00CC96')
    ))
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=10, b=10), 
        yaxis_title="Km / Litro",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x"
    )
    return fig

def build_spending_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Genera il grafico a barre per la spesa mensile."""
    # Resampling Mensile
    # Nota: usiamo .copy() per non modificare il df originale
    monthly = df.copy().set_index("Data")[["Costo"]].resample("M").sum().reset_index()
    monthly["MeseStr"] = monthly["Data"].dt.strftime('%b %y')
    
    fig = px.bar(
        monthly, x="MeseStr", y="Costo", 
        text_auto='.0f', 
        color_discrete_sequence=['#636EFA']
    )
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=10, b=10), 
        yaxis_title="Totale €", 
        xaxis_title=""
    )
    return fig