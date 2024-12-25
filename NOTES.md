# Development Guidelines

## Core Principles
1. Single Source of Truth
   - One location for assets (`assets/` directory)
   - One source for theme definitions
   - Centralized state management
   - No duplicate configurations

2. Visual Hierarchy Through Transparency
   - Base colors as foundation
   - Transparency layers for depth
   - Example layers:
     - Base: Solid background (#000000)
     - Containers: rgba(255, 255, 255, 0.1)
     - Borders: rgba(255, 255, 255, 0.15)
     - Hover: rgba(255, 255, 255, 0.07)

3. Container Structure
   - No redundant wrapper divs
   - Each container has clear, single purpose
   - Example chart structure:
     ```
     chart-container (handles resize + styling)
       └─ dcc.Graph (chart itself)
     ```

4. CSS Organization
   - Variables over direct values
   - Logical cascade structure
   - No style overwriting
   - Clear selector hierarchy

## Project Structure
1. Assets
   - Single `assets/` directory at root
   - No duplicate asset directories
   - All static files centralized

2. Styling
   - Theme definitions in `config/themes.py`
   - CSS using theme variables
   - Transparency for visual hierarchy
   - Consistent naming convention

3. State Management
   - Centralized state handling
   - Clear data flow
   - Predictable updates

## Best Practices
1. Container Creation
   - Only create containers with clear purpose
   - No redundant wrappers
   - Document container roles

2. Style Changes
   - Modify variables, not properties
   - Use transparency for depth
   - Follow visual hierarchy
   - Test with high contrast first

3. Performance
   - WebGL for charts (Scattergl)
   - Efficient CSS selectors
   - Minimal DOM nesting
   - Proper event handling

## Testing Process
1. Make dramatic changes first
2. Confirm visibility
3. Get user confirmation
4. Implement subtle styling
5. Get final approval

## Anti-Redundancy Checklist
1. File Structure
   - No duplicate directories
   - Clear organization
   - Proper imports

2. Code
   - No duplicate functions
   - No repeated logic
   - Clear dependencies

3. State
   - Single source of truth
   - Clear update flow
   - No state duplication

4. Styling
   - One theme source
   - Consistent variables
   - No duplicate rules

5. Documentation
   - Clear, non-redundant
   - Purpose-driven
   - Up-to-date

## Change Management
1. Document all changes
2. Keep change history
3. Track key functionality
4. Prevent accidental rollbacks

## When Making Changes
1. Check CHANGELOG.md first
2. Understand feature history
3. Preserve key functionality
4. Document new changes
5. Update both NOTES.md and CHANGELOG.md 