# Financial Dashboard Project Guide

## I. Core Concepts & Purpose

### Project Purpose
A financial dashboard designed for real-time tracking and analysis of financial instruments (stocks and cryptocurrencies), focusing on clear data visualization and user customization.

### Core Functionality
1. Data Tracking & Display
   - Multi-ticker tracking with real-time updates
   - Interactive price charts with customizable parameters
   - Support for multiple time intervals (from 1 hr to one month)
   - Price Normalization:
     - Converts absolute prices to relative performance (percentage basis)
     - There's a normalize-switch in the UI to toggle normalization
     - The normalization date (norm_date) can be set by:
         - Clicking any point on the chart
         - Using the saved reference from state
         - Defaulting to the last available data point
     - Formula: (current_price / reference_price) * 100
     - Enables direct performance comparison regardless of asset price scales
   - Data normalization and logarithmic scaling capabilities
   - Theme switching (dark/light modes support)
   - Dinamic data range selection(with chart zooming)
     - performance check: (data range/interval*number of reflected charts) < performance limit
   - Persistent user preferences

2. Tools
   - Python
   - SQLlite
   - Dash
   - Dash Mantine Components

3. Data Management
   - Multiple data provider support (Yahoo Finance, Alpha Vantage)
   - Historical data retrieval
   - Real-time data updates
   - Data caching and persistence

## II. Principles & Architecture

### Core Principles

1. Single Source of Truth
   - Centralized state management
   - One source for theme definitions
   - Centralized asset management
   - No duplicate configurations

2. Clean Code & Separation of Concerns
   - Clear component responsibilities
   - Modular architecture
   - Consistent coding patterns and styling
   - Proper error handling

3. Performance & Efficiency
   - Optimized data loading
   - Efficient state updates
   - Minimal DOM nesting
   - Smart caching strategies


2. State Management
   - File-based persistence
   - Centralized state handling
   - Predictable state updates
   - Error-resistant design

3. Data Flow
   - Unidirectional data flow
   - Clear update patterns
   - Controlled side effects
   - Proper error boundaries

## III. Implementation Guidelines



### Development Guidelines

1. Component Development
   - Single responsibility principle
   - Clear props interface
   - Proper error handling
   - Performance optimization

2. State Management
   - Atomic updates
   - Error-resistant operations
   - Clear update patterns
   - State persistence

3. Error Handling
   - Graceful degradation
   - User feedback
   - Error recovery
   - Logging

4. Testing Strategy
   - Component testing
   - State management testing
   - Integration testing
   - End-to-end testing

## IV. Dash Mantine Components v0.15.0 Guide

### Version Information
- Based on Mantine v7.0.0
- Breaking changes from previous versions
- New component architecture
- Important Note: The DatePicker rename to DatePickerInput aligns with upstream Mantine Library. A standalone DatePicker component is planned for future releases.
- Stability Note: Fewer breaking changes are expected going forward compared to past versions.


### Breaking Changes for Dash Mantine Components v0.15.0

1. Component Renames
   - `DatePicker` → `DatePickerInput`
   - Split `DatePickerRange` into separate `DatePickerInput` components

2. Date Input Changes
   - Props renamed:
     - `min_date_allowed` → `minDate`
     - `max_date_allowed` → `maxDate`
   - Values now in 'YYYY-MM-DD' format
   - New date parsing system

3. Theme System Changes
   - Removed Bootstrap theme system
   - Using Mantine's native theme system
   - Theme values: 'dark', 'light', 'auto'
   - Theme managed through MantineProvider
   - Removed props:
     - `inherit` from MantineProvider
     - `centered` from Modal

4. Prop Name Changes & Replacements
   - Layout:
     - `position` → `justify` in Group (for alignment control)
     - `spacing` → `gap` in Stack (for vertical spacing)
     - `spacing` → `gutter` in Grid (for grid gaps)
   - Typography:
     - `weight` → `fw` in Text components (for font weight)
   - Removed props and their replacements:
     - `loader` → Use `LoadingOverlay` component instead
     - `transitionTimingFunction` → Use `transitionProps` object
     - `focusRingStyles` → Use `styles.focusRing` in theme
     - `activeStyles` → Use `styles.active` in theme
     - `globalStyles` → Use `styles` prop or CSS files
     - `fn` → Use theme tokens and style props
     - `inherit` → Configure theme object directly
     - `centered` → Use `centered` prop on Modal's parent or `justify="center"`

### Callback Implementation

1. Pattern Changes
```python
@app.callback(
    Output("component-id", "prop", allow_duplicate=True),
    Input("trigger-id", "value"),
    prevent_initial_call=True
)
```

2. New Requirements
   - Use `allow_duplicate=True` for overlapping outputs
   - Add `prevent_initial_call=True` where needed
   - Use `ctx.triggered_id` for trigger detection

### Component Structure

1. Tabs Implementation
```python
dmc.Tabs([
    dmc.TabsList([
        dmc.TabsTab("Tab 1", value="tab1"),
        dmc.TabsTab("Tab 2", value="tab2"),
    ]),
    dmc.TabsPanel("Content 1", value="tab1"),
    dmc.TabsPanel("Content 2", value="tab2"),
], value="tab1")
```

2. Date Input Implementation
```python
dmc.DatePickerInput(
    id='date-input',
    label="Select Date",
    placeholder="Pick date",
    valueFormat="YYYY-MM-DD",
    minDate="2020-01-01",
    maxDate="2024-12-31"
)
```

