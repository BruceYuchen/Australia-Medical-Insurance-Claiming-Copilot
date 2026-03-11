#!/usr/bin/env python3
"""
Test Clinical Scenario Matching
Tests the enhanced MBS matcher with detailed clinical scenarios
"""
import requests
import json
import time

def test_clinical_scenario_matching():
    """Test the enhanced clinical scenario matching"""
    
    base_url = "http://localhost:8000"
    
    # Test case 1: 72-year-old male with emergency department presentation
    clinical_scenario_1 = """
    72-year-old male with ongoing cough and bilateral lower leg and foot swelling 
    HOPC: Ongoing cough with production of green sputum since discharge from John Faulkner Hospital six days ago following admission for exacerbation of COAD/influenza management No haemoptysis Worsening swelling of lower legs and feet bilaterally over the last week No systemic infective features reported 
    PMH: Atrial fibrillation Glaucoma Hypercholesterolaemia Gastro-oesophageal reflux disease Asthma TIA COPD, not on home oxygen Hypertension 
    Meds: Doplots (dutasteride 500 micrograms and tamsulosin 400 micrograms), 1 capsule at night Pantoprazole 40 milligrams, 1 tablet at night Giardians (Empug Liflozin) 10 milligrams, 1 tablet daily Fruzomide 20 milligrams in the morning Erythromycin 400 milligrams, 1 tablet daily, to be continued for 30 days Rivaroxaban 15 milligrams at night Emitrestor (sacubitril 24.3 milligrams and valsartan 25 milligrams), 1 tablet twice daily Caltrate, 1 tablet daily Digoxin 62.5 milligrams, 3 tablets daily Ventolin 
    Allergies: Allergic to morphine, develops high fevers 
    SH: Stopped smoking a few weeks ago 
    O/E: Oxygen saturation: 94% on good trace, 80s on poor trace Heart rate: 98, irregular Respiratory rate: 26 Blood pressure: 104/57 mmHg, MAP 69 Occasional chesty cough observed at bedside No wheeze or crackles on chest auscultation Soft, non-tender abdomen Pitting oedema of lower legs, especially ankles and feet No acute shortness of breath, but has laboured breathing 
    Impression: Cough possibly secondary to CCF or COAD Management Plan: Arrange blood tests and chest x-ray to evaluate for causes of cough and oedema Treat as both CCF and COAD exacerbation due to overlapping symptoms Recommend hospital admission for further management and monitoring
    """
    
    # Test case 2: Pediatric emergency case
    clinical_scenario_2 = """
    4-year-old female presents to emergency department with acute respiratory distress
    HOPC: Sudden onset of difficulty breathing, wheezing, and cough starting 2 hours ago. No fever. No recent illness. No known allergies.
    PMH: No significant past medical history
    O/E: Tachypneic, using accessory muscles, bilateral wheeze, oxygen saturation 88% on room air
    Impression: Acute asthma exacerbation
    Management: Nebulized bronchodilators, oxygen therapy, consider admission
    """
    
    # Test case 3: Elderly patient with complex comorbidities
    clinical_scenario_3 = """
    85-year-old female with multiple comorbidities presents to emergency department
    HOPC: Confusion, falls, decreased mobility over past 3 days. Family reports patient has been increasingly confused and unsteady.
    PMH: Dementia, hypertension, diabetes mellitus type 2, osteoarthritis, osteoporosis
    Meds: Multiple medications including antihypertensives, antidiabetics, pain management
    O/E: Confused, disoriented, unsteady gait, no focal neurological deficits
    Impression: Delirium, possible UTI, falls risk
    Management: Comprehensive geriatric assessment, investigations, multidisciplinary team involvement
    """
    
    test_cases = [
        {
            "name": "72-year-old male with respiratory and cardiovascular symptoms",
            "scenario": clinical_scenario_1,
            "expected_items": ["5016", "14270", "14272"],  # Emergency medicine items
            "expected_groups": ["T1", "T2"],
            "expected_keywords": ["emergency", "specialist", "aged 4 years or over but under 75 years old"]
        },
        {
            "name": "4-year-old female with acute respiratory distress",
            "scenario": clinical_scenario_2,
            "expected_items": ["5016", "14270", "14272"],  # Emergency medicine items
            "expected_groups": ["T1", "T2"],
            "expected_keywords": ["emergency", "pediatric", "respiratory"]
        },
        {
            "name": "85-year-old female with complex comorbidities",
            "scenario": clinical_scenario_3,
            "expected_items": ["5016", "14270", "14272"],  # Emergency medicine items
            "expected_groups": ["T1", "T2"],
            "expected_keywords": ["emergency", "aged 75 years or over", "elderly"]
        }
    ]
    
    print("🧪 Testing Clinical Scenario Matching")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Test the clinical scenario matching endpoint
            response = requests.post(
                f"{base_url}/match_clinical_scenario",
                json={
                    "transcript": test_case["scenario"],
                    "context": {
                        "setting": "emergency",
                        "duration": 30,
                        "provider": "specialist",
                        "referral": False,
                        "date": "2024-01-15T10:30:00",
                        "patient_type": "community"
                    },
                    "top_k": 5
                },
                params={"search_type": "hybrid"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                
                print(f"✅ Found {len(suggestions)} suggestions")
                
                # Display top suggestions
                for j, suggestion in enumerate(suggestions[:3], 1):
                    item_num = suggestion.get("item_num", "N/A")
                    score = suggestion.get("score", 0)
                    group = suggestion.get("group", "N/A")
                    description = suggestion.get("description", "")[:100] + "..."
                    evidence = suggestion.get("evidence", "")
                    
                    print(f"  {j}. Item {item_num} (Group: {group}, Score: {score:.3f})")
                    print(f"     Description: {description}")
                    print(f"     Evidence: {evidence}")
                    print()
                
                # Check for expected items
                found_items = [s["item_num"] for s in suggestions]
                expected_found = [item for item in test_case["expected_items"] if item in found_items]
                
                if expected_found:
                    print(f"✅ Found expected items: {expected_found}")
                else:
                    print(f"⚠️  Expected items not found: {test_case['expected_items']}")
                
                # Check for expected groups
                found_groups = [s["group"] for s in suggestions]
                expected_groups_found = [group for group in test_case["expected_groups"] if group in found_groups]
                
                if expected_groups_found:
                    print(f"✅ Found expected groups: {expected_groups_found}")
                else:
                    print(f"⚠️  Expected groups not found: {test_case['expected_groups']}")
                
                # Check for expected keywords in descriptions
                all_descriptions = " ".join([s["description"] for s in suggestions]).lower()
                keywords_found = [kw for kw in test_case["expected_keywords"] if kw.lower() in all_descriptions]
                
                if keywords_found:
                    print(f"✅ Found expected keywords: {keywords_found}")
                else:
                    print(f"⚠️  Expected keywords not found: {test_case['expected_keywords']}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print()
    
    print("🎯 Clinical Scenario Matching Test Complete!")

def test_emergency_department_specific_matching():
    """Test emergency department specific matching"""
    
    base_url = "http://localhost:8000"
    
    print("\n🏥 Testing Emergency Department Specific Matching")
    print("=" * 60)
    
    # Test emergency department specific queries
    emergency_queries = [
        {
            "name": "Emergency department high complexity",
            "query": "Emergency department specialist medical decision making high complexity aged 4 years or over but under 75 years old",
            "expected_item": "5016"
        },
        {
            "name": "Emergency department elderly patient",
            "query": "Emergency department specialist medical decision making high complexity aged 75 years or over",
            "expected_item": "5016"
        },
        {
            "name": "Emergency department management",
            "query": "Management fractures dislocations emergency department specialist",
            "expected_items": ["14270", "14272"]
        }
    ]
    
    for i, query_test in enumerate(emergency_queries, 1):
        print(f"\n🔍 Test {i}: {query_test['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/match_clinical_scenario",
                json={
                    "transcript": query_test["query"],
                    "context": {
                        "setting": "emergency",
                        "duration": 30,
                        "provider": "specialist",
                        "referral": False,
                        "date": "2024-01-15T10:30:00",
                        "patient_type": "community"
                    },
                    "top_k": 3
                },
                params={"search_type": "hybrid"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                
                print(f"✅ Found {len(suggestions)} suggestions")
                
                for j, suggestion in enumerate(suggestions, 1):
                    item_num = suggestion.get("item_num", "N/A")
                    score = suggestion.get("score", 0)
                    description = suggestion.get("description", "")[:100] + "..."
                    
                    print(f"  {j}. Item {item_num} (Score: {score:.3f})")
                    print(f"     Description: {description}")
                    print()
                
                # Check for expected items
                found_items = [s["item_num"] for s in suggestions]
                expected_items = query_test.get("expected_items", [query_test.get("expected_item")])
                expected_items = [item for item in expected_items if item]
                
                expected_found = [item for item in expected_items if item in found_items]
                
                if expected_found:
                    print(f"✅ Found expected items: {expected_found}")
                else:
                    print(f"⚠️  Expected items not found: {expected_items}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 Starting Clinical Scenario Matching Tests")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Please start the server first: python3 run_server.py")
        exit(1)
    
    # Run tests
    test_clinical_scenario_matching()
    test_emergency_department_specific_matching()
    
    print("\n🎉 All tests completed!")
