import { useState, useEffect, KeyboardEvent, useMemo, useRef, useCallback } from "react";
import { SearchMatch, NGramMatch, AppStatus } from "../types";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Scissors, FolderOpen, Play, BarChart3, Info, Sparkles, X, ChevronRight, Hash, Clock, Percent, Activity, Loader2 } from "lucide-react";

interface SearchDashboardProps {
  onSearch: (query: string, type: string, threshold: number) => void;
  onExport: (matches: SearchMatch[]) => void;
  onOpenFolder: (path: string) => void;
  onGetNGrams: (n: number) => void;
  matches: SearchMatch[];
  ngrams: NGramMatch[];
  isSearching: boolean;
  isNgramsLoading: boolean;
  status: AppStatus;
  progress: number;
}

export function SearchDashboard({ 
  onSearch, 
  onExport, 
  onOpenFolder,
  onGetNGrams, 
  matches, 
  ngrams, 
  isSearching, 
  isNgramsLoading,
  status, 
  progress 
}: SearchDashboardProps) {
  const [query, setQuery] = useState("");
  const [searchType, setSearchType] = useState("sentence");
  const [threshold, setThreshold] = useState(0.45);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [ngramN, setNgramN] = useState(1);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const triggerSearch = useCallback(() => {
    if (query.trim().length > 0) {
      setHasSearched(true);
      setStartTime(performance.now());
      onSearch(query.trim(), searchType, threshold);
    }
  }, [query, searchType, threshold, onSearch]);

  useEffect(() => {
    if (!isSearching && hasSearched && startTime > 0) {
      setSearchTime((performance.now() - startTime) / 1000);
    }
  }, [isSearching, hasSearched, startTime]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      triggerSearch();
    }
  };

  // Re-trigger search when type or threshold changes
  useEffect(() => {
    if (query.trim().length > 0 && hasSearched) {
      triggerSearch();
    }
  }, [searchType, threshold, triggerSearch]);

  // Fetch ngrams
  useEffect(() => {
    onGetNGrams(ngramN);
  }, [ngramN, onGetNGrams]);

  // Dynamic Heatmap Logic
  const heatmapData = useMemo(() => {
    if (matches.length === 0) return Array(60).fill(0);
    
    const buckets = Array(60).fill(0);
    const maxTime = matches.reduce((max, m) => Math.max(max, m.end), 60);
    
    matches.forEach(m => {
      const bucketIdx = Math.floor((m.start / maxTime) * 59);
      if (bucketIdx >= 0 && bucketIdx < 60) {
        buckets[bucketIdx]++;
      }
    });
    
    const maxVal = Math.max(...buckets, 1);
    return buckets.map(v => v / maxVal);
  }, [matches]);

  const clearSearch = () => {
    setQuery("");
    setHasSearched(false);
    setSearchTime(null);
    searchInputRef.current?.focus();
  };

  return (
    <div className="space-y-6">
      <section className="glass p-8 rounded-4xl border border-slate-800 min-h-[700px] flex flex-col shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/5 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-purple-500/5 blur-[100px] rounded-full pointer-events-none" />

        {/* Top Navigation / Controls */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10 relative z-10">
          <div className="space-y-1">
            <h2 className="text-2xl font-black tracking-tighter flex items-center gap-2">
              <BarChart3 className="text-blue-500" size={24} />
              DASHBOARD
            </h2>
            <AnimatePresence>
              {searchTime && !isSearching && matches.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest"
                >
                  <Sparkles size={10} className="text-amber-500" />
                  Found {matches.length} results in {searchTime.toFixed(2)}s
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <AnimatePresence>
              {matches.length > 0 && (
                <motion.button 
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  onClick={() => onExport(matches)}
                  className="px-6 py-2.5 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-500 hover:to-teal-500 text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-all shadow-lg shadow-green-900/40 active:scale-95 flex items-center gap-2 group"
                >
                  <Scissors size={14} className="group-hover:rotate-12 transition-transform" />
                  Export Supercut
                </motion.button>
              )}
            </AnimatePresence>
            
            <div className="flex p-1 bg-slate-950/80 rounded-2xl border border-slate-800/80 backdrop-blur-md">
              {["fragment", "sentence", "semantic"].map(t => (
                <button 
                  key={t}
                  onClick={() => setSearchType(t)} 
                  className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${searchType === t ? "bg-slate-800 text-blue-400 shadow-lg shadow-black/50" : "text-slate-600 hover:text-slate-400"}`}
                >
                  {t}
                </button>
              ))}
              <button 
                onClick={() => setSearchType("mash")} 
                className={`ml-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${searchType === "mash" ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg" : "text-slate-600 hover:text-slate-400 bg-slate-900/50"}`}
              >
                Mashup
              </button>
            </div>
          </div>
        </div>

        {/* Sub-controls (Threshold) */}
        <AnimatePresence>
          {searchType === "semantic" && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-8 px-5 py-4 bg-slate-900/40 rounded-3xl border border-slate-800/50 relative z-10 flex items-center gap-6"
            >
              <div className="flex-1">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <Percent size={12} className="text-blue-500" />
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Similarity Threshold</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-lg border border-blue-500/20">{Math.round(threshold * 100)}%</span>
                </div>
                <input type="range" min="0.1" max="0.9" step="0.05" value={threshold} onChange={(e) => setThreshold(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500" />
              </div>
              <div className="w-1/3 text-[9px] text-slate-500 italic flex items-start gap-2 border-l border-slate-800 pl-6">
                <Info size={14} className="shrink-0 text-slate-600" />
                Higher values return more precise matches but fewer results.
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Status Bars (Transcribing / Exporting) */}
        <AnimatePresence>
          {status === "transcribing" && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 p-6 bg-purple-900/10 rounded-3xl border border-purple-500/20 relative z-10"
            >
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-purple-500 animate-ping" />
                  <span className="text-xs font-black text-purple-400 uppercase tracking-[0.2em]">Whisper AI Transcription in Progress</span>
                </div>
                <span className="text-xs font-mono text-purple-300 font-bold">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-white/5 shadow-inner">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  className="h-full bg-gradient-to-r from-purple-600 to-blue-400 shadow-[0_0_20px_rgba(168,85,247,0.3)]"
                />
              </div>
              <p className="mt-3 text-[10px] text-slate-500 text-center italic">Generating word-level timestamps for precise matching...</p>
            </motion.div>
          )}

          {status === "exporting" && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 p-6 bg-green-900/10 rounded-3xl border border-green-500/20 relative z-10"
            >
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-ping" />
                  <span className="text-xs font-black text-green-400 uppercase tracking-[0.2em]">Exporting Supercut Compilation</span>
                </div>
                <span className="text-xs font-mono text-green-300 font-bold">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-white/5 shadow-inner">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  className="h-full bg-gradient-to-r from-green-600 to-teal-400 shadow-[0_0_20px_rgba(34,197,94,0.3)]"
                />
              </div>
              <p className="mt-3 text-[10px] text-slate-500 text-center italic">Concatenating clips and rendering final media...</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col md:flex-row gap-8 min-h-0 relative z-10">
          <div className="flex-1 space-y-4 overflow-y-auto pr-4 custom-scrollbar">
            <AnimatePresence mode="wait">
              {isSearching ? (
                <motion.div 
                  key="searching"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-full flex flex-col items-center justify-center p-12"
                >
                  <div className="relative mb-8">
                    <div className="w-20 h-20 border-4 border-blue-500/10 border-t-blue-500 rounded-full animate-spin"></div>
                    <Search className="absolute inset-0 m-auto text-blue-500 animate-pulse" size={32} />
                  </div>
                  <p className="text-2xl font-black uppercase tracking-[0.2em] text-blue-400 mb-2">
                    {searchType === "semantic" ? "Neural Mapping..." : "Scanning Database..."}
                  </p>
                  <div className="flex items-center gap-2 px-4 py-2 bg-slate-900 rounded-full border border-slate-800">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">CTranslate2 Engine Active</span>
                  </div>
                </motion.div>
              ) : matches.length > 0 ? (
                <motion.div 
                  key="results"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="grid grid-cols-1 gap-4 pb-8"
                >
                  {matches.map((match, idx) => (
                    <motion.div 
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      key={idx} 
                      className="p-5 bg-slate-900/30 hover:bg-slate-900/60 rounded-3xl border border-slate-800/40 transition-all group hover:border-blue-500/20 hover:shadow-2xl hover:shadow-blue-500/5 relative overflow-hidden"
                    >
                      <div className="flex gap-6">
                        <div className="w-56 aspect-video bg-slate-950 rounded-2xl shrink-0 overflow-hidden relative group/vid border border-white/5 shadow-2xl">
                          <video 
                            className="w-full h-full object-cover opacity-60 group-hover/vid:opacity-100 transition-opacity"
                            onLoadedMetadata={(e) => {
                              e.currentTarget.currentTime = match.start;
                            }}
                            onMouseOver={(e) => e.currentTarget.play()}
                            onMouseOut={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = match.start; }}
                            muted
                            preload="metadata"
                          >
                            <source src={`https://asset.localhost${match.file.startsWith('/') ? '' : '/'}${match.file}`} type="video/mp4" />
                          </video>
                          <div className="absolute inset-0 flex items-center justify-center pointer-events-none group-hover/vid:opacity-0 transition-opacity bg-black/20">
                            <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center">
                              <Play size={20} className="text-white fill-white ml-1" />
                            </div>
                          </div>
                          <div className="absolute bottom-3 right-3 px-2 py-1 bg-black/80 backdrop-blur-md rounded-lg text-[10px] font-mono font-bold text-white border border-white/10">
                            {Math.floor(match.start / 60)}:{(match.start % 60).toFixed(0).padStart(2, '0')}
                          </div>
                        </div>
                        
                        <div className="flex-1 min-w-0 flex flex-col py-1">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-[10px] font-black text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-md border border-blue-500/20 uppercase tracking-widest truncate max-w-[200px]">
                                {match.file.split("/").pop()}
                              </span>
                              {match.score && (
                                <div className="flex items-center gap-1.5 text-[10px] font-mono font-black text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                                  <Sparkles size={10} />
                                  {Math.round(match.score * 100)}%
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex-1">
                            <p className="text-slate-100 text-sm leading-relaxed font-medium line-clamp-3 relative">
                              <span className="text-blue-500/40 text-2xl font-serif absolute -left-4 -top-1">"</span>
                              {match.content}
                              <span className="text-blue-500/40 text-2xl font-serif">"</span>
                            </p>
                          </div>
                          
                          <div className="mt-5 flex items-center gap-3">
                            <button 
                              onClick={(e) => {
                                const card = e.currentTarget.closest('.group');
                                const video = card?.querySelector('video');
                                if (video) {
                                  video.currentTime = match.start;
                                  video.play();
                                }
                              }}
                              className="px-4 py-2 bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white text-[10px] font-black uppercase tracking-widest rounded-xl border border-blue-500/20 transition-all flex items-center gap-2"
                            >
                              <Play size={12} fill="currentColor" />
                              Preview Clip
                            </button>
                            <button 
                              onClick={() => onOpenFolder(match.file)}
                              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white text-[10px] font-black uppercase tracking-widest rounded-xl border border-slate-700/50 transition-all flex items-center gap-2"
                            >
                              <FolderOpen size={12} />
                              Source
                            </button>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              ) : hasSearched ? (
                <motion.div 
                  key="no-results"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="h-full flex flex-col items-center justify-center text-slate-700 p-12"
                >
                  <div className="w-24 h-24 rounded-full bg-slate-900/50 flex items-center justify-center mb-6 border border-slate-800">
                    <X size={48} className="opacity-20" />
                  </div>
                  <p className="text-xl font-black uppercase tracking-[0.2em] mb-2 opacity-50">Zero Matches</p>
                  <p className="text-xs text-slate-600 font-medium">Try a different keyword or lower the threshold</p>
                </motion.div>
              ) : (
                <motion.div 
                  key="idle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="h-full flex flex-col items-center justify-center text-slate-800 p-12"
                >
                  <div className="grid grid-cols-2 gap-4 max-w-md">
                    <div className="p-6 bg-slate-900/20 rounded-3xl border border-slate-800/40 text-center space-y-3">
                      <Hash className="mx-auto opacity-20" size={32} />
                      <p className="text-[10px] font-black uppercase tracking-widest opacity-40">Fragment</p>
                      <p className="text-[9px] text-slate-600 leading-tight">Precise word matching with sub-second accuracy.</p>
                    </div>
                    <div className="p-6 bg-slate-900/20 rounded-3xl border border-slate-800/40 text-center space-y-3">
                      <Activity className="mx-auto opacity-20" size={32} />
                      <p className="text-[10px] font-black uppercase tracking-widest opacity-40">Sentence</p>
                      <p className="text-[9px] text-slate-600 leading-tight">Returns full sentences containing your query.</p>
                    </div>
                    <div className="p-6 bg-slate-900/20 rounded-3xl border border-slate-800/40 text-center space-y-3">
                      <Sparkles className="mx-auto opacity-20" size={32} />
                      <p className="text-[10px] font-black uppercase tracking-widest opacity-40">Semantic</p>
                      <p className="text-[9px] text-slate-600 leading-tight">Search by concepts using neural embeddings.</p>
                    </div>
                    <div className="p-6 bg-slate-900/20 rounded-3xl border border-slate-800/40 text-center space-y-3">
                      <Scissors className="mx-auto opacity-20" size={32} />
                      <p className="text-[10px] font-black uppercase tracking-widest opacity-40">Mashup</p>
                      <p className="text-[9px] text-slate-600 leading-tight">Randomized clips of a specific recurring term.</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* NGrams Panel */}
          <div className="w-80 bg-slate-950/40 rounded-4xl border border-slate-800/60 flex flex-col overflow-hidden shadow-inner">
            <div className="p-5 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <BarChart3 size={14} className="text-purple-500" />
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">LINGUISTIC N-GRAMS</span>
              </div>
              <div className="flex p-0.5 bg-slate-950 rounded-lg border border-slate-800">
                {[1, 2, 3].map(n => (
                  <button 
                    key={n}
                    onClick={() => setNgramN(n)}
                    className={`px-2.5 py-1 rounded-md text-[9px] font-black transition-all ${ngramN === n ? "bg-slate-800 text-purple-400" : "text-slate-600 hover:text-slate-400"}`}
                  >
                    {n}G
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-1.5 custom-scrollbar">
              <AnimatePresence mode="wait">
                {isNgramsLoading ? (
                  <div className="h-full flex flex-col items-center justify-center p-8 space-y-4 opacity-50">
                    <div className="w-6 h-6 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin"></div>
                    <span className="text-[9px] font-black uppercase tracking-widest text-slate-600">Analyzing...</span>
                  </div>
                ) : ngrams.length > 0 ? (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-1"
                  >
                    {ngrams.slice(0, 50).map((g, i) => (
                      <button
                        key={i}
                        onClick={() => {
                          setQuery(g.ngram);
                          setHasSearched(true);
                          setStartTime(performance.now());
                          onSearch(g.ngram, searchType, threshold);
                          searchInputRef.current?.focus();
                        }}
                        className="w-full group text-left p-3 rounded-2xl hover:bg-purple-500/5 border border-transparent hover:border-purple-500/20 transition-all flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="w-6 h-6 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 group-hover:border-purple-500/30 group-hover:bg-purple-500/10 transition-colors">
                            <span className="text-[9px] font-mono text-slate-600 group-hover:text-purple-400">{i + 1}</span>
                          </div>
                          <span className="text-xs text-slate-300 font-medium group-hover:text-white truncate pr-2">{g.ngram}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono font-bold text-slate-600 group-hover:text-purple-500">{g.count}</span>
                          <ChevronRight size={10} className="text-slate-800 group-hover:text-purple-500 transition-colors" />
                        </div>
                      </button>
                    ))}
                  </motion.div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center p-8 text-center opacity-40">
                    <BarChart3 size={32} className="mb-4 text-slate-800" />
                    <p className="text-[10px] font-black uppercase tracking-widest text-slate-600 leading-relaxed">
                      Select a transcribed video to view linguistic patterns
                    </p>
                  </div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Search Input Bar */}
        <div className="mt-10 relative z-10">
          <div className="relative group">
            <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none text-slate-500 text-xl group-focus-within:text-blue-500 transition-colors">
              <Search size={24} />
            </div>
            <input
              ref={searchInputRef}
              type="text"
              placeholder={searchType === "mash" ? "Enter a word to mashup (e.g. 'actually')..." : `Search ${searchType} in video...`}
              className={`w-full bg-slate-950/80 border border-slate-800 rounded-3xl pl-16 pr-32 py-6 text-xl font-medium focus:outline-none focus:ring-4 transition-all placeholder:text-slate-800 shadow-2xl backdrop-blur-xl ${
                searchType === "mash" ? "focus:ring-purple-500/10 border-purple-500/30" : "focus:ring-blue-500/10 border-blue-500/30"
              }`}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <div className="absolute right-4 inset-y-4 flex gap-2">
              {query && (
                <button 
                  onClick={clearSearch}
                  className="px-4 text-slate-600 hover:text-slate-400 transition-colors"
                >
                  <X size={20} />
                </button>
              )}
            <button 
                onClick={triggerSearch} 
                disabled={isSearching}
                className={`px-8 h-full rounded-2xl font-black text-xs uppercase tracking-widest transition-all active:scale-95 shadow-lg flex items-center gap-2 ${
                  isSearching ? "bg-slate-800 text-slate-500 cursor-not-allowed" :
                  searchType === "mash" 
                    ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-purple-900/20" 
                    : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20"
                }`}
              >
                {isSearching ? <Loader2 size={14} className="animate-spin" /> : null}
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Timeline Heatmap */}
      <section className="glass p-8 rounded-4xl border border-slate-800 shadow-xl relative overflow-hidden group/heatmap">
        <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/5 blur-[60px] rounded-full pointer-events-none" />
        
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-sm font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)] animate-pulse"></div>
            Search Density • Temporal Distribution
          </h2>
          <div className="flex items-center gap-4 text-[10px] font-mono text-slate-600 uppercase tracking-widest">
            <span className="flex items-center gap-1.5"><Clock size={10} /> Normalized Scope</span>
            <span className="w-px h-3 bg-slate-800"></span>
            <span>{matches.length} Key Points</span>
          </div>
        </div>

        <div className="h-20 w-full bg-slate-950/80 rounded-2xl flex items-end overflow-hidden border border-slate-800/80 p-3 gap-1 shadow-inner">
          {heatmapData.map((val, i) => (
            <motion.div 
              key={i} 
              initial={{ height: "5%" }}
              animate={{ height: `${Math.max(val * 100, 5)}%` }}
              transition={{ delay: i * 0.01, duration: 0.5 }}
              className={`flex-1 rounded-full transition-all duration-300 ${
                val > 0 
                  ? "bg-gradient-to-t from-red-600 to-orange-400 shadow-[0_0_15px_rgba(239,68,68,0.2)]" 
                  : "bg-slate-900/30 group-hover/heatmap:bg-slate-900/50"
              }`}
              style={{ opacity: val > 0 ? 0.4 + (val * 0.6) : 0.15 }}
            />
          ))}
        </div>
        
        <div className="flex justify-between mt-4 text-[9px] font-black text-slate-600 uppercase tracking-[0.3em] px-1">
          <span className="flex items-center gap-2"><div className="w-1 h-1 bg-slate-800 rounded-full" /> START OF TIMELINE</span>
          <span className="text-slate-800 tracking-normal opacity-50">Density Projection Map</span>
          <span className="flex items-center gap-2">END OF SCOPE <div className="w-1 h-1 bg-slate-800 rounded-full" /></span>
        </div>
      </section>
    </div>
  );
}