3. Grid System
```python
dmc.Grid(
    children=[
        dmc.Col(span=6, children=[...]),
        dmc.Col(span=6, children=[...])
    ],
    gutter="md"  # Instead of spacing
)
```

### Common Issues & Solutions

1. React Version Issues
   - Always include React 18 scripts
   - Check component compatibility
   - Use correct initialization

2. Styling Issues
   - Use Mantine's theme system
   - Keep static assets in root
   - Use proper CSS hierarchy
   - Minimal style overrides

3. Component Props
   - Check documentation for v0.15.0
   - Use correct prop names
   - Verify prop types
   - Handle deprecated props

### Performance Optimization

1. Component Optimization
   - Proper prop usage
   - Minimal re-renders
   - Efficient callbacks

2. Style Optimization
   - Use theme variables
   - Efficient selectors
   - Minimal overrides

### Theme Implementation Notes

1. CSS Variables
   - Use Mantine's CSS variables system
   - Define custom properties through theme
   - Access via `var(--mantine-*)`

2. Style Overrides
   - Use `styles` prop for component customization
   - Avoid direct CSS where possible
   - Use theme tokens for consistency

3. Dark Mode
   - Use `colorScheme` for theme switching
   - Implement proper color variables
   - Handle transitions correctly

### MantineProvider Configuration

1. Supported Props
   ```python
   dmc.MantineProvider(
       theme=theme,                    # Theme configuration
       withStaticClasses=True,         # Enable static classes
       children=[...],                 # App content
       classNamesPrefix="mantine",     # Class prefix
       colorSchemeManager=...,         # Color scheme management
       cssVariablesResolver=...,       # CSS variables resolution
       cssVariablesSelector=":root",   # CSS variables target
       deduplicateCssVariables=True,   # Prevent duplicate CSS vars
       defaultColorScheme="dark",      # Default color scheme
       forceColorScheme=None,          # Force specific scheme
       id="mantine",                   # Provider ID
       stylesTransform=...,            # Style transformation
       withCssVariables=True,          # Enable CSS variables
       withGlobalClasses=True          # Enable global classes
   )
   ```

2. Not Supported Props
   - ❌ `withGlobalStyles` (removed in v0.15.0) → Replace with:
      - Use `theme.components` for component-level styles
      - Use external CSS files for global styles
      - Use `styles` prop on MantineProvider for global overrides
   - ❌ `inherit` (removed in v0.15.0) → Replace with:
      - Direct theme configuration in theme object
      - Use `theme.components` for component-specific styles
      - Use theme tokens and CSS variables

### Component Label Support

1. Components with Native Label Prop
   ```python
   # These components accept label prop directly
   dmc.DatePickerInput(label="Select Date", ...)
   dmc.Select(label="Choose Option", ...)
   dmc.MultiSelect(label="Select Multiple", ...)
   dmc.TextInput(label="Enter Text", ...)
   ```

2. Components Requiring Separate Label
   ```python
   # These need separate Text component
   dmc.Stack([
       dmc.Text("Choose Color"),
       dmc.ColorPicker(...),
   ])

   dmc.Stack([
       dmc.Text("Toggle Option"),
       dmc.Switch(...),
   ])
   ```

### Grid System Details

1. Grid Components
   ```python
   # Regular Grid - uses gutter
   dmc.Grid(
       children=[...],
       gutter="md"  # xs, sm, md, lg, xl or number
   )

   # SimpleGrid - uses spacing
   dmc.SimpleGrid(
       children=[...],
       spacing="md",  # xs, sm, md, lg, xl or number
       cols=3
   )
   ```

2. Spacing Values
   - Theme sizes: "xs", "sm", "md", "lg", "xl"
   - Pixel values: 10, 20, etc.
   - Example: `gutter={20}` or `spacing="md"`

### Detailed Tabs Implementation

1. Complete Structure
   ```python
   dmc.Tabs(
       value="tab1",  # Active tab value
       children=[
           # Tab buttons container
           dmc.TabsList([
               dmc.TabsTab("Settings", value="tab1"),
               dmc.TabsTab("Messages", value="tab2"),
               dmc.TabsTab("Account", value="tab3"),
           ]),
           
           # Content panels
           dmc.TabsPanel(
               "Settings Content",
               value="tab1",
               pt="xs"  # Padding top
           ),
           dmc.TabsPanel(
               "Messages Content",
               value="tab2",
               pt="xs"
           ),
           dmc.TabsPanel(
               "Account Content",
               value="tab3",
               pt="xs"
           ),
       ]
   )
   ```

2. Value Management
   ```python
   @app.callback(
       Output("tabs", "value"),
       Input("tabs", "value"),
       prevent_initial_call=True
   )
   def handle_tab_change(value):
       return value
   ```

3. Styling Options
   ```python
   dmc.Tabs(
       # Tab styling
       color="blue",
       variant="default",
       radius="sm",
       orientation="horizontal",
       
       # Placement
       placement="top",
       
       # Animation
       keepMounted=True,
       
       children=[...]
   )
   ```

## V. Change Management
Document changes: Record modifications to data processing, UI components, or state management
Update changelog: Note breaking changes, especially around Mantine component usage and data handling
Track functionality: Ensure core features (normalization, multi-ticker support, theme switching) remain working
Prevent regressions: Maintain list of known issues and their solutions in documentation
