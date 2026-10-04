import React, { useState, useEffect } from 'react';
import { feedbackApi } from '../api/api';
import FeedbackCard from '../components/FeedbackCard';

export default function Feedback() {
  const [inputText, setInputText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Filters
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [priority, setPriority] = useState('');

  // Load feedbacks on mount and when filters change
  const loadFeedbacks = async () => {
    try {
      setLoading(true);
      const data = await feedbackApi.getAll({
        search,
        category,
        sentiment,
        priority,
      });
      setFeedbacks(data);
    } catch (err) {
      setError('Failed to load feedback history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeedbacks();
  }, [category, sentiment, priority]);

  // Debounced or on-demand search
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadFeedbacks();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!inputText.trim()) {
      setError('Please enter feedback text to analyze.');
      return;
    }

    try {
      setAnalyzing(true);
      const newFeedback = await feedbackApi.create(inputText.trim());
      setLatestResult(newFeedback);
      setFeedbacks((prev) => [newFeedback, ...prev]);
      setInputText('');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to analyze feedback.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this feedback?')) return;
    try {
      await feedbackApi.delete(id);
      setFeedbacks((prev) => prev.filter((item) => item.id !== id));
      if (latestResult && latestResult.id === id) {
        setLatestResult(null);
      }
    } catch (err) {
      alert('Failed to delete feedback.');
    }
  };

  return (
    <div style={styles.container}>
      {/* 1. Input Section */}
      <section style={styles.section}>
        <div style={styles.header}>
          <h2 style={styles.title}>Customer Feedback Analysis</h2>
          <p style={styles.subtitle}>
            Enter raw customer feedback to instantly extract sentiment, category, priority, and summary.
          </p>
        </div>

        {error && <div style={styles.errorAlert}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <textarea
            rows="4"
            placeholder="Paste or type customer feedback here... e.g. 'I was charged twice for my subscription this month and customer support hasn't replied!'"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={analyzing}
            style={styles.textarea}
          />

          <div style={styles.actionRow}>
            <button
              type="submit"
              disabled={analyzing || !inputText.trim()}
              style={{
                ...styles.analyzeBtn,
                opacity: analyzing || !inputText.trim() ? 0.7 : 1,
              }}
            >
              {analyzing ? 'Analyzing with AI...' : 'Analyze Feedback'}
            </button>
          </div>
        </form>

        {/* 2. Latest AI Result Banner */}
        {latestResult && (
          <div style={styles.resultBanner}>
            <div style={styles.resultHeader}>
              <span style={styles.resultTag}>Latest AI Analysis Result</span>
              <button onClick={() => setLatestResult(null)} style={styles.dismissBtn}>
                Dismiss
              </button>
            </div>
            <FeedbackCard item={latestResult} />
          </div>
        )}
      </section>

      {/* 3. Filter & History Section */}
      <section style={styles.section}>
        <div style={styles.historyHeader}>
          <h3 style={styles.historyTitle}>
            Feedback History ({feedbacks.length})
          </h3>

          {/* Search bar */}
          <form onSubmit={handleSearchSubmit} style={styles.searchForm}>
            <input
              type="text"
              placeholder="Search feedback text..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={styles.searchInput}
            />
            <button type="submit" style={styles.searchBtn}>Search</button>
          </form>
        </div>

        {/* Filter Dropdowns */}
        <div style={styles.filterRow}>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={styles.select}
          >
            <option value="">All Categories</option>
            <option value="Payment/Transaction">Payment/Transaction</option>
            <option value="Product">Product</option>
            <option value="Support">Support</option>
            <option value="Account">Account</option>
            <option value="Delivery">Delivery</option>
            <option value="Bug">Bug</option>
            <option value="Other">Other</option>
          </select>

          <select
            value={sentiment}
            onChange={(e) => setSentiment(e.target.value)}
            style={styles.select}
          >
            <option value="">All Sentiments</option>
            <option value="Positive">Positive</option>
            <option value="Neutral">Neutral</option>
            <option value="Negative">Negative</option>
          </select>

          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            style={styles.select}
          >
            <option value="">All Priorities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>

          {(category || sentiment || priority || search) && (
            <button
              onClick={() => {
                setCategory('');
                setSentiment('');
                setPriority('');
                setSearch('');
              }}
              style={styles.clearBtn}
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Feedback List */}
        {loading ? (
          <div style={styles.emptyState}>Loading feedback...</div>
        ) : feedbacks.length === 0 ? (
          <div style={styles.emptyState}>
            No feedback found matching your criteria. Submit a new item above!
          </div>
        ) : (
          <div style={styles.feedList}>
            {feedbacks.map((item) => (
              <FeedbackCard
                key={item.id}
                item={item}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '2rem 1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
  },
  section: {
    background: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    padding: '1.75rem',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.04)',
  },
  header: {
    marginBottom: '1.25rem',
  },
  title: {
    fontSize: '1.35rem',
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: '0.25rem',
  },
  subtitle: {
    fontSize: '0.9rem',
    color: '#64748b',
  },
  errorAlert: {
    background: '#fef2f2',
    color: '#b91c1c',
    border: '1px solid #fecaca',
    padding: '0.75rem 1rem',
    borderRadius: '6px',
    fontSize: '0.875rem',
    marginBottom: '1rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  textarea: {
    width: '100%',
    padding: '0.85rem',
    borderRadius: '8px',
    border: '1px solid #cbd5e1',
    resize: 'vertical',
    fontSize: '0.95rem',
    lineHeight: '1.5',
    outline: 'none',
  },
  actionRow: {
    display: 'flex',
    justifyContent: 'flex-end',
  },
  analyzeBtn: {
    background: '#4f46e5',
    color: '#ffffff',
    padding: '0.65rem 1.5rem',
    borderRadius: '6px',
    border: 'none',
    fontWeight: '600',
    fontSize: '0.95rem',
  },
  resultBanner: {
    marginTop: '1.5rem',
    paddingTop: '1.25rem',
    borderTop: '1px dashed #cbd5e1',
  },
  resultHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.75rem',
  },
  resultTag: {
    fontSize: '0.85rem',
    fontWeight: '700',
    color: '#4338ca',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  dismissBtn: {
    background: 'none',
    border: 'none',
    color: '#64748b',
    fontSize: '0.85rem',
    cursor: 'pointer',
  },
  historyHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '1rem',
    marginBottom: '1.25rem',
  },
  historyTitle: {
    fontSize: '1.2rem',
    fontWeight: '700',
    color: '#0f172a',
  },
  searchForm: {
    display: 'flex',
    gap: '0.5rem',
  },
  searchInput: {
    padding: '0.45rem 0.75rem',
    borderRadius: '6px',
    border: '1px solid #cbd5e1',
    fontSize: '0.875rem',
    minWidth: '220px',
  },
  searchBtn: {
    background: '#f1f5f9',
    border: '1px solid #cbd5e1',
    padding: '0.45rem 0.85rem',
    borderRadius: '6px',
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  filterRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.75rem',
    marginBottom: '1.25rem',
  },
  select: {
    padding: '0.45rem 0.75rem',
    borderRadius: '6px',
    border: '1px solid #cbd5e1',
    background: '#ffffff',
    fontSize: '0.875rem',
    color: '#334155',
  },
  clearBtn: {
    background: 'none',
    border: 'none',
    color: '#4f46e5',
    fontSize: '0.875rem',
    cursor: 'pointer',
    fontWeight: '500',
    padding: '0.45rem',
  },
  feedList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  emptyState: {
    textAlign: 'center',
    padding: '2.5rem 1rem',
    color: '#94a3b8',
    fontSize: '0.95rem',
    background: '#f8fafc',
    borderRadius: '8px',
  }
};
