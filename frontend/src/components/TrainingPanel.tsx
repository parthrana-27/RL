import { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

import { useStore } from '../store/useStore';

const TrainingPanel = () => {
    const [isTraining, setIsTraining] = useState(false);
    const [progress, setProgress] = useState(0);
    const [metrics, setMetrics] = useState<Array<{ name: string; Reward: number; WaitTime?: number }>>([]);

    const startTraining = async () => {
        setIsTraining(true);
        setProgress(0);
        
        const interval = setInterval(() => {
            setProgress(p => Math.min(p + 5, 95));
        }, 300);

        try {
            const res = await axios.post('/api/train', { episodes: 1000 });
            clearInterval(interval);
            setProgress(100);
            
            const benchmark = res.data.benchmark;
            if (benchmark) {
                useStore.getState().setBenchmark(benchmark);
            }
            
            const m = res.data.metrics;
            const formatted = m.rewards.map((_: number, i: number) => ({
                name: `Ep ${i}`,
                Reward: Math.round(m.rewards[i])
            }));
            setMetrics(formatted);
        } catch (err) {
            console.error(err);
            alert("Backend logic error: Ensure backend is running at :8000");
            clearInterval(interval);
        } finally {
            setIsTraining(false);
        }
    };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800 shadow-xl mt-6 relative overflow-hidden">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4 relative z-10">
                <div>
                    <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-[#86efac]">Q-Learning Model Training</h2>
                    <p className="text-sm text-zinc-400 mt-1">Train the tabular Q-learning agent on simulated environment</p>
                </div>
                <button 
                  onClick={startTraining} 
                  disabled={isTraining}
                  className="bg-primary text-zinc-950 px-5 py-2.5 rounded-lg border-b-4 border-green-700 font-bold active:border-b-0 active:translate-y-1 transition-all disabled:opacity-50 disabled:border-b-0 disabled:translate-y-1"
                >
                    {isTraining ? 'Training...' : '▶ Start (1000 Episodes)'}
                </button>
            </div>
            
            {(isTraining || progress > 0) && (
                <div className="mb-6 relative z-10">
                    <div className="flex justify-between text-xs text-zinc-400 mb-2">
                        <span>Epsilon Decay: {Math.max(0.01, 1 - progress/100).toFixed(2)}</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="w-full bg-zinc-950 rounded-full h-3 border border-zinc-800 overflow-hidden">
                        <motion.div 
                          className="bg-gradient-to-r from-secondary to-primary h-full" 
                          initial={{ width: 0 }} 
                          animate={{ width: `${progress}%` }} 
                        />
                    </div>
                </div>
            )}

            {metrics.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="h-64 mt-8 relative z-10">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={metrics}>
                            <XAxis dataKey="name" stroke="#52525b" fontSize={11} tickMargin={10} />
                            <YAxis stroke="#52525b" fontSize={11} orientation="right" />
                            <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '8px' }} itemStyle={{color: '#fff'}} />
                            <Line type="monotone" dataKey="Reward" stroke="#a855f7" strokeWidth={3} dot={false} animationDuration={2000} />
                        </LineChart>
                    </ResponsiveContainer>
                    <div className="absolute top-0 left-0 bg-secondary/10 border border-secondary/30 text-secondary text-xs px-2 py-1 rounded">Reward Avg over Episodes</div>
                </motion.div>
            )}
            
            {/* Background design elements */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-primary/5 rounded-full blur-3xl" />
        </motion.div>
    );
};

export default TrainingPanel;
