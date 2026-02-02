"""
Finance Utility Functions
Provides financial calculations, ROI analysis, and budget optimization for the Finance Committee Platform.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from models import Sponsor, Event, Sponsorship
from sqlalchemy import func
from app import db

class FinanceCalculator:
    """Handles financial calculations and analysis."""
    
    @staticmethod
    def calculate_roi(investment: float, revenue: float) -> float:
        """
        Calculate Return on Investment (ROI)
        
        Args:
            investment: Total investment amount
            revenue: Total revenue generated
            
        Returns:
            ROI percentage (revenue - investment) / investment * 100
            Returns 0 if investment is 0 to avoid division by zero
        """
        if investment <= 0:
            return 0.0
        return ((revenue - investment) / investment) * 100
    
    @staticmethod
    def calculate_sponsor_roi(sponsor_id: int, event_id: Optional[int] = None) -> Dict:
        """
        Calculate ROI for a specific sponsor across all events or a specific event.
        
        Args:
            sponsor_id: ID of the sponsor
            event_id: Optional specific event ID
            
        Returns:
            Dictionary with ROI metrics
        """
        try:
            query = db.session.query(Sponsorship).filter(Sponsorship.sponsor_id == sponsor_id)
            
            if event_id:
                query = query.filter(Sponsorship.event_id == event_id)
            
            sponsorships = query.filter(Sponsorship.status == 'completed').all()
            
            total_investment = sum(s.amount for s in sponsorships)
            total_revenue = 0  # This would need to be calculated based on actual event data
            
            # Placeholder for revenue calculation - in real implementation, 
            # you'd calculate this based on event performance metrics
            for sponsorship in sponsorships:
                # Example: revenue = investment * (1 + ROI/100)
                if sponsorship.roi:
                    total_revenue += sponsorship.amount * (1 + sponsorship.roi / 100)
                else:
                    total_revenue += sponsorship.amount
            
            roi_percentage = FinanceCalculator.calculate_roi(total_investment, total_revenue)
            
            return {
                'sponsor_id': sponsor_id,
                'event_id': event_id,
                'total_investment': total_investment,
                'total_revenue': total_revenue,
                'roi_percentage': roi_percentage,
                'sponsorship_count': len(sponsorships),
                'net_profit': total_revenue - total_investment
            }
            
        except Exception as e:
            return {'error': f'Failed to calculate sponsor ROI: {str(e)}'}
    
    @staticmethod
    def get_event_financial_summary(event_id: int) -> Dict:
        """
        Get comprehensive financial summary for an event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            Dictionary with event financial metrics
        """
        try:
            event = Event.query.get(event_id)
            if not event:
                return {'error': 'Event not found'}
            
            sponsorships = db.session.query(Sponsorship).filter(
                Sponsorship.event_id == event_id,
                Sponsorship.status == 'completed'
            ).all()
            
            total_sponsorship = sum(s.amount for s in sponsorships)
            total_budget = float(event.budget)
            actual_revenue = float(event.revenue)
            
            # Calculate various financial metrics
            profit_margin = FinanceCalculator.calculate_profit_margin(actual_revenue, total_budget)
            budget_utilization = FinanceCalculator.calculate_budget_utilization(total_sponsorship, total_budget)
            roi = FinanceCalculator.calculate_roi(total_budget, actual_revenue)
            
            return {
                'event_id': event_id,
                'event_name': event.name,
                'event_date': event.date.isoformat(),
                'total_budget': total_budget,
                'actual_revenue': actual_revenue,
                'total_sponsorship': total_sponsorship,
                'net_profit': actual_revenue - total_budget,
                'profit_margin_percentage': profit_margin,
                'budget_utilization_percentage': budget_utilization,
                'roi_percentage': roi,
                'sponsor_count': len(sponsorships),
                'footfall': event.footfall,
                'revenue_per_attendee': actual_revenue / event.footfall if event.footfall > 0 else 0
            }
            
        except Exception as e:
            return {'error': f'Failed to get event financial summary: {str(e)}'}
    
    @staticmethod
    def calculate_profit_margin(revenue: float, costs: float) -> float:
        """Calculate profit margin percentage."""
        if revenue <= 0:
            return 0.0
        return ((revenue - costs) / revenue) * 100
    
    @staticmethod
    def calculate_budget_utilization(actual: float, planned: float) -> float:
        """Calculate budget utilization percentage."""
        if planned <= 0:
            return 0.0
        return (actual / planned) * 100
    
    @staticmethod
    def analyze_financial_trends(months: int = 12) -> Dict:
        """
        Analyze financial trends over specified months.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Get events in the date range
            events = Event.query.filter(
                Event.date >= start_date,
                Event.date <= end_date
            ).order_by(Event.date).all()
            
            if not events:
                return {'error': 'No events found in the specified period'}
            
            monthly_data = {}
            for event in events:
                month_key = event.date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'total_budget': 0,
                        'total_revenue': 0,
                        'event_count': 0,
                        'total_sponsorship': 0
                    }
                
                monthly_data[month_key]['total_budget'] += float(event.budget)
                monthly_data[month_key]['total_revenue'] += float(event.revenue)
                monthly_data[month_key]['event_count'] += 1
                
                # Get sponsorship data for this event
                sponsorships = db.session.query(Sponsorship).filter(
                    Sponsorship.event_id == event.id,
                    Sponsorship.status == 'completed'
                ).all()
                
                monthly_data[month_key]['total_sponsorship'] += sum(s.amount for s in sponsorships)
            
            # Calculate trends
            trend_data = list(monthly_data.values())
            trend_data.sort(key=lambda x: x['month'])
            
            # Calculate growth rates
            for i in range(1, len(trend_data)):
                prev_month = trend_data[i-1]
                curr_month = trend_data[i]
                
                if prev_month['total_revenue'] > 0:
                    curr_month['revenue_growth'] = ((curr_month['total_revenue'] - prev_month['total_revenue']) / prev_month['total_revenue']) * 100
                else:
                    curr_month['revenue_growth'] = 0
                
                if prev_month['event_count'] > 0:
                    curr_month['event_growth'] = ((curr_month['event_count'] - prev_month['event_count']) / prev_month['event_count']) * 100
                else:
                    curr_month['event_growth'] = 0
            
            return {
                'period_months': months,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'monthly_trends': trend_data,
                'total_events': len(events),
                'total_budget': sum(event.budget for event in events),
                'total_revenue': sum(event.revenue for event in events)
            }
            
        except Exception as e:
            return {'error': f'Failed to analyze financial trends: {str(e)}'}
    
    @staticmethod
    def get_top_performing_sponsors(limit: int = 10) -> List[Dict]:
        """
        Get top performing sponsors based on total investment and ROI.
        
        Args:
            limit: Maximum number of sponsors to return
            
        Returns:
            List of sponsor performance data
        """
        try:
            sponsors_data = db.session.query(
                Sponsor,
                func.sum(Sponsorship.amount).label('total_investment'),
                func.count(Sponsorship.id).label('sponsorship_count'),
                func.avg(Sponsorship.roi).label('avg_roi')
            ).join(
                Sponsorship, Sponsor.id == Sponsorship.sponsor_id
            ).filter(
                Sponsorship.status == 'completed'
            ).group_by(
                Sponsor.id
            ).order_by(
                func.sum(Sponsorship.amount).desc()
            ).limit(limit).all()
            
            results = []
            for sponsor, total_investment, sponsorship_count, avg_roi in sponsors_data:
                results.append({
                    'id': sponsor.id,
                    'name': sponsor.name,
                    'industry': sponsor.industry,
                    'total_investment': float(total_investment),
                    'sponsorship_count': sponsorship_count,
                    'average_roi': float(avg_roi) if avg_roi else 0,
                    'contact_person': sponsor.contact_person,
                    'email': sponsor.email
                })
            
            return results
            
        except Exception as e:
            return [{'error': f'Failed to get top sponsors: {str(e)}'}]
    
    @staticmethod
    def generate_financial_projections(projected_months: int = 6) -> Dict:
        """
        Generate financial projections based on historical data.
        
        Args:
            projected_months: Number of months to project
            
        Returns:
            Dictionary with financial projections
        """
        try:
            # Get last 6 months of actual data for projection
            historical_trends = FinanceCalculator.analyze_financial_trends(months=6)
            
            if 'error' in historical_trends:
                return historical_trends
            
            monthly_data = historical_trends['monthly_trends']
            
            if len(monthly_data) < 2:
                return {'error': 'Insufficient historical data for projections'}
            
            # Calculate average growth rates
            revenue_growth_rates = [m.get('revenue_growth', 0) for m in monthly_data[1:]]
            avg_revenue_growth = sum(revenue_growth_rates) / len(revenue_growth_rates) if revenue_growth_rates else 0
            
            event_growth_rates = [m.get('event_growth', 0) for m in monthly_data[1:]]
            avg_event_growth = sum(event_growth_rates) / len(event_growth_rates) if event_growth_rates else 0
            
            # Get latest month as baseline
            baseline = monthly_data[-1]
            
            projections = []
            current_revenue = baseline['total_revenue']
            current_events = baseline['event_count']
            
            for month in range(1, projected_months + 1):
                projected_revenue = current_revenue * (1 + avg_revenue_growth / 100)
                projected_events = int(current_events * (1 + avg_event_growth / 100))
                
                projections.append({
                    'month': month,
                    'projected_revenue': projected_revenue,
                    'projected_events': projected_events,
                    'growth_assumption': avg_revenue_growth
                })
                
                current_revenue = projected_revenue
                current_events = projected_events
            
            return {
                'projection_months': projected_months,
                'baseline_month': baseline['month'],
                'avg_revenue_growth_rate': avg_revenue_growth,
                'avg_event_growth_rate': avg_event_growth,
                'projections': projections,
                'total_projected_revenue': sum(p['projected_revenue'] for p in projections),
                'total_projected_events': sum(p['projected_events'] for p in projections)
            }
            
        except Exception as e:
            return {'error': f'Failed to generate financial projections: {str(e)}'}