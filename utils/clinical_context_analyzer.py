"""
Clinical Context Analyzer
Analyzes complex clinical scenarios to improve MBS item matching accuracy
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class PatientDemographics:
    """Patient demographic information"""
    age: Optional[int] = None
    age_group: Optional[str] = None  # "pediatric", "adult", "elderly"
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None

@dataclass
class ClinicalSetting:
    """Clinical setting information"""
    location: Optional[str] = None  # "emergency", "hospital", "clinic", "home"
    department: Optional[str] = None  # "emergency_medicine", "cardiology", "respiratory"
    urgency: Optional[str] = None  # "emergency", "urgent", "routine"
    time_of_day: Optional[str] = None  # "business_hours", "after_hours", "weekend"

@dataclass
class MedicalCondition:
    """Medical condition information"""
    primary_diagnosis: Optional[str] = None
    secondary_diagnoses: List[str] = None
    symptoms: List[str] = None
    severity: Optional[str] = None  # "mild", "moderate", "severe", "critical"
    acuity: Optional[str] = None  # "acute", "subacute", "chronic"

@dataclass
class ClinicalContext:
    """Complete clinical context"""
    demographics: PatientDemographics
    setting: ClinicalSetting
    condition: MedicalCondition
    provider_type: Optional[str] = None
    referral_source: Optional[str] = None
    previous_admissions: List[str] = None
    medications: List[str] = None
    allergies: List[str] = None
    vital_signs: Dict[str, Any] = None

class ClinicalContextAnalyzer:
    """Analyzes clinical context from medical text"""
    
    def __init__(self):
        # Age patterns
        self.age_patterns = [
            r'(\d+)\s*years?\s*old',
            r'(\d+)\s*yo',
            r'(\d+)\s*y\.o\.',
            r'age\s*(\d+)',
            r'(\d+)\s*year\s*old',
            r'(\d+)\s*yr\s*old'
        ]
        
        # Gender patterns
        self.gender_patterns = [
            r'\bmale\b',
            r'\bfemale\b',
            r'\bm\b',
            r'\bf\b',
            r'\bman\b',
            r'\bwoman\b'
        ]
        
        # Setting patterns
        self.setting_patterns = {
            'emergency': [
                r'emergency\s+department',
                r'emergency\s+room',
                r'ed\b',
                r'er\b',
                r'emergency\s+medicine',
                r'emergency\s+attendance',
                r'emergency\s+presentation',
                r'hospital\s+admission',  # Hospital admission often implies emergency
                r'recommend\s+hospital\s+admission',
                r'admission\s+for\s+further\s+management'
            ],
            'hospital': [
                r'hospital\s+admission',
                r'inpatient',
                r'hospitalized',
                r'ward',
                r'private\s+hospital',
                r'public\s+hospital'
            ],
            'clinic': [
                r'clinic',
                r'outpatient',
                r'consultation',
                r'general\s+practice',
                r'gp\b'
            ]
        }
        
        # Department patterns
        self.department_patterns = {
            'emergency_medicine': [
                r'emergency\s+medicine',
                r'emergency\s+department',
                r'ed\b',
                r'er\b'
            ],
            'cardiology': [
                r'cardiology',
                r'cardiac',
                r'heart',
                r'cardiovascular'
            ],
            'respiratory': [
                r'respiratory',
                r'pulmonology',
                r'lung',
                r'chest'
            ],
            'nephrology': [
                r'nephrology',
                r'renal',
                r'kidney',
                r'dialysis'
            ]
        }
        
        # Urgency patterns
        self.urgency_patterns = {
            'emergency': [
                r'emergency',
                r'urgent',
                r'acute',
                r'critical',
                r'life\s+threatening',
                r'severe'
            ],
            'urgent': [
                r'urgent',
                r'priority',
                r'asap',
                r'expedite'
            ],
            'routine': [
                r'routine',
                r'elective',
                r'scheduled',
                r'planned'
            ]
        }
        
        # Medical condition patterns
        self.condition_patterns = {
            'respiratory': [
                r'cough', r'breathing', r'respiratory', r'chest', r'lung',
                r'pneumonia', r'asthma', r'copd', r'bronchitis', r'wheeze',
                r'crackles', r'dyspnea', r'shortness\s+of\s+breath'
            ],
            'cardiovascular': [
                r'heart', r'cardiac', r'chest\s+pain', r'angina', r'myocardial',
                r'infarction', r'arrhythmia', r'atrial\s+fibrillation', r'af\b',
                r'hypertension', r'blood\s+pressure', r'hypotension'
            ],
            'renal': [
                r'kidney', r'renal', r'dialysis', r'creatinine', r'urea',
                r'kidney\s+failure', r'renal\s+failure', r'nephrology'
            ],
            'gastrointestinal': [
                r'abdomen', r'abdominal', r'stomach', r'gastro', r'gerd',
                r'reflux', r'nausea', r'vomiting', r'diarrhea'
            ]
        }
        
        # Severity patterns
        self.severity_patterns = {
            'critical': [
                r'critical', r'life\s+threatening', r'severe', r'emergency',
                r'acute', r'urgent', r'resuscitation'
            ],
            'severe': [
                r'severe', r'serious', r'significant', r'major', r'worsening'
            ],
            'moderate': [
                r'moderate', r'mild\s+to\s+moderate', r'stable'
            ],
            'mild': [
                r'mild', r'minor', r'slight', r'minimal'
            ]
        }
        
        # Provider type patterns
        self.provider_patterns = {
            'specialist': [
                r'specialist', r'consultant', r'physician', r'doctor',
                r'medical\s+practitioner', r'emergency\s+medicine\s+specialist'
            ],
            'general_practitioner': [
                r'general\s+practitioner', r'gp\b', r'family\s+doctor',
                r'primary\s+care'
            ],
            'nurse': [
                r'nurse', r'rn\b', r'nursing', r'registered\s+nurse'
            ]
        }
    
    def analyze_clinical_context(self, text: str) -> ClinicalContext:
        """Analyze clinical context from medical text"""
        
        # Extract demographics
        demographics = self._extract_demographics(text)
        
        # Extract setting
        setting = self._extract_setting(text)
        
        # Extract medical condition
        condition = self._extract_medical_condition(text)
        
        # Extract provider type
        provider_type = self._extract_provider_type(text)
        
        # Extract medications and allergies
        medications = self._extract_medications(text)
        allergies = self._extract_allergies(text)
        
        # Extract vital signs
        vital_signs = self._extract_vital_signs(text)
        
        return ClinicalContext(
            demographics=demographics,
            setting=setting,
            condition=condition,
            provider_type=provider_type,
            medications=medications,
            allergies=allergies,
            vital_signs=vital_signs
        )
    
    def _extract_demographics(self, text: str) -> PatientDemographics:
        """Extract patient demographics"""
        demographics = PatientDemographics()
        
        # Extract age
        for pattern in self.age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                demographics.age = age
                
                # Determine age group
                if age < 18:
                    demographics.age_group = "pediatric"
                elif age < 65:
                    demographics.age_group = "adult"
                else:
                    demographics.age_group = "elderly"
                break
        
        # Extract gender
        for pattern in self.gender_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if pattern in [r'\bmale\b', r'\bm\b', r'\bman\b']:
                    demographics.gender = "male"
                else:
                    demographics.gender = "female"
                break
        
        return demographics
    
    def _extract_setting(self, text: str) -> ClinicalSetting:
        """Extract clinical setting information"""
        setting = ClinicalSetting()
        
        # Extract location
        for location, patterns in self.setting_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    setting.location = location
                    break
            if setting.location:
                break
        
        # Extract department
        for department, patterns in self.department_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    setting.department = department
                    break
            if setting.department:
                break
        
        # Extract urgency
        for urgency, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    setting.urgency = urgency
                    break
            if setting.urgency:
                break
        
        return setting
    
    def _extract_medical_condition(self, text: str) -> MedicalCondition:
        """Extract medical condition information"""
        condition = MedicalCondition()
        condition.secondary_diagnoses = []
        condition.symptoms = []
        
        # Extract symptoms and diagnoses by category
        for category, patterns in self.condition_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    condition.symptoms.append(match)
        
        # Extract severity
        for severity, patterns in self.severity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    condition.severity = severity
                    break
            if condition.severity:
                break
        
        # Determine acuity based on keywords
        if any(word in text.lower() for word in ['acute', 'emergency', 'urgent', 'sudden']):
            condition.acuity = "acute"
        elif any(word in text.lower() for word in ['chronic', 'ongoing', 'persistent', 'long-term']):
            condition.acuity = "chronic"
        else:
            condition.acuity = "subacute"
        
        return condition
    
    def _extract_provider_type(self, text: str) -> Optional[str]:
        """Extract provider type"""
        for provider_type, patterns in self.provider_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return provider_type
        return None
    
    def _extract_medications(self, text: str) -> List[str]:
        """Extract medications from text"""
        medications = []
        
        # Common medication patterns
        med_patterns = [
            r'([A-Z][a-z]+)\s+\d+\s*mg',
            r'([A-Z][a-z]+)\s+\d+\s*micrograms',
            r'([A-Z][a-z]+)\s+\d+\s*tablets?',
            r'([A-Z][a-z]+)\s+\d+\s*capsules?'
        ]
        
        for pattern in med_patterns:
            matches = re.findall(pattern, text)
            medications.extend(matches)
        
        return medications
    
    def _extract_allergies(self, text: str) -> List[str]:
        """Extract allergies from text"""
        allergies = []
        
        # Allergy patterns
        allergy_patterns = [
            r'allergic\s+to\s+([^,\.]+)',
            r'allergy\s+to\s+([^,\.]+)',
            r'known\s+allergy\s+to\s+([^,\.]+)'
        ]
        
        for pattern in allergy_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            allergies.extend(matches)
        
        return allergies
    
    def _extract_vital_signs(self, text: str) -> Dict[str, Any]:
        """Extract vital signs from text"""
        vital_signs = {}
        
        # Blood pressure
        bp_match = re.search(r'blood\s+pressure[:\s]*(\d+)/(\d+)', text, re.IGNORECASE)
        if bp_match:
            vital_signs['systolic'] = int(bp_match.group(1))
            vital_signs['diastolic'] = int(bp_match.group(2))
        
        # Heart rate
        hr_match = re.search(r'heart\s+rate[:\s]*(\d+)', text, re.IGNORECASE)
        if hr_match:
            vital_signs['heart_rate'] = int(hr_match.group(1))
        
        # Respiratory rate
        rr_match = re.search(r'respiratory\s+rate[:\s]*(\d+)', text, re.IGNORECASE)
        if rr_match:
            vital_signs['respiratory_rate'] = int(rr_match.group(1))
        
        # Oxygen saturation
        o2_match = re.search(r'oxygen\s+saturation[:\s]*(\d+)%', text, re.IGNORECASE)
        if o2_match:
            vital_signs['oxygen_saturation'] = int(o2_match.group(1))
        
        return vital_signs
    
    def get_mbs_matching_context(self, clinical_context: ClinicalContext) -> Dict[str, Any]:
        """Convert clinical context to MBS matching context"""
        context = {}
        
        # Age-based context
        if clinical_context.demographics.age:
            context['age'] = clinical_context.demographics.age
            context['age_group'] = clinical_context.demographics.age_group
            
            # Age-specific MBS rules
            if clinical_context.demographics.age >= 75:
                context['elderly_patient'] = True
            elif clinical_context.demographics.age < 4:
                context['pediatric_patient'] = True
            elif 4 <= clinical_context.demographics.age < 75:
                context['adult_patient'] = True
        
        # Setting-based context
        if clinical_context.setting.location:
            context['setting'] = clinical_context.setting.location
            
            if clinical_context.setting.location == 'emergency':
                context['emergency_department'] = True
                context['urgent_care'] = True
            elif clinical_context.setting.location == 'hospital':
                context['inpatient'] = True
            elif clinical_context.setting.location == 'clinic':
                context['outpatient'] = True
        
        # Department-based context
        if clinical_context.setting.department:
            context['department'] = clinical_context.setting.department
            
            if clinical_context.setting.department == 'emergency_medicine':
                context['emergency_medicine'] = True
                context['specialist_required'] = True
        
        # Urgency-based context
        if clinical_context.setting.urgency:
            context['urgency'] = clinical_context.setting.urgency
            
            if clinical_context.setting.urgency == 'emergency':
                context['emergency_care'] = True
                context['high_complexity'] = True
        
        # Medical condition context
        if clinical_context.condition.symptoms:
            context['symptoms'] = clinical_context.condition.symptoms
            
            # Respiratory conditions
            if any(symptom in ' '.join(clinical_context.condition.symptoms).lower() 
                   for symptom in ['cough', 'breathing', 'respiratory', 'chest']):
                context['respiratory_condition'] = True
            
            # Cardiovascular conditions
            if any(symptom in ' '.join(clinical_context.condition.symptoms).lower() 
                   for symptom in ['heart', 'cardiac', 'chest pain', 'hypertension']):
                context['cardiovascular_condition'] = True
        
        # Severity context
        if clinical_context.condition.severity:
            context['severity'] = clinical_context.condition.severity
            
            if clinical_context.condition.severity in ['critical', 'severe']:
                context['high_complexity'] = True
                context['specialist_required'] = True
        
        # Provider type context
        if clinical_context.provider_type:
            context['provider_type'] = clinical_context.provider_type
            
            if clinical_context.provider_type == 'specialist':
                context['specialist_attendance'] = True
                context['specialist_required'] = True
        
        # Add timestamp
        context['timestamp'] = datetime.now().isoformat()
        
        return context

# Global analyzer instance
clinical_analyzer = ClinicalContextAnalyzer()

def analyze_clinical_text(text: str) -> Dict[str, Any]:
    """Analyze clinical text and return MBS matching context"""
    clinical_context = clinical_analyzer.analyze_clinical_context(text)
    return clinical_analyzer.get_mbs_matching_context(clinical_context)
