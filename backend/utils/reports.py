"""
Reports Utility Functions
Handles PDF report generation, Excel export, and document creation for Finance Committee Platform.
"""

import os
import io
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import send_file
from sqlalchemy import func
from models import Sponsor, Event, Sponsorship
from app import db

class ReportGenerator:
    """Handles various report generation tasks."""
    
    @staticmethod
    def generate_sponsor_report(format_type: str = 'summary', sponsor_id: Optional[int] = None) -> Dict:
        """
        Generate sponsor performance report.
        
        Args:
            format_type: Type of report ('summary', 'detailed', 'roi_analysis')
            sponsor_id: Optional specific sponsor ID, None for all sponsors
            
        Returns:
            Dictionary with report data
        """
        try:
            if sponsor_id:
                sponsors = Sponsor.query.filter(Sponsor.id == sponsor_id).all()
            else:
                sponsors = Sponsor.query.all()
            
            report_data = {
                'report_type': 'Sponsor Report',
                'format': format_type,
                'generated_at': datetime.now().isoformat(),
                'sponsor_count': len(sponsors),
                'sponsors': []
            }
            
            for sponsor in sponsors:
                sponsor_data = {
                    'id': sponsor.id,
                    'name': sponsor.name,
                    'industry': sponsor.industry,
                    'contact_person': sponsor.contact_person,
                    'email': sponsor.email,
                    'phone': sponsor.phone,
                    'total_invested': float(sponsor.total_invested) if sponsor.total_invested else 0,
                    'created_at': sponsor.created_at.isoformat() if sponsor.created_at else None
                }
                
                if format_type in ['detailed', 'roi_analysis']:
                    # Get sponsorship details
                    sponsorships = db.session.query(Sponsorship).filter(
                        Sponsorship.sponsor_id == sponsor.id
                    ).all()
                    
                    sponsor_data['sponsorship_count'] = len(sponsorships)
                    sponsor_data['sponsorships'] = []
                    
                    for sponsorship in sponsorships:
                        event = Event.query.get(sponsorship.event_id)
                        sponsorship_data = {
                            'amount': float(sponsorship.amount),
                            'status': sponsorship.status,
                            'roi': float(sponsorship.roi) if sponsorship.roi else 0,
                            'event_name': event.name if event else 'Unknown Event',
                            'event_date': event.date.isoformat() if event else None,
                            'created_at': sponsorship.created_at.isoformat() if sponsorship.created_at else None
                        }
                        sponsor_data['sponsorships'].append(sponsorship_data)
                
                if format_type == 'roi_analysis':
                    # Calculate ROI metrics
                    from .finance import FinanceCalculator
                    roi_metrics = FinanceCalculator.calculate_sponsor_roi(sponsor.id)
                    sponsor_data['roi_metrics'] = roi_metrics
                
                report_data['sponsors'].append(sponsor_data)
            
            return report_data
            
        except Exception as e:
            return {'error': f'Failed to generate sponsor report: {str(e)}'}
    
    @staticmethod
    def generate_event_report(format_type: str = 'summary', event_id: Optional[int] = None) -> Dict:
        """
        Generate event performance report.
        
        Args:
            format_type: Type of report ('summary', 'detailed', 'financial')
            event_id: Optional specific event ID, None for all events
            
        Returns:
            Dictionary with report data
        """
        try:
            if event_id:
                events = Event.query.filter(Event.id == event_id).all()
            else:
                events = Event.query.order_by(Event.date.desc()).all()
            
            report_data = {
                'report_type': 'Event Report',
                'format': format_type,
                'generated_at': datetime.now().isoformat(),
                'event_count': len(events),
                'events': []
            }
            
            for event in events:
                event_data = {
                    'id': event.id,
                    'name': event.name,
                    'date': event.date.isoformat(),
                    'budget': float(event.budget),
                    'revenue': float(event.revenue),
                    'footfall': event.footfall,
                    'created_at': event.created_at.isoformat() if event.created_at else None
                }
                
                if format_type in ['detailed', 'financial']:
                    # Get sponsorship details
                    sponsorships = db.session.query(Sponsorship).filter(
                        Sponsorship.event_id == event.id
                    ).all()
                    
                    event_data['sponsorship_count'] = len(sponsorships)
                    event_data['total_sponsorship'] = sum(s.amount for s in sponsorships)
                    event_data['sponsorships'] = []
                    
                    for sponsorship in sponsorships:
                        sponsor = Sponsor.query.get(sponsorship.sponsor_id)
                        sponsorship_data = {
                            'sponsor_name': sponsor.name if sponsor else 'Unknown Sponsor',
                            'amount': float(sponsorship.amount),
                            'status': sponsorship.status,
                            'roi': float(sponsorship.roi) if sponsorship.roi else 0,
                            'created_at': sponsorship.created_at.isoformat() if sponsorship.created_at else None
                        }
                        event_data['sponsorships'].append(sponsorship_data)
                
                if format_type == 'financial':
                    # Calculate financial metrics
                    from .finance import FinanceCalculator
                    financial_summary = FinanceCalculator.get_event_financial_summary(event.id)
                    event_data['financial_summary'] = financial_summary
                
                report_data['events'].append(event_data)
            
            return report_data
            
        except Exception as e:
            return {'error': f'Failed to generate event report: {str(e)}'}
    
    @staticmethod
    def generate_financial_summary(months: int = 12) -> Dict:
        """
        Generate comprehensive financial summary report.
        
        Args:
            months: Number of months to include in report
            
        Returns:
            Dictionary with financial summary data
        """
        try:
            from .finance import FinanceCalculator
            
            # Get various financial metrics
            trends = FinanceCalculator.analyze_financial_trends(months)
            top_sponsors = FinanceCalculator.get_top_performing_sponsors(10)
            projections = FinanceCalculator.generate_financial_projections(6)
            
            # Calculate overall metrics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            events = Event.query.filter(
                Event.date >= start_date,
                Event.date <= end_date
            ).all()
            
            total_budget = sum(event.budget for event in events)
            total_revenue = sum(event.revenue for event in events)
            total_events = len(events)
            total_footfall = sum(event.footfall for event in events)
            
            sponsorships = db.session.query(Sponsorship).filter(
                Sponsorship.created_at >= start_date,
                Sponsorship.created_at <= end_date
            ).all()
            
            total_sponsorship = sum(s.amount for s in sponsorships if s.status == 'completed')
            
            report_data = {
                'report_type': 'Financial Summary Report',
                'period_months': months,
                'generated_at': datetime.now().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                
                # Overall metrics
                'overall_metrics': {
                    'total_events': total_events,
                    'total_budget': float(total_budget),
                    'total_revenue': float(total_revenue),
                    'total_sponsorship': float(total_sponsorship),
                    'total_footfall': total_footfall,
                    'net_profit': float(total_revenue - total_budget),
                    'roi_percentage': float(((total_revenue - total_budget) / total_budget) * 100) if total_budget > 0 else 0,
                    'revenue_per_event': float(total_revenue / total_events) if total_events > 0 else 0,
                    'budget_per_event': float(total_budget / total_events) if total_events > 0 else 0
                },
                
                # Detailed data
                'trends': trends,
                'top_sponsors': top_sponsors,
                'projections': projections
            }
            
            return report_data
            
        except Exception as e:
            return {'error': f'Failed to generate financial summary: {str(e)}'}
    
    @staticmethod
    def generate_roi_analysis() -> Dict:
        """
        Generate comprehensive ROI analysis report.
        
        Returns:
            Dictionary with ROI analysis data
        """
        try:
            from .finance import FinanceCalculator
            
            # Get all sponsors with ROI data
            sponsors = db.session.query(
                Sponsor,
                func.sum(Sponsorship.amount).label('total_investment'),
                func.count(Sponsorship.id).label('sponsorship_count'),
                func.avg(Sponsorship.roi).label('avg_roi'),
                func.min(Sponsorship.roi).label('min_roi'),
                func.max(Sponsorship.roi).label('max_roi')
            ).join(
                Sponsorship, Sponsor.id == Sponsorship.sponsor_id
            ).filter(
                Sponsorship.status == 'completed'
            ).group_by(
                Sponsor.id
            ).all()
            
            roi_data = []
            total_investment = 0
            total_revenue = 0
            
            for sponsor, investment, count, avg_roi, min_roi, max_roi in sponsors:
                # Calculate actual revenue based on ROI
                revenue = investment * (1 + (avg_roi / 100)) if avg_roi else investment
                
                sponsor_roi = {
                    'sponsor_id': sponsor.id,
                    'sponsor_name': sponsor.name,
                    'industry': sponsor.industry,
                    'total_investment': float(investment),
                    'total_revenue': float(revenue),
                    'sponsorship_count': count,
                    'average_roi': float(avg_roi) if avg_roi else 0,
                    'minimum_roi': float(min_roi) if min_roi else 0,
                    'maximum_roi': float(max_roi) if max_roi else 0,
                    'net_profit': float(revenue - investment)
                }
                
                roi_data.append(sponsor_roi)
                total_investment += investment
                total_revenue += revenue
            
            # Sort by total investment (descending)
            roi_data.sort(key=lambda x: x['total_investment'], reverse=True)
            
            # Calculate overall metrics
            overall_roi = ((total_revenue - total_investment) / total_investment * 100) if total_investment > 0 else 0
            
            # Industry-wise analysis
            industry_analysis = {}
            for data in roi_data:
                industry = data['industry'] or 'Unknown'
                if industry not in industry_analysis:
                    industry_analysis[industry] = {
                        'sponsors': 0,
                        'total_investment': 0,
                        'total_revenue': 0,
                        'avg_roi': 0
                    }
                
                industry_analysis[industry]['sponsors'] += 1
                industry_analysis[industry]['total_investment'] += data['total_investment']
                industry_analysis[industry]['total_revenue'] += data['total_revenue']
            
            # Calculate industry averages
            for industry, data in industry_analysis.items():
                if data['total_investment'] > 0:
                    data['avg_roi'] = ((data['total_revenue'] - data['total_investment']) / data['total_investment']) * 100
            
            report_data = {
                'report_type': 'ROI Analysis Report',
                'generated_at': datetime.now().isoformat(),
                
                'overall_metrics': {
                    'total_sponsors': len(roi_data),
                    'total_investment': float(total_investment),
                    'total_revenue': float(total_revenue),
                    'total_net_profit': float(total_revenue - total_investment),
                    'overall_roi_percentage': float(overall_roi),
                    'average_investment_per_sponsor': float(total_investment / len(roi_data)) if roi_data else 0
                },
                
                'sponsor_details': roi_data,
                'industry_analysis': industry_analysis
            }
            
            return report_data
            
        except Exception as e:
            return {'error': f'Failed to generate ROI analysis: {str(e)}'}
    
    @staticmethod
    def generate_monthly_report(year: int, month: int) -> Dict:
        """
        Generate detailed monthly report.
        
        Args:
            year: Year for report
            month: Month for report (1-12)
            
        Returns:
            Dictionary with monthly report data
        """
        try:
            # Get date range for specified month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Get events in month
            events = Event.query.filter(
                Event.date >= start_date,
                Event.date <= end_date
            ).order_by(Event.date).all()
            
            # Get sponsorships in month
            sponsorships = db.session.query(Sponsorship).filter(
                Sponsorship.created_at >= start_date,
                Sponsorship.created_at <= end_date
            ).all()
            
            # Get new sponsors in month
            new_sponsors = Sponsor.query.filter(
                Sponsor.created_at >= start_date,
                Sponsor.created_at <= end_date
            ).all()
            
            # Calculate metrics
            total_budget = sum(event.budget for event in events)
            total_revenue = sum(event.revenue for event in events)
            total_footfall = sum(event.footfall for event in events)
            completed_sponsorships = [s for s in sponsorships if s.status == 'completed']
            total_sponsorship_amount = sum(s.amount for s in completed_sponsorships)
            
            report_data = {
                'report_type': 'Monthly Report',
                'year': year,
                'month': month,
                'month_name': datetime(year, month, 1).strftime('%B'),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'generated_at': datetime.now().isoformat(),
                
                'summary_metrics': {
                    'total_events': len(events),
                    'total_budget': float(total_budget),
                    'total_revenue': float(total_revenue),
                    'net_profit': float(total_revenue - total_budget),
                    'total_footfall': total_footfall,
                    'new_sponsors': len(new_sponsors),
                    'completed_sponsorships': len(completed_sponsorships),
                    'total_sponsorship_amount': float(total_sponsorship_amount),
                    'roi_percentage': float(((total_revenue - total_budget) / total_budget) * 100) if total_budget > 0 else 0
                },
                
                'detailed_data': {
                    'events': [
                        {
                            'id': event.id,
                            'name': event.name,
                            'date': event.date.isoformat(),
                            'budget': float(event.budget),
                            'revenue': float(event.revenue),
                            'footfall': event.footfall,
                            'profit': float(event.revenue - event.budget)
                        }
                        for event in events
                    ],
                    'new_sponsors': [
                        {
                            'id': sponsor.id,
                            'name': sponsor.name,
                            'industry': sponsor.industry,
                            'contact_person': sponsor.contact_person,
                            'email': sponsor.email,
                            'created_at': sponsor.created_at.isoformat() if sponsor.created_at else None
                        }
                        for sponsor in new_sponsors
                    ],
                    'sponsorships': [
                        {
                            'id': sponsorship.id,
                            'sponsor_name': Sponsor.query.get(sponsorship.sponsor_id).name if Sponsor.query.get(sponsorship.sponsor_id) else 'Unknown',
                            'event_name': Event.query.get(sponsorship.event_id).name if Event.query.get(sponsorship.event_id) else 'Unknown',
                            'amount': float(sponsorship.amount),
                            'status': sponsorship.status,
                            'roi': float(sponsorship.roi) if sponsorship.roi else 0,
                            'created_at': sponsorship.created_at.isoformat() if sponsorship.created_at else None
                        }
                        for sponsorship in sponsorships
                    ]
                }
            }
            
            return report_data
            
        except Exception as e:
            return {'error': f'Failed to generate monthly report: {str(e)}'}
    
    @staticmethod
    def export_to_excel(report_data: Dict, filename: Optional[str] = None) -> str:
        """
        Export report data to Excel format.
        Note: This is a placeholder implementation.
        In production, you would use libraries like pandas and openpyxl.
        
        Args:
            report_data: Dictionary containing report data
            filename: Optional custom filename
            
        Returns:
            Path to generated Excel file
        """
        try:
            # This is a placeholder for Excel export functionality
            # In a real implementation, you would:
            # 1. Convert report data to a pandas DataFrame
            # 2. Use openpyxl to create an Excel file with multiple sheets
            # 3. Save file and return path
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"finance_report_{timestamp}.xlsx"
            
            # Create a temporary file path
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            
            # Placeholder: Create a simple text file for demonstration
            with open(file_path, 'w') as f:
                f.write("Finance Committee Report\n")
                f.write("=" * 40 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write("This is a placeholder for Excel export.\n")
                f.write("In production, this would be a proper Excel file.\n")
            
            return file_path
            
        except Exception as e:
            return f"Error exporting to Excel: {str(e)}"
    
    @staticmethod
    def generate_pdf_report(report_data: Dict, filename: Optional[str] = None) -> str:
        """
        Generate PDF report from report data.
        Note: This is a placeholder implementation.
        In production, you would use libraries like ReportLab or WeasyPrint.
        
        Args:
            report_data: Dictionary containing report data
            filename: Optional custom filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            # This is a placeholder for PDF generation functionality
            # In a real implementation, you would:
            # 1. Use ReportLab or WeasyPrint to create a styled PDF
            # 2. Include charts, tables, and formatting
            # 3. Save file and return path
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"finance_report_{timestamp}.pdf"
            
            # Create a temporary file path
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            
            # Placeholder: Create a simple text file for demonstration
            with open(file_path, 'w') as f:
                f.write("Finance Committee Report (PDF Placeholder)\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Report Type: {report_data.get('report_type', 'Unknown')}\n\n")
                f.write("This is a placeholder for PDF generation.\n")
                f.write("In production, this would be a properly formatted PDF.\n")
            
            return file_path
            
        except Exception as e:
            return f"Error generating PDF: {str(e)}"