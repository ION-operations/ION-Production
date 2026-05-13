# NL Tags API Integration Guide

**Created:** 2025-10-31  
**Status:** Backend API endpoints created

## API Endpoints Created

FastAPI router with endpoints:
- `GET /nl-tags/file?path={file_path}` - Get tags for file
- `GET /nl-tags/coverage?module={module}` - Coverage statistics
- `GET /nl-tags/validate?path={file_path}` - Validate tags
- `GET /nl-tags/issues?path={file_path}` - Get validation issues
- `POST /nl-tags/suggest` - Suggest tags for code block
- `GET /nl-tags/health` - Health check

## Integration

To integrate into main API server:

```python
from packages.nl_tags.api import router as nl_tags_router

app.include_router(nl_tags_router)
```

## Status

- ✅ API endpoints created
- ✅ Pydantic models defined
- ✅ Error handling implemented
- ⏳ Integration with main API server (pending)
- ⏳ Phase 2 HHNI validation (pending)
- ⏳ Phase 4 VIF suggestions (pending)

## Next Steps

1. Integrate router into main API server (CMC API or MCP server)
2. Test endpoints with real data
3. Begin Phase 2: HHNI semantic validation

