"use client";

import { useState, useEffect } from "react";
import { Search, Sparkles, Code, CheckCircle, Circle, Play, GitPullRequest, Terminal, FileCode2, History, GitBranch, Mail, MessageSquare } from "lucide-react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion, AnimatePresence } from 'framer-motion';

type NodeUpdate = {
  node: string;
  update: any;
};

export default function Home() {
  const [issueUrl, setIssueUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [updates, setUpdates] = useState<NodeUpdate[]>([]);
  const [runId, setRunId] = useState("");
  const [activeTab, setActiveTab] = useState<"timeline" | "code" | "terminal">("timeline");
  
  const handleResolve = async () => {
    if (!issueUrl) return;
    setIsLoading(true);
    setUpdates([]);
    setRunId("");
    setActiveTab("timeline");
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/issues`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ issue_url: issueUrl }),
      });
      
      const data = await response.json();
      if (data.error) {
        alert(data.error);
        setIsLoading(false);
        return;
      }
      setRunId(data.run_id);
    } catch (error) {
      console.error(error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!runId) return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const eventSource = new EventSource(`${apiUrl}/api/issues/${runId}/stream`);

    eventSource.onmessage = (event) => {
      if (event.data === "[DONE]") {
        setIsLoading(false);
        eventSource.close();
        return;
      }

      try {
        const parsed = JSON.parse(event.data);
        if (parsed.error) {
          alert(`Error: ${parsed.error}`);
          setIsLoading(false);
          eventSource.close();
          return;
        }
        setUpdates((prev) => [...prev, parsed]);
      } catch (err) {
        console.error("Failed to parse SSE", err);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
      setIsLoading(false);
    };

    return () => eventSource.close();
  }, [runId]);

  const getNodeIcon = (nodeName: string) => {
    switch(nodeName) {
      case "code_reader": return <Search size={18} />;
      case "planner": return <Sparkles size={18} />;
      case "code_writer": return <Code size={18} />;
      case "test_writer": return <CheckCircle size={18} />;
      case "pr_opener": return <GitPullRequest size={18} />;
      case "sandbox": return <Terminal size={18} />;
      default: return <Circle size={18} />;
    }
  };
  
  // Helpers to extract data for the tabs
  const codeContext = updates.find(u => u.update?.code_context)?.update.code_context;
  const generatedPatch = updates.find(u => u.update?.patch)?.update.patch;
  const generatedTests = updates.find(u => u.update?.tests)?.update.tests;
  const sandboxOutput = updates.find(u => u.update?.test_result)?.update.test_result?.output;
  const isSandboxPassed = updates.find(u => u.update?.test_result)?.update.test_result?.passed;

  return (
    <main className="container">
      <div className="header">
        <h1>AgentGraph</h1>
        <p>The autonomous multi-agent GitHub issue resolver.</p>
      </div>

      <div className="glass-panel">
        <div className="search-container">
          <input 
            type="text" 
            className="input-field" 
            placeholder="Paste GitHub Issue URL (e.g. https://github.com/facebook/react/issues/123)"
            value={issueUrl}
            onChange={(e) => setIssueUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleResolve()}
          />
          <button 
            className="btn-primary" 
            onClick={handleResolve}
            disabled={isLoading || !issueUrl}
          >
            <Play size={18} />
            {isLoading ? "Running..." : "Resolve"}
          </button>
        </div>
        <div className="options-container">
          <button className="option-btn" onClick={() => setIssueUrl("https://github.com/facebook/react/issues/28774")}>
            <GitBranch size={14} /> React #28774
          </button>
          <button className="option-btn" onClick={() => setIssueUrl("https://github.com/vercel/next.js/issues/60111")}>
            <GitBranch size={14} /> Next.js #60111
          </button>
          <button className="option-btn" onClick={() => setIssueUrl("https://github.com/twbs/bootstrap/issues/37841")}>
            <GitBranch size={14} /> Bootstrap #37841
          </button>
        </div>
      </div>

      {(updates.length > 0 || isLoading) && (
        <div className="dashboard">
          {/* Tabs Navigation */}
          <div className="tabs-nav">
            <button 
              className={`tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
              onClick={() => setActiveTab('timeline')}
            >
              <History size={16} /> Timeline
            </button>
            <button 
              className={`tab-btn ${activeTab === 'code' ? 'active' : ''}`}
              onClick={() => setActiveTab('code')}
            >
              <FileCode2 size={16} /> Code Viewer
            </button>
            <button 
              className={`tab-btn ${activeTab === 'terminal' ? 'active' : ''}`}
              onClick={() => setActiveTab('terminal')}
            >
              <Terminal size={16} /> Sandbox Logs
            </button>
          </div>

          <div className="tab-content">
            <AnimatePresence mode="wait">
              
              {/* TIMELINE TAB */}
              {activeTab === 'timeline' && (
                <motion.div 
                  key="timeline"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="timeline"
                >
                  {updates.map((u, i) => {
                    const isLast = i === updates.length - 1;
                    const isDone = !isLoading && isLast;
                    
                    return (
                      <motion.div 
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        key={i} 
                        className={`timeline-item ${isLast && isLoading ? 'active' : 'done'}`}
                      >
                        <div className="timeline-icon">
                          {getNodeIcon(u.node)}
                        </div>
                        <div className="timeline-content">
                          <div className="timeline-header">
                            <span className="timeline-title">{u.node.replace('_', ' ')}</span>
                            <span className={`timeline-badge ${isLast && isLoading ? 'badge-running' : 'badge-done'}`}>
                              {isLast && isLoading ? "Running" : "Done"}
                            </span>
                          </div>
                          <div className="timeline-body-simple">
                            {u.node === 'planner' ? `Generated Plan:\nComplexity: ${u.update.complexity}` : 
                             u.node === 'pr_opener' ? `Successfully opened PR!\nURL: ${u.update.pr_url}` :
                             `Generated output for ${u.node}... (See tabs for details)`}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                  
                  {isLoading && (
                    <motion.div 
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                      className="timeline-item active"
                    >
                       <div className="timeline-icon">
                          <div className="animate-spin"><Sparkles size={18} /></div>
                       </div>
                       <div className="timeline-content">
                          <div className="timeline-header">
                            <span className="timeline-title">Agents are thinking...</span>
                            <span className="timeline-badge badge-running">Processing</span>
                          </div>
                       </div>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* CODE VIEWER TAB */}
              {activeTab === 'code' && (
                <motion.div 
                  key="code"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="code-viewer"
                >
                  {codeContext && (
                    <div className="code-section">
                      <h3>Repository Context</h3>
                      <SyntaxHighlighter language="python" style={vscDarkPlus} className="syntax-block">
                        {codeContext}
                      </SyntaxHighlighter>
                    </div>
                  )}
                  {generatedPatch && (
                    <div className="code-section mt-4">
                      <h3>Generated Patch</h3>
                      <SyntaxHighlighter language="diff" style={vscDarkPlus} className="syntax-block">
                        {generatedPatch}
                      </SyntaxHighlighter>
                    </div>
                  )}
                  {generatedTests && (
                    <div className="code-section mt-4">
                      <h3>Generated Tests</h3>
                      <SyntaxHighlighter language="python" style={vscDarkPlus} className="syntax-block">
                        {generatedTests}
                      </SyntaxHighlighter>
                    </div>
                  )}
                  {!codeContext && !generatedPatch && (
                    <div className="empty-state">Code viewer is waiting for agents...</div>
                  )}
                </motion.div>
              )}

              {/* TERMINAL TAB */}
              {activeTab === 'terminal' && (
                <motion.div 
                  key="terminal"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="terminal-viewer"
                >
                  {sandboxOutput ? (
                    <div className={`terminal-window ${isSandboxPassed ? 'passed' : 'failed'}`}>
                      <div className="terminal-header">
                        <span>pytest sandbox execution</span>
                        <span className={`status-text ${isSandboxPassed ? 'text-green' : 'text-red'}`}>
                          {isSandboxPassed ? 'PASSED' : 'FAILED'}
                        </span>
                      </div>
                      <SyntaxHighlighter language="bash" style={vscDarkPlus} className="syntax-block">
                        {sandboxOutput}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <div className="empty-state">Waiting for sandbox execution...</div>
                  )}
                </motion.div>
              )}

            </AnimatePresence>
          </div>
        </div>
      )}

      <footer className="footer">
        <div className="footer-links">
          <a href="https://github.com/yourusername/AgentGraph" target="_blank" rel="noopener noreferrer" className="footer-link">
            <GitBranch size={18} /> GitHub
          </a>
          <a href="mailto:contact@example.com" className="footer-link">
            <Mail size={18} /> Contact Us
          </a>
          <a href="#" className="footer-link">
            <MessageSquare size={18} /> Discord Community
          </a>
        </div>
        <p>&copy; {new Date().getFullYear()} AgentGraph. Autonomous multi-agent framework.</p>
      </footer>
    </main>
  );
}
