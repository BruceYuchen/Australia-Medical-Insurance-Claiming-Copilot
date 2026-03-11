# MBS Matching System

An AI-powered intelligent system for Medicare Benefits Schedule (MBS) item matching and validation, designed to assist healthcare providers in finding appropriate billing codes for patient consultations and procedures.

## 🌟 Features

### 🔍 Advanced Search Capabilities
- **Hybrid Search**: Combines traditional TF-IDF with AI-powered semantic understanding
- **Multiple Search Types**: TF-IDF, Semantic, and Hybrid search options
- **Context-Aware**: Medical context filtering (setting, duration, provider type)
- **Real-time Results**: Fast, accurate suggestions with confidence scoring

### 🎤 Voice Input Support
- **Speech Recognition**: Browser-based voice-to-text conversion
- **Multi-language**: Support for English and Chinese interfaces
- **Real-time Processing**: Instant voice input processing
- **Accessibility**: Enhanced accessibility for healthcare professionals

### 🧠 AI-Powered Intelligence
- **Semantic Understanding**: Advanced natural language processing
- **Data-Driven Optimization**: Intelligent result enhancement
- **Confidence Scoring**: Dynamic confidence calculation
- **Medical Terminology**: Domain-specific medical language support

### ✅ Validation & Compliance
- **Rule Engine**: Deterministic MBS item validation
- **Conflict Detection**: Identifies conflicting billing codes
- **Fix Suggestions**: Provides corrective recommendations
- **Evidence Generation**: Explains validation decisions

