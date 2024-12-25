# Changelog

## [Unreleased]

### Version History (0.14.0 to 0.15.0)

#### Version 0.15.0 (November 19, 2024)
- Breaking Changes:
  - Renamed `DatePicker` to `DatePickerInput` to align with upstream Mantine library
  - Date input changes:
    - Split `DatePickerRange` into separate `DatePickerInput` components
    - Props renamed: `min_date_allowed` → `minDate`, `max_date_allowed` → `maxDate`
    - Values are now in 'YYYY-MM-DD' format
  - Theme changes:
    - Removed Bootstrap theme system
    - Using Mantine's native theme system with `colorScheme` prop
    - Theme values: 'dark', 'light', 'auto'
    - Theme is managed through MantineProvider
  - Callback changes:
    - Added `allow_duplicate=True` for overlapping outputs
    - Added `prevent_initial_call=True` where needed
    - Updated to use `ctx.triggered_id` for trigger detection
  - Prop name changes:
    - `weight` → `fw` (font-weight) in Text components
    - `position` → `justify` in Group components
    - `spacing` → `gap` in Stack components
  - Removed props:
    - `inherit` from MantineProvider (use theme object directly)
    - `centered` from Modal
  - Theme object changes:
    - `colorScheme` is now managed by `useMantineColorScheme` hook
    - `dir` is now managed by `DirectionProvider`
    - Removed: `loader`, `transitionTimingFunction`, `focusRingStyles`, `activeStyles`, `globalStyles`, `fn`
    - Added: `scale`, `fontSmoothing`, `variantColorResolver`

#### Version 0.14.7 (November 5, 2024)
- New Features:
  - Added `autoScroll` prop to Carousel
  - New chart types: CompositeChart and BubbleChart
  - Added `n_submit` and `n_blur` props for input callbacks
- Changes:
  - Updated debounce prop to accept True/False/milliseconds
  - Upgraded to Mantine 7.13.4
- Fixes:
  - Fixed base64 images in Avatar
  - Fixed boxWrapperProps in Hovercard

#### Version 0.14.6 (October 16, 2024)
- New Features:
  - Added `autoplay` prop to Carousel
  - Added ChipGroup component
  - Added figure animation and right Y-axis support
- Changes:
  - Reduced package size
  - Upgraded to Mantine 7.13.2
- Fixes:
  - Improved loading state handling
  - Fixed Popover callbacks
  - Enhanced Stepper navigation

#### Version 0.14.5 (September 29, 2024)
- New Features:
  - Added MonthPickerInput and YearPickerInput
  - Enhanced BarChart with new props
- Fixes:
  - Improved date parsing with valueFormat
  - Fixed locale persistence
  - Updated Select/MultiSelect option handling

#### Version 0.14.4 (August 7, 2024)
- New Features:
  - Added readOnly prop to inputs
  - Added Spoiler state control
- Fixes:
  - Fixed base64 image support
  - Improved DateTimePicker parsing
  - Fixed MenuItem disabled state

#### Version 0.14.0 (April 14, 2024)
- Breaking Changes:
  - Upgraded to Mantine v7
  - Renamed DatePicker to DatePickerInput
- New Components:
  - NProgress
  - Chart components
  - Carousel
  - TagsInput
  - Burger

### Important Dash Requirements
- Static assets (CSS, JS, etc.) must be in `/assets/` directory at the root level
- Dash automatically loads all files from the root `/assets/` directory
- Moving assets to subdirectories (e.g., `/frontend/assets/`) breaks Dash's asset loading

### Dash Mantine Components v0.15.0 Notes

#### Component Changes
- `DatePicker` was renamed to `DatePickerInput`
  - This aligns with upstream Mantine library
  - `DatePickerInput` is an input field with dropdown calendar
  - Standalone `DatePicker` will be added in future releases

#### Label Support
- Components with `label` prop support:
  - `DatePickerInput`: Adds label above the input field
  - `Select`: Adds label above the dropdown
  - `MultiSelect`: Adds label above the multi-select field
  - `TextInput`: Adds label above the text input
- Components without `label` prop:
  - `ColorPicker`: Use separate `Text` component for labels
  - `Button`: Use separate `Text` component for labels
  - `Switch`: Use separate `Text` component for labels

#### Grid Components
- Different spacing props for different grid components:
  - `dmc.Grid`: Uses `gutter` prop for spacing between columns
  - `dmc.SimpleGrid`: Uses `spacing` prop for spacing between columns
  - Both accept Mantine theme sizes ("xs", "sm", "md", "lg", "xl") or pixel values
  - Example: `spacing="md"` or `gutter={20}`

#### Tabs Implementation
- Uses a combination of components:
  - `dmc.Tabs`: Main container
  - `dmc.TabsList`: Container for tab buttons
  - `dmc.TabsTab`: Individual tab buttons
  - `dmc.TabsPanel`: Content panels for each tab

#### Spacing System
- Different props for different components:
  - `gutter`: Used in Grid components for spacing between items
  - `spacing`: Used in SimpleGrid and other components
  - `gap`: Used in Stack and Flex containers
  - `m` and `p` prefixed props (e.g., `mb`, `mt`, `px`) for margins and padding

### Styling Implementation Notes

#### What Works (Current Implementation)
- Dash dropdowns use older React-Select classes (`.Select-control`, `.Select-menu-outer`, etc.)
- Dark theme is achieved through `.dash-dropdown-dark` class with explicit `!important` rules
- Background colors are set directly on Select components: `#1a1a1a` for backgrounds, `#444` for borders
- All dropdown states (hover, focus, selected) are properly handled with specific class selectors

#### What Doesn't Work (Failed Attempts)
- ❌ Using newer React-Select class names (`.Select__control`, `.Select__menu`, etc.)
- ❌ Trying to implement a new theme system on top of Bootstrap themes
- ❌ Removing `!important` declarations that override Dash defaults
- ❌ Creating separate theme files instead of using existing `main.css`
- ❌ Using CSS variables for colors when direct color values work
- ❌ Overcomplicating the styling with unnecessary abstraction layers
- ❌ Placing assets in subdirectories like `/frontend/assets/` where Dash can't find them

#### Correct Approach
1. Keep using the existing `.dash-dropdown-dark` class
2. Maintain `!important` rules for Dash component overrides
3. Use direct color values that are known to work
4. Target the correct React-Select class names:
   - `.Select-control` (not `.Select__control`)
   - `.Select-menu-outer` (not `.Select__menu`)
   - `.Select-option` (not `.Select__option`)
   - `.Select-value` (not `.Select__value`)
5. Keep all static assets in the root `/assets/` directory

#### Key CSS Rules to Preserve
```css
.dash-dropdown-dark .Select-control {
    background-color: #1a1a1a !important;
    border-color: #444 !important;
    color: white !important;
}

.dash-dropdown-dark .Select-menu-outer {
    background-color: #1a1a1a !important;
    border: 1px solid #444 !important;
}

.dash-dropdown-dark .Select-option {
    background-color: #1a1a1a !important;
    color: white !important;
}
``` 