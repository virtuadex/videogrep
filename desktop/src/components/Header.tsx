import { motion, AnimatePresence } from "framer-motion";
import { Zap, CheckCircle2 } from "lucide-react";

interface HeaderProps {
  message?: string | null;
}

export function Header({ message }: HeaderProps) {
  return (
    <header className="mb-12 flex justify-between items-start">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-5xl font-black bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent tracking-tighter">
          VOXGREP
        </h1>
        <div className="flex items-center gap-4 mt-2">
          <div className="flex items-center gap-2 px-3 py-1 bg-slate-900/50 rounded-full border border-slate-800/50">
            <Zap size={12} className="text-amber-400 fill-amber-400/20" />
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              System Online • Ready
            </p>
          </div>
          
          <AnimatePresence>
            {message && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8, y: -10 }}
                className="flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.1)]"
              >
                <CheckCircle2 size={10} />
                {message}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
      <div className="text-right">
        <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">Build Version</div>
        <div className="text-xs font-mono text-slate-600 bg-slate-900/80 px-2 py-1 rounded border border-slate-800/50">
          v0.2.0-alpha
        </div>
      </div>
    </header>
  );
}
