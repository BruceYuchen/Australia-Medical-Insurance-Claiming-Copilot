# MBS Matching System - Architecture Documentation

## Overview

The MBS (Medicare Benefits Schedule) Matching System is an AI-powered intelligent system designed to assist healthcare providers in finding and validating appropriate MBS items for patient consultations and procedures. The system combines traditional keyword search with modern semantic understanding and data-driven optimization to provide accurate, context-aware suggestions.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Interface Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  English Interface  │  Chinese Interface  │  Classic Interface  │
│  (enhanced_index_en)│  (enhanced_index)   │  (index.html)       │
│  + Voice Input      │  + Voice Input      │  + Basic Search     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Application (main.py)                                 │
│  • RESTful API Endpoints                                       │
│  • Request/Response Validation                                 │
│  • CORS & Static File Serving                                  │
│  • Health Monitoring                                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Enhanced Database Manager  │  Rule Engine  │  Data Optimizer  │
│  • Hybrid Search           │  • Validation │  • Intelligence   │
│  • Vector Operations       │  • Conflicts  │  • Enhancement    │
│  • Context Filtering       │  • Fixes      │  • Explanation    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & Model Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  Vector Databases  │  ML Models      │  Traditional DB        │
│  • FAISS          │  • Sentence     │  • SQLite              │
│  • ChromaDB       │    Transformers │  • TF-IDF Index        │
│  • Hybrid Search  │  • all-MiniLM   │  • Structured Rules    │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Web Interface Layer

#### English Interface (`enhanced_index_en.html`)
- **Primary Interface**: Modern, responsive web interface in English
- **Voice Input**: Browser-based speech recognition for symptom input
- **Search Types**: Support for TF-IDF, Semantic, and Hybrid search
- **Real-time Feedback**: Live confidence scoring and performance metrics
- **Context Awareness**: Medical context input (setting, duration, provider, etc.)

#### Chinese Interface (`enhanced_index.html`)
- **Localized Interface**: Chinese language support
- **Same Features**: All functionality of English interface
- **Cultural Adaptation**: Medical terminology in Chinese

#### Classic Interface (`index.html`)
- **Legacy Support**: Basic search functionality
- **Simple UI**: Minimal interface for basic operations

### 2. API Gateway Layer

#### FastAPI Application (`app/main.py`)
- **RESTful Endpoints**: Comprehensive API for all operations
- **Request Validation**: Pydantic models for type safety
- **Response Formatting**: Consistent JSON responses
- **Error Handling**: Graceful error management
- **Health Monitoring**: System status and performance metrics

#### Key Endpoints:
- `POST /suggest_items` - Traditional TF-IDF search
- `POST /suggest_items_enhanced` - Advanced hybrid search
- `POST /validate_claim` - MBS item validation
- `GET /performance` - System performance metrics
- `GET /search_types` - Available search methods
- `GET /health` - System health check

### 3. Business Logic Layer

#### Enhanced Database Manager (`app/enhanced_database.py`)
- **Hybrid Search Engine**: Combines TF-IDF and semantic search
- **Vector Operations**: FAISS and ChromaDB integration
- **Context Filtering**: Medical context-aware filtering
- **Performance Optimization**: Caching and efficient indexing

#### Rule Engine (`app/rule_engine.py`)
- **Deterministic Validation**: Rule-based claim validation
- **Conflict Detection**: Identifies conflicting MBS items
- **Fix Suggestions**: Provides corrective recommendations
- **Evidence Generation**: Explains validation decisions

#### Data-Driven Optimizer (`app/data_driven_optimizer.py`)
- **Intelligent Enhancement**: AI-powered result optimization
- **Keyword Weighting**: Context-aware keyword importance
- **Synonym Expansion**: Medical terminology expansion
- **Confidence Scoring**: Dynamic confidence calculation

### 4. Data & Model Layer

#### Vector Databases
- **FAISS**: High-performance similarity search
- **ChromaDB**: Persistent vector storage
- **Hybrid Indexing**: Combined TF-IDF and semantic vectors

#### Machine Learning Models
- **Sentence Transformers**: `all-MiniLM-L6-v2` for semantic understanding
- **TF-IDF**: Traditional keyword-based search
- **Custom Models**: Domain-specific medical terminology

#### Traditional Database
- **SQLite**: MBS items and rules storage
- **Structured Data**: Normalized MBS item information
- **Rule Storage**: Executable validation rules

## Data Flow

### 1. Search Request Flow
```
User Input → Voice/Text → Web Interface → API Gateway → Enhanced DB Manager
                                                              ↓
Vector Search ← Semantic Model ← Data Optimizer ← Context Filtering
     ↓
Results Ranking → Confidence Scoring → Response Formatting → User Display
```

### 2. Validation Flow
```
Selected Items → API Gateway → Rule Engine → Validation Logic
                                      ↓
Conflict Detection → Fix Suggestions → Evidence Generation → Response
```

### 3. Voice Input Flow
```
Voice Input → Browser Speech API → Text Processing → Search Query
                                                      ↓
Enhanced Search → Results → Confidence Scoring → Voice Feedback
```

