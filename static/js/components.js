/**
 * CommentGuard AI - UI Rendering Components
 * Handles table rows, stat cards, campaign clusters, drawer inspector, and toasts.
 */

const Components = {
  /**
   * Escapes HTML to prevent XSS.
   */
  escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  /**
   * Highlights spam links and suspicious keywords in comment text.
   */
  highlightComment(text) {
    if (!text) return '';
    let escaped = this.escapeHTML(text);

    // Highlight links
    const linkRegex = /(https?:\/\/[^\s]+|bit\.ly\/[^\s]+|t\.me\/[^\s]+|wa\.me\/[^\s]+|tinyurl\.com\/[^\s]+|[a-zA-Z0-9-]+\.(?:com|xyz|top)\/[^\s]*)/gi;
    escaped = escaped.replace(linkRegex, '<span class="highlight-spam">$1</span>');

    // Highlight high-risk keywords
    const keywords = [
      "telegram", "whatsapp", "crypto", "giveaway", "free gift card",
      "won an iphone", "passive income", "sub 4 sub", "check my channel",
      "recover", "airdrop"
    ];
    keywords.forEach(kw => {
      const regex = new RegExp(`(${kw})`, 'gi');
      escaped = escaped.replace(regex, '<span class="highlight-keyword">$1</span>');
    });

    return escaped;
  },

  /**
   * Formats relative timestamp or publication delta.
   */
  formatTiming(comment) {
    const secs = comment.seconds_after_upload;
    let deltaHtml = '';
    if (secs !== null && secs !== undefined) {
      if (secs <= 15) {
        deltaHtml = `<div class="timing-offset-chip" title="Instant bot burst timing">⚡ +${secs}s after upload</div>`;
      } else if (secs <= 60) {
        deltaHtml = `<div class="timing-offset-chip" title="Posted within 1 minute of video upload">+${secs}s after upload</div>`;
      } else if (secs < 3600) {
        deltaHtml = `<span style="font-size:0.75rem; color:#64748b;">+${Math.round(secs/60)}m after upload</span>`;
      }
    }

    // Relative date formatting
    let relText = "Recently";
    if (comment.published_at) {
      try {
        const d = new Date(comment.published_at);
        relText = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch (e) {}
    }

    return `
      <div class="timing-relative">${relText}</div>
      ${deltaHtml}
    `;
  },

  /**
   * Renders signal pills for a comment.
   */
  renderSignalPills(signals) {
    if (!signals || signals.length === 0) {
      return '<span style="color:#64748b; font-size:0.75rem;">None</span>';
    }
    return signals.slice(0, 3).map(s => {
      const cls = s.severity === 'high' ? 'high' : (s.severity === 'medium' ? 'medium' : '');
      return `<span class="signal-pill ${cls}" title="${this.escapeHTML(s.reason)}">${this.escapeHTML(s.signal)}</span>`;
    }).join('');
  },

  /**
   * Renders a single table row for a comment.
   */
  renderCommentRow(comment, isNewlyInjected = false) {
    const rowRiskClass = `row-${comment.verdict_class}`;
    const badgeRiskClass = `badge-${comment.verdict_class}`;
    const injectClass = isNewlyInjected ? 'newly-injected' : '';
    const campaignClass = comment.is_in_campaign ? 'in-campaign-row' : '';

    const avatarUrl = comment.author_avatar || 'https://www.gstatic.com/youtube/img/creator/avatar/default_avatar.svg';

    return `
      <tr class="feed-row ${rowRiskClass} ${injectClass} ${campaignClass}" id="row-${comment.comment_id}" data-id="${comment.comment_id}">
        <td>
          <div class="author-cell">
            <img class="author-avatar" src="${avatarUrl}" alt="Avatar" onerror="this.src='https://www.gstatic.com/youtube/img/creator/avatar/default_avatar.svg'" />
            <div class="author-info">
              <span class="author-name" title="${this.escapeHTML(comment.author_name)}">${this.escapeHTML(comment.author_name)}</span>
              <span class="author-handle">${this.escapeHTML(comment.author_handle || '@unknown')}</span>
            </div>
          </div>
        </td>
        <td class="comment-cell">
          <div class="comment-text-preview" title="${this.escapeHTML(comment.comment_text)}">
            ${this.highlightComment(comment.comment_text)}
          </div>
        </td>
        <td class="timing-cell">
          ${this.formatTiming(comment)}
        </td>
        <td>
          <div class="signals-cell">
            ${this.renderSignalPills(comment.signals)}
          </div>
        </td>
        <td class="score-cell">
          <div class="score-display">
            <span style="color: ${comment.verdict_color}">${comment.bot_score}</span>
            <div class="score-bar-mini">
              <div class="score-bar-fill" style="width: ${comment.bot_score}%; background: ${comment.verdict_color};"></div>
            </div>
          </div>
        </td>
        <td>
          <span class="badge ${badgeRiskClass}">
            ${comment.verdict}
          </span>
          ${comment.is_in_campaign ? '<span class="badge badge-campaign" style="margin-left: 0.35rem;" title="Part of coordinated cluster">CAMPAIGN</span>' : ''}
        </td>
        <td>
          <button class="inspect-btn" onclick="App.openInspector('${comment.comment_id}')">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            Inspect
          </button>
        </td>
      </tr>
    `;
  },

  /**
   * Renders the summary stats cards at the top.
   */
  renderSummaryStats(summary) {
    const totalEl = document.getElementById("stat-total-comments");
    const botsEl = document.getElementById("stat-likely-bots");
    const botsPctEl = document.getElementById("stat-bots-pct");
    const campaignEl = document.getElementById("stat-campaign-accounts");
    const avgScoreEl = document.getElementById("stat-avg-score");
    const avgBarEl = document.getElementById("stat-avg-bar");

    if (totalEl) totalEl.textContent = summary.total_comments;
    if (botsEl) botsEl.textContent = summary.likely_bots_count;
    if (botsPctEl) botsPctEl.textContent = `${summary.likely_bots_percentage}%`;
    if (campaignEl) campaignEl.textContent = summary.coordinated_accounts_count || 0;
    if (avgScoreEl) avgScoreEl.textContent = `${summary.avg_bot_score} / 100`;

    if (avgBarEl) {
      avgBarEl.style.width = `${summary.avg_bot_score}%`;
      if (summary.avg_bot_score >= 60) {
        avgBarEl.style.background = 'var(--danger-red)';
      } else if (summary.avg_bot_score >= 30) {
        avgBarEl.style.background = 'var(--warning-amber)';
      } else {
        avgBarEl.style.background = 'var(--safe-green)';
      }
    }
  },

  /**
   * Renders the Campaign Detector clusters in the right sidebar.
   */
  renderClusters(clusters) {
    const container = document.getElementById("campaign-clusters-container");
    const countBadge = document.getElementById("campaign-clusters-count");
    if (!container) return;

    if (countBadge) {
      countBadge.textContent = `${clusters.length} Active`;
    }

    if (!clusters || clusters.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 1.5rem; color:#64748b; font-size:0.8rem;">
          No coordinated clusters detected in current batch.
        </div>
      `;
      return;
    }

    container.innerHTML = clusters.map(cl => {
      const traitsHtml = (cl.shared_traits || []).map(t => 
        `<span class="signal-pill high" style="margin-right:0.25rem;">${this.escapeHTML(t)}</span>`
      ).join('');

      return `
        <div class="cluster-item" id="cluster-card-${cl.cluster_id}">
          <div class="cluster-item-header">
            <span class="cluster-name">${this.escapeHTML(cl.name)}</span>
            <span class="cluster-size-badge">${cl.account_count} accounts</span>
          </div>
          <div class="cluster-quote">"${this.escapeHTML(cl.sample_text)}"</div>
          <div style="margin: 0.4rem 0;">${traitsHtml}</div>
          <div class="cluster-meta-row">
            <span class="cluster-timespan">⏱️ Burst: ${cl.time_span_display}</span>
            <button class="btn-inspect-cluster" onclick="App.filterByCluster('${cl.cluster_id}')">
              Inspect Cluster
            </button>
          </div>
        </div>
      `;
    }).join('');
  },

  /**
   * Renders the Inspector Side Drawer for a specific comment.
   */
  renderInspector(comment) {
    const contentEl = document.getElementById("inspector-content");
    if (!contentEl || !comment) return;

    const reasonsHtml = (comment.signals || []).map(s => {
      const cls = s.severity === 'high' ? 'high' : (s.severity === 'medium' ? 'medium' : 'low');
      return `
        <div class="reason-item ${cls}">
          <span><strong>${this.escapeHTML(s.signal)}:</strong> ${this.escapeHTML(s.reason)}</span>
          <span class="badge" style="background: rgba(0,0,0,0.3);">${s.points} pts</span>
        </div>
      `;
    }).join('');

    let dupHtml = '';
    if (comment.duplicate_matches && comment.duplicate_matches.length > 0) {
      dupHtml = `
        <div style="padding: 0.85rem; background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 8px;">
          <div style="font-weight: 700; color: #c4b5fd; font-size: 0.8rem; margin-bottom: 0.4rem;">
            ⚠️ Sybil / Duplicate Copy-Paste Matches (${comment.duplicate_matches.length})
          </div>
          <div style="font-size: 0.75rem; color: #cbd5e1;">
            This text matches comments from: ${comment.duplicate_matches.map(m => `<code>${this.escapeHTML(m.author)}</code> (${Math.round(m.sim*100)}%)`).join(', ')}
          </div>
        </div>
      `;
    }

    contentEl.innerHTML = `
      <!-- Account Identity Hero -->
      <div class="account-hero-card">
        <img class="account-hero-avatar" src="${comment.author_avatar}" alt="Avatar" onerror="this.src='https://www.gstatic.com/youtube/img/creator/avatar/default_avatar.svg'" />
        <div class="account-hero-meta">
          <div class="account-hero-name">${this.escapeHTML(comment.author_name)}</div>
          <div class="account-hero-handle">${this.escapeHTML(comment.author_handle)}</div>
          <div class="account-hero-channel">ID: ${this.escapeHTML(comment.author_channel_id || 'N/A')}</div>
        </div>
      </div>

      <!-- Score Gauge Section -->
      <div class="drawer-score-section">
        <div class="gauge-wrapper">
          <div class="gauge-circle ${comment.verdict_class}">
            ${comment.bot_score}
          </div>
          <div>
            <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Bot Risk Assessment</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: ${comment.verdict_color};">${comment.verdict}</div>
          </div>
        </div>
        <div style="text-align: right; font-family: var(--font-mono); font-size: 0.75rem; color: #94a3b8;">
          <div>Age: ${comment.account_age_days !== null ? comment.account_age_days + 'd' : 'Unknown'}</div>
          <div>Timing: ${comment.seconds_after_upload !== null ? '+' + comment.seconds_after_upload + 's' : 'N/A'}</div>
        </div>
      </div>

      ${dupHtml}

      <!-- Signal Breakdown List -->
      <div>
        <div style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.5rem; color: #f8fafc;">
          Signal Breakdown & Scoring Rationale
        </div>
        <div class="reasons-list">
          ${reasonsHtml || '<div style="color:#64748b; font-size:0.8rem;">No malicious signals detected. Organic user.</div>'}
        </div>
      </div>

      <!-- Full Comment Box -->
      <div>
        <div style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.5rem; color: #f8fafc;">
          Raw Comment Text
        </div>
        <div class="drawer-comment-box">
          ${this.highlightComment(comment.comment_text)}
        </div>
      </div>

      <!-- Drawer Action Buttons -->
      <div class="drawer-footer-actions">
        <button class="btn btn-secondary" style="flex:1;" onclick="App.copyChannelId('${comment.author_channel_id}')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          Copy ID
        </button>
        <button class="btn btn-danger" style="flex:1;" onclick="App.simulateModeration('${comment.comment_id}')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>
          Flag Account
        </button>
      </div>
    `;
  },

  /**
   * Displays temporary toast notification.
   */
  showToast(message, type = 'info') {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = "toast";
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'danger') icon = '🚨';
    if (type === 'warning') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${this.escapeHTML(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }
};
