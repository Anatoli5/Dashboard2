# Changelog

## [Latest] - 2024-01-07

### Working
- Basic app functionality with Dash Mantine Components
- React 18 compatibility achieved with explicit script inclusion
- State management system with proper error handling
- Theme switching and persistence

### Needs Restoration
- Log scale functionality
- Normalization functionality
- Theme styling verification (possible older version being used)

### Implementation Notes
- Keep using `.dash-dropdown-dark` class and maintain `!important` rules for Dash component overrides
- React-Select class names must be targeted correctly for styling
- All static assets must be kept in root `/assets/` directory
- State management now uses a file-based approach with proper error handling
- Default state includes: selected_tickers, interval, log_scale, normalize, start_date, end_date, norm_date, theme

### Component Changes
- MantineProvider configuration updated:
  - Removed `inherit` prop
  - Added `withGlobalClasses` and `withCssVariables`
  - Theme structure includes colorScheme, primaryColor, and component-specific styles

### State Management
- File-based state persistence in `app_state.json`
- Default values provided for all state properties
- Error handling for file operations
- Methods available:
  - `get_state(key, default)`: Get single value
  - `set_state(key, value)`: Set single value
  - `get_full_state()`: Get entire state
  - `load_state()`: Alias for get_full_state
  - `update_state(updates)`: Batch update multiple values 