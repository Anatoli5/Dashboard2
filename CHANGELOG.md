# Changelog

All notable changes to this project will be documented in this file.

## [Current]

### Callback Fixes
- Fixed callback context imports to use `dash.ctx`:
  - Updated in settings.py
  - Updated in data.py
  - Removed deprecated `callback_context` import
  - Using modern Dash import pattern
  - Fixed direct ctx usage in data callbacks
- Corrected component ID references:
  - Changed `log-scale-switch` to `logarithmic-scale`
  - Changed `normalize-switch` to `normalize-prices`
- Ensured consistent state management in callbacks
- Maintained existing theme integration

### CSS Consolidation
- Consolidated CSS into single `frontend/assets/css/main.css`
- Removed redundant root `assets/css/main.css`
- Improved CSS organization:
  - Variables at top
  - Logical component grouping
  - Consistent selector patterns
  - Proper cascade structure

### Styling System Evolution
- Implemented transparency-based visual hierarchy
  - Base colors as foundation
  - Transparent overlays for depth
  - Consistent border styling with rgba(255, 255, 255, 0.15)
- Consolidated theme definitions in `config/themes.py`
- Using CSS variables for consistent styling

### Container Structure
- Removed redundant Chart wrapper div
- Simplified chart container hierarchy:
  ```
  chart-container (handles resize + styling)
    └─ dcc.Graph (chart itself)
  ```
- Each container now has a single, clear purpose

### Chart Optimizations
- Using Scattergl for better performance
- Click-to-normalize functionality
- Dynamic date range handling
- Proper theme integration

### State Management
- Centralized state handling through StateManager
- Proper theme state persistence
- Normalized price state management

### Project Structure
- Frontend-specific assets in `frontend/assets`
- Clear separation of concerns:
  - Theme definitions (`config/themes.py`)
  - Style rules (`frontend/assets/css/main.css`)
  - Component logic (respective files)

## [Key Functionality]

### Chart Features
- WebGL rendering for performance
- Click-to-normalize prices
- Dynamic date range
- Logarithmic scale option
- Multiple ticker support
- Custom color sequence

### Theme System
- Dark theme with transparency layers
- Consistent styling across components
- Bootstrap integration
- CSS variable usage

### Data Management
- Real-time data updates
- Price normalization
- Multiple data providers
- Efficient caching

### UI Components
- Resizable chart container
- Interactive dropdowns
- Date range picker
- Settings modal
- Debug menu

## [Upcoming]
- Theme switcher implementation
- Additional chart interactions
- Performance optimizations
- Enhanced error handling
- Improved state persistence 