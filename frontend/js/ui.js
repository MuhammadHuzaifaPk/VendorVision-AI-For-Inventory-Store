/**
 * VendorVision UI Controller
 */

const uiController = {
    elements: {
        navButtons: document.querySelectorAll('.nav-item'),
        tabContents: document.querySelectorAll('.tab-content'),
        metricCritical: document.getElementById('metric-critical'),
        metricLow: document.getElementById('metric-low'),
        metricAnalyzed: document.getElementById('metric-analyzed'),
        metricValue: document.getElementById('metric-value'),
        inventoryBody: document.getElementById('inventory-body'),
        commsList: document.getElementById('communications-list'),
        settingsForm: document.getElementById('settings-form'),
        settingApiKey: document.getElementById('setting-api-key'),
        settingModel: document.getElementById('setting-model'),
        settingFallback: document.getElementById('setting-fallback'),
        settingsStatusMsg: document.getElementById('settings-status-msg'),
        aiModal: document.getElementById('ai-modal'),
        modalLoading: document.getElementById('modal-loading'),
        modalResult: document.getElementById('modal-result'),
        emailTo: document.getElementById('email-to'),
        emailSubject: document.getElementById('email-subject'),
        emailBody: document.getElementById('email-body'),
        savingsAlert: document.getElementById('savings-alert'),
        savingsAmount: document.getElementById('savings-amount'),
        sendEmailBtn: document.getElementById('send-email-btn'),
        closeModalBtn: document.getElementById('close-modal')
    },

    switchTab(tabName) {
        document.querySelectorAll('.nav-item').forEach(btn => {
            if (btn.getAttribute('data-tab') === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        document.querySelectorAll('.tab-content').forEach(section => {
            if (section.id === `tab-${tabName}`) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        });
    },

    updateMetrics(summary) {
        const s = summary || {};
        if (this.elements.metricCritical) this.elements.metricCritical.textContent = s.critical_stockouts ?? s.critical_skus ?? 0;
        if (this.elements.metricLow) this.elements.metricLow.textContent = s.low_stock_warnings ?? s.warning_skus ?? 0;
        if (this.elements.metricAnalyzed) this.elements.metricAnalyzed.textContent = s.total_items_analyzed ?? s.total_skus ?? 0;

        if (this.elements.metricValue) {
            const val = s.total_estimated_reorder_value ?? 0;
            this.elements.metricValue.textContent = `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
    },

    renderInventoryTable(items, onReorderClick) {
        if (!this.elements.inventoryBody) return;
        if (!items || items.length === 0) {
            this.elements.inventoryBody.innerHTML = `<tr><td colspan="6" class="empty-state">No items found.</td></tr>`;
            return;
        }

        this.elements.inventoryBody.innerHTML = items.map(item => {
            const status = item.stock_status || item.status || 'HEALTHY';
            const days = item.days_until_stockout ?? 0;
            const daysText = days > 90 ? '> 90 days' : `${days} days`;
            const reorderQty = item.suggested_reorder_qty ?? item.recommended_reorder_qty ?? 0;

            return `
                <tr>
                    <td><strong>${this.escapeHtml(item.name)}</strong><br><small class="subtitle">${this.escapeHtml(item.sku)}</small></td>
                    <td><span class="badge ${status.toLowerCase()}">${status}</span></td>
                    <td><strong>${daysText}</strong></td>
                    <td>${item.current_stock} units</td>
                    <td><strong>${reorderQty}</strong> units<br><small class="subtitle">~$${Number(item.estimated_reorder_cost || 0).toFixed(2)}</small></td>
                    <td>
                        <button class="btn primary reorder-btn" data-id="${this.escapeHtml(item.id || item.sku)}">
                            🤖 Draft Reorder
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        document.querySelectorAll('.reorder-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-id');
                const selected = items.find(i => (i.id === id || i.sku === id));
                if (selected && onReorderClick) onReorderClick(selected);
            });
        });
    },

    renderCommunicationsList(comms) {
        if (!this.elements.commsList) return;
        if (!comms || comms.length === 0) {
            this.elements.commsList.innerHTML = `<p class="empty-state">No AI communications generated yet.</p>`;
            return;
        }

        this.elements.commsList.innerHTML = comms.map(c => `
            <div class="card" style="margin-bottom: 12px; border-left: 4px solid var(--primary);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <strong>To: ${this.escapeHtml(c.supplier_name)} (${this.escapeHtml(c.supplier_email)})</strong>
                    <small style="color: var(--text-secondary);">${c.timestamp || 'Recent'}</small>
                </div>
                <p style="margin-bottom: 8px;"><strong>Subject:</strong> ${this.escapeHtml(c.subject)}</p>
                <span class="badge" style="background:#e0e7ff; color:#3730a3; margin-bottom:12px; display:inline-block;">Engine: ${c.mode_used || 'AI'}</span>
                <textarea readonly class="form-control code-font" rows="6">${this.escapeHtml(c.body)}</textarea>
            </div>
        `).join('');
    },

    showModalLoading() {
        if (this.elements.aiModal) this.elements.aiModal.classList.remove('hidden');
        if (this.elements.modalLoading) this.elements.modalLoading.classList.remove('hidden');
        if (this.elements.modalResult) this.elements.modalResult.classList.add('hidden');
    },

    showModalResult(emailData) {
        if (this.elements.modalLoading) this.elements.modalLoading.classList.add('hidden');
        if (this.elements.modalResult) this.elements.modalResult.classList.remove('hidden');

        if (this.elements.emailTo) this.elements.emailTo.textContent = emailData.supplier_email;
        if (this.elements.emailSubject) this.elements.emailSubject.textContent = emailData.subject;
        if (this.elements.emailBody) this.elements.emailBody.value = emailData.email_content || emailData.body;

        const savings = emailData.estimated_savings_negotiated || 0;
        if (savings > 0 && this.elements.savingsAmount) {
            this.elements.savingsAmount.textContent = `$${Number(savings).toFixed(2)}`;
            if (this.elements.savingsAlert) this.elements.savingsAlert.classList.remove('hidden');
        } else if (this.elements.savingsAlert) {
            this.elements.savingsAlert.classList.add('hidden');
        }
    },

    hideModal() {
        if (this.elements.aiModal) this.elements.aiModal.classList.add('hidden');
    },

    escapeHtml(str) {
        return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
};

window.uiController = uiController;