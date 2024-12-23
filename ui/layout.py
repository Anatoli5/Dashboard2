# File: ui/layout.py

import streamlit as st
import plotly.graph_objects as go
import plotly.utils
import pandas as pd
import numpy as np
import json
import asyncio
import websockets
import threading
from datetime import datetime, date
from core.settings_manager import SettingsManager
from core.chart_manager import ChartManager
import streamlit.components.v1 as components


class PlotlyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Plotly figures"""
    def default(self, obj):
        try:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            if isinstance(obj, (np.float64, np.float32, np.float16)):
                return float(obj)
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            if pd.isna(obj):
                return None
            return plotly.utils.PlotlyJSONEncoder().default(obj)
        except:
            return str(obj)


class PlotlyEventServer:
    """WebSocket server to handle Plotly events"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlotlyEventServer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not PlotlyEventServer._initialized:
            self.port = 8765
            self.server = None
            self.loop = None
            self.thread = None
            PlotlyEventServer._initialized = True
    
    async def handler(self, websocket, path):
        """Handle WebSocket connections and messages"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'click':
                        date_str = data.get('date')
                        if date_str:
                            clicked_date = pd.to_datetime(date_str)
                            st.session_state.norm_date = clicked_date
                            st.session_state.needs_rerun = True
                            st.session_state.data_cache = {}
                            st.experimental_rerun()
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
        except websockets.exceptions.ConnectionClosed:
            pass
    
    def start_server(self):
        """Start the WebSocket server in a separate thread"""
        async def serve():
            async with websockets.serve(self.handler, "localhost", self.port):
                await asyncio.Future()  # run forever
        
        def run():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(serve())
            self.loop.run_forever()
        
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=run, daemon=True)
            self.thread.start()


class InteractivePlotly:
    """Plotly wrapper with WebSocket event handling"""
    def __init__(self):
        self.event_server = PlotlyEventServer()
        self.event_server.start_server()
    
    def render(self, fig):
        """Render Plotly figure with WebSocket event handling"""
        # Convert figure to JSON
        fig_json = json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder)
        config_json = json.dumps(ChartManager.CHART_CONFIG, cls=PlotlyJSONEncoder)
        
        # Create component with WebSocket connection
        components.html(
            f"""
            <div id="plotly-chart" style="width: 100%; height: 600px;"></div>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                (function() {{
                    // Create WebSocket connection
                    const ws = new WebSocket('ws://localhost:8765');
                    
                    // Parse figure data
                    const figData = {fig_json};
                    const config = {config_json};
                    
                    // Create the plot
                    Plotly.newPlot('plotly-chart', figData.data, figData.layout, config).then(function() {{
                        const plot = document.getElementById('plotly-chart');
                        
                        // Add click event handler
                        plot.on('plotly_click', function(data) {{
                            if (data.points && data.points.length > 0) {{
                                const point = data.points[0];
                                ws.send(JSON.stringify({{
                                    type: 'click',
                                    date: point.x
                                }}));
                            }}
                        }});
                    }});
                    
                    // WebSocket error handling
                    ws.onerror = function(error) {{
                        console.error('WebSocket Error:', error);
                    }};
                    
                    ws.onclose = function(event) {{
                        console.log('WebSocket connection closed:', event.code, event.reason);
                    }};
                }})();
            </script>
            """,
            height=600
        )


class DashboardLayout:
    """Handles the main layout of the dashboard"""
    
    _plotly = None
    
    @classmethod
    def get_plotly(cls):
        """Get or create the InteractivePlotly instance"""
        if cls._plotly is None:
            cls._plotly = InteractivePlotly()
        return cls._plotly
    
    @staticmethod
    def setup_page():
        """Setup the page configuration"""
        st.set_page_config(
            page_title="Financial Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None
            }
        )
        
        # Apply base styling
        st.markdown("""
            <style>
                .main .block-container {
                    padding: 1rem;
                    max-width: 100%;
                }
                
                [data-testid="stHorizontalBlock"] > div {
                    width: 100% !important;
                }
                
                #plotly-chart {
                    width: 100% !important;
                }
                
                [data-testid="stSidebar"] {
                    z-index: 1000;
                }
                
                .stCheckbox, .stSelectbox {
                    position: relative;
                    z-index: 1001;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_main_area(fig) -> None:
        """Render the main chart area"""
        try:
            # Create a container for the chart
            with st.container():
                # Use WebSocket-enabled Plotly wrapper
                plotly = DashboardLayout.get_plotly()
                plotly.render(fig)

                # Display normalization reference date if set
                norm_date = st.session_state.get('norm_date')
                if norm_date is not None:
                    st.write("**Normalization Reference Date:**", norm_date.strftime('%Y-%m-%d'))
        except Exception as e:
            st.error(f"Error rendering chart: {str(e)}")
            raise

