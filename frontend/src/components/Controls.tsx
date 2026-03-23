import { useStore } from '../store/useStore';
import axios from 'axios';

const Controls = () => {
    const { riders, drivers, timeOfDay, trafficLevel, setControls, updateStats, isSimulationRunning } = useStore();

    const runSimulation = async () => {
        setControls({ isSimulationRunning: true });
        try {
            const predRes = await axios.post('/api/simulate', {
                steps: 1,
                riders,
                drivers,
                time_val: timeOfDay,
                traffic_val: trafficLevel
            });
            
            if (predRes.data.simulation) {
                updateStats({ 
                    multiplier: predRes.data.simulation.recommended_multiplier
                });
            }

            const batchRes = await axios.post('/api/simulate', { steps: 24 });
            const s = batchRes.data.summary;
            updateStats({
                history: batchRes.data.history,
                rlRevenue: s.rl_revenue,
                staticRevenue: s.static_revenue,
                avgWaitTime: s.avg_wait_time,
                utilization: s.utilization
            });

        } catch (e) {
            console.error(e);
            alert("Backend is not running. Please start uvicorn in terminal.");
        } finally {
            setControls({ isSimulationRunning: false });
        }
    };

    return (
        <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800 shadow-xl mt-0">
            <h3 className="text-xl font-bold mb-6 text-zinc-100 flex items-center justify-between">
                Simulation Controls
            </h3>
            
            <div className="space-y-6">
                <div>
                    <label className="flex justify-between text-sm text-zinc-400 font-medium mb-1">
                        <span>Riders Demand</span>
                        <span className="text-primary font-bold">{riders}</span>
                    </label>
                    <input type="range" min="10" max="250" value={riders} onChange={(e) => setControls({riders: parseInt(e.target.value)})} className="w-full h-2 md:h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-primary" />
                </div>
                
                <div>
                    <label className="flex justify-between text-sm text-zinc-400 font-medium mb-1">
                        <span>Drivers Available</span>
                        <span className="text-secondary font-bold">{drivers}</span>
                    </label>
                    <input type="range" min="5" max="150" value={drivers} onChange={(e) => setControls({drivers: parseInt(e.target.value)})} className="w-full h-2 md:h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-secondary" />
                </div>
                
                <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="flex flex-col">
                        <label className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-2">Time of Day</label>
                        <select value={timeOfDay} onChange={(e) => setControls({timeOfDay: parseInt(e.target.value)})} className="bg-zinc-950/50 border border-zinc-700/50 hover:border-zinc-500 focus:border-primary transition-colors focus:outline-none rounded-lg p-3 text-sm font-medium text-zinc-200">
                            <option value={0}>Morning</option>
                            <option value={1}>Afternoon</option>
                            <option value={2}>Evening</option>
                            <option value={3}>Night</option>
                        </select>
                    </div>
                    <div className="flex flex-col">
                        <label className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-2">Traffic Level</label>
                        <select value={trafficLevel} onChange={(e) => setControls({trafficLevel: parseInt(e.target.value)})} className="bg-zinc-950/50 border border-zinc-700/50 hover:border-zinc-500 focus:border-secondary transition-colors focus:outline-none rounded-lg p-3 text-sm font-medium text-zinc-200">
                            <option value={0}>Low Traffic</option>
                            <option value={1}>Medium Traffic</option>
                            <option value={2}>High Traffic</option>
                        </select>
                    </div>
                </div>
                
                <div className="pt-4">
                    <button 
                        onClick={runSimulation} 
                        disabled={isSimulationRunning} 
                        className="w-full py-4 rounded-xl font-bold uppercase tracking-wider text-sm transition-all shadow-lg active:scale-95 disabled:scale-100 disabled:opacity-50"
                        style={{ backgroundColor: isSimulationRunning ? '#3f3f46' : '#22c55e', color: isSimulationRunning ? '#a1a1aa' : '#09090b', boxShadow: isSimulationRunning ? 'none' : '0 10px 25px -5px rgba(34, 197, 94, 0.4)' }}
                    >
                        {isSimulationRunning ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="w-4 h-4 rounded-full border-2 border-zinc-400 border-t-transparent animate-spin"/> Simulating
                            </span>
                        ) : 'Run Global Simulation'}
                    </button>
                    <p className="text-center text-xs text-zinc-500 mt-3 flex items-center justify-center gap-1">
                        Trigger <code className="bg-zinc-800 px-1 rounded text-[10px]">/simulate</code> on backend
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Controls;
