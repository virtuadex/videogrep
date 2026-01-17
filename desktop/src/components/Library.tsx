import { useState } from "react";
import { VideoFile } from "../types";
import { motion, AnimatePresence } from "framer-motion";
import { Library as LibraryIcon, Search, CheckCircle, Clock, HardDrive, Filter } from "lucide-react";

interface LibraryProps {
  library: VideoFile[];
  onSelect: (video: VideoFile) => void;
  selectedVideoPath?: string;
}

export function Library({ library, onSelect, selectedVideoPath }: LibraryProps) {
  const [filter, setFilter] = useState("");

  const filteredLibrary = library.filter(v => 
    v.filename.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <section className="glass p-6 rounded-3xl border border-slate-800 h-[600px] flex flex-col shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 rounded-xl text-purple-400">
            <LibraryIcon size={20} />
          </div>
          LIBRARY
        </h2>
        <span className="text-[10px] font-mono text-slate-500 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
          {library.length} ITEMS
        </span>
      </div>

      <div className="relative mb-6">
        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-slate-500">
          <Search size={14} />
        </div>
        <input 
          type="text" 
          placeholder="Filter library..." 
          className="w-full bg-slate-950/50 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-purple-500/50 transition-all placeholder:text-slate-700"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        {filter && (
          <button 
            onClick={() => setFilter("")}
            className="absolute inset-y-0 right-3 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
          >
            <span className="text-xs font-bold uppercase tracking-tighter">Clear</span>
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {filteredLibrary.length > 0 ? (
            filteredLibrary.map((video, idx) => (
              <motion.div
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2, delay: idx * 0.03 }}
                key={video.path}
                onClick={() => onSelect(video)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer group relative overflow-hidden ${
                  selectedVideoPath === video.path
                    ? "bg-blue-600/10 border-blue-500/50 shadow-[0_0_20px_rgba(59,130,246,0.1)]" 
                    : "bg-slate-900/40 hover:bg-slate-900/60 border-slate-800/50 hover:border-slate-700"
                }`}
              >
                {selectedVideoPath === video.path && (
                  <motion.div 
                    layoutId="active-indicator"
                    className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500" 
                  />
                )}
                
                <div className={`font-bold text-sm truncate transition-colors ${
                  selectedVideoPath === video.path ? "text-blue-400" : "group-hover:text-blue-300"
                }`}>
                  {video.filename}
                </div>
                
                <div className="flex flex-col gap-1.5 mt-3">
                  <div className="flex justify-between items-center text-[10px] font-mono uppercase tracking-tight">
                    <div className="flex items-center gap-3 text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock size={10} />
                        {new Date(video.created_at * 1000).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <HardDrive size={10} />
                        {(video.size_bytes / (1024 * 1024)).toFixed(1)}MB
                      </span>
                    </div>
                  </div>
                  
                  <div className={`flex items-center gap-1.5 text-[9px] font-black uppercase tracking-widest ${
                    video.has_transcript ? "text-green-500" : "text-amber-500"
                  }`}>
                    {video.has_transcript ? (
                      <>
                        <CheckCircle size={10} />
                        <span>Transcribed</span>
                      </>
                    ) : (
                      <>
                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                        <span>Ready to process</span>
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-700 p-8 text-center">
              <Filter size={32} className="mb-4 opacity-20" />
              <p className="text-xs font-bold uppercase tracking-widest opacity-50">No matches found</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
