"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, Bell, Settings, Terminal as TerminalIcon, 
  Box, Shield, Folder, Globe, CheckCircle, AlertTriangle, 
  X, Loader2, Play, Activity, FileText, ChevronRight, ChevronDown, Code
} from 'lucide-react';

const INITIAL_GROUPED_VULNS = [
  {
    project: 'Password-Manager',
    files: [
      {
        path: 'src/config/database.py',
        issues: [
          { line: 14, issue: 'Hardcoded PostgreSQL password detected', severity: 'Critical', snippet: "DB_PASS = 'super_secret_admin_123'\nconnect(user=DB_USER, password=DB_PASS)" },
          { line: 22, issue: 'Insecure SSL connection configured', severity: 'High', snippet: "sslmode='disable'" }
        ]
      },
      {
        path: 'docker-compose.yml',
        issues: [
          { line: 8, issue: 'Insecure port binding & root privileges', severity: 'High', snippet: "services:\n  db:\n    image: postgres:15\n    ports:\n      - \"2222:22\"" }
        ]
      }
    ]
  }
];

const SYSTEM_LOGS = [
  "[12:30:05] [INFO] TrustLens daemon started successfully.",
  "[12:31:12] [INFO] Connection established with Neon PostgreSQL.",
  "[12:35:44] [WARN] Scan initiated on 'Password-Manager' by User.",
  "[12:35:48] [ERROR] Semgrep detected 2 high-severity findings.",
  "[12:35:50] [INFO] Scan complete. Telemetry synced to cloud."
];

