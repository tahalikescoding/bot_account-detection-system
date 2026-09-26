/**
 * CommentGuard AI - Main Application Controller
 * Handles application lifecycle, API calls, filtering, sorting, drawer, and export.
 */

const App = {
  state: {
    video: null,
    comments: [],
    clusters: [],
    summary: {},
    explainability: {},
    activeFilter: 'all',
    activeClusterId: null,
    searchQuery: '',
    sortBy: 'score_desc',
    activePreset: 'crypto_attack',
    apiKey: localStorage.getItem('commentguard_yt_api_key') || '',
    isAnalyzing: false
  },

  /**
   * Initializes the application upon DOM load.
   */
  init() {
    this.bindEvents();
    // Pre-fill API key input if stored in localStorage
    const keyInput = document.getElementById("yt-api-key-input");
    if (keyInput && this.state.apiKey) {
      keyInput.value = this.state.apiKey;
    }
    // Run initial analysis with default preset
    this.analyze();
  },

  /**
   * Binds UI event listeners.
   */
  bindEvents() {
    // Analyze Form Submission
    const analyzeBtn = document.getElementById("btn-analyze");
    if (analyzeBtn) {
      analyzeBtn.addEventListener("click", () => this.analyze());
    }

    const urlInput = document.getElementById("yt-url-input");
    if (urlInput) {
      urlInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.analyze();
        }
      });
    }

    // Presets Click Handler
    document.querySelectorAll(".preset-chip").forEach(chip => {
      chip.addEventListener("click", (e) => {
        const preset = chip.getAttribute("data-preset");
        this.selectPreset(preset);
      });
    });

    // API Key Toggle & Save
    const toggleKeyBtn = document.getElementById("btn-toggle-api-key");
    const keyDrawer = document.getElementById("api-key-drawer");
    if (toggleKeyBtn && keyDrawer) {
      toggleKeyBtn.addEventListener("click", () => {
        keyDrawer.classList.toggle("open");
      });
    }

    const saveKeyBtn = document.getElementById("btn-save-api-key");
    const keyInput = document.getElementById("yt-api-key-input");
    if (saveKeyBtn && keyInput) {
      saveKeyBtn.addEventListener("click", () => {
        this.state.apiKey = keyInput.value.trim();
        localStorage.setItem('commentguard_yt_api_key', this.state.apiKey);
        Components.showToast('YouTube API Key saved in local storage.', 'success');
        keyDrawer.classList.remove("open");
      });
    }

    // Filter Buttons
    document.querySelectorAll(".filter-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.state.activeClusterId = null;
        this.state.activeFilter = btn.getAttribute("data-filter");
        this.renderTable();
      });
    });

    // Search Input
    const searchInput = document.getElementById("feed-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.state.searchQuery = e.target.value.toLowerCase().trim();
        this.renderTable();
      });
    }

    // Sort Dropdown
    const sortSelect = document.getElementById("feed-sort-select");
    if (sortSelect) {
      sortSelect.addEventListener("change", (e) => {
        this.state.sortBy = e.target.value;
        this.renderTable();
      });
    }

    // Drawer Backdrop & Close
    const backdrop = document.getElementById("drawer-backdrop");
    const closeBtn = document.getElementById("drawer-close-btn");
    if (backdrop) backdrop.addEventListener("click", () => this.closeInspector());
    if (closeBtn) closeBtn.addEventListener("click", () => this.closeInspector());
  },

  /**
   * Switches active preset and triggers analysis.
   */
  selectPreset(presetName) {
    this.state.activePreset = presetName;
    document.querySelectorAll(".preset-chip").forEach(c => {
      c.classList.toggle("active", c.getAttribute("data-preset") === presetName);
    });

    // Clear URL input when clicking preset chip so preset takes priority
    const urlInput = document.getElementById("yt-url-input");
    if (urlInput) urlInput.value = "";

    this.analyze();
  },

  /**
   * Calls /api/analyze to analyze comments for URL or preset.
   */
  async analyze() {
    if (this.state.isAnalyzing) return;
    this.state.isAnalyzing = true;

    const urlInput = document.getElementById("yt-url-input");
    const url = urlInput ? urlInput.value.trim() : "";
    const analyzeBtn = document.getElementById("btn-analyze");

    const urlPasted = url && url.length > 0;
    let origBtnText = "";
    if (analyzeBtn) {
      origBtnText = analyzeBtn.innerHTML;
      analyzeBtn.innerHTML = `
        <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
          <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
          <path d="M12 2a10 10 0 0 1 10 10"></path>
        </svg>
        ${urlPasted ? 'Fetching all comments… (may take ~15s)' : 'Loading...'}
      `;
      analyzeBtn.disabled = true;
    }

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url,
          api_key: this.state.apiKey,
          preset: this.state.activePreset,
          max_comments: 0   // 0 = fetch ALL (up to 2000 ceiling)
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed with status ${response.status}`);
      }

      const data = await response.json();

      if (data.status === 'success') {
        this.state.video = data.video;
        this.state.comments = data.comments;
        this.state.clusters = data.clusters;
        this.state.summary = data.summary;
        this.state.explainability = data.explainability;
        this.state.activeClusterId = null;

        // Render all UI components
        this.renderVideoMeta(data.video, data.data_source, data.source_notice, data.analysis_note);;
        this.render();

        Components.showToast(`Analyzed ${data.comments.length} comments successfully!`, 'success');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      Components.showToast(`Analysis error: ${err.message}`, 'warning');
    } finally {
      this.state.isAnalyzing = false;
      if (analyzeBtn) {
        analyzeBtn.innerHTML = origBtnText;
        analyzeBtn.disabled = false;
      }
    }
  },

  /**
   * Updates the video metadata bar.
   */
  renderVideoMeta(video, dataSource, notice, analysisNote) {
    if (!video) return;

    const thumbEl = document.getElementById("video-meta-thumb");
    const titleEl = document.getElementById("video-meta-title");
    const channelEl = document.getElementById("video-meta-channel");
    const sourceEl = document.getElementById("video-data-source");

    if (thumbEl) thumbEl.src = video.thumbnail || 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=640&q=80';
    if (titleEl) titleEl.textContent = video.title || 'Target Video';
    if (channelEl) {
      channelEl.innerHTML = `
        <span>Channel: <strong>${Components.escapeHTML(video.channel_title || 'Unknown')}</strong></span>
        <span>•</span>
        <span>Views: <strong>${video.view_count || 'N/A'}</strong></span>
        <span>•</span>
        <span>Likes: <strong>${video.like_count || 'N/A'}</strong></span>
      `;
    }

    if (sourceEl) {
      if (dataSource === 'live_youtube_api') {
        sourceEl.innerHTML = `🟢 Live — YouTube Data API v3`;
        sourceEl.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        sourceEl.style.color = '#34d399';
      } else if (dataSource === 'live_scrape') {
        sourceEl.innerHTML = `🟢 Live — Real Comments Scraped`;
        sourceEl.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        sourceEl.style.color = '#34d399';
      } else {
        sourceEl.innerHTML = `🟡 Demo Dataset (paste a real URL to scan live)`;
        sourceEl.style.borderColor = 'rgba(245, 158, 11, 0.4)';
        sourceEl.style.color = '#fbbf24';
      }
      if (notice) sourceEl.title = notice;

      if (analysisNote) {
        sourceEl.innerHTML += ` <span style="opacity:0.8; font-weight:400;">⚠️ ${Components.escapeHTML(analysisNote)}</span>`;
      }
    }

    /**
     * Main render trigger for all dashboard parts.
     */
    render(newlyInjectedIds = []) {
      Components.renderSummaryStats(this.state.summary);
      this.renderTable(newlyInjectedIds);
      Components.renderClusters(this.state.clusters);
      Explainability.render(this.state.explainability);
    },

    /**
     * Filters, sorts, and renders the comment feed table.
     */
    renderTable(newlyInjectedIds = []) {
      const tbody = document.getElementById("comment-feed-tbody");
      const countEl = document.getElementById("feed-visible-count");
      if (!tbody) return;

      let filtered = [...this.state.comments];

      // Filter by cluster if active
      if (this.state.activeClusterId) {
        const cluster = this.state.clusters.find(c => c.cluster_id === this.state.activeClusterId);
        if (cluster) {
          const idSet = new Set(cluster.member_comment_ids);
          filtered = filtered.filter(c => idSet.has(c.comment_id));
        }
      } else {
        // Filter by verdict category
        if (this.state.activeFilter === 'bot') {
          filtered = filtered.filter(c => c.verdict_class === 'bot');
        } else if (this.state.activeFilter === 'suspicious') {
          filtered = filtered.filter(c => c.verdict_class === 'suspicious');
        } else if (this.state.activeFilter === 'human') {
          filtered = filtered.filter(c => c.verdict_class === 'human');
        } else if (this.state.activeFilter === 'campaign') {
          filtered = filtered.filter(c => c.is_in_campaign);
        }
      }

      // Filter by Search Query
      if (this.state.searchQuery) {
        const q = this.state.searchQuery;
        filtered = filtered.filter(c =>
          (c.author_name && c.author_name.toLowerCase().includes(q)) ||
          (c.author_handle && c.author_handle.toLowerCase().includes(q)) ||
          (c.comment_text && c.comment_text.toLowerCase().includes(q))
        );
      }

      // Sort Comments
      if (this.state.sortBy === 'score_desc') {
        filtered.sort((a, b) => b.bot_score - a.bot_score);
      } else if (this.state.sortBy === 'score_asc') {
        filtered.sort((a, b) => a.bot_score - b.bot_score);
      } else if (this.state.sortBy === 'time_asc') {
        filtered.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
      } else if (this.state.sortBy === 'burst_fastest') {
        filtered.sort((a, b) => (a.seconds_after_upload ?? 999999) - (b.seconds_after_upload ?? 999999));
      }

      if (countEl) {
        countEl.textContent = `${filtered.length} visible (${this.state.comments.length} total)`;
      }

      if (filtered.length === 0) {
        tbody.innerHTML = `
        <tr>
          <td colspan="7" class="table-empty">
            No comments match current filter criteria.
          </td>
        </tr>
      `;
        return;
      }

      const injectedSet = new Set(newlyInjectedIds);
      tbody.innerHTML = filtered.map(c =>
        Components.renderCommentRow(c, injectedSet.has(c.comment_id))
      ).join('');
    },

    /**
     * Filters comment feed to highlight a specific coordinated campaign cluster.
     */
    filterByCluster(clusterId) {
      this.state.activeClusterId = clusterId;
      // Highlight active cluster card
      document.querySelectorAll(".cluster-item").forEach(card => {
        card.style.borderColor = card.id === `cluster-card-${clusterId}` ? 'var(--accent-purple)' : 'var(--border-subtle)';
      });

      this.renderTable();
      Components.showToast(`Filtered feed to cluster: ${clusterId.toUpperCase()}`, 'info');

      // Scroll to table smoothly
      const tableEl = document.querySelector(".feed-panel");
      if (tableEl) {
        tableEl.scrollIntoView({ behavior: 'smooth' });
      }
    },

    /**
     * Opens the slide-over inspector for a specific comment.
     */
    openInspector(commentId) {
      const comment = this.state.comments.find(c => c.comment_id === commentId);
      if (!comment) return;

      Components.renderInspector(comment);

      const drawer = document.getElementById("inspector-drawer");
      const backdrop = document.getElementById("drawer-backdrop");
      if (drawer) drawer.classList.add("open");
      if (backdrop) backdrop.classList.add("open");
    },

    /**
     * Closes the inspector drawer.
     */
    closeInspector() {
      const drawer = document.getElementById("inspector-drawer");
      const backdrop = document.getElementById("drawer-backdrop");
      if (drawer) drawer.classList.remove("open");
      if (backdrop) backdrop.classList.remove("open");
    },

    /**
     * Copies channel ID to clipboard.
     */
    copyChannelId(channelId) {
      if (!channelId || channelId === 'N/A') {
        Components.showToast('No channel ID available for this account.', 'warning');
        return;
      }
      navigator.clipboard.writeText(channelId).then(() => {
        Components.showToast(`Copied Channel ID ${channelId} to clipboard!`, 'success');
      }).catch(() => {
        Components.showToast('Failed to copy to clipboard.', 'warning');
      });
    },

    /**
     * Simulates moderation action (shadowban / flag).
     */
    simulateModeration(commentId) {
      const idx = this.state.comments.findIndex(c => c.comment_id === commentId);
      if (idx !== -1) {
        const author = this.state.comments[idx].author_name;
        Components.showToast(`Account "${author}" flagged for YouTube Studio moderation!`, 'danger');
        this.closeInspector();
      }
    },

    /**
     * Exports flagged bot accounts to a JSON or CSV file download.
     */
    exportReport(format = 'json') {
      const flagged = this.state.comments.filter(c => c.bot_score > 30);
      if (flagged.length === 0) {
        Components.showToast('No flagged bot accounts to export.', 'warning');
        return;
      }

      let fileContent = '';
      let mimeType = 'text/plain';
      let fileName = `CommentGuard_Bot_Report_${new Date().toISOString().slice(0, 10)}`;

      if (format === 'json') {
        mimeType = 'application/json';
        fileName += '.json';
        fileContent = JSON.stringify({
          exported_at: new Date().toISOString(),
          video: this.state.video,
          summary: this.state.summary,
          clusters: this.state.clusters,
          flagged_accounts: flagged
        }, null, 2);
      } else {
        mimeType = 'text/csv';
        fileName += '.csv';
        const headers = ['Comment_ID', 'Author_Name', 'Handle', 'Channel_ID', 'Bot_Score', 'Verdict', 'In_Campaign', 'Comment_Text', 'Reasons'];
        const rows = flagged.map(c => [
          `"${c.comment_id}"`,
          `"${(c.author_name || '').replace(/"/g, '""')}"`,
          `"${(c.author_handle || '').replace(/"/g, '""')}"`,
          `"${c.author_channel_id || ''}"`,
          c.bot_score,
          `"${c.verdict}"`,
          c.is_in_campaign ? 'YES' : 'NO',
          `"${(c.comment_text || '').replace(/"/g, '""')}"`,
          `"${(c.reasons || []).join('; ').replace(/"/g, '""')}"`
        ]);
        fileContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      }

      const blob = new Blob([fileContent], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      Components.showToast(`Exported ${flagged.length} accounts as ${format.toUpperCase()}`, 'success');
    }
  };

  // Auto-run on DOM ready
  document.addEventListener("DOMContentLoaded", () => {
    App.init();
  });
