# MBS Matching System - API Documentation

## Overview

The MBS Matching System provides a comprehensive REST API for intelligent Medicare Benefits Schedule item matching and validation. The API supports multiple search methods, voice input processing, and advanced validation features.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Content Type

All API requests and responses use JSON format with `Content-Type: application/json`.

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes
- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Core Endpoints

### 1. System Health

#### GET /health
Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_items": 5989,
  "rules_loaded": 9
}
```

#### GET /api
Get API information and available interfaces.

**Response:**
```json
{
  "message": "MBS Matching System API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "web_interface": "/static/enhanced_index_en.html",
  "chinese_interface": "/chinese",
  "classic_interface": "/classic"
}
```

### 2. Search Endpoints

#### POST /suggest_items
Traditional TF-IDF-based search for MBS items.

**Request Body:**
```json
{
  "transcript": "Patient symptom description",
  "context": {
    "setting": "consulting_rooms",
    "duration": 30,
    "provider": "general practitioner",
    "referral": false,
    "date": "2024-01-01T00:00:00Z",
    "patient_type": "community"
  },
  "top_k": 10
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "item_num": "3",
      "description": "Professional attendance by a general practitioner...",
      "score": 0.85,
      "evidence": "Keyword match: consultation",
      "group": "A1",
      "category": 1,
      "provider_type": "General Practitioner"
    }
  ],
  "total_found": 10
}
```

#### POST /suggest_items_enhanced
Advanced search with multiple search types (TF-IDF, Semantic, Hybrid).

**Query Parameters:**
- `search_type` (string): Search type - "tfidf", "semantic", or "hybrid" (default: "hybrid")

**Request Body:**
```json
{
  "transcript": "Patient symptom description",
  "context": {
    "setting": "consulting_rooms",
    "duration": 30,
    "provider": "general practitioner",
    "referral": false,
    "date": "2024-01-01T00:00:00Z",
    "patient_type": "community"
  },
  "top_k": 10
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "item_num": "3",
      "description": "Professional attendance by a general practitioner...",
      "score": 0.92,
      "evidence": "Semantic match: consultation, confidence: 0.92; Keyword match: 0.90; Item type: S; Group: T6; High confidence match",
      "group": "A1",
      "category": 1,
      "provider_type": "General Practitioner"
    }
  ],
  "total_found": 10
}
```

### 3. Validation Endpoints

#### POST /validate_claim
Validate selected MBS items for claim submission.

**Request Body:**
```json
{
  "selected_items": ["3", "4", "23"],
  "context": {
    "setting": "consulting_rooms",
    "duration": 30,
    "provider": "general practitioner",
    "referral": false,
    "date": "2024-01-01T00:00:00Z",
    "patient_type": "community"
  }
}
```

**Response:**
```json
{
  "result": {
    "billable_items": ["3", "4"],
    "rejected_items": ["23"],
    "conflicts": ["Item 23 conflicts with Item 4"],
    "fixes": ["Remove Item 23 or replace with Item 24"],
    "why": "Item 23 is not billable in the same session as Item 4 due to mutual exclusion rule"
  },
  "processing_time": 0.15
}
```

### 4. Item Management

#### GET /items/{item_num}
Get detailed information for a specific MBS item.

**Path Parameters:**
- `item_num` (string): MBS item number

**Response:**
```json
{
  "item_num": "3",
  "description": "Professional attendance by a general practitioner...",
  "group": "A1",
  "category": 1,
  "provider_type": "General Practitioner",
  "item_type": "S",
  "fee": 75.00
}
```

#### GET /items
Search items by criteria.

**Query Parameters:**
- `group` (string, optional): Item group filter
- `category` (integer, optional): Category filter
- `provider_type` (string, optional): Provider type filter
- `item_type` (string, optional): Item type filter
- `limit` (integer, optional): Maximum results (default: 100)

**Response:**
```json
{
  "items": [
    {
      "item_num": "3",
      "description": "Professional attendance...",
      "group": "A1",
      "category": 1,
      "provider_type": "General Practitioner"
    }
  ],
  "total": 150
}
```

### 5. System Information

#### GET /statistics
Get database statistics.

**Response:**
```json
{
  "total_items": 5989,
  "total_rules": 9,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

#### GET /rules
Get loaded validation rules information.

**Response:**
```json
{
  "total_rules": 9,
  "rules": [
    {
      "rule_id": "rule_001",
      "rule_type": "mutual_exclusion",
      "title": "Same Day Exclusion",
      "description": "Items cannot be billed on the same day",
      "priority": 1,
      "conditions_count": 2,
      "actions_count": 1
    }
  ]
}
```

#### GET /performance
Get system performance statistics.

**Response:**
```json
{
  "search_performance": {
    "tfidf": {
      "avg_time_ms": 3.2,
      "total_searches": 150,
      "success_rate": 0.98
    },
    "semantic": {
      "avg_time_ms": 8.5,
      "total_searches": 120,
      "success_rate": 0.95
    },
    "hybrid": {
      "avg_time_ms": 11.2,
      "total_searches": 200,
      "success_rate": 0.99
    }
  },
  "system_metrics": {
    "uptime_seconds": 3600,
    "memory_usage_mb": 256,
    "cpu_usage_percent": 15
  }
}
```

#### GET /search_types
Get available search types and their characteristics.

**Response:**
```json
{
  "search_types": [
    {
      "type": "tfidf",
      "name": "TF-IDF Search",
      "description": "Traditional keyword-based search method",
      "speed": "Fast",
      "accuracy": "Medium"
    },
    {
      "type": "semantic",
      "name": "Semantic Search",
      "description": "AI-powered semantic understanding search using Sentence Transformers",
      "speed": "Medium",
      "accuracy": "High"
    },
    {
      "type": "hybrid",
      "name": "Hybrid Search",
      "description": "Combines TF-IDF and semantic search for optimal results",
      "speed": "Medium",
      "accuracy": "Highest"
    }
  ]
}
```

## Data Models

### SuggestionRequest
```json
{
  "transcript": "string",
  "context": {
    "setting": "string",
    "duration": "integer",
    "provider": "string",
    "referral": "boolean",
    "date": "string (ISO 8601)",
    "patient_type": "string"
  },
  "top_k": "integer"
}
```

### ValidationRequest
```json
{
  "selected_items": ["string"],
  "context": {
    "setting": "string",
    "duration": "integer",
    "provider": "string",
    "referral": "boolean",
    "date": "string (ISO 8601)",
    "patient_type": "string"
  }
}
```

### ItemSuggestion
```json
{
  "item_num": "string",
  "description": "string",
  "score": "float (0.0-1.0)",
  "evidence": "string",
  "group": "string",
  "category": "integer",
  "provider_type": "string"
}
```

### ValidationResult
```json
{
  "billable_items": ["string"],
  "rejected_items": ["string"],
  "conflicts": ["string"],
  "fixes": ["string"],
  "why": "string"
}
```

## Context Parameters

### Setting Options
- `consulting_rooms` - General practice consulting rooms
- `hospital` - Hospital setting
- `home` - Home visit
- `nursing_home` - Nursing home setting

### Provider Types
- `general practitioner` - General practitioner
- `specialist` - Medical specialist
- `nurse` - Registered nurse
- `physiotherapist` - Physiotherapist

### Patient Types
- `community` - Community patient
- `inpatient` - Hospital inpatient
- `outpatient` - Hospital outpatient

## Search Types

### TF-IDF Search
- **Method**: Traditional keyword matching
- **Speed**: Fastest (3-5ms)
- **Accuracy**: Medium
- **Best for**: Simple, direct queries
- **Use case**: Quick keyword searches

### Semantic Search
- **Method**: AI-powered semantic understanding
- **Speed**: Medium (8-12ms)
- **Accuracy**: High
- **Best for**: Complex, nuanced queries
- **Use case**: Detailed symptom descriptions

### Hybrid Search
- **Method**: Combines TF-IDF and semantic search
- **Speed**: Medium (10-15ms)
- **Accuracy**: Highest
- **Best for**: All types of queries
- **Use case**: Production use, best overall performance

## Error Responses

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "transcript"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Not Found Error (404)
```json
{
  "detail": "Item 99999 not found"
}
```

### Server Error (500)
```json
{
  "detail": "Enhanced suggestion generation failed: Model not loaded"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. However, for production deployment, consider implementing rate limiting to prevent abuse.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins. This allows the web interface to make requests from any domain.

## WebSocket Support

Currently, the API does not support WebSocket connections. All communication is via HTTP/HTTPS.

## File Upload

The API does not currently support file uploads. All data is transmitted via JSON in request bodies.

## Pagination

For endpoints that return lists of items, pagination can be implemented using the `limit` parameter. The API returns the total count in the response.

## Caching

The API implements caching for:
- Vector search results
- TF-IDF search results
- Model predictions
- Database queries

Cache invalidation occurs when:
- New data is added to the database
- Models are updated
- System is restarted

## Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Frequency**: Can be called continuously
- **Response Time**: < 100ms
- **Dependencies**: Database, models, vector indexes

### Performance Metrics
- **Endpoint**: `/performance`
- **Metrics**: Response times, success rates, system resources
- **Retention**: Metrics are kept in memory during runtime

### Logging
- **Level**: INFO, WARNING, ERROR
- **Format**: JSON structured logging
- **Fields**: timestamp, level, message, request_id, user_id

## Security Considerations

### Input Validation
- All inputs are validated using Pydantic models
- SQL injection prevention through parameterized queries
- XSS prevention through input sanitization

### Data Privacy
- No personal data is stored
- Voice input is processed locally and not persisted
- All processing happens on the local server

### Access Control
- Currently no authentication required
- All endpoints are publicly accessible
- Consider implementing authentication for production use

## Examples

### Complete Search Workflow

1. **Health Check**
   ```bash
   curl -X GET "http://localhost:8000/health"
   ```

2. **Search for Items**
   ```bash
   curl -X POST "http://localhost:8000/suggest_items_enhanced?search_type=hybrid" \
     -H "Content-Type: application/json" \
     -d '{
       "transcript": "patient has chest pain and shortness of breath",
       "context": {
         "setting": "consulting_rooms",
         "duration": 30,
         "provider": "general practitioner",
         "referral": false,
         "date": "2024-01-01T00:00:00Z",
         "patient_type": "community"
       },
       "top_k": 5
     }'
   ```

3. **Validate Selected Items**
   ```bash
   curl -X POST "http://localhost:8000/validate_claim" \
     -H "Content-Type: application/json" \
     -d '{
       "selected_items": ["3", "4"],
       "context": {
         "setting": "consulting_rooms",
         "duration": 30,
         "provider": "general practitioner",
         "referral": false,
         "date": "2024-01-01T00:00:00Z",
         "patient_type": "community"
       }
     }'
   ```

4. **Get Performance Metrics**
   ```bash
   curl -X GET "http://localhost:8000/performance"
   ```

## SDK Examples

### Python
```python
import requests

# Search for items
response = requests.post(
    "http://localhost:8000/suggest_items_enhanced",
    params={"search_type": "hybrid"},
    json={
        "transcript": "chest pain and shortness of breath",
        "context": {
            "setting": "consulting_rooms",
            "duration": 30,
            "provider": "general practitioner",
            "referral": False,
            "date": "2024-01-01T00:00:00Z",
            "patient_type": "community"
        },
        "top_k": 5
    }
)

results = response.json()
print(f"Found {results['total_found']} items")
```

### JavaScript
```javascript
// Search for items
const response = await fetch('http://localhost:8000/suggest_items_enhanced?search_type=hybrid', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    transcript: 'chest pain and shortness of breath',
    context: {
      setting: 'consulting_rooms',
      duration: 30,
      provider: 'general practitioner',
      referral: false,
      date: '2024-01-01T00:00:00Z',
      patient_type: 'community'
    },
    top_k: 5
  })
});

const results = await response.json();
console.log(`Found ${results.total_found} items`);
```

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

*Last updated: January 2024*
*API Version: 1.0.0*
