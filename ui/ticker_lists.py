# File: ui/ticker_lists.py

import streamlit as st
from core.ticker_lists import TickerLists
from core.settings_manager import SettingsManager

class TickerListsUI:
    """UI component for managing ticker lists"""

    @staticmethod
    def render_ticker_lists_section():
        """Render the ticker lists management section"""
        st.sidebar.subheader("📋 Ticker Lists")
        
        # Initialize ticker lists
        TickerLists.initialize()
        
        # Create new list button
        if st.sidebar.button("➕ Create New List", key="create_list_btn"):
            st.session_state['show_create_list'] = True
        
        # Create new list form
        if st.session_state.get('show_create_list', False):
            with st.sidebar.form("create_list_form"):
                st.write("Create New List")
                name = st.text_input("List Name")
                description = st.text_area("Description")
                
                # Category selection for available tickers
                provider = SettingsManager.get_setting('data_provider')
                categories = ['crypto', 'stocks', 'indices']
                selected_category = st.selectbox(
                    "Category",
                    options=categories,
                    key="create_list_category"
                )
                
                # Show available tickers for the selected category
                available_tickers = TickerLists.get_available_tickers(provider, selected_category)
                selected_tickers = st.multiselect(
                    "Select Tickers",
                    options=available_tickers,
                    key="create_list_tickers"
                )
                
                submitted = st.form_submit_button("Create")
                if submitted and name and selected_tickers:
                    if TickerLists.create_list(name, description, selected_tickers, provider):
                        st.success(f"Created list: {name}")
                        st.session_state['show_create_list'] = False
                        st.rerun()
                    else:
                        st.error("Failed to create list")
        
        st.sidebar.markdown("---")
        
        # List selector
        lists = st.session_state.ticker_lists['lists']
        active_list = st.session_state.ticker_lists['active_list']
        
        # Create columns for list selection and actions
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            selected_list = st.selectbox(
                "Select List",
                options=list(lists.keys()),
                format_func=lambda x: lists[x]['name'],
                index=list(lists.keys()).index(active_list),
                key="list_selector"
            )
        
        with col2:
            if selected_list != 'default':
                if st.button("🗑️", key=f"delete_{selected_list}"):
                    if TickerLists.delete_list(selected_list):
                        st.success("List deleted")
                        st.rerun()
        
        # Set active list if changed
        if selected_list != active_list:
            TickerLists.set_active_list(selected_list)
            st.rerun()
        
        # Show current list details
        current_list = lists[selected_list]
        st.sidebar.caption(current_list.get('description', ''))
        
        # Edit current list
        st.sidebar.write("Edit List")
        provider = current_list['provider']
        
        # Category tabs for available tickers
        categories = ['crypto', 'stocks', 'indices']
        tabs = st.sidebar.tabs(categories)
        
        for category, tab in zip(categories, tabs):
            with tab:
                available_tickers = TickerLists.get_available_tickers(provider, category)
                selected = [t for t in current_list['tickers'] if t in available_tickers]
                
                new_selection = st.multiselect(
                    f"Select {category.title()}",
                    options=available_tickers,
                    default=selected,
                    key=f"edit_{selected_list}_{category}"
                )
                
                # Update list if selection changed
                if new_selection != selected:
                    # Combine selections from all categories
                    other_tickers = [t for t in current_list['tickers'] if t not in available_tickers]
                    updated_tickers = other_tickers + new_selection
                    if TickerLists.update_list(selected_list, updated_tickers):
                        st.rerun()

    @staticmethod
    def get_selected_tickers() -> list:
        """Get tickers from the active list"""
        TickerLists.initialize()
        active_list = TickerLists.get_active_list()
        return active_list['tickers'] 