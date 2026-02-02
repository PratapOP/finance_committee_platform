/**
 * Enhanced Dashboard with Error Handling for Finance Committee Platform
 * Uses centralized API client with proper error handling and user feedback.
 */

import { apiMethods, apiUtils } from './api.js';
import { ChartUtils } from './charts.js';

class DashboardManager {
    constructor() {
        this.charts = new Map();
        this.isLoading = false;
        this.init();
    }

    async init() {
        try {
            apiUtils.setLoading(true);
            await this.loadDashboardData();
            await this.initializeCharts();
            this.setupEventListeners();
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            apiUtils.showError(error, 'dashboard-error');
        } finally {
            apiUtils.setLoading(false);
        }
    }

    async loadDashboardData() {
        try {
            this.analyticsData = await apiMethods.analytics.getDashboard();
            
            if (!this.analyticsData) {
                throw new Error('No analytics data available');
            }

            this.updateStatCards();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            apiUtils.showError(error, 'analytics-error');
            
            // Set default values to prevent UI crashes
            this.analyticsData = {
                financial: {
                    total_budget: 0,
                    total_revenue: 0,
                    total_sponsor_investment: 0,
                    profit: 0
                }
            };
            this.updateStatCards();
        }
    }

    updateStatCards() {
        try {
            const financial = this.analyticsData.financial || {};
            // Animate numbers with error handling
            this.animateValue('revenue', 0, financial.total_revenue || 0, 1500);
            this.animateValue('investment', 0, financial.total_sponsor_investment || 0, 1500);
            this.animateValue('profit', 0, financial.profit || 0, 1500);
        } catch (error) {
            console.error('Failed to update stat cards:', error);
            // Fallback to direct text update
            const financial = this.analyticsData.financial || {};
            document.getElementById('revenue').textContent = apiUtils.formatCurrency(financial.total_revenue || 0);
            document.getElementById('investment').textContent = apiUtils.formatCurrency(financial.total_sponsor_investment || 0);
            document.getElementById('profit').textContent = apiUtils.formatCurrency(financial.profit || 0);
        }
    }

    animateValue(elementId, start, end, duration) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Element with ID '${elementId}' not found`);
            return;
        }

        const startTime = performance.now();
        const isRupee = element.textContent && element.textContent.includes('₹');
        
        const update = (currentTime) => {
            try {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Easing function for smooth deceleration
                const easeOut = 1 - Math.pow(1 - progress, 4);
                const current = Math.floor(start + (end - start) * easeOut);
                
                element.innerText = isRupee ? `₹ ${current.toLocaleString('en-IN')}` : current.toLocaleString('en-IN');
                
                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            } catch (error) {
                console.error('Animation error:', error);
                // Fallback to direct update
                element.innerText = isRupee ? `₹ ${end.toLocaleString('en-IN')}` : end.toLocaleString('en-IN');
            }
        };
        
        requestAnimationFrame(update);
    }

    async initializeCharts() {
        try {
            const ctx = document.getElementById('financeChart');
            if (!ctx) {
                console.warn('Chart canvas element not found');
                return;
            }

            // Create financial overview chart with error handling
            this.charts.set('financeChart', ChartUtils.createFinancialOverviewChart(ctx, this.analyticsData));
        } catch (error) {
            console.error('Failed to initialize charts:', error);
            apiUtils.showError(error, 'chart-error');
        }
    }

    setupEventListeners() {
        try {
            // Refresh data button
            const refreshBtn = document.getElementById('refresh-btn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', this.handleRefresh.bind(this));
            }

            // Export chart button
            const exportBtn = document.getElementById('export-chart-btn');
            if (exportBtn) {
                exportBtn.addEventListener('click', this.handleExportChart.bind(this));
            }

            // Handle window resize for responsive charts
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    this.resizeCharts();
                }, 250);
            });
        } catch (error) {
            console.error('Failed to setup event listeners:', error);
        }
    }

    async handleRefresh() {
        if (this.isLoading) return;

        try {
            this.isLoading = true;
            apiUtils.setLoading(true);
            
            await this.loadDashboardData();
            
            // Update charts with new data
            this.charts.forEach((chart, id) => {
                try {
                    if (id === 'financeChart') {
                        ChartUtils.updateChart(id, this.analyticsData);
                    }
                } catch (error) {
                    console.error(`Failed to update chart ${id}:`, error);
                }
            });
            
            apiUtils.showSuccess('Dashboard refreshed successfully!');
        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
            apiUtils.showError(error, 'refresh-error');
        } finally {
            this.isLoading = false;
            apiUtils.setLoading(false);
        }
    }

    handleExportChart() {
        try {
            const exportedUrl = ChartUtils.exportChart('financeChart', 'png');
            if (exportedUrl) {
                apiUtils.showSuccess('Chart exported successfully!');
            } else {
                throw new Error('Chart export failed');
            }
        } catch (error) {
            console.error('Failed to export chart:', error);
            apiUtils.showError(error, 'export-error');
        }
    }

    resizeCharts() {
        try {
            ChartUtils.getChartManager().resizeAllCharts();
        } catch (error) {
            console.error('Failed to resize charts:', error);
        }
    }

    // Cleanup method
    destroy() {
        try {
            ChartUtils.getChartManager().destroyAllCharts();
            this.charts.clear();
        } catch (error) {
            console.error('Failed to cleanup dashboard:', error);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    let dashboard;
    
    try {
        dashboard = new DashboardManager();
        
        // Global error handler
        window.addEventListener('error', (event) => {
            console.error('Global error caught:', event.error);
            apiUtils.showError(
                { message: 'An unexpected error occurred. Please refresh the page.' },
                'global-error'
            );
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            apiUtils.showError(
                { message: 'A network error occurred. Please check your connection.' },
                'promise-error'
            );
            event.preventDefault();
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (dashboard) {
                dashboard.destroy();
            }
        });

    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        apiUtils.showError(
            { message: 'Dashboard initialization failed. Please refresh the page.' },
            'init-error'
        );
    }
});

// Export for global access if needed
window.DashboardManager = DashboardManager;