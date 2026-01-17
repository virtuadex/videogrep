import { useState, useCallback } from "react";
import "./index.css";

import { Header } from "./components/Header";
import { InputSource } from "./components/InputSource";
import { Library } from "./components/Library";
import { SearchDashboard } from "./components/SearchDashboard";
import { VideoFile, AppStatus, SearchMatch } from "./types";
import { downloadVideo, openFolder } from "./api";
import { useLibrary } from "./hooks/useLibrary";
import { useSearch } from "./hooks/useSearch";

function App() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<AppStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<VideoFile | null>(null);
  const [useGPU, setUseGPU] = useState(false);
  const [ngramN, setNgramN] = useState(1);

  const { library, scan } = useLibrary();
  const { 
    matches, 
    isSearching, 
    search, 
    ngrams, 
    isNgramsLoading, 
    exportMatches 
  } = useSearch(selectedVideo, ngramN);

  const handleDownload = async () => {
    if (!url) return;
    setStatus("downloading");
    setProgress(10);
    try {
      await downloadVideo(url);
      setStatus("idle");
      setProgress(0);
      scan("downloads");
    } catch (e) {
      console.error("Download failed:", e);
      setStatus("error");
    }
  };

  const handleSelectVideo = (video: VideoFile) => {
    setSelectedVideo(prev => prev?.path === video.path ? null : video);
  };

  const handleSearch = useCallback((query: string, type: string, threshold: number) => {
    if (query.length > 0) {
      search({ query, type, threshold });
    }
  }, [search]);

  const handleExport = useCallback(async (matches: SearchMatch[]) => {
    if (matches.length === 0) return;
    setStatus("exporting");
    setProgress(0);
    
    const timestamp = Math.floor(Date.now() / 1000);
    const output = `downloads/supercut_${timestamp}.mp4`;
    
    try {
      await exportMatches({ matches, output });
      setMessage(`Supercut exported to ${output}`);
      setTimeout(() => setMessage(null), 5000);
      setStatus("idle");
      setProgress(0);
    } catch (e) {
      console.error("Export failed:", e);
      setStatus("error");
    }
  }, [exportMatches]);

  const handleOpenFolder = useCallback(async (path: string) => {
    try {
      await openFolder(path);
    } catch (e) {
      console.error("Failed to open folder:", e);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-['Inter']">
      <Header message={message} />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-1 space-y-8">
          <InputSource 
            url={url} 
            setUrl={setUrl} 
            useGPU={useGPU} 
            setUseGPU={setUseGPU} 
            status={status} 
            progress={progress} 
            onDownload={handleDownload} 
          />

          <Library 
            library={library} 
            onSelect={handleSelectVideo}
            selectedVideoPath={selectedVideo?.path}
          />
        </div>

        <div className="lg:col-span-3">
          <div className="mb-4 flex items-center gap-2">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Scope:</span>
            <span className={`text-xs font-mono px-2 py-1 rounded border ${selectedVideo ? "bg-blue-500/20 border-blue-500/50 text-blue-400" : "bg-slate-800 border-slate-700 text-slate-400"}`}>
              {selectedVideo ? selectedVideo.filename : "ALL INDEXED LIBRARY"}
            </span>
          </div>
          
          <SearchDashboard 
            onSearch={handleSearch} 
            onExport={handleExport}
            onOpenFolder={handleOpenFolder}
            onGetNGrams={setNgramN}
            matches={matches} 
            ngrams={ngrams}
            isSearching={isSearching}
            isNgramsLoading={isNgramsLoading}
            status={status}
            progress={progress}
          />
        </div>
      </div>
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}

export default App;
