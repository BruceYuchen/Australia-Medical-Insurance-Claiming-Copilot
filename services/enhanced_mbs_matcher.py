"""
Enhanced MBS Matcher
Uses clinical context analysis to improve MBS item matching accuracy
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from utils.clinical_context_analyzer import analyze_clinical_text, ClinicalContextAnalyzer
from core.enhanced_database import EnhancedDatabaseManager
from core.schemas import ItemSuggestion

class EnhancedMBSMatcher:
    """Enhanced MBS matcher with clinical context analysis"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
        self.clinical_analyzer = ClinicalContextAnalyzer()
        
        # MBS item patterns for specific clinical scenarios
        self.clinical_patterns = {
            'emergency_medicine': {
                'keywords': [
                    'emergency', 'urgent', 'acute', 'critical', 'resuscitation',
                    'trauma', 'injury', 'fracture', 'dislocation', 'chest pain',
                    'shortness of breath', 'severe', 'life threatening'
                ],
                'item_groups': ['T1', 'T2', 'T3'],
                'item_types': ['S', 'A'],
                'provider_types': ['specialist', 'emergency_medicine_specialist']
            },
            'respiratory_conditions': {
                'keywords': [
                    'cough', 'breathing', 'respiratory', 'chest', 'lung',
                    'pneumonia', 'asthma', 'copd', 'bronchitis', 'wheeze',
                    'crackles', 'dyspnea', 'shortness of breath', 'oxygen'
                ],
                'item_groups': ['T1', 'T2', 'T7'],
                'item_types': ['S', 'A'],
                'provider_types': ['specialist', 'general_practitioner']
            },
            'cardiovascular_conditions': {
                'keywords': [
                    'heart', 'cardiac', 'chest pain', 'angina', 'myocardial',
                    'infarction', 'arrhythmia', 'atrial fibrillation', 'af',
                    'hypertension', 'blood pressure', 'hypotension', 'edema'
                ],
                'item_groups': ['T1', 'T2', 'T3'],
                'item_types': ['S', 'A'],
                'provider_types': ['specialist', 'cardiologist']
            },
            'elderly_patients': {
                'keywords': [
                    'elderly', 'aged', 'senior', 'frail', 'multiple comorbidities',
                    'polypharmacy', 'falls', 'confusion', 'dementia'
                ],
                'item_groups': ['T1', 'T2', 'T3'],
                'item_types': ['S', 'A'],
                'provider_types': ['specialist', 'geriatrician']
            }
        }
        
        # Age-specific MBS rules
        self.age_rules = {
            'pediatric': {
                'min_age': 0,
                'max_age': 17,
                'preferred_groups': ['T1', 'T2'],
                'special_considerations': ['pediatric_specialist', 'family_presence']
            },
            'adult': {
                'min_age': 18,
                'max_age': 74,
                'preferred_groups': ['T1', 'T2', 'T3'],
                'special_considerations': ['general_practitioner', 'specialist']
            },
            'elderly': {
                'min_age': 75,
                'max_age': 120,
                'preferred_groups': ['T1', 'T2', 'T3'],
                'special_considerations': ['geriatrician', 'complex_care', 'multidisciplinary']
            }
        }
        
        # Emergency department specific patterns
        self.emergency_patterns = {
            'high_complexity': [
                'medical decision making of high complexity',
                'emergency department',
                'specialist in emergency medicine',
                'aged 4 years or over but under 75 years old',
                'aged 75 years or over'
            ],
            'medium_complexity': [
                'medical decision making of medium complexity',
                'emergency department',
                'specialist in emergency medicine'
            ],
            'low_complexity': [
                'medical decision making of low complexity',
                'emergency department',
                'specialist in emergency medicine'
            ]
        }
    
    def match_clinical_scenario(self, 
                              clinical_text: str, 
                              top_k: int = 10,
                              search_type: str = "hybrid") -> List[ItemSuggestion]:
        """Match MBS items based on clinical scenario"""
        
        # Analyze clinical context
        clinical_context = self.clinical_analyzer.analyze_clinical_context(clinical_text)
        mbs_context = self.clinical_analyzer.get_mbs_matching_context(clinical_context)
        
        # Extract key clinical terms for search
        search_terms = self._extract_search_terms(clinical_text, clinical_context)
        
        # Perform enhanced search
        suggestions = self.db_manager.search_items_by_text(
            query_text=search_terms,
            top_k=top_k * 2,  # Get more results for filtering
            search_type=search_type,
            context=mbs_context
        )
        
        # Apply clinical context filtering and scoring
        enhanced_suggestions = self._apply_clinical_filtering(
            suggestions, clinical_context, mbs_context
        )
        
        # Apply emergency department specific matching
        if mbs_context.get('emergency_department'):
            enhanced_suggestions = self._apply_emergency_matching(
                enhanced_suggestions, clinical_context, mbs_context
            )
        
        # Apply age-specific matching
        if mbs_context.get('age_group'):
            enhanced_suggestions = self._apply_age_specific_matching(
                enhanced_suggestions, mbs_context
            )
        
        # Sort by enhanced score and return top_k
        enhanced_suggestions.sort(key=lambda x: x.score, reverse=True)
        return enhanced_suggestions[:top_k]
    
    def _extract_search_terms(self, clinical_text: str, clinical_context) -> str:
        """Extract relevant search terms from clinical text"""
        terms = []
        
        # Add symptoms and conditions
        if clinical_context.condition.symptoms:
            terms.extend(clinical_context.condition.symptoms)
        
        # Add emergency department specific terms if setting is emergency
        if clinical_context.setting.location == 'emergency':
            terms.extend(['professional attendance', 'emergency department', 'specialist', 'medical decision making', 'high complexity'])
            
            # Add management terms for potential procedures
            if any(word in clinical_text.lower() for word in ['management', 'treat', 'care', 'monitoring']):
                terms.extend(['management', 'fractures', 'dislocations'])
        
        # Add setting-specific terms
        if clinical_context.setting.location == 'emergency':
            terms.extend(['emergency', 'urgent', 'acute', 'critical', 'emergency department', 'emergency medicine', 'specialist', 'medical decision making', 'high complexity'])
        elif clinical_context.setting.location == 'hospital':
            terms.extend(['hospital', 'inpatient', 'admission', 'emergency department'])
        elif clinical_context.setting.location == 'clinic':
            terms.extend(['clinic', 'outpatient', 'consultation'])
        
        # Add department-specific terms
        if clinical_context.setting.department:
            if clinical_context.setting.department == 'emergency_medicine':
                terms.extend(['emergency medicine', 'specialist', 'medical decision making'])
            elif clinical_context.setting.department == 'cardiology':
                terms.extend(['cardiology', 'cardiac', 'heart'])
            elif clinical_context.setting.department == 'respiratory':
                terms.extend(['respiratory', 'pulmonology', 'lung'])
        
        # Add urgency terms
        if clinical_context.setting.urgency:
            if clinical_context.setting.urgency == 'emergency':
                terms.extend(['emergency', 'urgent', 'critical', 'life threatening'])
            elif clinical_context.setting.urgency == 'urgent':
                terms.extend(['urgent', 'priority', 'asap'])
        
        # Add provider type terms
        if clinical_context.provider_type == 'specialist':
            terms.extend(['specialist', 'consultant', 'physician'])
        elif clinical_context.provider_type == 'general_practitioner':
            terms.extend(['general practitioner', 'gp', 'primary care'])
        
        # Add age-specific terms
        if clinical_context.demographics.age_group:
            if clinical_context.demographics.age_group == 'elderly':
                terms.extend(['elderly', 'aged', 'senior', 'aged 75 years or over'])
            elif clinical_context.demographics.age_group == 'pediatric':
                terms.extend(['pediatric', 'child', 'infant', 'aged under 4 years'])
            elif clinical_context.demographics.age_group == 'adult':
                terms.extend(['adult', 'aged 4 years or over but under 75 years old'])
        
        # Combine terms and remove duplicates
        unique_terms = list(set(terms))
        return ' '.join(unique_terms)
    
    def _apply_clinical_filtering(self, 
                                suggestions: List[ItemSuggestion], 
                                clinical_context,
                                mbs_context: Dict[str, Any]) -> List[ItemSuggestion]:
        """Apply clinical context filtering to suggestions"""
        filtered_suggestions = []
        
        for suggestion in suggestions:
            enhanced_score = suggestion.score
            enhancement_reasons = []
            
            # Age-based scoring
            if mbs_context.get('age_group') and clinical_context.demographics.age:
                age_score_boost = self._calculate_age_score_boost(
                    suggestion, clinical_context.demographics.age, mbs_context
                )
                if age_score_boost > 0:
                    enhanced_score += age_score_boost
                    enhancement_reasons.append(f"Age-appropriate: +{age_score_boost:.2f}")
            
            # Setting-based scoring
            if mbs_context.get('setting'):
                setting_score_boost = self._calculate_setting_score_boost(
                    suggestion, mbs_context['setting']
                )
                if setting_score_boost > 0:
                    enhanced_score += setting_score_boost
                    enhancement_reasons.append(f"Setting match: +{setting_score_boost:.2f}")
            
            # Department-based scoring
            if mbs_context.get('department'):
                department_score_boost = self._calculate_department_score_boost(
                    suggestion, mbs_context['department']
                )
                if department_score_boost > 0:
                    enhanced_score += department_score_boost
                    enhancement_reasons.append(f"Department match: +{department_score_boost:.2f}")
            
            # Urgency-based scoring
            if mbs_context.get('urgency'):
                urgency_score_boost = self._calculate_urgency_score_boost(
                    suggestion, mbs_context['urgency']
                )
                if urgency_score_boost > 0:
                    enhanced_score += urgency_score_boost
                    enhancement_reasons.append(f"Urgency match: +{urgency_score_boost:.2f}")
            
            # Medical condition scoring
            if clinical_context.condition.symptoms:
                condition_score_boost = self._calculate_condition_score_boost(
                    suggestion, clinical_context.condition.symptoms
                )
                if condition_score_boost > 0:
                    enhanced_score += condition_score_boost
                    enhancement_reasons.append(f"Condition match: +{condition_score_boost:.2f}")
            
            # Create enhanced suggestion
            enhanced_suggestion = ItemSuggestion(
                item_num=suggestion.item_num,
                description=suggestion.description,
                score=enhanced_score,
                group=suggestion.group,
                category=suggestion.category,
                provider_type=suggestion.provider_type,
                matched_fields=suggestion.matched_fields,
                evidence=f"{suggestion.evidence} | Clinical context: {'; '.join(enhancement_reasons)}"
            )
            
            filtered_suggestions.append(enhanced_suggestion)
        
        return filtered_suggestions
    
    def _apply_emergency_matching(self, 
                                suggestions: List[ItemSuggestion], 
                                clinical_context,
                                mbs_context: Dict[str, Any]) -> List[ItemSuggestion]:
        """Apply emergency department specific matching"""
        emergency_suggestions = []
        
        for suggestion in suggestions:
            enhanced_score = suggestion.score
            enhancement_reasons = []
            
            # Check for emergency department specific patterns
            description_lower = suggestion.description.lower()
            
            # High complexity emergency items
            if any(pattern in description_lower for pattern in self.emergency_patterns['high_complexity']):
                if mbs_context.get('high_complexity') or clinical_context.condition.severity in ['critical', 'severe']:
                    enhanced_score += 0.3
                    enhancement_reasons.append("High complexity emergency match: +0.30")
            
            # Age-specific emergency items
            if clinical_context.demographics.age:
                if 4 <= clinical_context.demographics.age < 75:
                    if 'aged 4 years or over but under 75 years old' in description_lower:
                        enhanced_score += 0.2
                        enhancement_reasons.append("Age 4-74 emergency match: +0.20")
                elif clinical_context.demographics.age >= 75:
                    if 'aged 75 years or over' in description_lower:
                        enhanced_score += 0.2
                        enhancement_reasons.append("Age 75+ emergency match: +0.20")
            
            # Emergency medicine specialist requirement
            if 'specialist in emergency medicine' in description_lower:
                if mbs_context.get('specialist_required') or clinical_context.provider_type == 'specialist':
                    enhanced_score += 0.15
                    enhancement_reasons.append("Emergency medicine specialist match: +0.15")
            
            # Emergency department setting
            if 'emergency department' in description_lower:
                if mbs_context.get('emergency_department'):
                    enhanced_score += 0.1
                    enhancement_reasons.append("Emergency department setting match: +0.10")
            
            # Create enhanced suggestion
            enhanced_suggestion = ItemSuggestion(
                item_num=suggestion.item_num,
                description=suggestion.description,
                score=enhanced_score,
                group=suggestion.group,
                category=suggestion.category,
                provider_type=suggestion.provider_type,
                matched_fields=suggestion.matched_fields,
                evidence=f"{suggestion.evidence} | Emergency matching: {'; '.join(enhancement_reasons)}"
            )
            
            emergency_suggestions.append(enhanced_suggestion)
        
        return emergency_suggestions
    
    def _apply_age_specific_matching(self, 
                                   suggestions: List[ItemSuggestion], 
                                   mbs_context: Dict[str, Any]) -> List[ItemSuggestion]:
        """Apply age-specific matching rules"""
        age_group = mbs_context.get('age_group')
        if not age_group:
            return suggestions
        
        age_rules = self.age_rules.get(age_group, {})
        if not age_rules:
            return suggestions
        
        enhanced_suggestions = []
        
        for suggestion in suggestions:
            enhanced_score = suggestion.score
            enhancement_reasons = []
            
            # Check if item group is preferred for this age group
            if suggestion.group in age_rules.get('preferred_groups', []):
                enhanced_score += 0.1
                enhancement_reasons.append(f"Preferred group for {age_group}: +0.10")
            
            # Check for age-specific descriptions
            description_lower = suggestion.description.lower()
            if age_group == 'elderly' and any(term in description_lower for term in ['elderly', 'aged', 'senior']):
                enhanced_score += 0.15
                enhancement_reasons.append("Elderly-specific item: +0.15")
            elif age_group == 'pediatric' and any(term in description_lower for term in ['pediatric', 'child', 'infant']):
                enhanced_score += 0.15
                enhancement_reasons.append("Pediatric-specific item: +0.15")
            
            # Create enhanced suggestion
            enhanced_suggestion = ItemSuggestion(
                item_num=suggestion.item_num,
                description=suggestion.description,
                score=enhanced_score,
                group=suggestion.group,
                category=suggestion.category,
                provider_type=suggestion.provider_type,
                matched_fields=suggestion.matched_fields,
                evidence=f"{suggestion.evidence} | Age-specific: {'; '.join(enhancement_reasons)}"
            )
            
            enhanced_suggestions.append(enhanced_suggestion)
        
        return enhanced_suggestions
    
    def _calculate_age_score_boost(self, suggestion: ItemSuggestion, age: int, mbs_context: Dict[str, Any]) -> float:
        """Calculate age-based score boost"""
        boost = 0.0
        
        # Age-specific MBS items
        description_lower = suggestion.description.lower()
        
        if 4 <= age < 75:
            if 'aged 4 years or over but under 75 years old' in description_lower:
                boost += 0.2
        elif age >= 75:
            if 'aged 75 years or over' in description_lower:
                boost += 0.2
        
        return boost
    
    def _calculate_setting_score_boost(self, suggestion: ItemSuggestion, setting: str) -> float:
        """Calculate setting-based score boost"""
        boost = 0.0
        description_lower = suggestion.description.lower()
        
        if setting == 'emergency':
            if 'emergency department' in description_lower:
                boost += 0.15
        elif setting == 'hospital':
            if 'hospital' in description_lower or 'inpatient' in description_lower:
                boost += 0.1
        elif setting == 'clinic':
            if 'clinic' in description_lower or 'outpatient' in description_lower:
                boost += 0.1
        
        return boost
    
    def _calculate_department_score_boost(self, suggestion: ItemSuggestion, department: str) -> float:
        """Calculate department-based score boost"""
        boost = 0.0
        description_lower = suggestion.description.lower()
        
        if department == 'emergency_medicine':
            if 'emergency medicine' in description_lower:
                boost += 0.15
        elif department == 'cardiology':
            if 'cardiology' in description_lower or 'cardiac' in description_lower:
                boost += 0.1
        elif department == 'respiratory':
            if 'respiratory' in description_lower or 'pulmonology' in description_lower:
                boost += 0.1
        
        return boost
    
    def _calculate_urgency_score_boost(self, suggestion: ItemSuggestion, urgency: str) -> float:
        """Calculate urgency-based score boost"""
        boost = 0.0
        description_lower = suggestion.description.lower()
        
        if urgency == 'emergency':
            if any(term in description_lower for term in ['emergency', 'urgent', 'critical', 'acute']):
                boost += 0.15
        elif urgency == 'urgent':
            if 'urgent' in description_lower:
                boost += 0.1
        
        return boost
    
    def _calculate_condition_score_boost(self, suggestion: ItemSuggestion, symptoms: List[str]) -> float:
        """Calculate condition-based score boost"""
        boost = 0.0
        description_lower = suggestion.description.lower()
        
        # Check for symptom matches in description
        symptom_matches = 0
        for symptom in symptoms:
            if symptom.lower() in description_lower:
                symptom_matches += 1
        
        if symptom_matches > 0:
            boost += min(0.1 * symptom_matches, 0.3)  # Cap at 0.3
        
        return boost
