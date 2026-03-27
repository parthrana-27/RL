import { motion } from 'framer-motion';
import { useStore } from '../store/useStore';
import { Target, TrendingUp, TrendingDown, Users } from 'lucide-react';

const BenchmarkResults = () => {
    const { benchmark } = useStore();

    if (!benchmark) {
        return (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-zinc-900/60 p-8 rounded-2xl border border-zinc-800/80 border-dashed relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 opacity-50"/>
                
                <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
                    <div className="flex-1 text-center md:text-left">
                        <div className="inline-flex p-3 bg-zinc-800 rounded-xl mb-4 border border-zinc-700 shadow-inner">
                            <Target size={24} className="text-zinc-500 animate-pulse" />
                        </div>
                        <h3 className="text-2xl font-black text-zinc-200 tracking-tight">Post-Training Benchmark</h3>
                        <p className="text-zinc-500 text-sm mt-2 max-w-sm leading-relaxed">
                            A rigorous 1,000-step validation will appear here once the model is trained. It benchmarks the <span className="text-zinc-400 font-bold">RL Policy</span> against <span className="text-zinc-400 font-bold">Static Pricing</span>.
                        </p>
                    </div>
                    
                    <div className="w-full md:w-auto flex flex-col gap-3 opacity-30 blur-[1px] grayscale pointer-events-none select-none">
                        <div className="bg-zinc-800/50 p-4 rounded-xl border border-zinc-700 w-48">
                            <div className="w-12 h-2 bg-zinc-600 rounded mb-3"/>
                            <div className="w-24 h-6 bg-zinc-500 rounded font-mono font-black text-xs flex items-center px-2">$---,---</div>
                        </div>
                        <div className="bg-zinc-800/50 p-4 rounded-xl border border-zinc-700 w-48">
                            <div className="w-16 h-2 bg-zinc-600 rounded mb-3"/>
                            <div className="w-20 h-6 bg-zinc-500 rounded font-mono font-black text-xs flex items-center px-2">--.-%</div>
                        </div>
                    </div>
                </div>

                <div className="mt-8 flex justify-center md:justify-start relative z-10">
                     <div className="px-4 py-2 bg-zinc-800/80 border border-zinc-700 rounded-lg text-xs font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
                         <div className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-pulse" />
                         Analysis Engine Standby
                     </div>
                </div>
            </motion.div>
        );
    }

    const { rl_utilization, static_utilization, rl_revenue, static_revenue } = benchmark;
    
    // Ensure safe divisor
    const revSafe = static_revenue === 0 ? 1 : static_revenue;
    const revDiff = (((rl_revenue - static_revenue) / revSafe) * 100).toFixed(1);
    const utilDiff = (rl_utilization - static_utilization).toFixed(1);

    const isRevPositive = rl_revenue >= static_revenue;
    const isUtilPositive = rl_utilization >= static_utilization;

    return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-zinc-900/80 p-6 sm:p-8 rounded-2xl border border-zinc-800 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -z-10 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-secondary/5 rounded-full blur-3xl -z-10 pointer-events-none" />
            
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-zinc-800 rounded-lg border border-zinc-700 shadow-inner">
                    <Target size={20} className="text-primary" />
                </div>
                <div>
                    <h2 className="text-xl font-extrabold text-zinc-100">Live 1K-Step Validation</h2>
                    <p className="text-sm text-zinc-400">Post-training dynamic simulation</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Revenue Card */}
                <div className="bg-zinc-950/80 border border-zinc-800 p-5 rounded-xl flex flex-col justify-between group hover:border-zinc-700 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                        <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Total Revenue</p>
                        <div className={`px-2 py-1 rounded text-xs font-bold flex items-center gap-1 ${isRevPositive ? 'bg-primary/20 text-primary' : 'bg-red-500/20 text-red-400'}`}>
                            {isRevPositive ? <TrendingUp size={12}/> : <TrendingDown size={12}/>}
                            {revDiff}%
                        </div>
                    </div>
                    
                    <div className="flex flex-col gap-3">
                        <div>
                            <p className="text-xs text-zinc-500 mb-1">RL Agent</p>
                            <p className="text-2xl font-black font-mono text-zinc-100">${rl_revenue.toLocaleString()}</p>
                        </div>
                        <div className="w-full h-px bg-zinc-800/50" />
                        <div>
                            <p className="text-xs text-zinc-500 mb-1">Static Rule</p>
                            <p className="text-xl font-bold font-mono text-zinc-400">${static_revenue.toLocaleString()}</p>
                        </div>
                    </div>
                </div>

                {/* Utilization Card */}
                <div className="bg-zinc-950/80 border border-zinc-800 p-5 rounded-xl flex flex-col justify-between group hover:border-zinc-700 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                        <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Fleet Utilization</p>
                        <div className={`px-2 py-1 rounded text-xs font-bold flex items-center gap-1 ${isUtilPositive ? 'bg-secondary/20 text-secondary' : 'bg-red-500/20 text-red-400'}`}>
                            {isUtilPositive ? <TrendingUp size={12}/> : <TrendingDown size={12}/>}
                            +{utilDiff}%
                        </div>
                    </div>
                    
                    <div className="flex flex-col gap-3">
                        <div>
                            <p className="text-xs text-zinc-500 mb-1">RL Agent</p>
                            <div className="flex items-baseline gap-2">
                                <p className="text-2xl font-black font-mono text-zinc-100">{rl_utilization.toFixed(1)}%</p>
                                <span className="text-xs text-zinc-500 font-medium">riders secured</span>
                            </div>
                        </div>
                        <div className="w-full h-px bg-zinc-800/50" />
                        <div>
                            <p className="text-xs text-zinc-500 mb-1">Static Rule</p>
                            <p className="text-xl font-bold font-mono text-zinc-400">{static_utilization.toFixed(1)}%</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div className="mt-6 bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 flex gap-3 text-blue-200">
                <Users size={18} className="shrink-0 mt-0.5" />
                <p className="text-sm">
                    <strong>Observation:</strong> Often, the RL Agent intentionally drops prices slightly underneath static barriers to dramatically enhance active fleet utilization (booking volume), reflecting <span className="text-blue-300 font-medium">real-world surge balancing behaviors</span>.
                </p>
            </div>
        </motion.div>
    );
};

export default BenchmarkResults;
