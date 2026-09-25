/**
 * CommentGuard AI - Model Explainability Component
 * Visualizes signal contribution weights and transparent scoring rationale.
 */

const Explainability = {
  /**
   * Renders the explainability bar chart breakdown.
   */
  render(explainabilityData) {
    const container = document.getElementById("explainability-bars-container");
    if (!container || !explainabilityData) return;

    const contributions = explainabilityData.aggregate_contributions || {};
    const config = explainabilityData.feature_weights_config || {};

    const categoryOrder = [
      "suspicious_content",
      "duplicate_text",
      "timing",
      "avatar",
      "username_pattern",
      "account_age",
      "formatting"
    ];

    const html = categoryOrder.map(catKey => {
      const cfg = config[catKey] || { label: catKey, max_pts: 20, desc: '' };
      const pct = contributions[catKey] !== undefined ? contributions[catKey] : 0;

      // Color gradation based on weight
      let barGradient = 'linear-gradient(90deg, #38bdf8 0%, #3b82f6 100%)';
      if (pct >= 25) {
        barGradient = 'linear-gradient(90deg, #ef4444 0%, #f43f5e 100%)';
      } else if (pct >= 15) {
        barGradient = 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)';
      }

      return `
        <div class="explain-bar-row" title="${Components.escapeHTML(cfg.desc)} (Max ${cfg.max_pts} pts)">
          <div class="explain-bar-header">
            <span class="explain-label">${Components.escapeHTML(cfg.label)}</span>
            <span class="explain-weight">${pct}%</span>
          </div>
          <div class="explain-bar-track">
            <div class="explain-bar-fill" style="width: ${Math.max(4, pct)}%; background: ${barGradient};"></div>
          </div>
        </div>
      `;
    }).join('');

    container.innerHTML = html;
  }
};
