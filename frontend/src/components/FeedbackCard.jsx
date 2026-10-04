import React from 'react';

export default function FeedbackCard({ item, onDelete }) {
  const getSentimentStyle = (sentiment) => {
    switch (sentiment) {
      case 'Positive':
        return { bg: '#dcfce7', text: '#15803d', border: '#bbf7d0' };
      case 'Negative':
        return { bg: '#fee2e2', text: '#b91c1c', border: '#fecaca' };
      default:
        return { bg: '#f1f5f9', text: '#475569', border: '#e2e8f0' };
    }
  };

  const getPriorityStyle = (priority) => {
    switch (priority) {
      case 'Critical':
        return { bg: '#fef2f2', text: '#dc2626', border: '#fca5a5' };
      case 'High':
        return { bg: '#fff7ed', text: '#c2410c', border: '#fed7aa' };
      case 'Medium':
        return { bg: '#fefce8', text: '#a16207', border: '#fef08a' };
      default:
        return { bg: '#f8fafc', text: '#64748b', border: '#e2e8f0' };
    }
  };

  const sentimentStyle = getSentimentStyle(item.sentiment);
  const priorityStyle = getPriorityStyle(item.priority);

  const formattedDate = item.createdAt
    ? new Date(item.createdAt).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '';

  return (
    <div style={styles.card}>
      <div style={styles.cardHeader}>
        <div style={styles.badgeGroup}>
          {item.category && (
            <span style={styles.categoryBadge}>{item.category}</span>
          )}
          {item.sentiment && (
            <span
              style={{
                ...styles.badge,
                backgroundColor: sentimentStyle.bg,
                color: sentimentStyle.text,
                borderColor: sentimentStyle.border,
              }}
            >
              {item.sentiment}
            </span>
          )}
          {item.priority && (
            <span
              style={{
                ...styles.badge,
                backgroundColor: priorityStyle.bg,
                color: priorityStyle.text,
                borderColor: priorityStyle.border,
              }}
            >
              {item.priority} Priority
            </span>
          )}
        </div>

        {onDelete && (
          <button
            onClick={() => onDelete(item.id)}
            style={styles.deleteBtn}
            title="Delete feedback"
          >
            ✕
          </button>
        )}
      </div>

      <p style={styles.text}>{item.text}</p>

      {item.summary && (
        <div style={styles.summaryBox}>
          <span style={styles.summaryLabel}>AI Summary:</span> {item.summary}
        </div>
      )}

      {formattedDate && (
        <div style={styles.date}>{formattedDate}</div>
      )}
    </div>
  );
}

const styles = {
  card: {
    background: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '1.25rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  badgeGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.4rem',
  },
  categoryBadge: {
    background: '#e0e7ff',
    color: '#3730a3',
    padding: '0.2rem 0.6rem',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: '600',
  },
  badge: {
    padding: '0.2rem 0.6rem',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: '600',
    border: '1px solid',
  },
  deleteBtn: {
    background: 'none',
    border: 'none',
    color: '#94a3b8',
    fontSize: '1rem',
    padding: '0.1rem 0.4rem',
    cursor: 'pointer',
    borderRadius: '4px',
  },
  text: {
    color: '#1e293b',
    fontSize: '0.95rem',
    lineHeight: '1.5',
    whiteSpace: 'pre-wrap',
  },
  summaryBox: {
    background: '#f8fafc',
    borderLeft: '3px solid #6366f1',
    padding: '0.6rem 0.85rem',
    borderRadius: '0 6px 6px 0',
    fontSize: '0.85rem',
    color: '#334155',
  },
  summaryLabel: {
    fontWeight: '600',
    color: '#4f46e5',
  },
  date: {
    fontSize: '0.75rem',
    color: '#94a3b8',
    alignSelf: 'flex-end',
  }
};
