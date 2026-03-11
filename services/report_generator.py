#!/usr/bin/env python3
"""
Medical Report Generator for MBS Claims and Records
Generates comprehensive medical reports for billing and documentation
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ReportType(Enum):
    """Report types"""
    CLAIM_SUMMARY = "claim_summary"
    DETAILED_RECORD = "detailed_record"
    BILLING_REPORT = "billing_report"
    AUDIT_TRAIL = "audit_trail"
    PATIENT_SUMMARY = "patient_summary"

class ReportFormat(Enum):
    """Report formats"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    TEXT = "text"

@dataclass
class PatientInfo:
    """Patient information"""
    patient_id: str
    name: str
    date_of_birth: str
    gender: str
    address: str
    medicare_number: str
    phone: str
    email: str = ""

@dataclass
class ProviderInfo:
    """Healthcare provider information"""
    provider_id: str
    name: str
    title: str
    specialty: str
    practice_name: str
    address: str
    phone: str
    email: str
    provider_number: str

@dataclass
class ConsultationInfo:
    """Consultation information"""
    consultation_id: str
    date: str
    time: str
    duration: int  # minutes
    setting: str
    chief_complaint: str
    history: str
    examination: str
    diagnosis: str
    treatment_plan: str
    follow_up: str
    referral: bool
    referral_reason: str = ""

@dataclass
class MBSItemInfo:
    """MBS item information"""
    item_number: str
    description: str
    fee: float
    group: str
    category: int
    provider_type: str
    confidence_score: float
    evidence: str
    validation_status: str
    validation_notes: str = ""

