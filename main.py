"""
MBS匹配系统 - FastAPI主应用
提供症状到候选项目的匹配和申报验证功能
"""
import time
import json
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from core.schemas import (
    SuggestionRequest, SuggestionResponse, ValidationRequest, ValidationResponse,
    ValidationContext, ItemSuggestion, ValidationResult
)
from core.database import get_db_manager, DatabaseManager
from core.enhanced_database import get_enhanced_db_manager, EnhancedDatabaseManager
from services.enhanced_mbs_matcher import EnhancedMBSMatcher
from services.advanced_ensemble_matcher import AdvancedEnsembleMatcher
from models.advanced_embeddings import get_advanced_embedding_manager
from models.medical_knowledge_graph import get_medical_knowledge_graph
from core.rule_processor import load_and_process_rules
from core.rule_engine import RuleEngine
from services.report_generator import (
    MedicalReportGenerator, ReportType, ReportFormat,
    PatientInfo, ProviderInfo, ConsultationInfo, MBSItemInfo,
    create_sample_patient, create_sample_provider, create_sample_consultation,
    create_sample_mbs_items, create_sample_validation_result
)

# 全局变量
db_manager: DatabaseManager = None
enhanced_db_manager: EnhancedDatabaseManager = None
enhanced_mbs_matcher: EnhancedMBSMatcher = None
advanced_ensemble_matcher: AdvancedEnsembleMatcher = None
rule_engine: RuleEngine = None
report_generator: MedicalReportGenerator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global db_manager, enhanced_db_manager, enhanced_mbs_matcher, advanced_ensemble_matcher, rule_engine, report_generator
    
    # 启动时初始化
    print("正在初始化MBS匹配系统...")
    
    # 初始化传统数据库管理器
    db_manager = get_db_manager()
    
    # 初始化增强版数据库管理器
    try:
        enhanced_db_manager = get_enhanced_db_manager(
            db_path="/Users/yz/Code/mbs-matcher/data/mbs.db",
            vector_db_type="faiss",
            use_semantic=True,
            semantic_model="all-MiniLM-L6-v2"
        )
        print("增强版数据库管理器初始化完成")
        
        # 初始化增强版MBS匹配器
        enhanced_mbs_matcher = EnhancedMBSMatcher(enhanced_db_manager)
        print("增强版MBS匹配器初始化完成")
        
        # 初始化高级集成匹配器
        try:
            advanced_ensemble_matcher = AdvancedEnsembleMatcher(enhanced_db_manager)
            print("高级集成匹配器初始化完成")
        except Exception as e:
            print(f"高级集成匹配器初始化失败: {e}")
            advanced_ensemble_matcher = None
    except Exception as e:
        print(f"增强版数据库管理器初始化失败: {e}")
        enhanced_db_manager = None
        enhanced_mbs_matcher = None
        advanced_ensemble_matcher = None
    
    # 加载并处理规则
    try:
        rules_file = "/Users/yz/Code/mbs-matcher/data/mbs_rules.json"
        structured_rules = load_and_process_rules(rules_file)
        print(f"加载了 {len(structured_rules)} 条结构化规则")
        
        # 初始化规则引擎
        rule_engine = RuleEngine("/Users/yz/Code/mbs-matcher/data/mbs.db", structured_rules)
        print("规则引擎初始化完成")
        
    except Exception as e:
        print(f"规则加载失败: {e}")
        structured_rules = []
        rule_engine = RuleEngine("/Users/yz/Code/mbs-matcher/data/mbs.db", [])
    
    # 初始化报告生成器
    try:
        report_generator = MedicalReportGenerator()
        print("报告生成器初始化完成")
    except Exception as e:
        print(f"报告生成器初始化失败: {e}")
        report_generator = None
    
    print("MBS匹配系统初始化完成")
    
    yield
    
    # 关闭时清理
    print("MBS匹配系统正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title="MBS匹配系统",
    description="基于症状文本的MBS项目匹配和申报验证系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_database() -> DatabaseManager:
    """获取数据库管理器依赖"""
    if db_manager is None:
        raise HTTPException(status_code=500, detail="数据库未初始化")
    return db_manager

def get_enhanced_database() -> EnhancedDatabaseManager:
    """获取增强版数据库管理器依赖"""
    if enhanced_db_manager is None:
        raise HTTPException(status_code=500, detail="增强版数据库未初始化")
    return enhanced_db_manager

def get_rule_engine() -> RuleEngine:
    """获取规则引擎依赖"""
    if rule_engine is None:
        raise HTTPException(status_code=500, detail="规则引擎未初始化")
    return rule_engine

def get_report_generator() -> MedicalReportGenerator:
    """获取报告生成器依赖"""
    if report_generator is None:
        raise HTTPException(status_code=500, detail="报告生成器未初始化")
    return report_generator

def get_enhanced_mbs_matcher() -> EnhancedMBSMatcher:
    """获取增强版MBS匹配器依赖"""
    if enhanced_mbs_matcher is None:
        raise HTTPException(status_code=500, detail="增强版MBS匹配器未初始化")
    return enhanced_mbs_matcher

def get_advanced_ensemble_matcher() -> AdvancedEnsembleMatcher:
    """获取高级集成匹配器依赖"""
    if advanced_ensemble_matcher is None:
        raise HTTPException(status_code=500, detail="高级集成匹配器未初始化")
    return advanced_ensemble_matcher

@app.get("/")
async def root():
    """Root path - redirect to enhanced English web interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/enhanced_index_en.html")

@app.get("/chinese")
async def chinese_interface():
    """Chinese web interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/enhanced_index.html")

@app.get("/classic")
async def classic_interface():
    """Classic web interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

@app.get("/api")
async def api_root():
    """API root path"""
    return {
        "message": "MBS Matching System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "web_interface": "/static/enhanced_index_en.html",
        "chinese_interface": "/chinese",
        "classic_interface": "/classic"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = get_database()
        stats = db.get_statistics()
        return {
            "status": "healthy",
            "database": "connected",
            "total_items": stats.get("total_items", 0),
            "rules_loaded": len(rule_engine.structured_rules) if rule_engine else 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/suggest_items", response_model=SuggestionResponse)
async def suggest_items(
    request: SuggestionRequest,
    db: DatabaseManager = Depends(get_database)
):
    """
    Suggest MBS items based on symptom text (Traditional TF-IDF search)
    
    - **transcript**: Patient symptom description or medical record text
    - **context**: Medical context information (setting, duration, provider, etc.)
    - **top_k**: Number of suggestions to return (default 10)
    """
    try:
        start_time = time.time()
        
        # 使用TF-IDF进行文本相似度搜索
        suggestions = db.search_items_by_text(request.transcript, request.top_k)
        
        # 根据上下文过滤建议
        filtered_suggestions = []
        for suggestion in suggestions:
            # 这里可以添加基于上下文的过滤逻辑
            # 例如：根据提供者类型、设置等过滤
            if _is_suggestion_relevant(suggestion, request.context):
                filtered_suggestions.append(suggestion)
        
        # 如果过滤后结果太少，返回原始结果
        if len(filtered_suggestions) < 3:
            filtered_suggestions = suggestions[:request.top_k]
        
        processing_time = time.time() - start_time
        
        return SuggestionResponse(
            suggestions=filtered_suggestions,
            total_found=len(filtered_suggestions)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"建议生成失败: {str(e)}")

@app.post("/suggest_items_enhanced", response_model=SuggestionResponse)
async def suggest_items_enhanced(
    request: SuggestionRequest,
    search_type: str = "hybrid",
    enhanced_db: EnhancedDatabaseManager = Depends(get_enhanced_database)
):
    """
    Suggest MBS items based on symptom text (Enhanced search)
    
    - **transcript**: Patient symptom description or medical record text
    - **context**: Medical context information (setting, duration, provider, etc.)
    - **top_k**: Number of suggestions to return (default 10)
    - **search_type**: Search type (tfidf/semantic/hybrid)
    """
    try:
        start_time = time.time()
        
        # 使用增强版搜索
        suggestions = enhanced_db.search_items_by_text(
            request.transcript, 
            request.top_k, 
            search_type=search_type,
            context=request.context.dict() if request.context else None
        )
        
        # 根据上下文过滤建议
        filtered_suggestions = []
        for suggestion in suggestions:
            if _is_suggestion_relevant(suggestion, request.context):
                filtered_suggestions.append(suggestion)
        
        # 如果过滤后结果太少，返回原始结果
        if len(filtered_suggestions) < 3:
            filtered_suggestions = suggestions[:request.top_k]
        
        processing_time = time.time() - start_time
        
        return SuggestionResponse(
            suggestions=filtered_suggestions,
            total_found=len(filtered_suggestions)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced suggestion generation failed: {str(e)}")

@app.post("/match_clinical_scenario", response_model=SuggestionResponse)
async def match_clinical_scenario(
    request: SuggestionRequest,
    search_type: str = "hybrid",
    matcher: EnhancedMBSMatcher = Depends(get_enhanced_mbs_matcher)
):
    """
    Match MBS items based on detailed clinical scenario analysis
    
    - **transcript**: Complete clinical text including patient demographics, symptoms, setting, etc.
    - **context**: Additional medical context information
    - **top_k**: Number of suggestions to return (default 10)
    - **search_type**: Search type (tfidf/semantic/hybrid)
    
    This endpoint uses advanced clinical context analysis to provide more accurate
    MBS item matching based on:
    - Patient demographics (age, gender)
    - Clinical setting (emergency, hospital, clinic)
    - Medical conditions and symptoms
    - Provider type and specialty
    - Urgency and complexity
    """
    try:
        start_time = time.time()
        
        # Use enhanced clinical scenario matching
        suggestions = matcher.match_clinical_scenario(
            clinical_text=request.transcript,
            top_k=request.top_k,
            search_type=search_type
        )
        
        processing_time = time.time() - start_time
        
        return SuggestionResponse(
            suggestions=suggestions,
            total_found=len(suggestions),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clinical scenario matching failed: {str(e)}")

@app.post("/match_clinical_scenario_advanced", response_model=SuggestionResponse)
async def match_clinical_scenario_advanced(
    request: SuggestionRequest,
    matcher: AdvancedEnsembleMatcher = Depends(get_advanced_ensemble_matcher)
):
    """
    Advanced ensemble matching for clinical scenarios with maximum accuracy
    
    - **transcript**: Complete clinical text including patient demographics, symptoms, setting, etc.
    - **context**: Additional medical context information
    - **top_k**: Number of suggestions to return (default 10)
    
    This endpoint uses advanced ensemble methods including:
    - Multiple embedding models (Clinical BERT, BioBERT, etc.)
    - Medical knowledge graph
    - Named Entity Recognition
    - Ensemble scoring with weighted components
    - Advanced medical concept matching
    """
    try:
        start_time = time.time()
        
        # Use advanced ensemble matching
        ensemble_results = matcher.match_clinical_scenario_advanced(
            clinical_text=request.transcript,
            context=request.context,
            top_k=request.top_k
        )
        
        # Convert to ItemSuggestion format
        suggestions = []
        for result in ensemble_results:
            suggestion = ItemSuggestion(
                item_num=result.item_num,
                description=result.description,
                score=result.final_score,
                group=result.group,
                category=result.category,
                provider_type=result.provider_type,
                matched_fields=["ensemble"],
                evidence=result.evidence
            )
            suggestions.append(suggestion)
        
        processing_time = time.time() - start_time
        
        return SuggestionResponse(
            suggestions=suggestions,
            total_found=len(suggestions),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced ensemble matching failed: {str(e)}")

@app.post("/validate_claim", response_model=ValidationResponse)
async def validate_claim(
    request: ValidationRequest,
    db: DatabaseManager = Depends(get_database),
    engine: RuleEngine = Depends(get_rule_engine)
):
    """
    Validate selected MBS items for claim submission
    
    - **selected_items**: List of selected item numbers
    - **context**: Medical context information
    """
    try:
        start_time = time.time()
        
        # Validate that items exist
        valid_items = []
        for item_num in request.selected_items:
            item = db.get_item_by_number(item_num)
            if item:
                valid_items.append(item_num)
            else:
                print(f"Warning: Item {item_num} not found")
        
        if not valid_items:
            raise HTTPException(status_code=400, detail="No valid items found")
        
        # Use rule engine for validation
        validation_result = engine.validate_claim(valid_items, request.context)
        
        processing_time = time.time() - start_time
        
        return ValidationResponse(
            result=validation_result,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/items/{item_num}")
async def get_item_details(
    item_num: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get detailed information for a specific item"""
    try:
        item = db.get_item_by_number(item_num)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_num} not found")
        
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item details: {str(e)}")

