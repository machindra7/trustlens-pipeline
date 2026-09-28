"use client";

import { useState, useEffect } from "react";

interface Finding {
  id: number;
  severity: string;
  scanner: string;
  ruleId: string;
  title: string;
  description: string;
  category: string;
  filePath: string;
  startLine: number | null;
}

export default function Dashboard() {
  const [data, setData] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState("ALL");
  const [selectedTool, setSelectedTool] = useState("ALL");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [sortBy, setSortBy] = useState("severity-desc");

  const loadData = () => {
    setLoading(true);
    fetch("/api/findings")
      .then((res) => res.json())
      .then((resData) => {
        if (Array.isArray(resData)) setData(resData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedSeverity("ALL");
    setSelectedTool("ALL");
    setSelectedCategory("ALL");
    setSortBy("severity-desc");
  };

  const filteredData = data.filter((item) => {
    const query = searchQuery.toLowerCase();
    const matchesSearch = 
      item.title.toLowerCase().includes(query) ||
      item.ruleId.toLowerCase().includes(query) ||
      item.filePath.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query);

    const matchesSeverity = selectedSeverity === "ALL" || item.severity.toUpperCase() === selectedSeverity.toUpperCase();
    const matchesTool = selectedTool === "ALL" || item.scanner.toUpperCase() === selectedTool.toUpperCase();
    const matchesCategory = selectedCategory === "ALL" || (item.category && item.category.toUpperCase() === selectedCategory.toUpperCase());

    return matchesSearch && matchesSeverity && matchesTool && matchesCategory;
  });

  const sortedData = [...filteredData].sort((a, b) => {
    const severityRank: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, UNKNOWN: 0 };
    if (sortBy === "severity-desc") {
      return (severityRank[b.severity.toUpperCase()] || 0) - (severityRank[a.severity.toUpperCase()] || 0);
    } else if (sortBy === "severity-asc") {
      return (severityRank[a.severity.toUpperCase()] || 0) - (severityRank[b.severity.toUpperCase()] || 0);
    } else if (sortBy === "rule-asc") {
      return a.ruleId.localeCompare(b.ruleId);
    }
    return 0;
  });

  const exportCSV = () => {
    if (sortedData.length === 0) return alert("No data to export!");
    const headers = ["Severity", "Tool", "Rule ID", "Title", "File", "Lines"];
    const rows = sortedData.map(f => [
      `"${f.severity}"`, `"${f.scanner}"`, `"${f.ruleId}"`, 
      `"${f.title.replace(/"/g, '""')}"`, `"${f.filePath}"`, `"${f.startLine || ''}"`
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", "trustlens_findings.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportJSON = () => {
    if (sortedData.length === 0) return alert("No data to export!");
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sortedData, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", "trustlens_findings.json");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const stats = {
    total: data.length,
    critical: data.filter(f => f.severity.toUpperCase() === "CRITICAL").length,
    high: data.filter(f => f.severity.toUpperCase() === "HIGH").length,
    medium: data.filter(f => f.severity.toUpperCase() === "MEDIUM").length,
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case "CRITICAL": return "text-red-600 font-bold bg-red-50 px-2 py-0.5 rounded";
      case "HIGH": return "text-orange-600 font-bold bg-orange-50 px-2 py-0.5 rounded";
      case "MEDIUM": return "text-yellow-600 font-bold bg-yellow-50 px-2 py-0.5 rounded";
      case "LOW": return "text-blue-600 font-bold bg-blue-50 px-2 py-0.5 rounded";
      default: return "text-gray-600 font-bold bg-gray-50 px-2 py-0.5 rounded";
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 font-sans text-slate-800">
      <header className="bg-slate-900 text-white px-8 py-3 flex items-center justify-between shadow">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-lg tracking-wider">🔒 TrustLens</span>
        </div>
        <div className="text-sm text-slate-300">Security Findings Dashboard</div>
        <button 
          onClick={loadData}
          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1.5 rounded border border-slate-700 transition cursor-pointer"
        >
          🔄 Refresh
        </button>
      </header>

      {/* Expanded width container with generous padding */}
      <main className="w-full px-8 py-6 flex flex-col gap-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div onClick={() => setSelectedSeverity("ALL")} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 cursor-pointer hover:border-slate-300 transition text-center">
            <div className="text-2xl font-bold text-slate-900">{stats.total}</div>
            <div className="text-xs font-medium text-slate-500 uppercase mt-1">Total Findings</div>
          </div>
          <div onClick={() => setSelectedSeverity("CRITICAL")} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 cursor-pointer hover:border-red-300 transition text-center">
            <div className="text-2xl font-bold text-red-600">{stats.critical}</div>
            <div className="text-xs font-medium text-slate-500 uppercase mt-1">Critical</div>
          </div>
          <div onClick={() => setSelectedSeverity("HIGH")} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 cursor-pointer hover:border-orange-300 transition text-center">
            <div className="text-2xl font-bold text-orange-600">{stats.high}</div>
            <div className="text-xs font-medium text-slate-500 uppercase mt-1">High</div>
          </div>
          <div onClick={() => setSelectedSeverity("MEDIUM")} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 cursor-pointer hover:border-yellow-300 transition text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.medium}</div>
            <div className="text-xs font-medium text-slate-500 uppercase mt-1">Medium</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-3 items-center">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Search</label>
            <input 
              type="text"
              placeholder="Search title, rule, file..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none focus:ring-1 focus:ring-slate-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Severity</label>
            <select 
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Tool</label>
            <select 
              value={selectedTool}
              onChange={(e) => setSelectedTool(e.target.value)}
              className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none"
            >
              <option value="ALL">All Tools</option>
              <option value="TRIVY">Trivy</option>
              <option value="SEMGREP">Semgrep</option>
              <option value="CHECKOV">Checkov</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Category</label>
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none"
            >
              <option value="ALL">All Categories</option>
              <option value="vulnerability">Vulnerability</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Sort By</label>
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none"
            >
              <option value="severity-desc">Severity (High to Low)</option>
              <option value="severity-asc">Severity (Low to High)</option>
              <option value="rule-asc">Rule ID (A-Z)</option>
            </select>
          </div>
          <div className="flex items-end h-full pt-5">
            <button 
              onClick={clearFilters}
              className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded bg-slate-50 hover:bg-slate-100 text-slate-700 transition flex items-center justify-center gap-1 cursor-pointer"
            >
              ✕ Clear
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <span className="font-semibold text-sm text-slate-700">Findings ({sortedData.length})</span>
            <div className="flex gap-2">
              <button onClick={exportJSON} className="text-xs px-3 py-1 border border-slate-300 rounded bg-white hover:bg-slate-50 font-medium text-slate-700 cursor-pointer">
                📥 Export JSON
              </button>
              <button onClick={exportCSV} className="text-xs px-3 py-1 border border-slate-300 rounded bg-white hover:bg-slate-50 font-medium text-slate-700 cursor-pointer">
                📄 Export CSV
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-100 text-slate-600 font-semibold text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3 text-left w-32">Severity</th>
                  <th className="px-6 py-3 text-left w-32">Tool</th>
                  <th className="px-6 py-3 text-left w-48">Rule ID</th>
                  <th className="px-6 py-3 text-left">Title</th>
                  <th className="px-6 py-3 text-left w-64">File</th>
                  <th className="px-6 py-3 text-left w-24">Lines</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-slate-500">Loading findings...</td>
                  </tr>
                ) : sortedData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-500">No findings match your filters.</td>
                  </tr>
                ) : (
                  sortedData.map((f) => (
                    <tr key={f.id} className="hover:bg-slate-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap align-top">
                        <span className={getSeverityBadge(f.severity)}>{f.severity}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap align-top font-medium text-slate-700">{f.scanner}</td>
                      <td className="px-6 py-4 whitespace-nowrap align-top font-mono text-xs text-indigo-600 font-semibold">{f.ruleId}</td>
                      <td className="px-6 py-4 align-top text-slate-900 break-words">{f.title}</td>
                      <td className="px-6 py-4 align-top font-mono text-xs text-slate-600 break-all">{f.filePath}</td>
                      <td className="px-6 py-4 align-top font-mono text-xs text-slate-500 whitespace-nowrap">{f.startLine || "-"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
