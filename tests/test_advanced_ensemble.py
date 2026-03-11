#!/usr/bin/env python3
"""
Test script for Advanced Ensemble Matching System
Demonstrates the enhanced accuracy with multiple models and medical knowledge
"""

import requests
import json
import time

def test_advanced_ensemble_matching():
    """Test the advanced ensemble matching system"""
    
    print("🚀 Testing Advanced Ensemble Matching System")
    print("=" * 60)
    
    # Your complex clinical scenario
    clinical_text = """
    72-year-old male with ongoing cough and bilateral lower leg and foot swelling 
    HOPC: Ongoing cough with production of green sputum since discharge from John Faulkner Hospital six days ago following admission for exacerbation of COAD/influenza management No haemoptysis Worsening swelling of lower legs and feet bilaterally over the last week No systemic infective features reported 
    PMH: Atrial fibrillation Glaucoma Hypercholesterolaemia Gastro-oesophageal reflux disease Asthma TIA COPD, not on home oxygen Hypertension 
    Meds: Doplots (dutasteride 500 micrograms and tamsulosin 400 micrograms), 1 capsule at night Pantoprazole 40 milligrams, 1 tablet at night Giardians (Empug Liflozin) 10 milligrams, 1 tablet daily Fruzomide 20 milligrams in the morning Erythromycin 400 milligrams, 1 tablet daily, to be continued for 30 days Rivaroxaban 15 milligrams at night Emitrestor (sacubitril 24.3 milligrams and valsartan 25 milligrams), 1 tablet twice daily Caltrate, 1 tablet daily Digoxin 62.5 milligrams, 3 tablets daily Ventolin 
    Allergies: Allergic to morphine, develops high fevers 
    SH: Stopped smoking a few weeks ago 
    O/E: Oxygen saturation: 94% on good trace, 80s on poor trace Heart rate: 98, irregular Respiratory rate: 26 Blood pressure: 104/57 mmHg, MAP 69 Occasional chesty cough observed at bedside No wheeze or crackles on chest auscultation Soft, non-tender abdomen Pitting oedema of lower legs, especially ankles and feet No acute shortness of breath, but has laboured breathing 
    Impression: Cough possibly secondary to CCF or COAD Management Plan: Arrange blood tests and chest x-ray to evaluate for causes of cough and oedema Treat as both CCF and COAD exacerbation due to overlapping symptoms Recommend hospital admission for further management and monitoring
    """
    
    context = {
        "setting": "emergency",
        "duration": 30,
        "provider": "specialist",
        "referral": False,
        "date": "2024-01-15T10:30:00",
        "patient_type": "community",
        "age_group": "elderly",
        "severity": "severe"
    }
    
    print("📋 Input Clinical Scenario:")
    print(f"Patient: 72-year-old male")
    print(f"Chief Complaint: Ongoing cough and bilateral lower leg and foot swelling")
    print(f"Setting: Emergency department (hospital admission recommended)")
    print(f"Complexity: High (multiple comorbidities)")
    print()
    
    # Test different endpoints
    endpoints = [
        {
            "name": "Basic Enhanced",
            "url": "http://localhost:8000/suggest_items_enhanced",
            "params": {"search_type": "hybrid"}
        },
        {
            "name": "Clinical Scenario",
            "url": "http://localhost:8000/match_clinical_scenario",
            "params": {"search_type": "hybrid"}
        },
        {
            "name": "Advanced Ensemble",
            "url": "http://localhost:8000/match_clinical_scenario_advanced",
            "params": {}
        }
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"🔍 Testing {endpoint['name']} System")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                endpoint["url"],
                json={
                    "transcript": clinical_text,
                    "context": context,
                    "top_k": 5
                },
                params=endpoint["params"],
                timeout=60  # Longer timeout for advanced models
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"✅ Found {len(suggestions)} suggestions in {processing_time:.2f}s")
                
                target_items_found = []
                for i, suggestion in enumerate(suggestions, 1):
                    item_num = suggestion.get('item_num', 'N/A')
                    score = suggestion.get('score', 0)
                    group = suggestion.get('group', 'N/A')
                    description = suggestion.get('description', '')[:100] + '...'
                    evidence = suggestion.get('evidence', '')
                    
                    print(f"{i}. Item {item_num} (Group: {group}, Score: {score:.3f})")
                    print(f"   {description}")
                    print(f"   Evidence: {evidence[:150]}...")
                    
                    if item_num in ['5016', '14270', '14272']:
                        target_items_found.append(item_num)
                        print(f"   🎯 TARGET ITEM FOUND: {item_num}")
                    print()
                
                results[endpoint['name']] = {
                    "success": True,
                    "processing_time": processing_time,
                    "total_found": len(suggestions),
                    "target_items": target_items_found,
                    "top_score": suggestions[0].get('score', 0) if suggestions else 0
                }
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(response.text)
                results[endpoint['name']] = {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results[endpoint['name']] = {
                "success": False,
                "error": str(e)
            }
        
        print()
    
    # Compare results
    print("📊 COMPARISON RESULTS")
    print("=" * 60)
    
    for name, result in results.items():
        if result["success"]:
            print(f"{name}:")
            print(f"  ✅ Processing time: {result['processing_time']:.2f}s")
            print(f"  📈 Total found: {result['total_found']}")
            print(f"  🎯 Target items: {result['target_items']}")
            print(f"  📊 Top score: {result['top_score']:.3f}")
            print(f"  🏆 Accuracy: {len(result['target_items'])}/3 target items")
        else:
            print(f"{name}: ❌ Failed - {result['error']}")
        print()
    
    # Summary
    print("🎉 SUMMARY")
    print("=" * 60)
    
    successful_results = [r for r in results.values() if r["success"]]
    if successful_results:
        best_result = max(successful_results, key=lambda x: len(x["target_items"]))
        best_name = [name for name, result in results.items() if result == best_result][0]
        
        print(f"🏆 Best performing system: {best_name}")
        print(f"   Target items found: {len(best_result['target_items'])}/3")
        print(f"   Processing time: {best_result['processing_time']:.2f}s")
        print(f"   Top score: {best_result['top_score']:.3f}")
        
        if len(best_result['target_items']) == 3:
            print("   🎯 PERFECT MATCH: All target items found!")
        elif len(best_result['target_items']) >= 2:
            print("   ✅ EXCELLENT: Most target items found!")
        elif len(best_result['target_items']) >= 1:
            print("   👍 GOOD: Some target items found!")
        else:
            print("   ⚠️  NEEDS IMPROVEMENT: No target items found")
    
    print()
    print("🔧 Advanced Features Demonstrated:")
    print("• Multiple embedding models (Clinical BERT, BioBERT, etc.)")
    print("• Medical knowledge graph with concept relationships")
    print("• Named Entity Recognition for medical terms")
    print("• Ensemble scoring with weighted components")
    print("• Advanced medical concept matching")
    print("• Context-aware scoring algorithms")
    print("• Detailed evidence generation")

if __name__ == "__main__":
    test_advanced_ensemble_matching()