@app.get("/items")
async def search_items(
    group: str = None,
    category: int = None,
    provider_type: str = None,
    item_type: str = None,
    limit: int = 100,
    db: DatabaseManager = Depends(get_database)
):
    """Search items by criteria"""
    try:
        items = db.search_items_by_criteria(
            group=group,
            category=category,
            provider_type=provider_type,
            item_type=item_type,
            limit=limit
        )
        
        return {
            "items": items,
            "total": len(items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/statistics")
async def get_statistics(db: DatabaseManager = Depends(get_database)):
    """Get database statistics"""
    try:
        stats = db.get_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/rules")
async def get_rules(engine: RuleEngine = Depends(get_rule_engine)):
    """Get loaded rules information"""
    try:
        rules_info = []
        for rule in engine.structured_rules:
            rules_info.append({
                "rule_id": rule.rule_id,
                "rule_type": rule.rule_type,
                "title": rule.title,
                "description": rule.description,
                "priority": rule.priority,
                "conditions_count": len(rule.conditions),
                "actions_count": len(rule.actions)
            })
        
        return {
            "total_rules": len(rules_info),
            "rules": rules_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rules information: {str(e)}")

@app.get("/performance")
async def get_performance(enhanced_db: EnhancedDatabaseManager = Depends(get_enhanced_database)):
    """Get system performance statistics"""
    try:
        performance_stats = enhanced_db.get_search_performance()
        return performance_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance statistics: {str(e)}")

@app.get("/search_types")
async def get_search_types():
    """Get available search types"""
    return {
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

@app.post("/generate_report")
async def generate_report(
    report_type: str = "claim_summary",
    format: str = "html",
    patient_data: dict = None,
    provider_data: dict = None,
    consultation_data: dict = None,
    mbs_items_data: list = None,
    validation_data: dict = None,
    generator: MedicalReportGenerator = Depends(get_report_generator)
):
    """Generate medical report for claims and records"""
    try:
        # Convert string parameters to enums
        try:
            report_type_enum = ReportType(report_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")
        
        try:
            format_enum = ReportFormat(format)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
        
        # Use sample data if not provided
        if patient_data is None:
            patient = create_sample_patient()
        else:
            patient = PatientInfo(**patient_data)
        
        if provider_data is None:
            provider = create_sample_provider()
        else:
            provider = ProviderInfo(**provider_data)
        
        if consultation_data is None:
            consultation = create_sample_consultation()
        else:
            consultation = ConsultationInfo(**consultation_data)
        
        if mbs_items_data is None:
            mbs_items = create_sample_mbs_items()
        else:
            mbs_items = [MBSItemInfo(**item) for item in mbs_items_data]
        
        if validation_data is None:
            validation_result = create_sample_validation_result()
        else:
            validation_result = validation_data
        
        # Generate report
        result = generator.generate_report(
            report_type=report_type_enum,
            patient=patient,
            provider=provider,
            consultation=consultation,
            mbs_items=mbs_items,
            validation_result=validation_result,
            format=format_enum
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Report generated successfully",
                "report_id": result["report_metadata"]["report_id"],
                "filepath": result["filepath"],
                "filename": result["filename"],
                "generated_at": result["generated_at"],
                "report_type": result["report_type"],
                "format": result["format"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {result['error']}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@app.get("/generate_sample_report")
async def generate_sample_report(
    report_type: str = "claim_summary",
    format: str = "html",
    generator: MedicalReportGenerator = Depends(get_report_generator)
):
    """Generate a sample medical report for demonstration"""
    try:
        # Convert string parameters to enums
        try:
            report_type_enum = ReportType(report_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")
        
        try:
            format_enum = ReportFormat(format)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
        
        # Use sample data
        patient = create_sample_patient()
        provider = create_sample_provider()
        consultation = create_sample_consultation()
        mbs_items = create_sample_mbs_items()
        validation_result = create_sample_validation_result()
        
        # Generate report
        result = generator.generate_report(
            report_type=report_type_enum,
            patient=patient,
            provider=provider,
            consultation=consultation,
            mbs_items=mbs_items,
            validation_result=validation_result,
            format=format_enum
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Sample report generated successfully",
                "report_id": result["report_metadata"]["report_id"],
                "filepath": result["filepath"],
                "filename": result["filename"],
                "generated_at": result["generated_at"],
                "report_type": result["report_type"],
                "format": result["format"],
                "preview": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Sample report generation failed: {result['error']}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample report generation error: {str(e)}")

@app.get("/report_types")
async def get_report_types():
    """Get available report types"""
    return {
        "report_types": [
            {
                "type": "claim_summary",
                "name": "Claim Summary",
                "description": "Summary report for MBS claim submission"
            },
            {
                "type": "detailed_record",
                "name": "Detailed Record",
                "description": "Comprehensive medical record with full details"
            },
            {
                "type": "billing_report",
                "name": "Billing Report",
                "description": "Financial billing report for accounting"
            },
            {
                "type": "audit_trail",
                "name": "Audit Trail",
                "description": "System audit trail and validation log"
            },
            {
                "type": "patient_summary",
                "name": "Patient Summary",
                "description": "Patient-focused summary report"
            }
        ],
        "formats": [
            {
                "format": "html",
                "name": "HTML",
                "description": "Web-friendly HTML format"
            },
            {
                "format": "json",
                "name": "JSON",
                "description": "Machine-readable JSON format"
            },
            {
                "format": "text",
                "name": "Text",
                "description": "Plain text format"
            }
        ]
    }

@app.get("/offline_capability")
async def get_offline_capability():
    """Get information about offline capabilities"""
    return {
        "offline_capable": True,
        "description": "The MBS Matching System runs completely offline without internet dependency",
        "features": {
            "local_processing": "All data processing happens locally on your machine",
            "no_external_apis": "No data is sent to external services or APIs",
            "local_database": "Uses local SQLite database for MBS items and rules",
            "local_ai_models": "Uses locally downloaded Sentence Transformers models",
            "local_vector_db": "Uses local FAISS vector database for semantic search",
            "voice_processing": "Voice input is processed locally using browser Web Speech API",
            "report_generation": "All reports are generated locally without external dependencies"
        },
        "data_sources": {
            "mbs_database": "Local SQLite database with 5,989+ MBS items",
            "validation_rules": "Local rule engine with 9+ validation rules",
            "ai_models": "Local Sentence Transformers model (all-MiniLM-L6-v2)",
            "vector_index": "Local FAISS index for semantic search"
        },
        "privacy": {
            "no_data_transmission": "No patient data leaves your local machine",
            "no_cloud_dependencies": "No cloud services or external APIs used",
            "local_storage": "All data stored locally in SQLite database",
            "secure_processing": "All processing happens in your secure environment"
        },
        "requirements": {
            "internet_initial_setup": "Only required for initial model download",
            "offline_operation": "Fully functional without internet after setup",
            "browser_voice": "Voice input requires browser with Web Speech API support",
            "local_resources": "Requires local storage for models and database"
        }
    }

def _is_suggestion_relevant(suggestion: ItemSuggestion, context: ValidationContext) -> bool:
    """Check if suggestion is relevant to context"""
    # Simplified relevance check
    # Can be extended with more complex logic as needed
    
    # Check provider type match
    if context.provider and suggestion.provider_type:
        if context.provider.lower() not in suggestion.provider_type.lower():
            return False
    
    # Check setting match
    if context.setting == "consulting_rooms":
        # Consulting room setting usually suitable for most items
        return True
    elif context.setting == "institution":
        # Institution setting may require special items
        return "institution" in suggestion.description.lower() or "facility" in suggestion.description.lower()
    
    return True

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
