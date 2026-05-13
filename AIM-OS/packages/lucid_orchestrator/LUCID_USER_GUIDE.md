# 🧠 Lucid Orchestrator User Guide

## Overview

The Lucid Orchestrator transforms your IDE into a "visor to the organism" - providing real-time code intelligence that understands your code's specifications, relationships, performance, and governance. This guide will help you master all the powerful features.

## 🚀 Quick Start

### 1. Launch the System
```bash
# Windows
launch_lucid_ide.bat

# Manual launch
# Terminal 1: Start daemon
cd packages/lucid_orchestrator/daemon
python http_daemon.py

# Terminal 2: Start IDE
cd packages/ide_chat_app
npm run dev
```

### 2. Open a Code File
- Open any TypeScript/JavaScript file in the IDE
- Look for gutter icons next to functions and components
- Click `[SPEC]`, `[BLUEPRINT]`, or `[TIMELINE]` to explore intelligence

## 🎯 Core Features

### SPEC Folds - Code Specifications
**What it shows:**
- **Responsibility**: What the code is supposed to do
- **Must Never**: Critical constraints and forbidden behaviors
- **Inputs/Outputs**: Data flow specifications
- **Security Level**: Risk classification (low/medium/high/critical)
- **Performance Budget**: Maximum allowed execution time
- **Status**: Current health (clean/drift/violation)
- **Governance**: Change history and approvals

**How to use:**
1. Click `[SPEC]` next to any function/component
2. Review the specification and constraints
3. Use "Propose Change" for modifications
4. Monitor drift status for violations

### BLUEPRINT Folds - Code Relationships
**What it shows:**
- **Center Node**: The current function/component
- **Incoming Dependencies**: What calls this code
- **Outgoing Dependencies**: What this code calls
- **Blast Radius**: Impact analysis of changes
- **Edge Types**: How components connect (calls, updatesUI, queriesDB, etc.)

**How to use:**
1. Click `[BLUEPRINT]` to see relationship graph
2. Understand code dependencies
3. Assess change impact before modifying
4. Navigate to related components

### TIMELINE Folds - Performance Monitoring
**What it shows:**
- **Recent Executions**: Last few runs with timing
- **Performance Metrics**: Average duration, violations
- **Execution Cascade**: Step-by-step breakdown of slow runs
- **Violation Tracking**: When constraints are breached

**How to use:**
1. Click `[TIMELINE]` to see performance data
2. Monitor execution times and violations
3. Identify performance bottlenecks
4. Track improvement over time

## 🤝 Collaboration Features

### Real-Time Collaboration
- **Multi-user Support**: See other developers working on the same code
- **Live Cursors**: View where team members are focused
- **Shared Focus**: Synchronized node focus across team
- **Collaborative Folds**: Team members can see your intelligence views

### How to Collaborate
1. **Enable Collaboration**: Set `enableCollaboration={true}` in editor
2. **View Team**: Click the users indicator in top-right
3. **Share Focus**: When you focus a node, team sees it
4. **Sync Folds**: Your fold states are shared with team

## 🎨 Advanced Features

### Change Proposals
**What it does:**
- Analyzes blast radius of proposed changes
- Identifies affected components and risks
- Requires governance approval for high-risk changes
- Tracks change rationale and accountability

**How to use:**
1. Click "Propose Change" in any SPEC fold
2. Review blast radius and risk factors
3. Add rationale for the change
4. Get required approvals before proceeding

### Node Navigation
**What it does:**
- Jump between related components
- Auto-open SPEC folds for focused nodes
- Maintain context across navigation
- Track exploration history

**How to use:**
1. Click on node names in BLUEPRINT folds
2. Use keyboard shortcuts for quick navigation
3. Follow the relationship graph to understand architecture

## 🔧 Configuration

### Editor Settings
```typescript
<CollaborativeLucidMonacoEditor
  enableLucidFolds={true}        // Enable/disable intelligence folds
  enableCollaboration={true}     // Enable/disable real-time collaboration
  theme="vs-dark"               // Editor theme
  readOnly={false}              // Read-only mode
/>
```

### Daemon Configuration
```python
# In http_daemon.py
app.run(
  host='0.0.0.0',    # Allow external connections
  port=5000,         # Daemon port
  debug=True         # Development mode
)
```

