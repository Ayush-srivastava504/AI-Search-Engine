import React, { useState, useEffect } from 'react';
import { Search, Zap, Calendar, Heart, MessageCircle, Eye, TrendingUp, Loader } from 'lucide-react';

export default function SearchEngine() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [trending, setTrending] = useState([]);
  const [sortBy, setSortBy] = useState('relevance');
  const [topK, setTopK] = useState(10);
  const [executionTime, setExecutionTime] = useState(0);

  useEffect(() => {
    fetchTrending();
  }, []);

  const fetchTrending = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/trending');
      const data = await response.json();
      setTrending(data.trending_topics || []);
    } catch (error) {
      console.error('Error fetching trending:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: query,
        top_k: topK,
        sort_by: sortBy
      });
      const response = await fetch(`http://localhost:8000/api/search?${params}`);
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      setResults(data.results || []);
      setExecutionTime(data.execution_time_ms || 0);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTrendingClick = (topic) => {
    setQuery(topic);
    setTimeout(() => {
      document.querySelector('form')?.dispatchEvent(
        new Event('submit', { bubbles: true })
      );
    }, 0);
  };

  const getSourceColor = (source) => {
    const colors = {
      devto: 'bg-slate-700 text-white',
      medium: 'bg-slate-600 text-white',
      hackernews: 'bg-amber-600 text-white'
    };
    return colors[source] || 'bg-slate-500 text-white';
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', width: '100vw', margin: '0', padding: '0' }}>
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        html, body, #root {
          width: 100%;
          margin: 0;
          padding: 0;
          overflow-x: hidden;
        }
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
          background-color: #0f172a;
        }
        .search-input {
          width: 100%;
          padding: 14px 18px;
          font-size: 16px;
          border: 2px solid #1e293b;
          border-radius: 6px;
          background-color: #1e293b;
          color: #e2e8f0;
          outline: none;
          transition: border-color 0.2s;
        }
        .search-input:focus {
          border-color: #f59e0b;
        }
        .search-input::placeholder {
          color: #94a3b8;
        }
        .btn-search {
          padding: 14px 32px;
          background-color: #f59e0b;
          color: #0f172a;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          font-size: 15px;
          cursor: pointer;
          transition: background-color 0.2s;
          display: flex;
          align-items: center;
          gap: 8px;
          white-space: nowrap;
        }
        .btn-search:hover:not(:disabled) {
          background-color: #d97706;
        }
        .btn-search:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .result-card {
          display: block;
          padding: 24px;
          background-color: #1e293b;
          border: 1px solid #334155;
          border-radius: 8px;
          text-decoration: none;
          color: #e2e8f0;
          transition: all 0.2s;
          margin-bottom: 20px;
        }
        .result-card:hover {
          border-color: #f59e0b;
          background-color: #334155;
        }
        .result-title {
          font-size: 20px;
          font-weight: 700;
          color: #f1f5f9;
          margin-bottom: 10px;
          transition: color 0.2s;
        }
        .result-card:hover .result-title {
          color: #f59e0b;
        }
        .result-meta {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 16px;
          font-size: 14px;
          color: #cbd5e1;
          flex-wrap: wrap;
        }
        .result-snippet {
          color: #cbd5e1;
          line-height: 1.7;
          margin-bottom: 18px;
          font-size: 15px;
        }
        .result-stats {
          display: flex;
          gap: 28px;
          font-size: 14px;
          color: #94a3b8;
          flex-wrap: wrap;
        }
        .stat-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .score-badge {
          color: #f59e0b;
          font-weight: 600;
        }
        .select-filter {
          padding: 10px 14px;
          background-color: #1e293b;
          border: 1px solid #334155;
          border-radius: 5px;
          font-size: 14px;
          color: #e2e8f0;
          cursor: pointer;
          transition: border-color 0.2s;
        }
        .select-filter:focus {
          outline: none;
          border-color: #f59e0b;
        }
        .select-filter option {
          background-color: #1e293b;
          color: #e2e8f0;
        }
        .trending-badge {
          display: inline-block;
          padding: 8px 14px;
          background-color: #1e293b;
          border: 1px solid #334155;
          border-radius: 20px;
          color: #f59e0b;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          margin-bottom: 10px;
          margin-right: 10px;
        }
        .trending-badge:hover {
          background-color: #334155;
          border-color: #f59e0b;
        }
        .spinner {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
          .btn-search {
            padding: 12px 24px;
            font-size: 14px;
          }
          .result-title {
            font-size: 18px;
          }
          .result-stats {
            gap: 16px;
          }
          .result-meta {
            gap: 12px;
          }
        }
        
        @media (max-width: 480px) {
          .search-input {
            padding: 12px 14px;
            font-size: 16px;
          }
          .btn-search {
            padding: 12px 20px;
            font-size: 13px;
          }
          .result-card {
            padding: 16px;
            margin-bottom: 16px;
          }
          .result-title {
            font-size: 16px;
          }
          .result-snippet {
            font-size: 14px;
          }
          .trending-badge {
            padding: 6px 10px;
            font-size: 12px;
          }
        }
      `}</style>

      <div style={{ margin: '0 auto', maxWidth: '720px', padding: '48px 24px', width: '100%' }}>
        <div style={{ marginBottom: '56px' }}>
          <h1 style={{ fontSize: '44px', fontWeight: '800', color: '#f1f5f9', marginBottom: '8px', letterSpacing: '-0.02em' }}>
            TechSearch
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '16px' }}>
            AI-powered semantic search for developer blogs
          </p>
        </div>

        <form onSubmit={handleSearch} style={{ marginBottom: '48px' }}>
          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '200px', position: 'relative' }}>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search tech articles..."
                className="search-input"
              />
              <Search style={{ position: 'absolute', right: '18px', top: '14px', width: '20px', height: '20px', color: '#64748b', pointerEvents: 'none' }} />
            </div>
            <button type="submit" disabled={loading} className="btn-search">
              {loading ? (
                <Loader style={{ width: '20px', height: '20px' }} className="spinner" />
              ) : (
                <Zap style={{ width: '20px', height: '20px' }} />
              )}
              Search
            </button>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="select-filter">
              <option value="relevance">Most Relevant</option>
              <option value="recent">Most Recent</option>
              <option value="trending">Trending</option>
            </select>
            <select value={topK} onChange={(e) => setTopK(Number(e.target.value))} className="select-filter">
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
              <option value={50}>Top 50</option>
            </select>
            {executionTime > 0 && (
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>
                Found in {executionTime.toFixed(0)} ms
              </span>
            )}
          </div>
        </form>

        {trending.length > 0 && (
          <div style={{ marginBottom: '48px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <TrendingUp style={{ width: '22px', height: '22px', color: '#f59e0b' }} />
              <h2 style={{ fontSize: '17px', fontWeight: '700', color: '#f1f5f9' }}>
                Trending Topics
              </h2>
            </div>
            <div>
              {trending.slice(0, 8).map((topic, idx) => (
                <button key={idx} onClick={() => handleTrendingClick(topic)} className="trending-badge">
                  #{topic}
                </button>
              ))}
            </div>
          </div>
        )}

        <div>
          {results.length > 0 && (
            <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '24px', color: '#f1f5f9' }}>
              {results.length} Results
            </h2>
          )}
          {results.map((result) => (
            <a key={result.id} href={result.url} target="_blank" rel="noopener noreferrer" className="result-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px', marginBottom: '12px', flexWrap: 'wrap' }}>
                <h3 className="result-title">{result.title}</h3>
                <span className={getSourceColor(result.source)} style={{ padding: '6px 12px', borderRadius: '4px', fontSize: '12px', fontWeight: '600', whiteSpace: 'nowrap', flexShrink: 0 }}>
                  {result.source.toUpperCase()}
                </span>
              </div>
              <div className="result-meta">
                <span>{result.author}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Calendar style={{ width: '16px', height: '16px' }} />
                  {new Date(result.published_at).toLocaleDateString()}
                </span>
              </div>
              <p className="result-snippet">{result.snippet}</p>
              <div className="result-stats">
                <div className="stat-item">
                  <Eye style={{ width: '16px', height: '16px' }} />
                  {result.views}
                </div>
                <div className="stat-item">
                  <Heart style={{ width: '16px', height: '16px' }} />
                  {result.likes}
                </div>
                <div className="stat-item">
                  <MessageCircle style={{ width: '16px', height: '16px' }} />
                  {result.comments}
                </div>
                <div className="stat-item score-badge">
                  Score: {result.ranking_score.toFixed(2)}
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}