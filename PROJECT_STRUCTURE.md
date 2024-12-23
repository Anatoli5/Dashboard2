# Project Structure

## Root Directory
```
project/
├── app.py                 # Main Dash application entry point
│
├── frontend/             # Frontend-related code
│   ├── components/       # UI Components
│   │   ├── __init__.py
│   │   ├── chart/
│   │   │   ├── price_chart.py
│   │   │   └── chart_controls.py
│   │   ├── sidebar/
│   │   │   ├── controls.py
│   │   │   └── filters.py
│   │   └── ticker_list/
│   │       ├── list_view.py
│   │       └── list_editor.py
│   │
│   ├── layouts/         # Page layouts and structure
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── dashboard.py
│   │
│   ├── callbacks/       # UI interaction handlers
│   │   ├── __init__.py
│   │   ├── chart.py
│   │   ├── sidebar.py
│   │   └── ticker.py
│   │
│   └── assets/         # Static assets
│       ├── css/
│       └── js/
│
├── backend/            # Backend-related code
│   ├── __init__.py
│   │
│   ├── data/          # Data handling
│   │   ├── __init__.py
│   │   ├── providers/     # Data source providers
│   │   │   ├── yahoo.py
│   │   │   └── alpha_vantage.py
│   │   ├── database/      # Database operations
│   │   │   ├── models.py
│   │   │   └── operations.py
│   │   └── manager.py     # Data management logic
│   │
│   ├── services/      # Business logic services
│   │   ├── __init__.py
│   │   ├── ticker_service.py
│   │   └── chart_service.py
│   │
│   └── utils/         # Utility functions
│       ├── __init__.py
│       ├── date_utils.py
│       └── calculations.py
│
├── state/             # State management
│   ├── __init__.py
│   ├── store.py      # Central state store
│   ├── actions.py    # State actions/mutations
│   └── selectors.py  # State access patterns
│
├── config/           # Configuration
│   ├── __init__.py
│   ├── settings.py   # App settings
│   └── theme.py      # Theme configuration
│
└── requirements.txt  # Project dependencies
```

## Architecture Overview

### Frontend Layer
- **Components**: Pure UI components with minimal logic
- **Layouts**: Page structure and component composition
- **Callbacks**: UI interaction handlers
- **Assets**: Static resources

### Backend Layer
- **Data**: Data access and manipulation
  - Providers: External data source integrations
  - Database: Local data storage
  - Manager: Data orchestration
- **Services**: Business logic implementation
- **Utils**: Helper functions and utilities

### State Management
Central state management system:
- **Store**: State container and management
- **Actions**: State modifications
- **Selectors**: State access patterns

## Data Flow
```
Frontend Components
      ↕
   Callbacks
      ↕
State Management
      ↕
Backend Services
      ↕
Data Layer (Providers/Database)
```

## Migration Strategy

1. **Phase 1 - Core Structure**:
   - Set up basic directory structure
   - Migrate essential dependencies
   - Create basic app entry point

2. **Phase 2 - Backend Migration**:
   - Move data providers
   - Set up database operations
   - Implement services

3. **Phase 3 - State Management**:
   - Implement state store
   - Define actions and selectors
   - Set up state persistence

4. **Phase 4 - Frontend Migration**:
   - Implement core components
   - Set up layouts
   - Create callbacks

5. **Phase 5 - Integration**:
   - Connect frontend to state
   - Link state to backend
   - Implement full data flow

## State Management Details

1. **Central Store**:
   - Uses Dash's dcc.Store for client-side state
   - Implements browser's localStorage for persistence
   - Manages application-wide state

2. **State Categories**:
   - UI State (current view, filters, etc.)
   - Data State (cached data, results)
   - User Preferences (theme, settings)

3. **State Access Patterns**:
   - Components access state through selectors
   - State updates through defined actions
   - Automatic state persistence

## Development Guidelines

1. **Component Development**:
   - Stateless where possible
   - Clear props interface
   - Documented behavior

2. **State Management**:
   - Single source of truth
   - Predictable state updates
   - Clear update patterns

3. **Data Handling**:
   - Cached where appropriate
   - Clear error handling
   - Loading states

4. **Testing Strategy**:
   - Unit tests for services
   - Integration tests for data flow
   - Component tests for UI
   - End-to-end tests for critical paths