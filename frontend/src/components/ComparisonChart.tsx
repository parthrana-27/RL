import { useStore } from '../store/useStore';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RTC, ResponsiveContainer, CartesianGrid, Cell, LineChart, Line } from 'recharts';

const ComparisonChart = () => {
    const { benchmark, history, globalRlRevenue, globalStaticRevenue } = useStore();
    const isTrained = !!benchmark;

    const revData = [
        { name: 'Static (1.0x)', Revenue: Math.round(globalStaticRevenue) },
        { name: isTrained ? 'RL Dynamic' : 'RL (Untrained)', Revenue: Math.round(globalRlRevenue) }
    ];

    const gain = globalStaticRevenue > 0 ? ((globalRlRevenue - globalStaticRevenue) / globalStaticRevenue * 100).toFixed(1) : "0";
    
    // Process history data for the line chart (multiplier over last 24 steps)
    const lineData = history.slice(-24).map((h, i) => ({
      step: `H-${24-i}`,
      Multiplier: h.multiplier,
      Reward: h.reward
    }));

    return (
        <div className="space-y-6 mt-6">
            <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800 shadow-xl overflow-hidden relative">
                <h3 className="font-bold text-lg text-zinc-100 flex items-center justify-between">
                    Revenue Comparison
                    {parseFloat(gain) > 0 && <span className="bg-primary/10 text-primary border border-primary/20 text-xs px-2 py-1 rounded-full animate-pulse">+{gain}%</span>}
                </h3>
                
                {globalRlRevenue > 0 ? (
                    <div className="h-44 mt-4 w-full relative z-10">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={revData} margin={{top: 20, right: 30, left: 0, bottom: 5}} barSize={50}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                                <XAxis dataKey="name" stroke="#71717a" fontSize={11} tickMargin={10} />
                                <RTC cursor={{fill: '#18181b', opacity: 0.5}} contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '12px', padding: '12px' }} formatter={(value) => [`$${value}`, "Revenue"]} />
                                <Bar dataKey="Revenue" radius={[6, 6, 0, 0]}>
                                  {
                                    revData.map((_, index) => (
                                      <Cell 
                                        key={`cell-${index}`} 
                                        fill={index === 0 ? '#71717a' : (isTrained ? '#22c55e' : '#3f3f46')} 
                                      />
                                    ))
                                  }
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                ) : (
                    <div className="h-44 mt-4 flex flex-col items-center justify-center text-zinc-600 border border-zinc-800/50 rounded-xl bg-zinc-900/30 relative overflow-hidden">
                        <div className="flex items-end gap-12 absolute inset-x-0 bottom-4 justify-center opacity-10 pointer-events-none">
                            <div className="w-10 h-16 bg-zinc-500 rounded-t-sm" />
                            <div className="w-10 h-24 bg-primary rounded-t-sm" />
                        </div>
                        <p className="text-xs font-bold uppercase tracking-widest text-zinc-500 relative z-10 mb-1">Graph Unavailable</p>
                        <p className="text-[10px] text-zinc-600 relative z-10 max-w-[200px] text-center">Run a global simulation to unlock real-time revenue comparisons</p>
                    </div>
                )}
            </div>

            {/* Micro-chart: Multiplier variation over 24h simulation */}
            {history.length > 0 && (
              <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800 shadow-xl">
                 <h3 className="font-bold text-sm text-zinc-100 mb-4">RL Multiplier Trajectory (24 Steps)</h3>
                 <div className="h-32">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={lineData}>
                             <CartesianGrid strokeDasharray="1 3" vertical={false} stroke="#27272a" />
                             <XAxis dataKey="step" hide />
                             <YAxis domain={[0.8, 2.2]} hide />
                             <RTC contentStyle={{ backgroundColor: '#09090b', border: '1px solid #27272a' }} />
                             <Line type="step" dataKey="Multiplier" stroke="#a855f7" strokeWidth={2} dot={false} activeDot={{r: 6, fill: '#a855f7', stroke: '#09090b', strokeWidth: 2}} />
                        </LineChart>
                    </ResponsiveContainer>
                 </div>
              </div>
            )}
        </div>
    );
};

export default ComparisonChart;
