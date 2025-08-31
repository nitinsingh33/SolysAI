"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, TrendingUp, MessageSquare, Building2, Calendar, RefreshCw, Search } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
interface Stats {
  total_comments: number;
  total_oems: number;
  oem_breakdown: Record<string, number>;
  sentiment_breakdown: Record<string, number>;
  monthly_breakdown: Record<string, number>;
  last_updated: string;
}

interface Comment {
  id: string;
  text: string;
  author: string;
  likes: number;
  time: string;
  date: string;
  video_id: string;
  is_reply: boolean;
  extraction_method: string;
  sentiment: string;
  sentiment_score: number;
  oem: string;
  month: string;
}

interface PaginatedComments {
  comments: Comment[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

interface OEM {
  name: string;
  count: number;
}

// Colors for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

const SentimentColors = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral: '#6b7280'
};

export default function Dashboard() {
  // State
  const [stats, setStats] = useState<Stats | null>(null);
  const [comments, setComments] = useState<PaginatedComments | null>(null);
  const [oems, setOEMs] = useState<OEM[]>([]);
  const [loading, setLoading] = useState(true);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [selectedOEM, setSelectedOEM] = useState<string>('all');
  const [selectedSentiment, setSelectedSentiment] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [limit] = useState(25);

  // Fetch functions
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to load statistics');
    }
  };

  const fetchOEMs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/oems`);
      if (!response.ok) throw new Error('Failed to fetch OEMs');
      const data = await response.json();
      setOEMs(data.oems);
    } catch (err) {
      console.error('Error fetching OEMs:', err);
    }
  };

  const fetchComments = async (page = 1, resetPage = false) => {
    if (resetPage) {
      setCurrentPage(1);
      page = 1;
    }
    
    setCommentsLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });
      
      if (selectedOEM !== 'all') params.append('oem', selectedOEM);
      if (selectedSentiment !== 'all') params.append('sentiment', selectedSentiment);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());

      const response = await fetch(`${API_BASE_URL}/comments?${params}`);
      if (!response.ok) throw new Error('Failed to fetch comments');
      const data = await response.json();
      setComments(data);
      setCurrentPage(page);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setError('Failed to load comments');
    } finally {
      setCommentsLoading(false);
    }
  };

  // Effects
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchOEMs()]);
      await fetchComments();
      setLoading(false);
    };
    
    loadData();
  }, []);

  useEffect(() => {
    fetchComments(1, true);
  }, [selectedOEM, selectedSentiment, searchQuery]);

  // Helper functions
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const getSentimentBadgeColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'negative': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const refreshData = async () => {
    setLoading(true);
    await Promise.all([fetchStats(), fetchOEMs(), fetchComments()]);
    setLoading(false);
  };

  // Prepare chart data
  const oemChartData = stats ? Object.entries(stats.oem_breakdown).map(([name, count]) => ({
    name,
    count
  })) : [];

  const sentimentChartData = stats ? Object.entries(stats.sentiment_breakdown).map(([name, count]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    count,
    fill: SentimentColors[name as keyof typeof SentimentColors] || '#6b7280'
  })) : [];

  const monthlyChartData = stats ? Object.entries(stats.monthly_breakdown).map(([month, count]) => ({
    month,
    count
  })) : [];

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={refreshData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SolysAI Dashboard</h1>
              <p className="text-gray-600 mt-2">EV Sentiment Analysis Platform</p>
            </div>
            <Button onClick={refreshData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          {stats && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {new Date(stats.last_updated).toLocaleString()}
            </p>
          )}
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Comments</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatNumber(stats.total_comments)}</div>
                <p className="text-xs text-muted-foreground">Across all platforms</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">EV Brands</CardTitle>
                <Building2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_oems}</div>
                <p className="text-xs text-muted-foreground">Brands analyzed</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Positive Sentiment</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatNumber(stats.sentiment_breakdown.positive || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats.total_comments > 0 ? 
                    `${((stats.sentiment_breakdown.positive || 0) / stats.total_comments * 100).toFixed(1)}%` : 
                    '0%'
                  } of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Data Sources</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Object.keys(stats.monthly_breakdown).length}</div>
                <p className="text-xs text-muted-foreground">Months of data</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Charts */}
        {stats && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* OEM Breakdown Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Comments by EV Brand</CardTitle>
                <CardDescription>Distribution of comments across different EV manufacturers</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={oemChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Sentiment Distribution Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Sentiment Distribution</CardTitle>
                <CardDescription>Overall sentiment analysis of comments</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sentimentChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {sentimentChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Monthly Trend Chart */}
        {stats && Object.keys(stats.monthly_breakdown).length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Monthly Comment Trends</CardTitle>
              <CardDescription>Comment volume over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Comments Section */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Comments</CardTitle>
            <CardDescription>Browse and filter comments from the database</CardDescription>
            
            {/* Filters */}
            <div className="flex flex-wrap gap-4 mt-4">
              <div className="flex-1 min-w-[200px]">
                <Input
                  placeholder="Search comments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              
              <Select value={selectedOEM} onValueChange={setSelectedOEM}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by OEM" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All OEMs</SelectItem>
                  {oems.map((oem) => (
                    <SelectItem key={oem.name} value={oem.name}>
                      {oem.name} ({oem.count})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedSentiment} onValueChange={setSelectedSentiment}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Sentiment" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sentiments</SelectItem>
                  <SelectItem value="positive">Positive</SelectItem>
                  <SelectItem value="negative">Negative</SelectItem>
                  <SelectItem value="neutral">Neutral</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          
          <CardContent>
            {commentsLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
                <span className="ml-2">Loading comments...</span>
              </div>
            ) : comments && comments.comments.length > 0 ? (
              <>
                <div className="space-y-4">
                  {comments.comments.map((comment) => (
                    <div key={comment.id} className="border rounded-lg p-4 bg-white">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{comment.oem}</Badge>
                          <Badge className={getSentimentBadgeColor(comment.sentiment)}>
                            {comment.sentiment}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            Score: {comment.sentiment_score.toFixed(2)}
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          {comment.date} • {comment.likes} likes
                        </div>
                      </div>
                      <p className="text-gray-900 mb-2">{comment.text}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500">
                        <span>by {comment.author}</span>
                        <span>{comment.extraction_method}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                <div className="flex justify-between items-center mt-6">
                  <div className="text-sm text-gray-500">
                    Showing {((currentPage - 1) * limit) + 1} to {Math.min(currentPage * limit, comments.total)} of {formatNumber(comments.total)} comments
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => fetchComments(currentPage - 1)}
                      disabled={currentPage <= 1 || commentsLoading}
                    >
                      Previous
                    </Button>
                    <span className="flex items-center px-3">
                      Page {currentPage} of {comments.total_pages}
                    </span>
                    <Button
                      variant="outline"
                      onClick={() => fetchComments(currentPage + 1)}
                      disabled={currentPage >= comments.total_pages || commentsLoading}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No comments found with current filters</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