export default function TrustLensDashboard() {
  const [currentView, setCurrentView] = useState('scans'); 
  const [projects, setProjects] = useState<any[]>([
    { id: 1, name: 'Password-Manager', path: 'https://github.com/machindra7/Password-Manager', status: 'vulnerable', vulns: 3, lastScan: '5 mins ago' }
  ]); 
  const [groupedVulns, setGroupedVulns] = useState(INITIAL_GROUPED_VULNS);
  const [scanningProjectId, setScanningProjectId] = useState<number | null>(null);
  
  // Real-time Honeypot Telemetry State from Neon PostgreSQL
  const [honeypotLogs, setHoneypotLogs] = useState<any[]>([]);

  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Accordion State
  const [expandedProjects, setExpandedProjects] = useState<string[]>(['Password-Manager']);
  const [expandedFiles, setExpandedFiles] = useState<string[]>(['Password-Manager/src/config/database.py', 'Password-Manager/docker-compose.yml']);

  // CLI & Modal State
  const [isTerminalOpen, setIsTerminalOpen] = useState(false);
  const [cliState, setCliState] = useState('idle');
  const [terminalOutput, setTerminalOutput] = useState([
    "TrustLens CLI initialized.",
    "Type 'trustlens' to start a scan or 'help' for commands."
  ]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [scanType, setScanType] = useState('github');
  const [scanTarget, setScanTarget] = useState('');
  const [isScanning, setIsScanning] = useState(false);

  const endOfTerminalRef = useRef<HTMLDivElement>(null);

  // --- AUTO-FETCH HONEYPOT LOGS EVERY 5 SECONDS ---
  useEffect(() => {
    const fetchHoneypotLogs = async () => {
      try {
        const res = await fetch('/api/honeypot-logs');
        const data = await res.json();
        if (data.success) {
          setHoneypotLogs(data.logs);
        }
      } catch (err) {
        console.error("Failed to fetch honeypot logs:", err);
      }
    };

    fetchHoneypotLogs();
    const interval = setInterval(fetchHoneypotLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    endOfTerminalRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [terminalOutput, isTerminalOpen]);

  // Ctrl+K Search Focus
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const toggleProject = (projectName: string) => {
    setExpandedProjects(prev => prev.includes(projectName) ? prev.filter(p => p !== projectName) : [...prev, projectName]);
  };

  const toggleFile = (fileKey: string) => {
    setExpandedFiles(prev => prev.includes(fileKey) ? prev.filter(f => f !== fileKey) : [...prev, fileKey]);
  };

  // --- RE-SCAN SPECIFIC PROJECT ---
  const handleReScanProject = async (proj: any, e: React.MouseEvent) => {
    e.stopPropagation(); 
    setScanningProjectId(proj.id);
    
    await new Promise(resolve => setTimeout(resolve, 2500));

    setProjects(prev => prev.map(p => p.id === proj.id ? { ...p, lastScan: 'Just now' } : p));
    setScanningProjectId(null);
    setCurrentView('vulnerabilities'); 
  };

  // --- MOCK VULNERABILITY GENERATOR ---
  const processNewScanResults = (target: string) => {
    const projectName = target.split('/').pop() || 'new-scanned-project';
    const generatedVulnsCount = Math.floor(Math.random() * 4) + 1;
    
    setProjects(prev => [{
      id: Date.now(),
      name: projectName,
      path: target,
      status: 'vulnerable',
      vulns: generatedVulnsCount,
      lastScan: 'Just now'
    }, ...prev]);

    const newVulnEntry = {
      project: projectName,
      files: [
        {
          path: 'src/main.py',
          issues: Array.from({ length: generatedVulnsCount }).map((_, idx) => ({
            line: Math.floor(Math.random() * 100) + 10,
            issue: idx === 0 ? 'Secret token found in commit history' : 'Unsanitized input allows injection',
            severity: idx === 0 ? 'Critical' : 'Medium',
            snippet: idx === 0 ? `API_KEY = "sk_live_123456789"\nprint(API_KEY)` : `query = f"SELECT * FROM users WHERE name = '{user_input}'"`
          }))
        }
      ]
    };
    
    setGroupedVulns(prev => [newVulnEntry, ...prev]);
    setExpandedProjects(prev => [...prev, projectName]);
  };

  // --- CLI INTERACTION ---
  const handleTerminalInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const val = e.currentTarget.value;
      if (!val.trim() && cliState === 'idle') return;
      
      setTerminalOutput(prev => [...prev, `ubuntu@trustlens:~$ ${val}`]);
      e.currentTarget.value = '';

      if (cliState === 'awaiting_path') {
        const target = val.trim() || '.';
        setCliState('idle');
        
        setTerminalOutput(prev => [
          ...prev, `> Initializing scan for: ${target}`, `> Running static analysis...`
        ]);

        setTimeout(() => {
          processNewScanResults(target);
          setTerminalOutput(prev => [
            ...prev, `> Scan complete. Dashboard synchronized successfully!`
          ]);
        }, 3000);
        return;
      }

      if (val.trim() === 'trustlens') {
        setCliState('awaiting_path');
        setTimeout(() => setTerminalOutput(prev => [
          ...prev, "🛡️ Welcome to TrustLens CLI", "? Enter local path or GitHub URL to scan [Default: .]:"
        ]), 100);
      } else if (val.trim() !== '') {
        setTimeout(() => setTerminalOutput(prev => [...prev, `Command not found: ${val}`]), 100);
      }
    }
  };

  // --- UI SCAN BUTTON ---
  const handleUiScan = async () => {
    if (!scanTarget.trim()) return;
    setIsScanning(true);
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    processNewScanResults(scanTarget);
    
    setIsScanning(false);
    setIsAddModalOpen(false);
    setScanTarget('');
    setCurrentView('vulnerabilities');
  };

  // --- SEARCH FILTERING ---
  const filteredProjects = projects.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()) || p.path.toLowerCase().includes(searchQuery.toLowerCase()));
  const filteredVulns = groupedVulns.filter(v => v.project.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="flex flex-col h-screen bg-[#0B1015] text-gray-300 font-sans overflow-hidden">
      
      {/* TOP NAVIGATION */}
      <div className="h-12 bg-[#0B1015] border-b border-[#232931] flex items-center justify-between px-4 shrink-0">
        <div onClick={() => setCurrentView('scans')} className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
          <Shield className="w-5 h-5 text-blue-500" />
          <span className="text-white font-semibold tracking-wide">trustlens</span>
          <span className="bg-[#1A202A] text-[10px] text-gray-300 px-1.5 py-0.5 rounded border border-[#2A313C] ml-1">PERSONAL</span>
        </div>
        
        <div className="flex-1 max-w-lg mx-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              ref={searchInputRef}
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search projects..." 
              className="w-full bg-[#151B23] border border-[#2A313C] rounded-md py-1 pl-9 pr-4 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 font-mono">Ctrl+K</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Bell className="w-4 h-4 text-gray-400 hover:text-white cursor-pointer relative" />
          <Settings className="w-4 h-4 text-gray-400 hover:text-white cursor-pointer" />
          <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold cursor-pointer">M</div>
        </div>
      </div>

      {/* MAIN BODY */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* SIDEBAR */}
        <div className="w-60 bg-[#0B1015] border-r border-[#232931] flex flex-col shrink-0">
          <div className="py-4">
            <div className="px-4 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">Dashboard</div>
            <ul className="space-y-0.5 text-sm">
              <li onClick={() => setCurrentView('scans')} className={`px-4 py-2 cursor-pointer flex items-center gap-3 border-l-2 ${currentView === 'scans' ? 'bg-[#1A202A] text-white border-blue-500' : 'text-gray-400 hover:text-white hover:bg-[#151B23] border-transparent'}`}><Box className="w-4 h-4" /> Scans</li>
              <li onClick={() => setCurrentView('vulnerabilities')} className={`px-4 py-2 cursor-pointer flex items-center gap-3 border-l-2 ${currentView === 'vulnerabilities' ? 'bg-[#1A202A] text-white border-blue-500' : 'text-gray-400 hover:text-white hover:bg-[#151B23] border-transparent'}`}><AlertTriangle className="w-4 h-4" /> Vulnerabilities</li>
              <li onClick={() => setCurrentView('logs')} className={`px-4 py-2 cursor-pointer flex items-center gap-3 border-l-2 ${currentView === 'logs' ? 'bg-[#1A202A] text-white border-blue-500' : 'text-gray-400 hover:text-white hover:bg-[#151B23] border-transparent'}`}><Activity className="w-4 h-4" /> Logs</li>
            </ul>
          </div>
        </div>

        {/* CONTENT AREA */}
        <div className="flex-1 bg-[#0F141B] flex flex-col relative overflow-y-auto">
          <div className="px-8 py-5 border-b border-[#232931] flex items-center justify-between shrink-0">
            <h1 className="text-xl font-semibold text-white capitalize">{currentView}</h1>
            {currentView === 'scans' && projects.length > 0 && (
              <div className="flex items-center gap-3">
                <button onClick={() => {setScanType('local'); setIsAddModalOpen(true);}} className="flex items-center gap-2 bg-[#151B23] border border-[#2A313C] hover:bg-[#1A202A] text-gray-300 text-sm px-3 py-1.5 rounded transition-colors"><Folder className="w-4 h-4" /> Local Path</button>
                <button onClick={() => {setScanType('github'); setIsAddModalOpen(true);}} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-sm px-3 py-1.5 rounded transition-colors"><Globe className="w-4 h-4" /> GitHub Repo</button>
              </div>
            )}
          </div>

          <div className="p-8">
            
            {/* VIEW: SCANS */}
            {currentView === 'scans' && (
              <>
                {filteredProjects.length === 0 ? (
                  <p className="text-gray-500 text-center mt-10">No projects found.</p>
                ) : (
                  <div className="grid gap-3">
                    {filteredProjects.map((proj) => (
                      <div key={proj.id} className="bg-[#151B23] border border-[#232931] p-4 rounded-lg flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <Box className="w-5 h-5 text-blue-500" />
                          <div>
                            <h3 className="text-white font-medium text-sm">{proj.name}</h3>
                            <p className="text-xs text-gray-500 font-mono mt-0.5">{proj.path}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-red-500 flex items-center gap-1 text-sm"><AlertTriangle className="w-4 h-4"/> {proj.vulns} Issues</span>
                          <button 
                            onClick={(e) => handleReScanProject(proj, e)}
                            title="Re-run Scan"
                            className="p-2 hover:bg-[#2A313C] rounded text-gray-400 hover:text-white transition-colors"
                          >
                            {scanningProjectId === proj.id ? (
                              <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                            ) : (
                              <Play className="w-4 h-4 fill-current" />
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            {/* VIEW: VULNERABILITIES */}
            {currentView === 'vulnerabilities' && (
              <div className="w-full flex flex-col gap-3">
                {filteredVulns.map((proj) => {
                  const isProjOpen = expandedProjects.includes(proj.project);
                  return (
                    <div key={proj.project} className="bg-[#151B23] border border-[#232931] rounded-lg overflow-hidden">
                      <div onClick={() => toggleProject(proj.project)} className="p-3 bg-[#1A202A] flex items-center gap-3 cursor-pointer hover:bg-[#1f2733] transition-colors">
                        {isProjOpen ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                        <Folder className="w-4 h-4 text-blue-400" />
                        <span className="text-white font-medium text-sm">{proj.project}</span>
                        <span className="ml-auto text-xs bg-[#0B1015] border border-[#232931] px-2 py-1 rounded text-gray-400">{proj.files.length} Files Affected</span>
                      </div>

                      {isProjOpen && (
                        <div className="flex flex-col border-t border-[#232931]">
                          {proj.files.map((file) => {
                            const fileKey = `${proj.project}/${file.path}`;
                            const isFileOpen = expandedFiles.includes(fileKey);
                            return (
                              <div key={file.path} className="border-b border-[#232931] last:border-0">
                                <div onClick={() => toggleFile(fileKey)} className="p-3 pl-8 flex items-center gap-3 cursor-pointer hover:bg-[#1C2431] transition-colors bg-[#11161d]">
                                  {isFileOpen ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500" />}
                                  <FileText className="w-4 h-4 text-gray-400" />
                                  <span className="text-gray-300 text-sm font-mono">{file.path}</span>
                                  <span className="ml-auto text-xs text-red-400 font-medium">{file.issues.length} Issues</span>
                                </div>

                                {isFileOpen && (
                                  <div className="p-4 pl-14 bg-[#0B1015] flex flex-col gap-3">
                                    {file.issues.map((issue, idx) => (
                                      <div key={idx} className="bg-[#151B23] border border-[#232931] rounded-md p-4">
                                        <div className="flex items-start justify-between mb-3">
                                          <div className="flex items-center gap-3">
                                            <span className="bg-[#2A313C] text-gray-300 text-xs px-2 py-1 rounded font-mono">Line {issue.line}</span>
                                            <span className="text-gray-200 text-sm font-medium">{issue.issue}</span>
                                            
                                            {/* ACTIVE DEFENSE BADGE FOR HONEYPOT TRAP */}
                                            {(file.path.includes("docker-compose") || issue.snippet.includes("2222")) && (
                                              <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                                                <Shield className="w-3 h-3" /> Active Defense Deployed (Port 2222)
                                              </span>
                                            )}
                                          </div>
                                          <span className={`inline-flex px-2 py-1 rounded text-xs font-semibold ${issue.severity === 'Critical' ? 'bg-red-500/20 text-red-500 border border-red-500/30' : issue.severity === 'High' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'}`}>{issue.severity}</span>
                                        </div>
                                        <div className="bg-black border border-[#232931] rounded flex flex-col mt-2">
                                          <div className="flex items-center gap-2 px-3 py-1.5 border-b border-[#232931] bg-[#11151A]"><Code className="w-3 h-3 text-gray-500" /><span className="text-[10px] uppercase text-gray-500 font-semibold tracking-wider">Vulnerable Block</span></div>
                                          <pre className="p-3 text-xs font-mono text-blue-300 overflow-x-auto whitespace-pre-wrap">{issue.snippet}</pre>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* VIEW: LOGS (SYSTEM LOGS + LIVE NEON HONEYPOT TELEMETRY) */}
            {currentView === 'logs' && (
              <div className="flex flex-col gap-6">
                
                {/* LIVE HONEYPOT TELEMETRY TABLE */}
                <div className="bg-[#151B23] border border-[#232931] rounded-lg p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Shield className="w-5 h-5 text-emerald-400" />
                      <div>
                        <h3 className="text-white text-sm font-semibold">Ephemeral Micro-Honeypot Telemetry</h3>
                        <p className="text-xs text-gray-400 font-mono">Connected to Neon PostgreSQL • Listening on Port 2222</p>
                      </div>
                    </div>
                    <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2.5 py-1 rounded-full flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Live Telemetry Syncing
                    </span>
                  </div>

                  <div className="w-full bg-[#0B1015] border border-[#232931] rounded-md overflow-hidden font-mono">
                    <table className="w-full text-left text-xs text-gray-300">
                      <thead className="bg-[#1A202A] text-gray-400 uppercase tracking-wider">
                        <tr>
                          <th className="p-3">Timestamp</th>
                          <th className="p-3">Source IP</th>
                          <th className="p-3">Port</th>
                          <th className="p-3">Captured Attacker Payload</th>
                        </tr>
                      </thead>
                      <tbody>
                        {honeypotLogs.length === 0 ? (
                          <tr>
                            <td colSpan={4} className="p-4 text-center text-gray-500">
                              No attacker probes captured yet. Listening for connections...
                            </td>
                          </tr>
                        ) : (
                          honeypotLogs.map((log) => (
                            <tr key={log.id} className="border-b border-[#232931] hover:bg-[#11161d] transition-colors">
                              <td className="p-3 text-gray-400">{new Date(log.timestamp).toLocaleTimeString()}</td>
                              <td className="p-3 text-blue-400 font-semibold">{log.ip_address}</td>
                              <td className="p-3 text-yellow-400">{log.port}</td>
                              <td className="p-3 text-red-400 font-bold bg-red-950/20">{log.payload || "(Empty Banner Probe)"}</td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* SYSTEM DAEMON LOGS */}
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">System Daemon Output</h4>
                  <div className="w-full h-[200px] bg-black border border-[#232931] rounded-lg p-4 font-mono text-sm overflow-y-auto">
                    {SYSTEM_LOGS.map((log, index) => (
                      <div key={index} className={`mb-1 ${log.includes('[ERROR]') ? 'text-red-400' : log.includes('[WARN]') ? 'text-yellow-400' : 'text-gray-300'}`}>
                        {log}
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

          </div>
        </div>
      </div>

      {/* FOOTER BAR */}
      <div className="h-8 bg-[#0B1015] border-t border-[#232931] flex items-center justify-between px-4 shrink-0 text-xs">
        <div className="flex items-center gap-6"><span className="text-gray-500">TrustLens Scanner v1.0.0</span></div>
        <button onClick={() => setIsTerminalOpen(!isTerminalOpen)} className={`flex items-center gap-2 font-mono font-medium hover:text-white transition-colors px-2 py-1 rounded ${isTerminalOpen ? 'text-white bg-[#1A202A]' : 'text-gray-400'}`}>&gt;_ Terminal</button>
      </div>

      {/* ADD PROJECT MODAL */}
      {isAddModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#151B23] border border-[#232931] rounded-xl w-full max-w-md shadow-2xl">
            <div className="flex justify-between items-center p-4 border-b border-[#232931]">
              <h3 className="text-sm font-semibold text-white">Add Project to Scan</h3>
              <button onClick={() => setIsAddModalOpen(false)} className="text-gray-400 hover:text-white"><X className="w-4 h-4" /></button>
            </div>
            <div className="p-5">
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wide">{scanType === 'github' ? 'Repository URL' : 'Absolute Folder Path'}</label>
              <input type="text" value={scanTarget} onChange={(e) => setScanTarget(e.target.value)} placeholder={scanType === 'github' ? 'https://github.com/user/repo' : '/home/ubuntu/project'} className="w-full bg-[#0B1015] border border-[#232931] rounded p-2 text-sm text-white focus:outline-none focus:border-blue-500 mb-4" />
              <button onClick={handleUiScan} disabled={isScanning || !scanTarget.trim()} className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-2 rounded flex justify-center items-center gap-2 text-sm">
                {isScanning ? <><Loader2 className="w-4 h-4 animate-spin" /> Scanning...</> : 'Run Scan'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CLI TERMINAL OVERLAY */}
      {isTerminalOpen && (
        <div className="absolute bottom-8 right-0 w-full md:w-[600px] h-[350px] bg-[#0B1015] border-t border-l border-[#232931] flex flex-col shadow-2xl z-40">
          <div className="bg-[#151B23] p-2 flex justify-between items-center border-b border-[#232931]">
            <span className="text-xs text-gray-400 font-mono tracking-wider ml-2">TERMINAL</span>
            <button onClick={() => setIsTerminalOpen(false)} className="text-gray-400 hover:text-white p-1"><X className="w-4 h-4" /></button>
          </div>
          <div className="flex-1 p-3 font-mono text-sm overflow-y-auto bg-black" style={{ color: '#00ff00' }}>
            {terminalOutput.map((line, i) => (<div key={i} className="mb-0.5">{line}</div>))}
            <div className="flex items-center mt-1">
              <span className="text-blue-400 mr-2">{cliState === 'awaiting_path' ? '>' : 'ubuntu@trustlens:~$'}</span>
              <input type="text" className="flex-1 bg-transparent outline-none border-none text-green-400" autoFocus onKeyDown={handleTerminalInput} autoComplete="off" spellCheck="false" />
            </div>
            <div ref={endOfTerminalRef} />
          </div>
        </div>
      )}
    </div>
  );
}