class MedicalReportGenerator:
    """Medical report generator for MBS claims and records"""
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        
        # Create directories if they don't exist
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize templates
        self._load_templates()
    
    def _load_templates(self):
        """Load report templates"""
        self.templates = {
            ReportType.CLAIM_SUMMARY: self._get_claim_summary_template(),
            ReportType.DETAILED_RECORD: self._get_detailed_record_template(),
            ReportType.BILLING_REPORT: self._get_billing_report_template(),
            ReportType.AUDIT_TRAIL: self._get_audit_trail_template(),
            ReportType.PATIENT_SUMMARY: self._get_patient_summary_template()
        }
    
    def generate_report(self, 
                       report_type: ReportType,
                       patient: PatientInfo,
                       provider: ProviderInfo,
                       consultation: ConsultationInfo,
                       mbs_items: List[MBSItemInfo],
                       validation_result: Dict[str, Any],
                       format: ReportFormat = ReportFormat.HTML,
                       additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a medical report
        
        Args:
            report_type: Type of report to generate
            patient: Patient information
            provider: Provider information
            consultation: Consultation information
            mbs_items: List of MBS items
            validation_result: Validation results
            format: Output format
            additional_data: Additional data for the report
            
        Returns:
            Dictionary containing report data and file path
        """
        try:
            # Prepare report data
            report_data = self._prepare_report_data(
                patient, provider, consultation, mbs_items, 
                validation_result, additional_data
            )
            
            # Generate report based on type and format
            if format == ReportFormat.HTML:
                content = self._generate_html_report(report_type, report_data)
                file_extension = "html"
            elif format == ReportFormat.JSON:
                content = self._generate_json_report(report_type, report_data)
                file_extension = "json"
            elif format == ReportFormat.TEXT:
                content = self._generate_text_report(report_type, report_data)
                file_extension = "txt"
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type.value}_{timestamp}.{file_extension}"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "report_type": report_type.value,
                "format": format.value,
                "filepath": filepath,
                "filename": filename,
                "generated_at": datetime.now().isoformat(),
                "content": content,
                "data": report_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "report_type": report_type.value,
                "format": format.value
            }
    
    def _prepare_report_data(self, 
                           patient: PatientInfo,
                           provider: ProviderInfo,
                           consultation: ConsultationInfo,
                           mbs_items: List[MBSItemInfo],
                           validation_result: Dict[str, Any],
                           additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare data for report generation"""
        
        # Calculate totals
        total_fee = sum(item.fee for item in mbs_items)
        billable_items = [item for item in mbs_items if item.validation_status == "approved"]
        rejected_items = [item for item in mbs_items if item.validation_status == "rejected"]
        
        billable_total = sum(item.fee for item in billable_items)
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "report_id": f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            },
            "patient": {
                "patient_id": patient.patient_id,
                "name": patient.name,
                "date_of_birth": patient.date_of_birth,
                "gender": patient.gender,
                "address": patient.address,
                "medicare_number": patient.medicare_number,
                "phone": patient.phone,
                "email": patient.email
            },
            "provider": {
                "provider_id": provider.provider_id,
                "name": provider.name,
                "title": provider.title,
                "specialty": provider.specialty,
                "practice_name": provider.practice_name,
                "address": provider.address,
                "phone": provider.phone,
                "email": provider.email,
                "provider_number": provider.provider_number
            },
            "consultation": {
                "consultation_id": consultation.consultation_id,
                "date": consultation.date,
                "time": consultation.time,
                "duration": consultation.duration,
                "setting": consultation.setting,
                "chief_complaint": consultation.chief_complaint,
                "history": consultation.history,
                "examination": consultation.examination,
                "diagnosis": consultation.diagnosis,
                "treatment_plan": consultation.treatment_plan,
                "follow_up": consultation.follow_up,
                "referral": consultation.referral,
                "referral_reason": consultation.referral_reason
            },
            "mbs_items": [
                {
                    "item_number": item.item_number,
                    "description": item.description,
                    "fee": item.fee,
                    "group": item.group,
                    "category": item.category,
                    "provider_type": item.provider_type,
                    "confidence_score": item.confidence_score,
                    "evidence": item.evidence,
                    "validation_status": item.validation_status,
                    "validation_notes": item.validation_notes
                }
                for item in mbs_items
            ],
            "validation": validation_result,
            "financial_summary": {
                "total_items": len(mbs_items),
                "billable_items": len(billable_items),
                "rejected_items": len(rejected_items),
                "total_fee": total_fee,
                "billable_total": billable_total,
                "rejected_total": total_fee - billable_total
            },
            "additional_data": additional_data or {}
        }
    
    def _generate_html_report(self, report_type: ReportType, data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        template = self.templates[report_type]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Report - {data['report_metadata']['report_id']}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="report-container">
        <header class="report-header">
            <h1>Medical Report</h1>
            <div class="report-meta">
                <p><strong>Report ID:</strong> {data['report_metadata']['report_id']}</p>
                <p><strong>Generated:</strong> {data['report_metadata']['generated_at']}</p>
            </div>
        </header>
        
        {template.format(**data)}
        
        <footer class="report-footer">
            <p>Generated by MBS Matching System v{data['report_metadata']['generator_version']}</p>
            <p>This report is generated locally and contains no external data transmission.</p>
        </footer>
    </div>
</body>
</html>
        """
        
        # Replace template placeholders
        html = html.replace('{mbs_items_table_rows}', self.generate_mbs_items_table_rows(data['mbs_items']))
        html = html.replace('{mbs_items_detailed_table_rows}', self.generate_detailed_mbs_items_table_rows(data['mbs_items']))
        html = html.replace('{billing_items_table_rows}', self.generate_billing_items_table_rows(data['mbs_items']))
        html = html.replace('{billable_items_list}', self.generate_billable_items_list(data['validation']))
        html = html.replace('{rejected_items_section}', self.generate_rejected_items_section(data['validation']))
        html = html.replace('{conflicts_section}', self.generate_conflicts_section(data['validation']))
        html = html.replace('{fixes_section}', self.generate_fixes_section(data['validation']))
        html = html.replace('{referral_section}', self.generate_referral_section(data['consultation']))
        
        # Format the template with data
        try:
            html = html.format(**data)
        except KeyError as e:
            print(f"Template formatting error: {e}")
            # Fallback to basic formatting
            html = html.replace('{patient[name]}', data.get('patient', {}).get('name', 'N/A'))
            html = html.replace('{patient[date_of_birth]}', data.get('patient', {}).get('date_of_birth', 'N/A'))
            html = html.replace('{patient[gender]}', data.get('patient', {}).get('gender', 'N/A'))
            html = html.replace('{patient[medicare_number]}', data.get('patient', {}).get('medicare_number', 'N/A'))
            html = html.replace('{patient[phone]}', data.get('patient', {}).get('phone', 'N/A'))
            html = html.replace('{patient[email]}', data.get('patient', {}).get('email', 'N/A'))
            html = html.replace('{patient[address]}', data.get('patient', {}).get('address', 'N/A'))
            
            html = html.replace('{provider[name]}', data.get('provider', {}).get('name', 'N/A'))
            html = html.replace('{provider[title]}', data.get('provider', {}).get('title', 'N/A'))
            html = html.replace('{provider[specialty]}', data.get('provider', {}).get('specialty', 'N/A'))
            html = html.replace('{provider[practice_name]}', data.get('provider', {}).get('practice_name', 'N/A'))
            html = html.replace('{provider[provider_number]}', data.get('provider', {}).get('provider_number', 'N/A'))
            html = html.replace('{provider[phone]}', data.get('provider', {}).get('phone', 'N/A'))
            
            html = html.replace('{consultation[date]}', data.get('consultation', {}).get('date', 'N/A'))
            html = html.replace('{consultation[time]}', data.get('consultation', {}).get('time', 'N/A'))
            html = html.replace('{consultation[duration]}', str(data.get('consultation', {}).get('duration', 'N/A')))
            html = html.replace('{consultation[setting]}', data.get('consultation', {}).get('setting', 'N/A'))
            html = html.replace('{consultation[chief_complaint]}', data.get('consultation', {}).get('chief_complaint', 'N/A'))
            html = html.replace('{consultation[history]}', data.get('consultation', {}).get('history', 'N/A'))
            html = html.replace('{consultation[examination]}', data.get('consultation', {}).get('examination', 'N/A'))
            html = html.replace('{consultation[diagnosis]}', data.get('consultation', {}).get('diagnosis', 'N/A'))
            html = html.replace('{consultation[treatment_plan]}', data.get('consultation', {}).get('treatment_plan', 'N/A'))
            html = html.replace('{consultation[follow_up]}', data.get('consultation', {}).get('follow_up', 'N/A'))
            
            html = html.replace('{validation[billable_items]}', str(data.get('validation', {}).get('billable_items', [])))
            html = html.replace('{validation[rejected_items]}', str(data.get('validation', {}).get('rejected_items', [])))
            html = html.replace('{validation[conflicts]}', str(data.get('validation', {}).get('conflicts', [])))
            html = html.replace('{validation[fixes]}', str(data.get('validation', {}).get('fixes', [])))
            html = html.replace('{validation[why]}', data.get('validation', {}).get('why', 'N/A'))
            
            html = html.replace('{financial_summary[total_items]}', str(data.get('financial_summary', {}).get('total_items', 0)))
            html = html.replace('{financial_summary[billable_items]}', str(data.get('financial_summary', {}).get('billable_items', 0)))
            html = html.replace('{financial_summary[rejected_items]}', str(data.get('financial_summary', {}).get('rejected_items', 0)))
            html = html.replace('{financial_summary[billable_total]}', f"{data.get('financial_summary', {}).get('billable_total', 0):.2f}")
            
            html = html.replace('{report_metadata[report_id]}', data.get('report_metadata', {}).get('report_id', 'N/A'))
            html = html.replace('{report_metadata[generated_at]}', data.get('report_metadata', {}).get('generated_at', 'N/A'))
            html = html.replace('{report_metadata[generator_version]}', data.get('report_metadata', {}).get('generator_version', 'N/A'))
        
        return html
    
    def _generate_json_report(self, report_type: ReportType, data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _generate_text_report(self, report_type: ReportType, data: Dict[str, Any]) -> str:
        """Generate text report"""
        template = self.templates[report_type]
        
        # Convert HTML template to text format
        text_template = template.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n')
        text_template = text_template.replace('<strong>', '').replace('</strong>', '')
        text_template = text_template.replace('<em>', '').replace('</em>', '')
        text_template = text_template.replace('<ul>', '').replace('</ul>', '')
        text_template = text_template.replace('<li>', '• ').replace('</li>', '\n')
        
        return text_template.format(**data)
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML reports"""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .report-container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .report-header {
            border-bottom: 3px solid #2c5aa0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .report-header h1 {
            color: #2c5aa0;
            margin: 0;
            font-size: 2.5em;
        }
        
        .report-meta {
            margin-top: 10px;
            color: #666;
        }
        
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #fafafa;
        }
        
        .section h2 {
            color: #2c5aa0;
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 10px;
            margin-top: 0;
        }
        
        .section h3 {
            color: #444;
            margin-top: 20px;
        }
        
        .patient-info, .provider-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .info-item {
            margin-bottom: 10px;
        }
        
        .info-label {
            font-weight: bold;
            color: #555;
        }
        
        .mbs-items-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .mbs-items-table th,
        .mbs-items-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        .mbs-items-table th {
            background-color: #2c5aa0;
            color: white;
            font-weight: bold;
        }
        
        .mbs-items-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        .status-approved {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-rejected {
            color: #dc3545;
            font-weight: bold;
        }
        
        .financial-summary {
            background-color: #e8f4fd;
            border: 2px solid #2c5aa0;
        }
        
        .financial-summary h3 {
            color: #2c5aa0;
        }
        
        .total-amount {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c5aa0;
        }
        
        .validation-results {
            background-color: #fff3cd;
            border: 2px solid #ffc107;
        }
        
        .validation-results h3 {
            color: #856404;
        }
        
        .conflict-item {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }
        
        .fix-suggestion {
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }
        
        .report-footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .consultation-details {
            background-color: #f8f9fa;
        }
        
        .consultation-details h3 {
            color: #495057;
        }
        
        .consultation-field {
            margin-bottom: 15px;
        }
        
        .consultation-field strong {
            display: inline-block;
            width: 150px;
            color: #495057;
        }
        
        @media print {
            body { background-color: white; }
            .report-container { box-shadow: none; }
        }
        """
    
    def _get_claim_summary_template(self) -> str:
        """Get claim summary template"""
        return """
        <div class="section">
            <h2>Patient Information</h2>
            <div class="patient-info">
                <div>
                    <div class="info-item">
                        <span class="info-label">Name:</span> {patient[name]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">DOB:</span> {patient[date_of_birth]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Gender:</span> {patient[gender]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Medicare #:</span> {patient[medicare_number]}
                    </div>
                </div>
                <div>
                    <div class="info-item">
                        <span class="info-label">Phone:</span> {patient[phone]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span> {patient[email]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Address:</span> {patient[address]}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Provider Information</h2>
            <div class="provider-info">
                <div>
                    <div class="info-item">
                        <span class="info-label">Name:</span> {provider[name]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Title:</span> {provider[title]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Specialty:</span> {provider[specialty]}
                    </div>
                </div>
                <div>
                    <div class="info-item">
                        <span class="info-label">Practice:</span> {provider[practice_name]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Provider #:</span> {provider[provider_number]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone:</span> {provider[phone]}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section consultation-details">
            <h2>Consultation Summary</h2>
            <div class="consultation-field">
                <strong>Date:</strong> {consultation[date]} at {consultation[time]}
            </div>
            <div class="consultation-field">
                <strong>Duration:</strong> {consultation[duration]} minutes
            </div>
            <div class="consultation-field">
                <strong>Setting:</strong> {consultation[setting]}
            </div>
            <div class="consultation-field">
                <strong>Chief Complaint:</strong> {consultation[chief_complaint]}
            </div>
            <div class="consultation-field">
                <strong>Diagnosis:</strong> {consultation[diagnosis]}
            </div>
        </div>
        
        <div class="section">
            <h2>MBS Items Summary</h2>
            <table class="mbs-items-table">
                <thead>
                    <tr>
                        <th>Item #</th>
                        <th>Description</th>
                        <th>Fee</th>
                        <th>Status</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {mbs_items_table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section financial-summary">
            <h2>Financial Summary</h2>
            <div class="info-item">
                <span class="info-label">Total Items:</span> {financial_summary[total_items]}
            </div>
            <div class="info-item">
                <span class="info-label">Billable Items:</span> {financial_summary[billable_items]}
            </div>
            <div class="info-item">
                <span class="info-label">Rejected Items:</span> {financial_summary[rejected_items]}
            </div>
            <div class="info-item total-amount">
                <span class="info-label">Total Amount:</span> ${financial_summary[billable_total]:.2f}
            </div>
        </div>
        """
    
    def _get_detailed_record_template(self) -> str:
        """Get detailed record template"""
        return """
        <div class="section">
            <h2>Patient Information</h2>
            <div class="patient-info">
                <div>
                    <div class="info-item">
                        <span class="info-label">Name:</span> {patient[name]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">DOB:</span> {patient[date_of_birth]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Gender:</span> {patient[gender]}
                    </div>
                </div>
                <div>
                    <div class="info-item">
                        <span class="info-label">Medicare #:</span> {patient[medicare_number]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone:</span> {patient[phone]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span> {patient[email]}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section consultation-details">
            <h2>Detailed Consultation Record</h2>
            <div class="consultation-field">
                <strong>Date & Time:</strong> {consultation[date]} at {consultation[time]}
            </div>
            <div class="consultation-field">
                <strong>Duration:</strong> {consultation[duration]} minutes
            </div>
            <div class="consultation-field">
                <strong>Setting:</strong> {consultation[setting]}
            </div>
            <div class="consultation-field">
                <strong>Chief Complaint:</strong> {consultation[chief_complaint]}
            </div>
            <div class="consultation-field">
                <strong>History:</strong> {consultation[history]}
            </div>
            <div class="consultation-field">
                <strong>Examination:</strong> {consultation[examination]}
            </div>
            <div class="consultation-field">
                <strong>Diagnosis:</strong> {consultation[diagnosis]}
            </div>
            <div class="consultation-field">
                <strong>Treatment Plan:</strong> {consultation[treatment_plan]}
            </div>
            <div class="consultation-field">
                <strong>Follow-up:</strong> {consultation[follow_up]}
            </div>
            {referral_section}
        </div>
        
        <div class="section">
            <h2>MBS Items Detail</h2>
            <table class="mbs-items-table">
                <thead>
                    <tr>
                        <th>Item #</th>
                        <th>Description</th>
                        <th>Group</th>
                        <th>Category</th>
                        <th>Fee</th>
                        <th>Status</th>
                        <th>Confidence</th>
                        <th>Evidence</th>
                    </tr>
                </thead>
                <tbody>
                    {mbs_items_detailed_table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section validation-results">
            <h2>Validation Results</h2>
            <h3>Billable Items</h3>
            <ul>
                {billable_items_list}
            </ul>
            
            {rejected_items_section}
            {conflicts_section}
            {fixes_section}
        </div>
        """
    
    def _get_billing_report_template(self) -> str:
        """Get billing report template"""
        return """
        <div class="section">
            <h2>Billing Report</h2>
            <div class="info-item">
                <span class="info-label">Report Date:</span> {report_metadata[generated_at]}
            </div>
            <div class="info-item">
                <span class="info-label">Provider:</span> {provider[name]} ({provider[provider_number]})
            </div>
            <div class="info-item">
                <span class="info-label">Patient:</span> {patient[name]} ({patient[medicare_number]})
            </div>
        </div>
        
        <div class="section">
            <h2>Billing Items</h2>
            <table class="mbs-items-table">
                <thead>
                    <tr>
                        <th>Item #</th>
                        <th>Description</th>
                        <th>Fee</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {billing_items_table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section financial-summary">
            <h2>Billing Summary</h2>
            <div class="info-item">
                <span class="info-label">Total Items:</span> {financial_summary[total_items]}
            </div>
            <div class="info-item">
                <span class="info-label">Billable Items:</span> {financial_summary[billable_items]}
            </div>
            <div class="info-item total-amount">
                <span class="info-label">Total Amount:</span> ${financial_summary[billable_total]:.2f}
            </div>
        </div>
        """
    
    def _get_audit_trail_template(self) -> str:
        """Get audit trail template"""
        return """
        <div class="section">
            <h2>Audit Trail</h2>
            <div class="info-item">
                <span class="info-label">Report ID:</span> {report_metadata[report_id]}
            </div>
            <div class="info-item">
                <span class="info-label">Generated:</span> {report_metadata[generated_at]}
            </div>
            <div class="info-item">
                <span class="info-label">Generator Version:</span> {report_metadata[generator_version]}
            </div>
        </div>
        
        <div class="section">
            <h2>System Information</h2>
            <div class="info-item">
                <span class="info-label">Local Processing:</span> Yes (No external data transmission)
            </div>
            <div class="info-item">
                <span class="info-label">Data Source:</span> Local MBS database
            </div>
            <div class="info-item">
                <span class="info-label">Validation Engine:</span> Local rule engine
            </div>
        </div>
        
        <div class="section">
            <h2>Validation Audit</h2>
            <h3>Validation Results</h3>
            <ul>
                <li><strong>Billable Items:</strong> {validation[billable_items]}</li>
                <li><strong>Rejected Items:</strong> {validation[rejected_items]}</li>
                <li><strong>Conflicts:</strong> {validation[conflicts]}</li>
                <li><strong>Fixes:</strong> {validation[fixes]}</li>
            </ul>
            
            <h3>Validation Explanation</h3>
            <p>{validation[why]}</p>
        </div>
        """
    
    def _get_patient_summary_template(self) -> str:
        """Get patient summary template"""
        return """
        <div class="section">
            <h2>Patient Summary</h2>
            <div class="patient-info">
                <div>
                    <div class="info-item">
                        <span class="info-label">Name:</span> {patient[name]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">DOB:</span> {patient[date_of_birth]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Gender:</span> {patient[gender]}
                    </div>
                </div>
                <div>
                    <div class="info-item">
                        <span class="info-label">Medicare #:</span> {patient[medicare_number]}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone:</span> {patient[phone]}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section consultation-details">
            <h2>Recent Consultation</h2>
            <div class="consultation-field">
                <strong>Date:</strong> {consultation[date]}
            </div>
            <div class="consultation-field">
                <strong>Provider:</strong> {provider[name]}
            </div>
            <div class="consultation-field">
                <strong>Chief Complaint:</strong> {consultation[chief_complaint]}
            </div>
            <div class="consultation-field">
                <strong>Diagnosis:</strong> {consultation[diagnosis]}
            </div>
        </div>
        
        <div class="section">
            <h2>Billing Summary</h2>
            <div class="info-item">
                <span class="info-label">Total Items:</span> {financial_summary[total_items]}
            </div>
            <div class="info-item">
                <span class="info-label">Billable Amount:</span> ${financial_summary[billable_total]:.2f}
            </div>
        </div>
        """
    
    def generate_mbs_items_table_rows(self, mbs_items) -> str:
        """Generate HTML table rows for MBS items"""
        rows = []
        for item in mbs_items:
            if isinstance(item, dict):
                status_class = "status-approved" if item.get('validation_status') == "approved" else "status-rejected"
                rows.append(f"""
                    <tr>
                        <td>{item.get('item_number', 'N/A')}</td>
                        <td>{item.get('description', 'N/A')[:50]}...</td>
                        <td>${item.get('fee', 0):.2f}</td>
                        <td class="{status_class}">{item.get('validation_status', 'unknown')}</td>
                        <td>{item.get('confidence_score', 0):.1%}</td>
                    </tr>
                """)
            else:
                status_class = "status-approved" if item.validation_status == "approved" else "status-rejected"
                rows.append(f"""
                    <tr>
                        <td>{item.item_number}</td>
                        <td>{item.description[:50]}...</td>
                        <td>${item.fee:.2f}</td>
                        <td class="{status_class}">{item.validation_status}</td>
                        <td>{item.confidence_score:.1%}</td>
                    </tr>
                """)
        return "".join(rows)
    
    def generate_detailed_mbs_items_table_rows(self, mbs_items) -> str:
        """Generate detailed HTML table rows for MBS items"""
        rows = []
        for item in mbs_items:
            if isinstance(item, dict):
                status_class = "status-approved" if item.get('validation_status') == "approved" else "status-rejected"
                rows.append(f"""
                    <tr>
                        <td>{item.get('item_number', 'N/A')}</td>
                        <td>{item.get('description', 'N/A')}</td>
                        <td>{item.get('group', 'N/A')}</td>
                        <td>{item.get('category', 'N/A')}</td>
                        <td>${item.get('fee', 0):.2f}</td>
                        <td class="{status_class}">{item.get('validation_status', 'unknown')}</td>
                        <td>{item.get('confidence_score', 0):.1%}</td>
                        <td>{item.get('evidence', 'N/A')}</td>
                    </tr>
                """)
            else:
                status_class = "status-approved" if item.validation_status == "approved" else "status-rejected"
                rows.append(f"""
                    <tr>
                        <td>{item.item_number}</td>
                        <td>{item.description}</td>
                        <td>{item.group}</td>
                        <td>{item.category}</td>
                        <td>${item.fee:.2f}</td>
                        <td class="{status_class}">{item.validation_status}</td>
                        <td>{item.confidence_score:.1%}</td>
                        <td>{item.evidence}</td>
                    </tr>
                """)
        return "".join(rows)
    
    def generate_billing_items_table_rows(self, mbs_items) -> str:
        """Generate billing table rows for MBS items"""
        rows = []
        for item in mbs_items:
            if isinstance(item, dict):
                if item.get('validation_status') == "approved":
                    rows.append(f"""
                        <tr>
                            <td>{item.get('item_number', 'N/A')}</td>
                            <td>{item.get('description', 'N/A')}</td>
                            <td>${item.get('fee', 0):.2f}</td>
                            <td class="status-approved">Approved</td>
                        </tr>
                    """)
            else:
                if item.validation_status == "approved":
                    rows.append(f"""
                        <tr>
                            <td>{item.item_number}</td>
                            <td>{item.description}</td>
                            <td>${item.fee:.2f}</td>
                            <td class="status-approved">Approved</td>
                        </tr>
                    """)
        return "".join(rows)
    
    def generate_billable_items_list(self, validation_result) -> str:
        """Generate billable items list"""
        if isinstance(validation_result, dict):
            items = validation_result.get('billable_items', [])
        else:
            items = getattr(validation_result, 'billable_items', [])
        
        if not items:
            return "<li>No billable items</li>"
        
        return "".join([f"<li>Item {item}</li>" for item in items])
    
    def generate_rejected_items_section(self, validation_result) -> str:
        """Generate rejected items section"""
        if isinstance(validation_result, dict):
            rejected = validation_result.get('rejected_items', [])
        else:
            rejected = getattr(validation_result, 'rejected_items', [])
        
        if not rejected:
            return ""
        
        items_html = "".join([f"<li>Item {item}</li>" for item in rejected])
        return f"""
            <h3>Rejected Items</h3>
            <ul>
                {items_html}
            </ul>
        """
    
    def generate_conflicts_section(self, validation_result) -> str:
        """Generate conflicts section"""
        if isinstance(validation_result, dict):
            conflicts = validation_result.get('conflicts', [])
        else:
            conflicts = getattr(validation_result, 'conflicts', [])
        
        if not conflicts:
            return ""
        
        conflicts_html = "".join([f'<div class="conflict-item">{conflict}</div>' for conflict in conflicts])
        return f"""
            <h3>Conflicts</h3>
            {conflicts_html}
        """
    
    def generate_fixes_section(self, validation_result) -> str:
        """Generate fixes section"""
        if isinstance(validation_result, dict):
            fixes = validation_result.get('fixes', [])
        else:
            fixes = getattr(validation_result, 'fixes', [])
        
        if not fixes:
            return ""
        
        fixes_html = "".join([f'<div class="fix-suggestion">{fix}</div>' for fix in fixes])
        return f"""
            <h3>Fix Suggestions</h3>
            {fixes_html}
        """
    
    def generate_referral_section(self, consultation) -> str:
        """Generate referral section"""
        if isinstance(consultation, dict):
            referral = consultation.get('referral', False)
            referral_reason = consultation.get('referral_reason', '')
        else:
            referral = getattr(consultation, 'referral', False)
            referral_reason = getattr(consultation, 'referral_reason', '')
        
        if not referral:
            return ""
        
        return f"""
            <div class="consultation-field">
                <strong>Referral:</strong> Yes
            </div>
            <div class="consultation-field">
                <strong>Referral Reason:</strong> {referral_reason}
            </div>
        """

# Convenience functions for easy use
def create_sample_patient() -> PatientInfo:
    """Create a sample patient for testing"""
    return PatientInfo(
        patient_id="P001",
        name="John Smith",
        date_of_birth="1980-05-15",
        gender="Male",
        address="123 Main St, Sydney, NSW 2000",
        medicare_number="1234567890",
        phone="0412345678",
        email="john.smith@email.com"
    )

def create_sample_provider() -> ProviderInfo:
    """Create a sample provider for testing"""
    return ProviderInfo(
        provider_id="PR001",
        name="Dr. Jane Wilson",
        title="General Practitioner",
        specialty="General Practice",
        practice_name="Sydney Medical Centre",
        address="456 Health St, Sydney, NSW 2000",
        phone="0298765432",
        email="j.wilson@medical.com",
        provider_number="1234567A"
    )

def create_sample_consultation() -> ConsultationInfo:
    """Create a sample consultation for testing"""
    return ConsultationInfo(
        consultation_id="C001",
        date="2024-01-15",
        time="10:30 AM",
        duration=30,
        setting="consulting_rooms",
        chief_complaint="Chest pain and shortness of breath",
        history="Patient reports chest pain that started 2 days ago, associated with shortness of breath on exertion.",
        examination="Blood pressure 140/90, heart rate 88 bpm, chest clear, no signs of distress.",
        diagnosis="Possible angina, rule out myocardial infarction",
        treatment_plan="ECG, blood tests, cardiology referral if needed",
        follow_up="Return in 1 week or sooner if symptoms worsen",
        referral=True,
        referral_reason="Cardiology consultation for chest pain evaluation"
    )

def create_sample_mbs_items() -> List[MBSItemInfo]:
    """Create sample MBS items for testing"""
    return [
        MBSItemInfo(
            item_number="3",
            description="Professional attendance by a general practitioner",
            fee=75.00,
            group="A1",
            category=1,
            provider_type="General Practitioner",
            confidence_score=0.92,
            evidence="High confidence match based on consultation type",
            validation_status="approved",
            validation_notes="Valid for general consultation"
        ),
        MBSItemInfo(
            item_number="4",
            description="Professional attendance by a general practitioner - extended",
            fee=150.00,
            group="A1",
            category=1,
            provider_type="General Practitioner",
            confidence_score=0.88,
            evidence="Good match for extended consultation",
            validation_status="approved",
            validation_notes="Valid for extended consultation"
        ),
        MBSItemInfo(
            item_number="23",
            description="Professional attendance by a general practitioner - after hours",
            fee=100.00,
            group="A1",
            category=1,
            provider_type="General Practitioner",
            confidence_score=0.75,
            evidence="Moderate match for after hours consultation",
            validation_status="rejected",
            validation_notes="Not applicable during regular hours"
        )
    ]

def create_sample_validation_result() -> Dict[str, Any]:
    """Create sample validation result for testing"""
    return {
        "billable_items": ["3", "4"],
        "rejected_items": ["23"],
        "conflicts": ["Item 23 not applicable during regular hours"],
        "fixes": ["Remove Item 23 or use Item 24 for after-hours consultation"],
        "why": "Item 23 is for after-hours consultations only, but this consultation was during regular hours"
    }
