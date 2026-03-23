import { create } from 'zustand';

interface BenchmarkData {
  rl_utilization: number;
  static_utilization: number;
  rl_revenue: number;
  static_revenue: number;
}

interface RideState {
  riders: number;
  drivers: number;
  timeOfDay: number; // 0=Morning, 1=Afternoon, 2=Evening, 3=Night
  trafficLevel: number; // 0, 1, 2
  multiplier: number;
  rlRevenue: number;
  staticRevenue: number;
  avgWaitTime: number;
  utilization: number;
  history: Record<string, unknown>[];
  isSimulationRunning: boolean;
  theme: 'dark' | 'light';
  benchmark: BenchmarkData | null;
  
  setControls: (controls: Partial<RideState>) => void;
  updateStats: (stats: Partial<RideState>) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setBenchmark: (benchmark: BenchmarkData) => void;
}

export const useStore = create<RideState>((set) => ({
  riders: 80,
  drivers: 30,
  timeOfDay: 2, // Evening
  trafficLevel: 1, // Medium
  multiplier: 1.0,
  rlRevenue: 0,
  staticRevenue: 0,
  avgWaitTime: 0,
  utilization: 0,
  history: [],
  isSimulationRunning: false,
  theme: 'dark',
  benchmark: null,
  
  setControls: (controls) => set((state) => ({ ...state, ...controls })),
  updateStats: (stats) => set((state) => ({ ...state, ...stats })),
  setTheme: (theme) => set({ theme }),
  setBenchmark: (benchmark) => set({ benchmark }),
}));
