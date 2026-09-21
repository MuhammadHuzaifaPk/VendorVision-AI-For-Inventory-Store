/**
 * VendorVision API Client - Sanitized Base Path
 */

let clientHost = window.location.hostname || '127.0.0.1';
if (clientHost === '0.0.0.0') {
    clientHost = '127.0.0.1';
}

const API_BASE_URL = window.location.port === '8000'
    ? '/api/v1'
    : `${window.location.protocol}//${clientHost}:8000/api/v1`;

const apiClient = {
    async analyzeInventory(items) {
        try {
            const response = await fetch(`${API_BASE_URL}/inventory/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ items })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
                throw new Error(errorData.detail || 'Failed to analyze inventory');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error (analyzeInventory):', error);
            throw error;
        }
    },

    async generateEmailDraft(emailData) {
        try {
            const response = await fetch(`${API_BASE_URL}/supplier/draft-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(emailData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
                throw new Error(errorData.detail || 'Failed to generate email draft');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error (generateEmailDraft):', error);
            throw error;
        }
    }
};

window.apiClient = apiClient;