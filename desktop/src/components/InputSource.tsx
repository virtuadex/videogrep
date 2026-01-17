import { AppStatus } from "../types";
import { motion, AnimatePresence } from "framer-motion";
import { Download, Cpu, Activity, AlertCircle, Youtube, Loader2 } from "lucide-react";

interface InputSourceProps {
  url: string;
  setUrl: (url: string) => void;
  useGPU: boolean;
  setUseGPU: (use: boolean) => void;
  status: AppStatus;
  progress: number;
  onDownload: () => void;
}

export function InputSource({
  url,
  setUrl,
  useGPU,
  setUseGPU,
  status,
  progress,
  onDownload,
}: InputSourceProps) {
  const isProcessing = status !== "idle" && status !== "error";

  return (
    <section className="glass p-6 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
      
      <h2 className="text-lg font-bold mb-6 flex items-center gap-3">
        <div className="p-2 bg-blue-500/20 rounded-xl text-blue-400">
          <Download size={20} />
        </div>
        INPUT SOURCE
      </h2>

      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Video URL / Local Path</label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-blue-500 transition-colors">
              <Youtube size={18} />
            </div>
            <input
              type="text"
              placeholder="Paste YouTube URL or Local File..."
              className="w-full bg-slate-950/50 border border-slate-800 rounded-2xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-all placeholder:text-slate-700"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isProcessing}
            />
          </div>
        </div>

        <div className="flex items-center gap-3 px-1 py-3 bg-slate-900/30 rounded-2xl border border-slate-800/50">
          <div className={`p-2 rounded-lg transition-colors ${useGPU ? "bg-amber-500/20 text-amber-500" : "bg-slate-800 text-slate-500"}`}>
            <Cpu size={16} />
          </div>
          <div className="flex-1">
            <div className="text-[10px] font-black text-slate-400 uppercase tracking-tight">Acceleration</div>
            <label
              htmlFor="gpuToggle"
              className="text-xs text-slate-500 cursor-pointer select-none flex items-center justify-between"
            >
              Use GPU (Apple Silicon / CUDA)
              <input
                type="checkbox"
                id="gpuToggle"
                checked={useGPU}
                onChange={(e) => setUseGPU(e.target.checked)}
                className="w-4 h-4 accent-amber-500 rounded cursor-pointer"
                disabled={isProcessing}
              />
            </label>
          </div>
        </div>

        <button
          onClick={onDownload}
          disabled={isProcessing || !url}
          className={`w-full relative overflow-hidden group transition-all py-4 rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-lg active:scale-95 flex items-center justify-center gap-3 ${
            isProcessing 
              ? "bg-slate-800 text-slate-500" 
              : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20"
          }`}
        >
          {isProcessing ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Activity size={16} className="group-hover:animate-pulse" />
              Analyze Video
            </>
          )}
        </button>

        <AnimatePresence>
          {status !== "idle" && (
            <motion.div 
              initial={{ opacity: 0, height: 0, y: 10 }}
              animate={{ opacity: 1, height: "auto", y: 0 }}
              exit={{ opacity: 0, height: 0, y: 10 }}
              className="mt-4 p-5 bg-slate-950/80 rounded-2xl border border-slate-800/80 shadow-inner"
            >
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  {status === "error" ? (
                    <AlertCircle size={14} className="text-red-500" />
                  ) : (
                    <div className={`w-2 h-2 rounded-full animate-ping ${
                      status === "downloading" ? "bg-blue-500" : 
                      status === "transcribing" ? "bg-purple-500" : "bg-green-500"
                    }`} />
                  )}
                  <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${
                    status === "downloading" ? "text-blue-400" :
                    status === "transcribing" ? "text-purple-400" :
                    status === "exporting" ? "text-green-400" : "text-red-400"
                  }`}>
                    {status === "downloading" ? "Downloading" :
                     status === "transcribing" ? "Transcribing" :
                     status === "exporting" ? "Exporting" : "Failed"}
                  </span>
                </div>
                <span className="text-xs font-mono text-slate-400">{Math.round(progress)}%</span>
              </div>
              
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-white/5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  className={`h-full shadow-[0_0_10px_rgba(0,0,0,0.5)] ${
                    status === "downloading" ? "bg-gradient-to-r from-blue-600 to-blue-400" :
                    status === "transcribing" ? "bg-gradient-to-r from-purple-600 to-purple-400" :
                    status === "exporting" ? "bg-gradient-to-r from-green-600 to-green-400" :
                    "bg-red-600"
                  }`}
                />
              </div>
              
              {status === "transcribing" && (
                <p className="mt-3 text-[9px] text-slate-600 text-center italic leading-relaxed">
                  Extracting dialog patterns using Whisper neural network...
                </p>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
