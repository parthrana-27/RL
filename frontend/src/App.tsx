import BenchmarkResults from './components/BenchmarkResults';
import TrainingPanel from './components/TrainingPanel';
import Controls from './components/Controls';
import ComparisonChart from './components/ComparisonChart';
import { useStore } from './store/useStore';
import { motion } from 'framer-motion';
import { Download, RefreshCw, Moon, Sun, MonitorPlay } from 'lucide-react';


function App() {
  const { multiplier, rlRevenue, avgWaitTime, utilization, theme, setTheme, history } = useStore();

  const handleExportCSV = () => {
    if(!history.length) return alert('No simulation history to export.');
    
    const csvRows = [];
    csvRows.push(['Step', 'Multiplier', 'Reward', 'Wait_Time', 'TimeOfDay', 'Traffic_Level'].join(','));
    history.forEach(row => {
        csvRows.push([row.step, row.multiplier, row.reward, row.wait_time, row.time_val, row.traffic_val].join(','));
    });
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', 'simulation_history.csv');
    a.click();
  };

  return (
    <div className={`min-h-screen font-sans ${theme === 'dark' ? 'bg-[#050505] text-white' : 'bg-white text-zinc-950'} transition-colors duration-500`}>
      <div className="max-w-[1400px] mx-auto p-4 md:p-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between py-4 mb-8">
            <div>
                <motion.h1 initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="text-3xl md:text-4xl font-extrabold tracking-tighter flex flex-col md:flex-row items-start md:items-center justify-start gap-3">
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary relative shrink-0">
                        RideSurge RL
                        <div className="absolute -inset-1 blur-2xl bg-gradient-to-r from-primary/30 to-secondary/30 -z-10 rounded-full"/>
                    </span>
                </motion.h1>
                <p className="text-zinc-400 font-medium text-sm mt-3 tracking-wide flex items-center gap-2">
                    <MonitorPlay size={14} className="text-primary shrink-0"/> AI that prices rides smarter <span className="border border-primary/30 bg-primary/10 text-primary/90 rounded-full px-2 py-0.5 text-xs ml-1">(India Edition)</span>
                </p>
            </div>
            <div className="flex gap-3 mt-4 md:mt-0">
                <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="p-2.5 bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg hover:text-white transition-colors">
                    {theme === 'dark' ? <Sun size={18}/> : <Moon size={18}/>}
                </button>
                <button className="flex items-center gap-2 text-sm px-4 py-2.5 bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-red-400 rounded-lg transition-colors font-medium">
                    <RefreshCw size={16}/> Reset Env
                </button>
                <button onClick={handleExportCSV} className="flex items-center gap-2 text-sm px-5 py-2.5 border border-zinc-700 bg-zinc-800/80 backdrop-blur text-zinc-100 hover:border-zinc-500 rounded-lg transition-colors font-medium relative group overflow-hidden">
                    <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity"/>
                    <Download size={16}/> Export Trajectory
                </button>
            </div>
        </header>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
            
            {/* Left Column (Main views) */}
            <div className="col-span-1 lg:col-span-8 flex flex-col gap-6">
                
                {/* Stats cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { l: 'Live Multiplier', v: `${multiplier.toFixed(1)}x`, c: 'text-primary' },
                      { l: 'Total Revenue', v: `$${Math.round(rlRevenue)}`, c: 'text-white' },
                      { l: 'Avg Wait Time', v: `${Math.round(avgWaitTime)}s`, c: 'text-white' },
                      { l: 'Driver Utilization', v: `${utilization.toFixed(1)}%`, c: 'text-secondary' }
                    ].map((s, i) => (
                      <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="bg-zinc-900/50 backdrop-blur-md p-5 rounded-2xl border border-zinc-800 hover:bg-zinc-800/50 transition-colors relative overflow-hidden group">
                          <div className="absolute -inset-0.5 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity z-0 pointer-events-none"/>
                          <p className="text-zinc-500 text-xs font-bold uppercase tracking-widest relative z-10">{s.l}</p>
                          <p className={`text-3xl font-black font-mono mt-2 tracking-tight ${s.c} relative z-10 drop-shadow-sm`}>{s.v}</p>
                      </motion.div>
                    ))}
                </div>

                {/* Benchmark Validation */}
                <BenchmarkResults />
                
                {/* Training */}
                <TrainingPanel />
            </div>

            {/* Right Column (Controls & Analytics) */}
            <div className="col-span-1 lg:col-span-4 flex flex-col">
                <Controls />
                <ComparisonChart />
            </div>
            
        </div>

        {/* Footer */}
        <footer className="mt-20 py-8 border-t border-zinc-800/50 text-center text-xs text-zinc-500 flex flex-col md:flex-row justify-between items-center bg-zinc-950/20 px-8 rounded-2xl gap-4 md:gap-0">
            <p className="font-medium tracking-wide text-zinc-400">
                Built with <span className="text-primary italic">Q-Learning</span> + <span className="text-secondary italic">FastAPI</span> + <span className="text-blue-400 italic">React 18</span> — <span className="text-zinc-300">India Dataset Powered</span>
            </p>
            <div className="flex gap-6 font-medium tracking-wider">
                <a href="https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard" target="_blank" rel="noreferrer" className="hover:text-primary hover:underline transition-all underline-offset-4">India Kaggle Dataset</a>
                <a href="#" className="hover:text-secondary hover:underline transition-all underline-offset-4">GitHub Repository</a>
            </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
