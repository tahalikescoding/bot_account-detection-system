/**
 * CommentGuard AI - Live Fraud / Bot Test Injector
 * Facilitates interactive live demo fraud injections.
 */

const Injector = {
  isInjecting: false,

  /**
   * Triggers an injection of synthetic bot accounts into the live feed.
   */
  async inject(injectionType) {
    if (this.isInjecting) return;
    this.isInjecting = true;

    // Visual button feedback
    const btnId = `btn-inject-${injectionType.replace('_', '-')}`;
    const btn = document.getElementById(btnId);
    let originalText = '';
    if (btn) {
      originalText = btn.innerHTML;
      btn.innerHTML = `<span class="pulse-dot"></span> Injecting...`;
      btn.style.opacity = '0.7';
    }

    try {
      const response = await fetch('/api/inject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          injection_type: injectionType,
          current_comments: App.state.comments
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.status === 'success') {
        // Update App state
        App.state.comments = data.comments;
        App.state.clusters = data.clusters;
        App.state.summary = data.summary;
        App.state.explainability = data.explainability;

        // Render updated components with newly injected comment IDs
        App.render(data.injected_ids || []);

        // Notification messages
        if (injectionType === 'spam_bot') {
          Components.showToast('🚨 Injected 1 high-risk Spam Bot account! Scored in real-time.', 'danger');
        } else if (injectionType === 'coordinated_campaign') {
          Components.showToast(`⚡ Injected 5 coordinated bots! Campaign Detector updated (${data.clusters.length} active rings).`, 'danger');
        } else if (injectionType === 'sleeper_account') {
          Components.showToast('🕵️ Injected 1 Sleeper Account! Dormant account signature flagged.', 'warning');
        }

        // Scroll to top of table to see injected items
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
          tableContainer.scrollTop = 0;
        }
      }
    } catch (err) {
      console.error('Injection failed:', err);
      Components.showToast(`Injection failed: ${err.message}`, 'warning');
    } finally {
      this.isInjecting = false;
      if (btn && originalText) {
        btn.innerHTML = originalText;
        btn.style.opacity = '1';
      }
    }
  },

  /**
   * Resets feed back to the original baseline preset.
   */
  resetFeed() {
    App.analyze();
    Components.showToast('Feed reset to clean preset baseline.', 'info');
  }
};
