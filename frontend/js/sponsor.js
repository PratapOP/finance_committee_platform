/**
 * Enhanced Sponsors Page with Error Handling for Finance Committee Platform
 * Uses centralized API client with proper error handling and user feedback.
 */

import { apiMethods, apiUtils } from './api.js';

class SponsorsManager {
    constructor() {
        this.sponsors = [];
        this.isLoading = false;
        this.init();
    }

    async init() {
        try {
            apiUtils.setLoading(true);
            await this.loadSponsors();
            this.setupEventListeners();
            this.renderSponsors();
        } catch (error) {
            console.error('Sponsors page initialization failed:', error);
            apiUtils.showError(error, 'sponsors-error');
        } finally {
            apiUtils.setLoading(false);
        }
    }

    async loadSponsors() {
        try {
            this.sponsors = await apiMethods.sponsors.getAll();
            
            if (!this.sponsors || !Array.isArray(this.sponsors)) {
                throw new Error('Invalid sponsors data received');
            }
        } catch (error) {
            console.error('Failed to load sponsors:', error);
            apiUtils.showError(error, 'load-sponsors-error');
            
            // Set empty array to prevent UI crashes
            this.sponsors = [];
        }
    }

    setupEventListeners() {
        try {
            // Search functionality
            const searchInput = document.getElementById('search-sponsors');
            if (searchInput) {
                searchInput.addEventListener('input', 
                    apiUtils.debounce(this.handleSearch.bind(this), 300)
                );
            }

            // Add sponsor button
            const addBtn = document.getElementById('add-sponsor-btn');
            if (addBtn) {
                addBtn.addEventListener('click', this.handleAddSponsor.bind(this));
            }

            // Refresh button
            const refreshBtn = document.getElementById('refresh-sponsors-btn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', this.handleRefresh.bind(this));
            }

            // Filter by industry
            const industryFilter = document.getElementById('industry-filter');
            if (industryFilter) {
                industryFilter.addEventListener('change', this.handleFilter.bind(this));
            }
        } catch (error) {
            console.error('Failed to setup event listeners:', error);
        }
    }

    renderSponsors(sponsorsToRender = this.sponsors) {
        try {
            const container = document.getElementById('sponsorList');
            if (!container) {
                console.warn('Sponsor list container not found');
                return;
            }

            if (sponsorsToRender.length === 0) {
                container.innerHTML = `
                    <div class="no-data">
                        <p>No sponsors found.</p>
                        <button class="btn-primary" onclick="window.sponsorsManager.handleAddSponsor()">
                            Add First Sponsor
                        </button>
                    </div>
                `;
                return;
            }

            const sponsorsHTML = sponsorsToRender.map(sponsor => this.createSponsorCard(sponsor)).join('');
            container.innerHTML = sponsorsHTML;

            // Add click handlers for sponsor cards
            this.attachSponsorCardHandlers();
        } catch (error) {
            console.error('Failed to render sponsors:', error);
            apiUtils.showError(error, 'render-error');
            
            // Show fallback message
            const container = document.getElementById('sponsorList');
            if (container) {
                container.innerHTML = '<p class="error-message">Failed to load sponsors. Please try again.</p>';
            }
        }
    }

    createSponsorCard(sponsor) {
        const investment = sponsor.total_invested || 0;
        const industry = sponsor.industry || 'Not specified';
        const contact = sponsor.contact_person || 'Not specified';

        return `
            <div class="sponsor-card" data-id="${sponsor.id}">
                <div class="sponsor-header">
                    <h3>${this.escapeHtml(sponsor.name)}</h3>
                    <span class="industry-badge">${this.escapeHtml(industry)}</span>
                </div>
                <div class="sponsor-details">
                    <div class="detail-item">
                        <span class="label">Contact:</span>
                        <span class="value">${this.escapeHtml(contact)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Email:</span>
                        <span class="value">${this.escapeHtml(sponsor.email || 'Not specified')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Investment:</span>
                        <span class="value investment">${apiUtils.formatCurrency(investment)}</span>
                    </div>
                </div>
                <div class="sponsor-actions">
                    <button class="btn-secondary edit-sponsor" data-id="${sponsor.id}">
                        Edit
                    </button>
                    <button class="btn-danger delete-sponsor" data-id="${sponsor.id}">
                        Delete
                    </button>
                </div>
            </div>
        `;
    }

    attachSponsorCardHandlers() {
        try {
            // Edit buttons
            document.querySelectorAll('.edit-sponsor').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const sponsorId = parseInt(e.target.dataset.id);
                    this.handleEditSponsor(sponsorId);
                });
            });

            // Delete buttons
            document.querySelectorAll('.delete-sponsor').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const sponsorId = parseInt(e.target.dataset.id);
                    this.handleDeleteSponsor(sponsorId);
                });
            });
        } catch (error) {
            console.error('Failed to attach sponsor card handlers:', error);
        }
    }

    handleSearch(event) {
        try {
            const searchTerm = event.target.value.toLowerCase().trim();
            
            if (searchTerm === '') {
                this.renderSponsors();
                return;
            }

            const filteredSponsors = this.sponsors.filter(sponsor => 
                sponsor.name.toLowerCase().includes(searchTerm) ||
                (sponsor.industry && sponsor.industry.toLowerCase().includes(searchTerm)) ||
                (sponsor.contact_person && sponsor.contact_person.toLowerCase().includes(searchTerm)) ||
                (sponsor.email && sponsor.email.toLowerCase().includes(searchTerm))
            );

            this.renderSponsors(filteredSponsors);
        } catch (error) {
            console.error('Search failed:', error);
            apiUtils.showError(error, 'search-error');
        }
    }

    handleFilter(event) {
        try {
            const selectedIndustry = event.target.value;
            
            if (selectedIndustry === '') {
                this.renderSponsors();
                return;
            }

            const filteredSponsors = this.sponsors.filter(sponsor => 
                sponsor.industry === selectedIndustry
            );

            this.renderSponsors(filteredSponsors);
        } catch (error) {
            console.error('Filter failed:', error);
            apiUtils.showError(error, 'filter-error');
        }
    }

    async handleAddSponsor() {
        try {
            const sponsorData = await this.handleSponsorSubmit();
            if (!sponsorData) return; // User cancelled

            apiUtils.setLoading(true);
            const result = await apiMethods.sponsors.create(sponsorData);
            
            // Add to local array
            this.sponsors.push(result.sponsor);
            this.renderSponsors();
            
            this.showModal('Sponsor added successfully!', false);
        } catch (error) {
            console.error('Failed to add sponsor:', error);
            this.showModal(error.message, true);
        } finally {
            apiUtils.setLoading(false);
        }
    }

    async handleEditSponsor(sponsorId) {
        try {
            const sponsor = this.sponsors.find(s => s.id === sponsorId);
            if (!sponsor) {
                throw new Error('Sponsor not found');
            }

            const updatedData = await this.handleSponsorSubmit(sponsor);
            if (!updatedData) return; // User cancelled

            apiUtils.setLoading(true);
            const result = await apiMethods.sponsors.update(sponsorId, updatedData);
            
            // Update local array
            const index = this.sponsors.findIndex(s => s.id === sponsorId);
            if (index !== -1) {
                this.sponsors[index] = result.sponsor;
            }
            
            this.renderSponsors();
            this.showModal('Sponsor updated successfully!', false);
        } catch (error) {
            console.error('Failed to edit sponsor:', error);
            this.showModal(error.message, true);
        } finally {
            apiUtils.setLoading(false);
        }
    }

    async handleDeleteSponsor(sponsorId) {
        try {
            const sponsor = this.sponsors.find(s => s.id === sponsorId);
            if (!sponsor) {
                throw new Error('Sponsor not found');
            }

            const confirmed = confirm(`Are you sure you want to delete "${sponsor.name}"?`);
            if (!confirmed) return;

            apiUtils.setLoading(true);
            await apiMethods.sponsors.delete(sponsorId);
            
            // Remove from local array
            this.sponsors = this.sponsors.filter(s => s.id !== sponsorId);
            this.renderSponsors();
            
            apiUtils.showSuccess('Sponsor deleted successfully!');
        } catch (error) {
            console.error('Failed to delete sponsor:', error);
            apiUtils.showError(error, 'delete-sponsor-error');
        } finally {
            apiUtils.setLoading(false);
        }
    }

    async handleRefresh() {
        if (this.isLoading) return;

        try {
            this.isLoading = true;
            apiUtils.setLoading(true);
            
            await this.loadSponsors();
            this.renderSponsors();
            
            apiUtils.showSuccess('Sponsors refreshed successfully!');
        } catch (error) {
            console.error('Failed to refresh sponsors:', error);
            apiUtils.showError(error, 'refresh-error');
        } finally {
            this.isLoading = false;
            apiUtils.setLoading(false);
        }
    }

    openModal(sponsor = null) {
        const modal = document.getElementById('sponsorModal');
        const form = document.getElementById('sponsorForm');
        const title = document.getElementById('sponsorModalTitle');
        
        // Clear previous messages
        this.clearMessages();
        
        if (sponsor) {
            // Edit mode - populate form
            title.textContent = 'Edit Sponsor';
            document.getElementById('sponsorName').value = sponsor.name || '';
            document.getElementById('sponsorIndustry').value = sponsor.industry || '';
            document.getElementById('sponsorContact').value = sponsor.contact_person || '';
            document.getElementById('sponsorEmail').value = sponsor.email || '';
            document.getElementById('sponsorPhone').value = sponsor.phone || '';
            form.dataset.sponsorId = sponsor.id;
        } else {
            // Add mode - clear form
            title.textContent = 'Add Sponsor';
            form.reset();
            delete form.dataset.sponsorId;
        }
        
        modal.style.display = 'block';
    }

    closeModal() {
        const modal = document.getElementById('sponsorModal');
        modal.style.display = 'none';
        this.clearMessages();
    }

    clearMessages() {
        const errorContainer = document.getElementById('sponsor-error-container');
        const successContainer = document.getElementById('sponsor-success-container');
        if (errorContainer) {
            errorContainer.style.display = 'none';
            errorContainer.textContent = '';
        }
        if (successContainer) {
            successContainer.style.display = 'none';
            successContainer.textContent = '';
        }
    }

    showModal(message, isError = false) {
        const container = isError ? 
            document.getElementById('sponsor-error-container') : 
            document.getElementById('sponsor-success-container');
        
        if (container) {
            container.textContent = message;
            container.style.display = 'block';
            
            // Auto-hide success messages after 3 seconds
            if (!isError) {
                setTimeout(() => {
                    container.style.display = 'none';
                    container.textContent = '';
                }, 3000);
            }
        }
    }

    handleSponsorSubmit(sponsor = null) {
        return new Promise((resolve, reject) => {
            this.openModal(sponsor);
            
            const form = document.getElementById('sponsorForm');
            const submitHandler = async (e) => {
                e.preventDefault();
                
                try {
                    const formData = new FormData(form);
                    const sponsorData = {
                        name: formData.get('sponsorName')?.trim(),
                        industry: formData.get('sponsorIndustry')?.trim() || null,
                        contact_person: formData.get('sponsorContact')?.trim() || null,
                        email: formData.get('sponsorEmail')?.trim() || null,
                        phone: formData.get('sponsorPhone')?.trim() || null
                    };
                    
                    if (!sponsorData.name) {
                        this.showModal('Sponsor name is required', true);
                        return;
                    }
                    
                    this.closeModal();
                    resolve(sponsorData);
                } catch (error) {
                    this.showModal(error.message, true);
                    reject(error);
                } finally {
                    form.removeEventListener('submit', submitHandler);
                }
            };
            
            form.addEventListener('submit', submitHandler);
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize sponsors page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.sponsorsManager = new SponsorsManager();
        
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
    } catch (error) {
        console.error('Failed to initialize sponsors page:', error);
        apiUtils.showError(
            { message: 'Sponsors page initialization failed. Please refresh the page.' },
            'init-error'
        );
    }
});