### 🌐 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Multiple Languages**: English and Chinese interfaces
- **Real-time Feedback**: Live performance metrics
- **Export Functionality**: Download search results

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser with JavaScript enabled
- Microphone access for voice input (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mbs-matcher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the system**
   ```bash
   python run_server.py
   ```

5. **Access the web interface**
   - Open your browser and go to `http://localhost:8000`
   - English interface: `http://localhost:8000/`
   - Chinese interface: `http://localhost:8000/chinese`
   - Classic interface: `http://localhost:8000/classic`

## 📖 Usage

### Basic Search
1. Enter patient symptoms or medical descriptions in the text area
2. Select appropriate medical context (setting, duration, provider type)
3. Choose search type (Hybrid recommended for best results)
4. Click "Search Items" to get suggestions
5. Review results with confidence scores and evidence

### Voice Input
1. Click the microphone button in the text area
2. Speak your symptoms or medical description clearly
3. The system will automatically convert speech to text
4. Proceed with normal search process

### Item Validation
1. Select relevant items from search results
2. Click "Validate Claim" to check for conflicts
3. Review validation results and fix suggestions
4. Export results for documentation

### Search Types

#### 🔍 TF-IDF Search
- **Speed**: Fastest (3-5ms)
- **Accuracy**: Medium
- **Best for**: Quick keyword-based searches
- **Use case**: Simple, direct queries

#### 🧠 Semantic Search
- **Speed**: Medium (8-12ms)
- **Accuracy**: High
- **Best for**: Complex, nuanced queries
- **Use case**: Detailed symptom descriptions

#### ⚡ Hybrid Search (Recommended)
- **Speed**: Medium (10-15ms)
- **Accuracy**: Highest
- **Best for**: All types of queries
- **Use case**: Production use, best overall performance

## 🏗️ Architecture

The system is built with a modern, scalable architecture:

```
Web Interface → API Gateway → Business Logic → Data & Models
     ↓              ↓             ↓              ↓
Voice Input → FastAPI → Enhanced DB → Vector DBs
Text Input → Validation → Rule Engine → ML Models
```

### Key Components
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Backend**: FastAPI, Python
- **AI/ML**: Sentence Transformers, FAISS, ChromaDB
- **Database**: SQLite with vector indexing
- **Voice**: Web Speech API

## 📊 Performance

### Search Performance
- **TF-IDF**: ~3-5ms average response time
- **Semantic**: ~8-12ms average response time
- **Hybrid**: ~10-15ms average response time

### Accuracy Metrics
- **Hybrid Search**: Highest accuracy (recommended)
- **Semantic Search**: High accuracy for complex queries
- **TF-IDF Search**: Medium accuracy, fastest response

### System Capacity
- **MBS Items**: 5,989+ items supported
- **Concurrent Users**: Multiple simultaneous users
- **Response Time**: Consistent under load
- **Memory Usage**: Optimized for production

## 🔧 API Documentation

### Core Endpoints

#### Search
- `POST /suggest_items` - Traditional TF-IDF search
- `POST /suggest_items_enhanced` - Advanced hybrid search
- `GET /search_types` - Available search methods

#### Validation
- `POST /validate_claim` - MBS item validation
- `GET /rules` - Rule information

#### System
- `GET /health` - Health check
- `GET /performance` - Performance metrics
- `GET /statistics` - Database statistics

### Interactive API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Development

### Project Structure
```
mbs-matcher/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application
│   ├── schemas.py         # Pydantic models
│   ├── database.py        # Traditional database manager
│   ├── enhanced_database.py # Advanced database manager
│   ├── vector_db.py       # Vector database operations
│   ├── data_driven_optimizer.py # AI optimization
│   ├── rule_engine.py     # Validation rules
│   └── rule_processor.py  # Rule processing
├── static/                # Web interface files
│   ├── enhanced_index_en.html # English interface
│   ├── enhanced_index.html    # Chinese interface
│   └── index.html         # Classic interface
├── data/                  # Data files
│   └── mbs.db            # SQLite database
├── models/               # ML model cache
├── static_files/         # FAISS index files
└── requirements.txt      # Python dependencies
```

### Running Tests
```bash
# Test basic functionality
python test_system.py

# Test enhanced features
python test_enhanced_system.py

# Test data-driven optimization
python test_data_driven_optimization.py

# Test comprehensive features
python test_comprehensive_optimization.py
```

### Configuration
The system can be configured through environment variables:
- `MBS_DB_PATH`: Path to SQLite database
- `VECTOR_DB_TYPE`: Vector database type (faiss/chroma)
- `SEMANTIC_MODEL`: Sentence transformer model name
- `LOG_LEVEL`: Logging level

## 🔒 Security & Privacy

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

## 🌍 Internationalization

### Supported Languages
- **English**: Primary interface with full functionality
- **Chinese**: Localized interface for Chinese users
- **Voice Input**: Supports multiple languages via browser

### Localization Features
- **Interface Translation**: Complete UI translation
- **Medical Terminology**: Localized medical terms
- **Cultural Adaptation**: Region-specific medical practices
- **Accessibility**: Multi-language accessibility support

## 📈 Monitoring & Analytics

### Health Monitoring
- **System Status**: Real-time system health
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Comprehensive error logging
- **Usage Analytics**: Search patterns and performance

### Debugging
- **Debug Mode**: Enable detailed logging
- **Browser Console**: Client-side error tracking
- **Server Logs**: Backend error monitoring
- **Health Checks**: System status verification

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 Python style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and architecture docs
- **API Docs**: Visit `/docs` for interactive API documentation
- **Health Check**: Visit `/health` for system status
- **Issues**: Report bugs and feature requests via GitHub issues

### Troubleshooting
1. **Voice Input Issues**: Check browser permissions and microphone access
2. **Slow Performance**: Verify model loading and system resources
3. **No Search Results**: Check query format and context settings
4. **Validation Errors**: Review rule configuration and item selection

## 🗺️ Roadmap

### Upcoming Features
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Usage insights and reporting
- **Multi-language Support**: Additional language interfaces
- **API Versioning**: Backward compatibility support

### Planned Improvements
- **Microservices**: Service decomposition for scalability
- **Containerization**: Docker deployment support
- **Cloud Integration**: AWS/Azure deployment options
- **Auto-scaling**: Dynamic resource allocation

## 🙏 Acknowledgments

- **MBS Data**: Medicare Benefits Schedule data
- **AI Models**: Sentence Transformers and Hugging Face
- **Web Technologies**: FastAPI, Tailwind CSS, and modern web standards
- **Open Source**: Community contributions and libraries

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: Production Ready

For more detailed technical information, see [ARCHITECTURE.md](ARCHITECTURE.md).