## 📊 Understanding the Data

### Status Indicators
- 🟢 **Clean**: Code meets all specifications
- 🟡 **Drift**: Minor violations, needs attention
- 🔴 **Violation**: Critical issues, immediate action required

### Security Levels
- **Low**: Public-facing, minimal risk
- **Medium**: Internal use, moderate risk
- **High**: Sensitive data, significant risk
- **Critical**: Security-critical, maximum risk

### Performance Budgets
- **UI Components**: < 16ms (60fps)
- **API Calls**: < 500ms
- **Data Processing**: < 100ms
- **Background Tasks**: < 1000ms

## 🚨 Troubleshooting

### Common Issues

**Daemon Not Connecting**
```bash
# Check if daemon is running
curl http://localhost:5000/api/health

# Restart daemon
cd packages/lucid_orchestrator/daemon
python http_daemon.py
```

**No Gutter Icons**
- Ensure file is TypeScript/JavaScript
- Check that `enableLucidFolds={true}`
- Verify file has functions/components

**Collaboration Not Working**
- Check `enableCollaboration={true}`
- Verify network connectivity
- Restart both IDE and daemon

**Performance Issues**
- Reduce number of active folds
- Close unused collaboration panels
- Check daemon resource usage

### Debug Mode
```typescript
// Enable debug logging
console.log('Lucid Debug:', {
  symbols: symbols.length,
  activeFolds: Array.from(activeFolds),
  collaborationUsers: collaborationUsers.length
});
```

## 🎯 Best Practices

### For Individual Developers
1. **Review SPECs First**: Always check specifications before modifying code
2. **Monitor Performance**: Use TIMELINE folds to track performance
3. **Understand Dependencies**: Check BLUEPRINT before making changes
4. **Propose Changes**: Use governance workflow for significant changes

### For Teams
1. **Enable Collaboration**: Share intelligence across team
2. **Focus Synchronization**: Use shared focus for code reviews
3. **Change Proposals**: Use governance for team coordination
4. **Regular Reviews**: Check drift status regularly

### For Code Quality
1. **Write Clear SPECs**: Document responsibilities and constraints
2. **Monitor Drift**: Address violations promptly
3. **Performance Budgets**: Set and enforce performance limits
4. **Security Classification**: Properly categorize security levels

## 🔮 Future Features

### Coming Soon
- **Interactive Graph Visualization**: Drag-and-drop relationship editing
- **AI-Powered Spec Generation**: Automatic specification creation
- **Performance Prediction**: ML-based performance forecasting
- **Code Quality Scoring**: Automated quality metrics
- **Integration Testing**: Automated constraint validation

### Advanced Integrations
- **Git Integration**: Link changes to commits
- **CI/CD Pipeline**: Automated quality gates
- **Monitoring Integration**: Real-time performance data
- **Security Scanning**: Automated vulnerability detection

## 💡 Tips and Tricks

### Keyboard Shortcuts
- `Ctrl+Shift+L`: Toggle Lucid Intelligence panel
- `Ctrl+Shift+F`: Focus on current symbol
- `Ctrl+Shift+B`: Open Blueprint view
- `Ctrl+Shift+T`: Open Timeline view

### Power User Features
- **Bulk Operations**: Select multiple symbols for batch analysis
- **Custom Filters**: Filter by security level, performance, or status
- **Export Data**: Export intelligence data for analysis
- **Custom Views**: Create personalized intelligence dashboards

## 🆘 Support

### Getting Help
1. **Check this guide** for common solutions
2. **Review console logs** for error messages
3. **Test with sample code** to isolate issues
4. **Check daemon status** at http://localhost:5000/api/health

### Reporting Issues
When reporting issues, include:
- IDE version and browser
- Daemon status and logs
- Code file type and content
- Steps to reproduce
- Expected vs actual behavior

## 🎉 Conclusion

The Lucid Orchestrator transforms how you understand and work with code. By providing real-time intelligence about specifications, relationships, and performance, it enables you to build better software with greater confidence.

**Remember**: This is not just a tool - it's a "visor to the organism" that helps you see the living structure of your codebase.

Happy coding with Lucid intelligence! 🧠✨
