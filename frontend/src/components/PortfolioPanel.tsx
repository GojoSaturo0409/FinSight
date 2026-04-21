import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Tooltip,
    Legend,
} from 'chart.js';
import { ArrowUpRight, ArrowDownRight, TrendingUp } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface PortfolioItem {
    symbol: string;
    price: number;
    trend: string;
    change_pct?: number;
    stale?: boolean;
}

const PortfolioPanel = () => {
    // Mock portfolio data (same structure as /investments/portfolio response)
    const portfolio: PortfolioItem[] = [
        { symbol: 'SPY', price: 523.40, trend: 'up', change_pct: 0.42 },
        { symbol: 'BND', price: 72.85, trend: 'up', change_pct: 0.21 },
        { symbol: 'VTI', price: 261.20, trend: 'up', change_pct: 0.54 },
    ];

    const totalValue = portfolio.reduce((sum, item) => sum + item.price, 0);

    const allocationData = {
        labels: portfolio.map((p) => p.symbol),
        datasets: [
            {
                label: 'Allocation',
                data: portfolio.map((p) => ((p.price / totalValue) * 100)),
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                ],
                borderWidth: 0,
                borderRadius: 6,
                barThickness: 28,
            },
        ],
    };

    const allocationOptions = {
        indexAxis: 'y' as const,
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(10, 10, 10, 0.95)',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                titleColor: '#e5e5e5',
                bodyColor: '#a3a3a3',
                padding: 10,
                cornerRadius: 8,
                callbacks: {
                    label: function (context: any) {
                        return `${context.parsed.x.toFixed(1)}%`;
                    },
                },
            },
        },
        scales: {
            x: {
                grid: { color: 'rgba(255,255,255,0.03)' },
                border: { display: false },
                ticks: {
                    color: '#737373',
                    font: { size: 10 },
                    callback: function (value: any) { return value + '%'; },
                },
                max: 100,
            },
            y: {
                grid: { display: false },
                border: { display: false },
                ticks: { color: '#a3a3a3', font: { size: 12, weight: 'bold' as const } },
            },
        },
    };

    return (
        <div className="space-y-6">
            {/* Portfolio Header */}
            <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-xl border border-indigo-500/20 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <TrendingUp size={22} className="text-indigo-400" />
                        <h3 className="text-xl font-bold">Investment Portfolio</h3>
                    </div>
                    <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-md border border-indigo-500/30">
                        Live Data
                    </span>
                </div>

                {/* Portfolio items */}
                <div className="space-y-3 mt-6">
                    {portfolio.map((item) => (
                        <div key={item.symbol}
                            className="flex items-center justify-between p-4 bg-neutral-900/50 rounded-xl border border-white/5 hover:border-white/10 transition-all duration-200 group"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-neutral-800 rounded-lg flex items-center justify-center text-sm font-bold text-indigo-300 group-hover:bg-indigo-500/20 transition-colors">
                                    {item.symbol.charAt(0)}
                                </div>
                                <div>
                                    <div className="font-semibold text-sm">{item.symbol}</div>
                                    <div className="text-xs text-neutral-500">
                                        {item.symbol === 'SPY' && 'S&P 500 ETF'}
                                        {item.symbol === 'BND' && 'Total Bond Market'}
                                        {item.symbol === 'VTI' && 'Total Stock Market'}
                                    </div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold text-sm">${item.price.toFixed(2)}</div>
                                <div className={`flex items-center justify-end gap-1 text-xs ${item.trend === 'up' ? 'text-emerald-400' : 'text-rose-400'
                                    }`}>
                                    {item.trend === 'up' ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                                    <span>{item.change_pct ? `${item.change_pct > 0 ? '+' : ''}${item.change_pct}%` : item.trend}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Allocation Chart */}
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4">Allocation</h3>
                <div className="h-[120px]">
                    <Bar data={allocationData} options={allocationOptions} />
                </div>
            </div>
        </div>
    );
};

export default PortfolioPanel;
