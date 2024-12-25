# Changelog

## [Unreleased]

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

#### Correct Approach
1. Keep using the existing `.dash-dropdown-dark` class
2. Maintain `!important` rules for Dash component overrides
3. Use direct color values that are known to work
4. Target the correct React-Select class names:
   - `.Select-control` (not `.Select__control`)
   - `.Select-menu-outer` (not `.Select__menu`)
   - `.Select-option` (not `.Select__option`)
   - `.Select-value` (not `.Select__value`)

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