# Comprehensive Panel Diagnostics & Error Reporting System

## Overview

The Panel Diagnostics & Resource Monitor is a comprehensive system for tracking, diagnosing, and reporting issues with IDE panels. It provides real-time monitoring, error tracking, performance metrics, and one-click error reporting capabilities.

## Key Features

### 1. **Multi-View Dashboard**
- **Overview**: Complete panel status with resource usage
- **Errors**: Focused view of panels with errors
- **Performance**: Performance metrics and render statistics
- **Network**: Network request tracking (future enhancement)
- **Diagnostics**: Full diagnostic reports with export capabilities

### 2. **Error Tracking & Reporting**

#### Automatic Error Capture
- All errors caught by `ErrorBoundary` are automatically tracked
- Includes full stack traces, component stacks, and context
- Tracks error resolution status
- Maintains error history (last 50 errors per panel)

#### Error Details Captured
- Error message and stack trace
- React component stack
- Timestamp and resolution status
- User context (user agent, URL, etc.)
- Custom context data

### 3. **One-Click Error Reporting**

#### Copy Functions
- **Copy Diagnostics (JSON)**: Full diagnostic data in JSON format
- **Copy Markdown Report**: Human-readable markdown report
- **Copy Individual Error**: Copy specific error details
- **Download JSON**: Download full diagnostics as JSON file

#### Report Formats

**JSON Format** includes:
```json
{
  "timestamp": "ISO timestamp",
  "summary": {
    "totalPanels": 15,
    "panelsWithErrors": 2,
    "totalErrors": 5,
    "unresolvedErrors": 3
  },
  "panels": [...],
  "fullErrors": [...]
}
```

**Markdown Format** includes:
- Summary statistics
- Detailed error reports per panel
- Performance metrics
- Component stacks and stack traces

### 4. **Performance Monitoring**

#### Metrics Tracked
- **Mount Count**: How many times panel was mounted
- **Render Count**: Total render cycles
- **Load Time**: Initial load duration
- **Average Render Time**: Average render performance
- **Slowest Render**: Worst-case render time
- **Memory Usage**: Estimated memory consumption

#### Integration
- Automatically synced with `resourceTracker`
- Real-time updates during panel lifecycle
- Performance observer integration for accurate timing

### 5. **Panel Status Tracking**

#### Status Types
- **Healthy**: No errors, normal operation
- **Error**: Has unresolved errors
- **Warning**: Performance issues or warnings
- **Loading**: Currently loading
- **Mounted**: Active and visible
- **Cached**: Loaded but not visible

### 6. **Advanced Features**

#### Search & Filter
- Search panels by name or ID
- Filter by status (all, errors, warnings, healthy)
- Real-time filtering as you type

#### Expandable Panel Details
- Click any panel to expand detailed view
- Shows errors, performance metrics, network requests
- Console error tracking
- One-click copy for each section

#### Real-Time Updates
- Auto-refresh toggle (1 second intervals)
- Manual refresh button
- Event-driven updates on errors

## Usage Guide

### Accessing Diagnostics

1. Open the **Resource Monitor** panel (bottom left toolbar)
2. Select view mode from tabs (Overview, Errors, Performance, Diagnostics)
3. Use search and filters to find specific panels

### Reporting Errors

#### For a Specific Panel:
1. Find the panel in the list
2. Click to expand if needed
3. Click **Copy Diagnostics** button next to the panel
4. Paste the JSON into your bug report

#### For All Panels:
1. Go to **Diagnostics** view
2. Click **Copy Full Diagnostics (JSON)** or **Copy Markdown Report**
3. Share with developers or save for debugging

#### For Individual Errors:
1. Expand a panel with errors
2. Click the **Copy** icon next to any error
3. Full error details (message, stack, component stack) copied to clipboard

### Understanding Error Reports

#### Error Structure
- **Error ID**: Unique identifier for tracking
- **Panel**: Which panel encountered the error
- **Message**: Human-readable error message
- **Stack Trace**: JavaScript stack trace
- **Component Stack**: React component hierarchy
- **Timestamp**: When error occurred
- **Resolution Status**: Resolved or unresolved

