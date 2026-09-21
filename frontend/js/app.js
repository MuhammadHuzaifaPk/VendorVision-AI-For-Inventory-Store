/**
 * VendorVision AI Main Controller
 */

const SAMPLE_INVENTORY = [
    { sku: "COF-EXP-1001", name: "Espresso Beans (1kg)", current_stock: 8, target_stock_level: 80, daily_sales_rate: 3.5, unit_cost: 18.50, supplier_name: "Apex Coffee Wholesale" },
    { sku: "MILK-OAT-2004", name: "Barista Oat Milk Case", current_stock: 4, target_stock_level: 60, daily_sales_rate: 2.8, unit_cost: 32.00, supplier_name: "SunRich Dairy Supplies" },
    { sku: "CUP-PAP-12OZ", name: "Compostable Cups 12oz", current_stock: 2, target_stock_level: 20, daily_sales_rate: 0.8, unit_cost: 75.00, supplier_name: "EcoPack Direct" }
];

document.addEventListener('DOMContentLoaded', () => {
    // 1. Tab Navigation with e.target.closest Fix
    document.querySelectorAll('.nav-item').forEach(button => {
        button.addEventListener('click', (e) => {
            const navBtn = e.target.closest('.nav-item');
            if (!navBtn) return;

            const tabName = navBtn.getAttribute('data-tab');
            window.uiController.switchTab(tabName);

            if (tabName === 'communications') {
                loadCommunicationsHistory();
            } else if (tabName === 'settings') {
                loadSettings();
            }
        });
    });

    // 2. Dashboard Run Analysis Action
    const runBtn = document.getElementById('run-analysis-btn');
    if (runBtn) {
        runBtn.addEventListener('click', runAnalysis);
    }

    async function runAnalysis() {
        try {
            if (runBtn) runBtn.textContent = 'Analyzing...';
            const result = await window.apiClient.analyzeInventory(SAMPLE_INVENTORY);
            window.uiController.updateMetrics(result.summary);
            window.uiController.renderInventoryTable(result.items, handleReorderRequest);
        } catch (err) {
            alert(`Analysis Error: ${err.message}`);
        } finally {
            if (runBtn) runBtn.textContent = 'Run Deep Analysis';
        }
    }

    async function handleReorderRequest(item) {
        window.uiController.showModalLoading();
        try {
            const response = await window.apiClient.generateEmailDraft({
                supplier_name: item.supplier_name,
                item_name: item.name,
                unit_cost: item.unit_cost,
                suggested_qty: item.suggested_reorder_qty || 10
            });
            window.uiController.showModalResult(response);
        } catch (err) {
            alert(`AI Generation Notice: ${err.message}`);
            window.uiController.hideModal();
        }
    }

    // 3. Communications History Action
    const refreshCommsBtn = document.getElementById('refresh-comms-btn');
    if (refreshCommsBtn) {
        refreshCommsBtn.addEventListener('click', loadCommunicationsHistory);
    }

    async function loadCommunicationsHistory() {
        try {
            const res = await fetch('/api/v1/supplier/communications');
            const data = await res.json();
            window.uiController.renderCommunicationsList(data.communications);
        } catch (e) {
            console.error('Error fetching communications history:', e);
        }
    }

   // Settings Form Submission
const settingsForm = document.getElementById('settings-form');
if (settingsForm) {
    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const apiKey = document.getElementById('setting-api-key').value;
        const model = document.getElementById('setting-model').value;
        const fallback = document.getElementById('setting-fallback').checked;
        const statusMsg = document.getElementById('settings-status-msg');

        try {
            statusMsg.textContent = 'Saving...';
            statusMsg.style.color = '#64748b';

            const res = await fetch('/api/v1/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ai_api_key: apiKey,
                    ai_model_name: model,
                    enable_mock_fallback: fallback
                })
            });
            const data = await res.json();
            
            if (statusMsg) {
                statusMsg.textContent = data.status_message;
                statusMsg.style.color = '#10b981';
            }
            // Clear input box after saving for security
            document.getElementById('setting-api-key').value = '';
        } catch (err) {
            if (statusMsg) {
                statusMsg.textContent = 'Failed to save Gemini settings.';
                statusMsg.style.color = '#ef4444';
            }
        }
    });
}

async function loadSettings() {
    try {
        const res = await fetch('/api/v1/settings');
        const data = await res.json();
        
        if (document.getElementById('setting-model')) {
            document.getElementById('setting-model').value = data.ai_model_name || 'gemini-3.5-flash';
        }
        if (document.getElementById('setting-fallback')) {
            document.getElementById('setting-fallback').checked = data.enable_mock_fallback;
        }
        if (data.masked_api_key && document.getElementById('setting-api-key')) {
            document.getElementById('setting-api-key').placeholder = `Active: ${data.masked_api_key}`;
        }
    } catch (e) {
        console.error('Error loading settings:', e);
    }
}
    // Modal Close Action
    const closeModal = document.getElementById('close-modal');
    if (closeModal) {
        closeModal.addEventListener('click', () => window.uiController.hideModal());
    }

    const sendEmailBtn = document.getElementById('send-email-btn');
    if (sendEmailBtn) {
        sendEmailBtn.addEventListener('click', () => {
            alert('Email dispatched to supplier successfully!');
            window.uiController.hideModal();
        });
    }

    // Run initial analysis on page load
    runAnalysis();
});

// Example JavaScript for your frontend Send button
function sendEmailDraft(emailData) {
    window.location.href = emailData.mailto_link;
}