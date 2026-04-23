import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { apiFetch } from '../api';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface PortfolioItem {
    symbol: string;
    price: number;
    trend: 'up' | 'down';
    change_pct?: number;
    stale?: boolean;
}

const PortfolioPanel = () => {
    const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPortfolio = async () => {
            try {
                const data = await apiFetch('/investments/portfolio');
                setPortfolio(data.portfolio);
            } catch {
                setPortfolio([]);
            } finally {
                setLoading(false);
            }
        };
        fetchPortfolio();
    }, []);

    const totalValue = portfolio.reduce((sum, item) => sum + item.price, 0);

    const data = {
        labels: portfolio.map((p) => p.symbol),
        datasets: [
            {
                label: 'Allocation',
                data: portfolio.map((p) => ((p.price / (totalValue || 1)) * 100)),
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(244, 63, 94, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                ],
                borderRadius: 4,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (context: any) => `${context.raw.toFixed(1)}%`,
                },
            },
        },
        scales: {
            y: {
                display: false,
                grid: { display: false },
            },
            x: {
                grid: { display: false, drawBorder: false },
                ticks: { color: 'rgba(255, 255, 255, 0.5)' },
            },
        },
    };

    if (loading) {
        return (
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-12 flex justify-center">
                <div className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="text-xl font-bold">Investment Portfolio</h3>
                    </div>
                    <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-md border border-indigo-500/30">
                        {portfolio.some(p => p.stale) ? 'Cached Data' : 'Live Data'}
                    </span>
                </div>

                <div className="h-[200px] mb-6">
                    <Bar data={data} options={options} />
                </div>

                <div className="space-y-3">
                    {portfolio.map((item) => (
                        <div key={item.symbol} className="flex items-center justify-between p-3 bg-neutral-800/50 rounded-xl border border-white/5 hover:bg-neutral-800 transition-colors">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-neutral-900 flex items-center justify-center font-bold text-neutral-300 border border-white/5">
                                    {item.symbol.substring(0, 2)}
                                </div>
                                <div>
                                    <div className="font-bold flex items-center gap-2">{item.symbol}</div>
                                    <div className="text-xs text-neutral-500">ETF</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold text-sm">${item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                                <div className={`text-xs flex items-center justify-end font-medium ${item.trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {item.trend === 'up' ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                                    <span>{item.change_pct ? `${item.change_pct > 0 ? '+' : ''}${item.change_pct}%` : item.trend}</span>
                                    {item.stale && <span className="text-neutral-600 ml-1">(cached)</span>}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
export default PortfolioPanel;