#### Performance Metrics
- **Mount Count**: Higher = panel frequently opened/closed
- **Render Count**: Higher = frequent re-renders (potential optimization target)
- **Load Time**: Higher = slow initial load (code splitting or bundle size issue)
- **Average Render Time**: Higher = performance bottleneck
- **Slowest Render**: Identifies worst-case scenarios

## Technical Architecture

### Components

1. **ErrorTracker** (`utils/errorTracker.ts`)
   - Central error tracking service
   - Error storage and retrieval
   - Report generation (JSON/Markdown)
   - Event subscription system

2. **ResourceTracker** (`utils/resourceTracker.ts`)
   - Panel lifecycle tracking
   - Memory usage estimation
   - Performance metrics collection
   - Integrated with ErrorTracker

3. **ErrorBoundary** (`components/ErrorBoundary.tsx`)
   - React error boundary wrapper
   - Automatic error reporting to ErrorTracker
   - User-friendly error display

4. **ResourceMonitor** (`panels/ResourceMonitor.tsx`)
   - Comprehensive UI for diagnostics
   - Multi-view dashboard
   - Copy/download functionality
   - Real-time updates

### Data Flow

```
Panel Error Occurs
    ↓
ErrorBoundary catches error
    ↓
ErrorTracker.trackError()
    ↓
Error stored with full context
    ↓
ResourceMonitor displays error
    ↓
User clicks "Copy Diagnostics"
    ↓
ErrorTracker.generateDiagnosticsReport()
    ↓
JSON/Markdown copied to clipboard
```

### Integration Points

- **ErrorBoundary**: Automatically reports all caught errors
- **ResourceTracker**: Syncs performance metrics
- **LazyPanelWrapper**: Tracks panel loading states
- **Performance API**: Uses browser Performance API for timing

## Best Practices

### For Developers

1. **Always use ErrorBoundary**: Wrap panels with ErrorBoundary for automatic error tracking
2. **Provide Panel Names**: Use descriptive `panelName` props for better error reports
3. **Add Context**: Include relevant context when tracking errors manually
4. **Check Diagnostics**: Regularly review diagnostics panel for performance issues

### For Debugging

1. **Start with Overview**: Get high-level view of all panels
2. **Filter to Errors**: Focus on problematic panels
3. **Expand Details**: See full error context
4. **Copy Full Report**: Share complete diagnostics with team
5. **Check Performance**: Identify slow panels in Performance view

### For Error Reports

1. **Include Full Diagnostics**: Copy full JSON report
2. **Add Steps to Reproduce**: Document user actions
3. **Note Browser/Environment**: Include user agent info
4. **Check Related Errors**: Look for patterns across panels

## Future Enhancements

### Planned Features
- Network request tracking per panel
- Console error correlation with panels
- Error grouping and deduplication
- Performance regression detection
- Export to external tools (Sentry, etc.)
- Error resolution workflow
- Historical error trends
- Performance benchmarking

### Integration Opportunities
- React DevTools integration
- Browser DevTools integration
- External error reporting services
- Performance monitoring tools
- Analytics platforms

## API Reference

### ErrorTracker Methods

```typescript
// Track an error
errorTracker.trackError(panelId, panelName, error, errorInfo?, context?)

// Get panel diagnostics
errorTracker.getPanelDiagnostics(panelId)

// Generate reports
errorTracker.generateDiagnosticsReport(panelId?)
errorTracker.generateMarkdownReport(panelId?)

// Subscribe to errors
errorTracker.subscribe((panelId, error) => { ... })

// Update metrics
errorTracker.updatePanelMetrics(panelId, panelName, metrics)
```

### ResourceTracker Integration

```typescript
// Automatically syncs with ErrorTracker
resourceTracker.markMounted(id)
resourceTracker.incrementRenderCount(id)
resourceTracker.recordLoadTime(id, duration)
```

## Summary

This comprehensive diagnostics system provides:
- ✅ **Automatic Error Tracking**: All errors captured automatically
- ✅ **One-Click Reporting**: Copy full diagnostics instantly
- ✅ **Performance Monitoring**: Track render times and memory usage
- ✅ **Multiple Formats**: JSON and Markdown reports
- ✅ **Real-Time Updates**: Live monitoring of panel health
- ✅ **Search & Filter**: Quickly find problematic panels
- ✅ **Detailed Context**: Full error details with stacks and traces

The system is designed to make debugging panel issues as easy as possible, with comprehensive data capture and one-click export capabilities.

