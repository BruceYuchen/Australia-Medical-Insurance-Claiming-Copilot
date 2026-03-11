"""
Advanced Ensemble Matching System
Combines multiple models and techniques for maximum accuracy
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from collections import defaultdict
import time

from models.advanced_embeddings import get_advanced_embedding_manager
from models.medical_knowledge_graph import get_medical_knowledge_graph
from core.enhanced_database import EnhancedDatabaseManager
from core.schemas import ItemSuggestion

logger = logging.getLogger(__name__)

@dataclass
class EnsembleResult:
    """Result from ensemble matching"""
    item_num: str
    final_score: float
    component_scores: Dict[str, float]
    explanations: List[str]
    confidence: float
    evidence: str

class AdvancedEnsembleMatcher:
    """Advanced ensemble matcher combining multiple techniques"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
        self.embedding_manager = get_advanced_embedding_manager()
        self.knowledge_graph = get_medical_knowledge_graph()
        
        # Ensemble weights for different components
        self.component_weights = {
            "tfidf": 0.15,
            "semantic": 0.20,
            "hybrid": 0.15,
            "knowledge_graph": 0.25,
            "clinical_context": 0.15,
            "medical_ner": 0.10
        }
        
        # Advanced scoring parameters
        self.scoring_params = {
            "base_similarity_weight": 0.3,
            "medical_relevance_weight": 0.25,
            "context_match_weight": 0.20,
            "age_appropriateness_weight": 0.15,
            "setting_appropriateness_weight": 0.10
        }
        
        # Medical concept importance weights
        self.concept_weights = {
            "disease": 1.0,
            "symptom": 0.9,
            "treatment": 0.8,
            "procedure": 0.9,
            "medication": 0.7,
            "demographic": 0.6,
            "setting": 0.5
        }
    
    def match_clinical_scenario_advanced(self, 
                                       clinical_text: str,
                                       context: Dict[str, Any] = None,
                                       top_k: int = 10) -> List[EnsembleResult]:
        """Advanced ensemble matching for clinical scenarios"""
        
        start_time = time.time()
        
        # Step 1: Extract medical concepts using knowledge graph
        medical_concepts = self.knowledge_graph.find_concepts_by_text(clinical_text)
        concept_explanations = self.knowledge_graph.get_concept_explanations(clinical_text)
        
        # Step 2: Get embeddings using multiple models
        embeddings = self._get_ensemble_embeddings(clinical_text)
        
        # Step 3: Get medical entities using NER
        medical_entities = self.embedding_manager.get_medical_entities(clinical_text)
        
        # Step 4: Perform multiple search strategies
        search_results = self._perform_ensemble_search(
            clinical_text, embeddings, medical_concepts, context
        )
        
        # Step 5: Advanced scoring and ranking
        ensemble_results = self._calculate_ensemble_scores(
            search_results, medical_concepts, medical_entities, context
        )
        
        # Step 6: Generate detailed explanations
        final_results = self._generate_detailed_explanations(
            ensemble_results, medical_concepts, concept_explanations, context
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Advanced ensemble matching completed in {processing_time:.2f}s")
        
        return final_results[:top_k]
    
    def _get_ensemble_embeddings(self, text: str) -> Dict[str, np.ndarray]:
        """Get embeddings from multiple models (simplified for performance)"""
        embeddings = {}
        
        # Only use the most effective models to avoid timeout
        priority_models = ["clinical_sentence_transformer", "domain_specific"]
        
        for model_name in priority_models:
            if model_name in self.embedding_manager.models:
                try:
                    embedding = self.embedding_manager.get_embeddings(text, model_name)
                    if embedding.size > 0:
                        embeddings[model_name] = embedding
                except Exception as e:
                    logger.warning(f"Failed to get embeddings from {model_name}: {e}")
                    continue
        
        return embeddings
    
    def _perform_ensemble_search(self, 
                               clinical_text: str,
                               embeddings: Dict[str, np.ndarray],
                               medical_concepts: List,
                               context: Dict[str, Any] = None) -> Dict[str, List[ItemSuggestion]]:
        """Perform multiple search strategies"""
        search_results = {}
        
        # 1. TF-IDF search
        try:
            tfidf_results = self.db_manager.search_items_by_text(
                clinical_text, top_k=20, search_type="tfidf", context=context
            )
            search_results["tfidf"] = tfidf_results
        except Exception as e:
            logger.warning(f"TF-IDF search failed: {e}")
            search_results["tfidf"] = []
        
        # 2. Semantic search
        try:
            semantic_results = self.db_manager.search_items_by_text(
                clinical_text, top_k=20, search_type="semantic", context=context
            )
            search_results["semantic"] = semantic_results
        except Exception as e:
            logger.warning(f"Semantic search failed: {e}")
            search_results["semantic"] = []
        
        # 3. Hybrid search
        try:
            hybrid_results = self.db_manager.search_items_by_text(
                clinical_text, top_k=20, search_type="hybrid", context=context
            )
            search_results["hybrid"] = hybrid_results
        except Exception as e:
            logger.warning(f"Hybrid search failed: {e}")
            search_results["hybrid"] = []
        
        # 4. Knowledge graph search
        try:
            kg_recommendations = self.knowledge_graph.get_mbs_recommendations(
                clinical_text, context
            )
            search_results["knowledge_graph"] = self._convert_kg_to_suggestions(kg_recommendations)
        except Exception as e:
            logger.warning(f"Knowledge graph search failed: {e}")
            search_results["knowledge_graph"] = []
        
        # 5. Medical concept-based search (simplified)
        try:
            concept_results = self._search_by_medical_concepts(medical_concepts, context)
            search_results["medical_concepts"] = concept_results
        except Exception as e:
            logger.warning(f"Medical concept search failed: {e}")
            search_results["medical_concepts"] = []
        
        # Skip advanced embedding search to avoid timeout
        search_results["advanced_embeddings"] = []
        
        return search_results
    
    def _convert_kg_to_suggestions(self, kg_recommendations: List[Dict[str, Any]]) -> List[ItemSuggestion]:
        """Convert knowledge graph recommendations to ItemSuggestion format"""
        suggestions = []
        
        for rec in kg_recommendations:
            # Get item details from database
            item = self.db_manager.get_item_by_number(rec["item_num"])
            if item:
                suggestion = ItemSuggestion(
                    item_num=rec["item_num"],
                    description=item.description,
                    score=rec["score"],
                    group=item.group,
                    category=item.category,
                    provider_type=item.provider_type,
                    matched_fields=["knowledge_graph"],
                    evidence=f"Knowledge graph: {rec['reason']}"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _search_by_medical_concepts(self, 
                                  medical_concepts: List,
                                  context: Dict[str, Any] = None) -> List[ItemSuggestion]:
        """Search based on medical concepts"""
        suggestions = []
        
        for concept in medical_concepts:
            if concept.mbs_items:
                for item_num in concept.mbs_items:
                    item = self.db_manager.get_item_by_number(item_num)
                    if item:
                        # Calculate concept-based score
                        concept_score = self._calculate_concept_score(concept, context)
                        
                        suggestion = ItemSuggestion(
                            item_num=item_num,
                            description=item.description,
                            score=concept_score,
                            group=item.group,
                            category=item.category,
                            provider_type=item.provider_type,
                            matched_fields=["medical_concept"],
                            evidence=f"Medical concept: {concept.name} ({concept.concept_type})"
                        )
                        suggestions.append(suggestion)
        
        return suggestions
    
    def _search_by_advanced_embeddings(self, 
                                     embeddings: Dict[str, np.ndarray],
                                     context: Dict[str, Any] = None) -> List[ItemSuggestion]:
        """Search using advanced embeddings"""
        suggestions = []
        
        # This would require implementing similarity search with embeddings
        # For now, return empty list
        return suggestions
    
    def _calculate_concept_score(self, concept, context: Dict[str, Any] = None) -> float:
        """Calculate score based on medical concept"""
        base_score = 1.0
        
        # Apply concept type weight
        concept_type_weight = self.concept_weights.get(concept.concept_type, 0.5)
        base_score *= concept_type_weight
        
        # Apply context filters
        if context:
            # Age group appropriateness
            if "age_group" in context and concept.age_groups:
                if context["age_group"] in concept.age_groups:
                    base_score *= 1.2
                else:
                    base_score *= 0.8
            
            # Setting appropriateness
            if "setting" in context and concept.settings:
                if context["setting"] in concept.settings:
                    base_score *= 1.1
                else:
                    base_score *= 0.9
            
            # Severity appropriateness
            if "severity" in context and concept.severity_levels:
                if context["severity"] in concept.severity_levels:
                    base_score *= 1.1
                else:
                    base_score *= 0.9
        
        return base_score
    
    def _calculate_ensemble_scores(self, 
                                 search_results: Dict[str, List[ItemSuggestion]],
                                 medical_concepts: List,
                                 medical_entities: List[Dict[str, Any]],
                                 context: Dict[str, Any] = None) -> List[EnsembleResult]:
        """Calculate ensemble scores for all items"""
        
        # Collect all unique items
        all_items = {}
        for search_type, results in search_results.items():
            for suggestion in results:
                item_num = suggestion.item_num
                if item_num not in all_items:
                    all_items[item_num] = {
                        "item_num": item_num,
                        "description": suggestion.description,
                        "group": suggestion.group,
                        "category": suggestion.category,
                        "provider_type": suggestion.provider_type,
                        "component_scores": {},
                        "explanations": []
                    }
                
                # Store component score
                all_items[item_num]["component_scores"][search_type] = suggestion.score
                all_items[item_num]["explanations"].append(suggestion.evidence)
        
        # Calculate ensemble scores
        ensemble_results = []
        for item_num, item_data in all_items.items():
            final_score = self._calculate_final_score(
                item_data, medical_concepts, medical_entities, context
            )
            
            # Calculate confidence based on score consistency
            component_scores = list(item_data["component_scores"].values())
            confidence = self._calculate_confidence(component_scores)
            
            ensemble_result = EnsembleResult(
                item_num=item_num,
                final_score=final_score,
                component_scores=item_data["component_scores"],
                explanations=item_data["explanations"],
                confidence=confidence,
                evidence="; ".join(item_data["explanations"])
            )
            
            ensemble_results.append(ensemble_result)
        
        # Sort by final score
        ensemble_results.sort(key=lambda x: x.final_score, reverse=True)
        
        return ensemble_results
    
    def _calculate_final_score(self, 
                             item_data: Dict[str, Any],
                             medical_concepts: List,
                             medical_entities: List[Dict[str, Any]],
                             context: Dict[str, Any] = None) -> float:
        """Calculate final ensemble score"""
        
        # Weighted average of component scores
        weighted_score = 0.0
        total_weight = 0.0
        
        for search_type, score in item_data["component_scores"].items():
            weight = self.component_weights.get(search_type, 0.1)
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            base_score = weighted_score / total_weight
        else:
            base_score = 0.0
        
        # Apply advanced scoring factors
        final_score = base_score
        
        # Medical relevance boost
        medical_relevance = self._calculate_medical_relevance(
            item_data, medical_concepts, medical_entities
        )
        final_score += medical_relevance * self.scoring_params["medical_relevance_weight"]
        
        # Context match boost
        context_match = self._calculate_context_match(item_data, context)
        final_score += context_match * self.scoring_params["context_match_weight"]
        
        # Age appropriateness boost
        age_appropriateness = self._calculate_age_appropriateness(item_data, context)
        final_score += age_appropriateness * self.scoring_params["age_appropriateness_weight"]
        
        # Setting appropriateness boost
        setting_appropriateness = self._calculate_setting_appropriateness(item_data, context)
        final_score += setting_appropriateness * self.scoring_params["setting_appropriateness_weight"]
        
        return max(0.0, final_score)
    
    def _calculate_medical_relevance(self, 
                                   item_data: Dict[str, Any],
                                   medical_concepts: List,
                                   medical_entities: List[Dict[str, Any]]) -> float:
        """Calculate medical relevance score"""
        relevance = 0.0
        
        # Check if item is related to found medical concepts
        for concept in medical_concepts:
            if concept.mbs_items and item_data["item_num"] in concept.mbs_items:
                concept_weight = self.concept_weights.get(concept.concept_type, 0.5)
                relevance += concept_weight
        
        # Check medical entities
        for entity in medical_entities:
            if entity.get("entity_group") in ["DISEASE", "SYMPTOM", "TREATMENT"]:
                relevance += 0.1
        
        return min(1.0, relevance)
    
    def _calculate_context_match(self, 
                               item_data: Dict[str, Any],
                               context: Dict[str, Any] = None) -> float:
        """Calculate context match score"""
        if not context:
            return 0.0
        
        match_score = 0.0
        
        # Check group appropriateness
        if "setting" in context:
            if context["setting"] == "emergency" and item_data["group"] in ["T1", "A21"]:
                match_score += 0.3
            elif context["setting"] == "clinic" and item_data["group"] in ["A1", "A2"]:
                match_score += 0.3
        
        # Check provider type appropriateness
        if "provider" in context and item_data["provider_type"]:
            if context["provider"] == "specialist" and "specialist" in item_data["provider_type"].lower():
                match_score += 0.2
        
        return min(1.0, match_score)
    
    def _calculate_age_appropriateness(self, 
                                     item_data: Dict[str, Any],
                                     context: Dict[str, Any] = None) -> float:
        """Calculate age appropriateness score"""
        if not context or "age_group" not in context:
            return 0.0
        
        age_group = context["age_group"]
        item_num = item_data["item_num"]
        
        # Check age-specific MBS items
        if age_group == "elderly" and item_num in ["5011", "5014", "5019"]:
            return 0.5
        elif age_group == "adult" and item_num in ["5001", "5012", "5016"]:
            return 0.5
        elif age_group == "pediatric" and item_num in ["5004", "5013", "5017"]:
            return 0.5
        
        return 0.0
    
    def _calculate_setting_appropriateness(self, 
                                         item_data: Dict[str, Any],
                                         context: Dict[str, Any] = None) -> float:
        """Calculate setting appropriateness score"""
        if not context or "setting" not in context:
            return 0.0
        
        setting = context["setting"]
        description = item_data["description"].lower()
        
        if setting == "emergency" and "emergency department" in description:
            return 0.5
        elif setting == "hospital" and "hospital" in description:
            return 0.3
        elif setting == "clinic" and "consultation" in description:
            return 0.3
        
        return 0.0
    
    def _calculate_confidence(self, component_scores: List[float]) -> float:
        """Calculate confidence based on score consistency"""
        if not component_scores:
            return 0.0
        
        if len(component_scores) == 1:
            return component_scores[0]
        
        # Calculate coefficient of variation (lower is more consistent)
        mean_score = np.mean(component_scores)
        std_score = np.std(component_scores)
        
        if mean_score == 0:
            return 0.0
        
        cv = std_score / mean_score
        confidence = max(0.0, 1.0 - cv)
        
        return confidence
    
    def _generate_detailed_explanations(self, 
                                      ensemble_results: List[EnsembleResult],
                                      medical_concepts: List,
                                      concept_explanations: List[Dict[str, Any]],
                                      context: Dict[str, Any] = None) -> List[EnsembleResult]:
        """Generate detailed explanations for ensemble results"""
        
        for result in ensemble_results:
            explanations = []
            
            # Add component score explanations
            for component, score in result.component_scores.items():
                explanations.append(f"{component}: {score:.3f}")
            
            # Add medical concept explanations
            for concept in medical_concepts:
                if concept.mbs_items and result.item_num in concept.mbs_items:
                    explanations.append(f"Medical concept: {concept.name} ({concept.concept_type})")
            
            # Add confidence explanation
            if result.confidence > 0.8:
                explanations.append("High confidence match")
            elif result.confidence > 0.6:
                explanations.append("Medium confidence match")
            else:
                explanations.append("Low confidence match")
            
            # Add ensemble explanation
            explanations.append(f"Ensemble score: {result.final_score:.3f}")
            
            # Update evidence
            result.evidence = " | ".join(explanations)
        
        return ensemble_results
    
    def get_ensemble_statistics(self) -> Dict[str, Any]:
        """Get statistics about the ensemble system"""
        return {
            "component_weights": self.component_weights,
            "scoring_params": self.scoring_params,
            "concept_weights": self.concept_weights,
            "embedding_models": len(self.embedding_manager.models),
            "knowledge_graph_concepts": len(self.knowledge_graph.concepts),
            "knowledge_graph_relations": len(self.knowledge_graph.relations)
        }
