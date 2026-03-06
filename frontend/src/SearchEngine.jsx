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
      devto: 'bg-gray-900 text-white',
      medium: 'bg-black text-white',
      hackernews: 'bg-orange-500 text-white'
    };
    return colors[source] || 'bg-gray-500 text-white';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <style>{`

        body {
          font-family: Inter, system-ui, sans-serif;
        }

        .search-input {
          background: white;
          border: 1px solid #e5e7eb;
          color: #111827;
          transition: all 0.2s ease;
        }

        .search-input:focus {
          border-color: #2563eb;
          box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
        }

        .result-card {
          background: white;
          border: 1px solid #e5e7eb;
          transition: all 0.2s ease;
        }

        .result-card:hover {
          border-color: #c7d2fe;
          box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        }

        .snippet {
          color: #4b5563;
          line-height: 1.6;
        }

        .trending-badge {
          background: #eef2ff;
          border: 1px solid #c7d2fe;
          color: #3730a3;
        }

        .trending-badge:hover {
          background: #e0e7ff;
          cursor: pointer;
        }

        @keyframes fadeIn {
          from { opacity:0; transform:translateY(10px);}
          to { opacity:1; transform:translateY(0);}
        }

        .result-card {
          animation: fadeIn 0.3s ease forwards;
        }

        .spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform:rotate(0deg);}
          to { transform:rotate(360deg);}
        }

      `}</style>

      <div className="max-w-5xl mx-auto px-4 py-10">

        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            TechSearch
          </h1>
          <p className="text-gray-500">
            AI-powered semantic search for developer blogs
          </p>
        </div>

        <form onSubmit={handleSearch} className="mb-10">
          <div className="flex gap-3">
            <div className="flex-1 relative">

              <input
                type="text"
                value={query}
                onChange={(e)=>setQuery(e.target.value)}
                placeholder="Search tech articles..."
                className="search-input w-full px-5 py-3 rounded-lg outline-none"
              />

              <Search className="absolute right-4 top-3.5 w-5 h-5 text-gray-400"/>

            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-7 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition flex items-center gap-2 disabled:opacity-50"
            >
              {loading
                ? <Loader className="w-5 h-5 spin"/>
                : <Zap className="w-5 h-5"/>}
              Search
            </button>
          </div>

          <div className="mt-4 flex gap-4 items-center flex-wrap">

            <select
              value={sortBy}
              onChange={(e)=>setSortBy(e.target.value)}
              className="px-3 py-2 bg-white border border-gray-300 rounded text-sm"
            >
              <option value="relevance">Most Relevant</option>
              <option value="recent">Most Recent</option>
              <option value="trending">Trending</option>
            </select>

            <select
              value={topK}
              onChange={(e)=>setTopK(Number(e.target.value))}
              className="px-3 py-2 bg-white border border-gray-300 rounded text-sm"
            >
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
              <option value={50}>Top 50</option>
            </select>

            {executionTime > 0 && (
              <span className="text-gray-500 text-sm">
                Found in {executionTime.toFixed(0)} ms
              </span>
            )}

          </div>
        </form>

        {trending.length > 0 && (
          <div className="mb-10">

            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-orange-500"/>
              <h2 className="font-semibold text-gray-800">
                Trending Topics
              </h2>
            </div>

            <div className="flex flex-wrap gap-2">

              {trending.slice(0,8).map((topic,idx)=>(
                <button
                  key={idx}
                  onClick={()=>handleTrendingClick(topic)}
                  className="trending-badge px-3 py-1 rounded-full text-sm font-medium transition"
                >
                  #{topic}
                </button>
              ))}

            </div>

          </div>
        )}

        <div>

          {results.length > 0 && (
            <h2 className="text-lg font-semibold mb-5 text-gray-800">
              {results.length} Results
            </h2>
          )}

          <div className="space-y-4">

            {results.map((result)=>(
              <a
                key={result.id}
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="result-card block p-5 rounded-lg"
              >

                <div className="flex justify-between items-start gap-4 mb-2">

                  <h3 className="text-gray-900 text-lg font-semibold hover:text-blue-600 transition">
                    {result.title}
                  </h3>

                  <span className={`${getSourceColor(result.source)} px-3 py-1 rounded text-xs font-semibold`}>
                    {result.source.toUpperCase()}
                  </span>

                </div>

                <div className="flex items-center gap-4 mb-3 text-sm text-gray-500">

                  <span>{result.author}</span>

                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4"/>
                    {new Date(result.published_at).toLocaleDateString()}
                  </span>

                </div>

                <p className="snippet mb-4">
                  {result.snippet}
                </p>

                <div className="flex gap-6 text-sm text-gray-500">

                  <span className="flex items-center gap-1">
                    <Eye className="w-4 h-4"/> {result.views}
                  </span>

                  <span className="flex items-center gap-1">
                    <Heart className="w-4 h-4"/> {result.likes}
                  </span>

                  <span className="flex items-center gap-1">
                    <MessageCircle className="w-4 h-4"/> {result.comments}
                  </span>

                  <span className="text-blue-600">
                    Score: {result.ranking_score.toFixed(2)}
                  </span>

                </div>

              </a>
            ))}

          </div>

        </div>

      </div>
    </div>
  );
}