#!/usr/bin/env python3
"""
Script to update import statements after reorganizing the project structure
"""
import os
import re

def update_imports_in_file(file_path):
    """Update import statements in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define import mappings
    import_mappings = {
        r'from \.database import': 'from core.database import',
        r'from \.enhanced_database import': 'from core.enhanced_database import',
        r'from \.schemas import': 'from core.schemas import',
        r'from \.rule_processor import': 'from core.rule_processor import',
        r'from \.rule_engine import': 'from core.rule_engine import',
        r'from \.vector_db import': 'from utils.vector_db import',
        r'from \.clinical_context_analyzer import': 'from utils.clinical_context_analyzer import',
        r'from \.data_driven_optimizer import': 'from models.data_driven_optimizer import',
        r'from \.matching_optimizer import': 'from models.matching_optimizer import',
        r'from \.advanced_embeddings import': 'from models.advanced_embeddings import',
        r'from \.medical_knowledge_graph import': 'from models.medical_knowledge_graph import',
        r'from \.enhanced_mbs_matcher import': 'from services.enhanced_mbs_matcher import',
        r'from \.advanced_ensemble_matcher import': 'from services.advanced_ensemble_matcher import',
        r'from \.report_generator import': 'from services.report_generator import',
    }
    
    # Apply mappings
    for old_pattern, new_pattern in import_mappings.items():
        content = re.sub(old_pattern, new_pattern, content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated imports in {file_path}")

def main():
    """Update imports in all Python files"""
    # Files to update
    files_to_update = [
        'core/enhanced_database.py',
        'core/rule_engine.py',
        'core/rule_processor.py',
        'services/enhanced_mbs_matcher.py',
        'services/advanced_ensemble_matcher.py',
        'services/report_generator.py',
        'models/advanced_embeddings.py',
        'models/medical_knowledge_graph.py',
        'models/data_driven_optimizer.py',
        'models/matching_optimizer.py',
        'utils/clinical_context_analyzer.py',
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            update_imports_in_file(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()






