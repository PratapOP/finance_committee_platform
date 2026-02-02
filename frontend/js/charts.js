/**
 * Charts Utility Functions for Finance Committee Platform
 * Provides Chart.js configurations and data processing for various financial charts.
 */

import Chart from 'chart.js/auto';

/**
 * Chart Configuration Factory
 * Creates consistent chart configurations with premium styling.
 */
class ChartFactory {
    /**
     * Default chart options
     */
    static getBaseOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 28, 46, 0.95)',
                    titleFont: {
                        family: 'Inter',
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        family: 'Inter',
                        size: 13
                    },
                    padding: 16,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: (context) => {
                            return this.formatTooltipLabel(context);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: '#8A95A3',
                        font: { family: 'Inter', size: 12, weight: '500' }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8A95A3',
                        font: { family: 'Inter', size: 12 },
                        callback: (value) => {
                            return this.formatYAxisLabel(value);
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        };
    }

    /**
     * Format tooltip label
     */
    static formatTooltipLabel(context) {
        const label = context.dataset.label || context.label || '';
        const value = context.parsed.y || context.parsed;
        
        if (this.isCurrencyDataset(context.dataset.label)) {
            return `${label}: ₹${Number(value).toLocaleString('en-IN')}`;
        }
        
        return `${label}: ${Number(value).toLocaleString('en-IN')}`;
    }

    /**
     * Format Y-axis label
     */
    static formatYAxisLabel(value) {
        if (value >= 1000000) {
            return `₹${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
            return `₹${(value / 1000).toFixed(0)}K`;
        }
        return `₹${value}`;
    }

    /**
     * Check if dataset represents currency values
     */
    static isCurrencyDataset(label) {
        const currencyKeywords = ['budget', 'revenue', 'investment', 'profit', 'amount'];
        return currencyKeywords.some(keyword => 
            label && label.toLowerCase().includes(keyword)
        );
    }

    /**
     * Create bar chart
     */
    static createBarChart(ctx, data, options = {}) {
        const defaultData = {
            labels: data.labels || [],
            datasets: [{
                label: data.datasetLabel || 'Value',
                data: data.values || [],
                backgroundColor: [
                    'rgba(27, 47, 74, 0.8)',
                    'rgba(17, 197, 217, 0.8)',
                    'rgba(245, 193, 108, 0.8)',
                    'rgba(33, 230, 162, 0.8)',
                    'rgba(233, 75, 75, 0.8)',
                    'rgba(114, 137, 218, 0.8)'
                ],
                borderColor: [
                    'rgba(27, 47, 74, 1)',
                    'rgba(17, 197, 217, 1)',
                    'rgba(245, 193, 108, 1)',
                    'rgba(33, 230, 162, 1)',
                    'rgba(233, 75, 75, 1)',
                    'rgba(114, 137, 218, 1)'
                ],
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false,
            }]
        };

        const mergedOptions = this.mergeOptions(
            this.getBaseOptions(),
            options
        );

        return new Chart(ctx, {
            type: 'bar',
            data: defaultData,
            options: mergedOptions
        });
    }

    /**
     * Create line chart
     */
    static createLineChart(ctx, data, options = {}) {
        const defaultData = {
            labels: data.labels || [],
            datasets: [{
                label: data.datasetLabel || 'Value',
                data: data.values || [],
                borderColor: 'rgba(17, 197, 217, 1)',
                backgroundColor: 'rgba(17, 197, 217, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(17, 197, 217, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        };

        const mergedOptions = this.mergeOptions(
            this.getBaseOptions(),
            options
        );

        return new Chart(ctx, {
            type: 'line',
            data: defaultData,
            options: mergedOptions
        });
    }

    /**
     * Create pie chart
     */
    static createPieChart(ctx, data, options = {}) {
        const defaultData = {
            labels: data.labels || [],
            datasets: [{
                label: data.datasetLabel || 'Value',
                data: data.values || [],
                backgroundColor: [
                    'rgba(17, 197, 217, 0.8)',
                    'rgba(245, 193, 108, 0.8)',
                    'rgba(33, 230, 162, 0.8)',
                    'rgba(114, 137, 218, 0.8)',
                    'rgba(233, 75, 75, 0.8)',
                    'rgba(156, 39, 176, 0.8)'
                ],
                borderColor: '#fff',
                borderWidth: 2,
                hoverOffset: 4
            }]
        };

        const pieOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: '#C8D1D9',
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 28, 46, 0.95)',
                    titleFont: {
                        family: 'Inter',
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        family: 'Inter',
                        size: 13
                    },
                    padding: 16,
                    cornerRadius: 8,
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ₹${Number(value).toLocaleString('en-IN')} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1500,
                easing: 'easeOutQuart'
            }
        };

        const mergedOptions = this.mergeOptions(pieOptions, options);

        return new Chart(ctx, {
            type: 'pie',
            data: defaultData,
            options: mergedOptions
        });
    }

    /**
     * Create doughnut chart
     */
    static createDoughnutChart(ctx, data, options = {}) {
        const doughnutOptions = {
            cutout: '70%',
            ...options
        };

        return this.createPieChart(ctx, data, doughnutOptions);
    }

    /**
     * Create multi-dataset chart
     */
    static createMultiDatasetChart(ctx, data, chartType = 'bar', options = {}) {
        const defaultData = {
            labels: data.labels || [],
            datasets: data.datasets || []
        };

        const mergedOptions = this.mergeOptions(
            this.getBaseOptions(),
            {
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#C8D1D9',
                            font: {
                                family: 'Inter',
                                size: 12
                            },
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            },
            options
        );

        return new Chart(ctx, {
            type: chartType,
            data: defaultData,
            options: mergedOptions
        });
    }

    /**
     * Merge chart options
     */
    static mergeOptions(...options) {
        return options.reduce((merged, option) => {
            return this.deepMerge(merged, option);
        }, {});
    }

    /**
     * Deep merge objects
     */
    static deepMerge(target, source) {
        const result = { ...target };
        
        for (const key in source) {
            if (source.hasOwnProperty(key)) {
                if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
                    result[key] = this.deepMerge(result[key] || {}, source[key]);
                } else {
                    result[key] = source[key];
                }
            }
        }
        
        return result;
    }
}

/**
 * Chart Data Processor
 * Processes financial data for chart visualization.
 */
class ChartDataProcessor {
    /**
     * Process financial overview data for bar chart
     */
    static processFinancialOverview(data) {
        return {
            labels: ['Budget', 'Revenue', 'Investment', 'Profit'],
            values: [
                data.total_budget || 0,
                data.total_revenue || 0,
                data.total_sponsor_investment || 0,
                data.profit || 0
            ],
            datasetLabel: 'Amount (₹)'
        };
    }

    /**
     * Process monthly trends data for line chart
     */
    static processMonthlyTrends(data) {
        const sortedData = data.sort((a, b) => a.month.localeCompare(b.month));
        
        return {
            labels: sortedData.map(item => {
                const date = new Date(item.month);
                return date.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
            }),
            values: sortedData.map(item => item.total_revenue),
            datasetLabel: 'Monthly Revenue'
        };
    }

    /**
     * Process sponsor ROI data for bar chart
     */
    static processSponsorROI(data) {
        const sortedData = data.sort((a, b) => b.total_investment - a.total_investment).slice(0, 10);
        
        return {
            labels: sortedData.map(item => item.sponsor_name),
            values: sortedData.map(item => item.total_investment),
            datasetLabel: 'Total Investment (₹)'
        };
    }

    /**
     * Process industry distribution data for pie chart
     */
    static processIndustryDistribution(data) {
        const industryCounts = {};
        
        data.forEach(sponsor => {
            const industry = sponsor.industry || 'Unknown';
            industryCounts[industry] = (industryCounts[industry] || 0) + 1;
        });

        const sortedIndustries = Object.entries(industryCounts)
            .sort((a, b) => b[1] - a[1]);

        return {
            labels: sortedIndustries.map(([industry]) => industry),
            values: sortedIndustries.map(([, count]) => count),
            datasetLabel: 'Number of Sponsors'
        };
    }

    /**
     * Process revenue vs budget data for multi-dataset chart
     */
    static processRevenueVsBudget(data) {
        const sortedData = data.sort((a, b) => a.date.localeCompare(b.date));
        
        return {
            labels: sortedData.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
            }),
            datasets: [
                {
                    label: 'Budget',
                    data: sortedData.map(item => item.budget),
                    backgroundColor: 'rgba(27, 47, 74, 0.8)',
                    borderColor: 'rgba(27, 47, 74, 1)',
                    borderWidth: 1,
                    borderRadius: 6
                },
                {
                    label: 'Revenue',
                    data: sortedData.map(item => item.revenue),
                    backgroundColor: 'rgba(17, 197, 217, 0.8)',
                    borderColor: 'rgba(17, 197, 217, 1)',
                    borderWidth: 1,
                    borderRadius: 6
                },
                {
                    label: 'Sponsorship',
                    data: sortedData.map(item => item.total_sponsorship || 0),
                    backgroundColor: 'rgba(245, 193, 108, 0.8)',
                    borderColor: 'rgba(245, 193, 108, 1)',
                    borderWidth: 1,
                    borderRadius: 6
                }
            ]
        };
    }

    /**
     * Process ROI performance data for chart
     */
    static processROIPerformance(data) {
        const sortedData = data.sort((a, b) => b.average_roi - a.average_roi).slice(0, 8);
        
        return {
            labels: sortedData.map(item => item.sponsor_name),
            values: sortedData.map(item => item.average_roi || 0),
            datasetLabel: 'Average ROI (%)'
        };
    }

    /**
     * Process event performance data
     */
    static processEventPerformance(data) {
        const sortedData = data.sort((a, b) => b.revenue - a.revenue).slice(0, 10);
        
        return {
            labels: sortedData.map(item => item.name),
            datasets: [
                {
                    label: 'Revenue',
                    data: sortedData.map(item => item.revenue),
                    backgroundColor: 'rgba(33, 230, 162, 0.8)',
                    borderColor: 'rgba(33, 230, 162, 1)',
                    borderWidth: 1,
                    borderRadius: 6
                },
                {
                    label: 'Profit',
                    data: sortedData.map(item => item.revenue - item.budget),
                    backgroundColor: 'rgba(17, 197, 217, 0.8)',
                    borderColor: 'rgba(17, 197, 217, 1)',
                    borderWidth: 1,
                    borderRadius: 6
                }
            ]
        };
    }
}

/**
 * Chart Manager
 * Manages chart instances and updates.
 */
class ChartManager {
    constructor() {
        this.charts = new Map();
    }

    /**
     * Register a chart instance
     */
    registerChart(id, chart) {
        this.charts.set(id, chart);
    }

    /**
     * Get a chart instance
     */
    getChart(id) {
        return this.charts.get(id);
    }

    /**
     * Update a chart with new data
     */
    updateChart(id, data) {
        const chart = this.charts.get(id);
        if (chart) {
            chart.data = data;
            chart.update('active');
        }
    }

    /**
     * Destroy a chart
     */
    destroyChart(id) {
        const chart = this.charts.get(id);
        if (chart) {
            chart.destroy();
            this.charts.delete(id);
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }

    /**
     * Export chart as image
     */
    exportChart(id, format = 'png') {
        const chart = this.charts.get(id);
        if (chart) {
            const url = chart.toBase64Image();
            
            // Create download link
            const link = document.createElement('a');
            link.download = `chart_${id}_${Date.now()}.${format}`;
            link.href = url;
            link.click();
            
            return url;
        }
        return null;
    }

    /**
     * Resize all charts
     */
    resizeAllCharts() {
        this.charts.forEach(chart => chart.resize());
    }
}

// Create global chart manager instance
const chartManager = new ChartManager();

/**
 * Utility Functions
 */
export const ChartUtils = {
    /**
     * Create financial overview chart
     */
    createFinancialOverviewChart(ctx, data) {
        const chartData = ChartDataProcessor.processFinancialOverview(data);
        const chart = ChartFactory.createBarChart(ctx, chartData);
        
        chartManager.registerChart('financial-overview', chart);
        return chart;
    },

    /**
     * Create monthly trends chart
     */
    createMonthlyTrendsChart(ctx, data) {
        const chartData = ChartDataProcessor.processMonthlyTrends(data);
        const chart = ChartFactory.createLineChart(ctx, chartData);
        
        chartManager.registerChart('monthly-trends', chart);
        return chart;
    },

    /**
     * Create sponsor ROI chart
     */
    createSponsorROIChart(ctx, data) {
        const chartData = ChartDataProcessor.processSponsorROI(data);
        const chart = ChartFactory.createBarChart(ctx, chartData);
        
        chartManager.registerChart('sponsor-roi', chart);
        return chart;
    },

    /**
     * Create industry distribution chart
     */
    createIndustryDistributionChart(ctx, data) {
        const chartData = ChartDataProcessor.processIndustryDistribution(data);
        const chart = ChartFactory.createDoughnutChart(ctx, chartData);
        
        chartManager.registerChart('industry-distribution', chart);
        return chart;
    },

    /**
     * Create revenue vs budget chart
     */
    createRevenueVsBudgetChart(ctx, data) {
        const chartData = ChartDataProcessor.processRevenueVsBudget(data);
        const chart = ChartFactory.createMultiDatasetChart(ctx, chartData, 'bar');
        
        chartManager.registerChart('revenue-vs-budget', chart);
        return chart;
    },

    /**
     * Create ROI performance chart
     */
    createROIPerformanceChart(ctx, data) {
        const chartData = ChartDataProcessor.processROIPerformance(data);
        const chart = ChartFactory.createBarChart(ctx, chartData);
        
        chartManager.registerChart('roi-performance', chart);
        return chart;
    },

    /**
     * Create event performance chart
     */
    createEventPerformanceChart(ctx, data) {
        const chartData = ChartDataProcessor.processEventPerformance(data);
        const chart = ChartFactory.createMultiDatasetChart(ctx, chartData, 'bar');
        
        chartManager.registerChart('event-performance', chart);
        return chart;
    },

    /**
     * Update chart data
     */
    updateChart(id, data, processor = null) {
        if (processor) {
            const processedData = processor(data);
            chartManager.updateChart(id, processedData);
        } else {
            chartManager.updateChart(id, data);
        }
    },

    /**
     * Destroy chart
     */
    destroyChart(id) {
        chartManager.destroyChart(id);
    },

    /**
     * Export chart
     */
    exportChart(id, format = 'png') {
        return chartManager.exportChart(id, format);
    },

    /**
     * Get chart manager instance
     */
    getChartManager() {
        return chartManager;
    }
};

export { ChartFactory, ChartDataProcessor, ChartManager, chartManager };
export default ChartUtils;