## Technology Stack

### Frontend
- **HTML5**: Semantic markup and structure
- **Tailwind CSS**: Utility-first styling framework
- **JavaScript (ES6+)**: Modern JavaScript features
- **Web Speech API**: Browser-based voice recognition
- **Font Awesome**: Icon library

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

### Data Processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning utilities
- **SQLite**: Relational database

### AI/ML Components
- **Sentence Transformers**: Semantic text understanding
- **FAISS**: Vector similarity search
- **ChromaDB**: Vector database
- **Transformers**: Hugging Face model integration

### Development Tools
- **Git**: Version control
- **Pip**: Package management
- **Virtual Environment**: Dependency isolation

## Performance Characteristics

### Search Performance
- **TF-IDF Search**: ~3-5ms average response time
- **Semantic Search**: ~8-12ms average response time
- **Hybrid Search**: ~10-15ms average response time
- **Vector Index Build**: ~1.5-2 seconds (one-time)

### Accuracy Metrics
- **Hybrid Search**: Highest accuracy (recommended)
- **Semantic Search**: High accuracy, good for complex queries
- **TF-IDF Search**: Medium accuracy, fastest response

### Scalability
- **Concurrent Users**: Supports multiple simultaneous users
- **Data Volume**: Handles 5,989+ MBS items efficiently
- **Memory Usage**: Optimized for production deployment
- **Response Time**: Consistent performance under load

## Security & Privacy

### Data Protection
- **Local Processing**: All data processed locally
- **No External APIs**: No data sent to external services
- **Secure Storage**: SQLite database with proper access controls
- **Input Validation**: Comprehensive input sanitization

### Privacy Features
- **No Data Persistence**: Voice data not stored
- **Session Isolation**: User sessions are independent
- **Audit Trail**: Complete logging of all operations
- **Compliance**: Designed for healthcare data standards

## Deployment Architecture

### Development Environment
```
Local Machine
├── Python Virtual Environment
├── SQLite Database
├── FAISS Index Files
├── Model Cache
└── Static Files
```

### Production Considerations
```
Load Balancer
├── Multiple FastAPI Instances
├── Shared Database (PostgreSQL/MySQL)
├── Redis Cache
├── CDN for Static Files
└── Monitoring & Logging
```

## Configuration

### Environment Variables
- `MBS_DB_PATH`: Path to SQLite database
- `VECTOR_DB_TYPE`: Vector database type (faiss/chroma)
- `SEMANTIC_MODEL`: Sentence transformer model name
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

### Model Configuration
- **Default Model**: `all-MiniLM-L6-v2`
- **Vector Dimension**: 384
- **Max Sequence Length**: 256 tokens
- **Batch Size**: 32

## Monitoring & Observability

### Health Checks
- **System Status**: Overall system health
- **Database Connectivity**: SQLite connection status
- **Model Loading**: AI model availability
- **Performance Metrics**: Response times and throughput

### Logging
- **Request Logging**: All API requests logged
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Response time tracking
- **User Activity**: Search and validation tracking

## Future Enhancements

### Planned Features
- **Multi-language Support**: Additional language interfaces
- **Advanced Analytics**: Usage analytics and insights
- **Mobile App**: Native mobile application
- **API Versioning**: Backward compatibility support

### Scalability Improvements
- **Microservices**: Service decomposition
- **Containerization**: Docker deployment
- **Cloud Integration**: AWS/Azure deployment
- **Auto-scaling**: Dynamic resource allocation

## API Documentation

### Core Endpoints

#### Search Endpoints
- `POST /suggest_items` - Traditional search
- `POST /suggest_items_enhanced` - Advanced search
- `GET /search_types` - Available search methods

#### Validation Endpoints
- `POST /validate_claim` - Item validation
- `GET /rules` - Rule information

#### System Endpoints
- `GET /health` - Health check
- `GET /performance` - Performance metrics
- `GET /statistics` - Database statistics

### Request/Response Formats

#### Search Request
```json
{
  "transcript": "Patient symptom description",
  "context": {
    "setting": "consulting_rooms",
    "duration": 30,
    "provider": "general practitioner",
    "referral": false,
    "date": "2024-01-01T00:00:00Z"
  },
  "top_k": 10
}
```

#### Search Response
```json
{
  "suggestions": [
    {
      "item_num": "3",
      "description": "Professional attendance...",
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

## Troubleshooting

### Common Issues
1. **Voice Input Not Working**: Check browser permissions
2. **Slow Search**: Verify model loading and index status
3. **No Results**: Check query format and context
4. **Validation Errors**: Review rule configuration

### Debug Mode
- Enable debug logging in configuration
- Check browser console for client-side errors
- Review server logs for backend issues
- Use health check endpoint for system status

## Contributing

### Development Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize database and models
5. Run development server: `python run_server.py`

### Code Standards
- Follow PEP 8 Python style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions:
- Check the documentation
- Review the API documentation at `/docs`
- Examine the health check at `/health`
- Contact the development team

---

*Last updated: January 2024*
*Version: 1.0.0*
