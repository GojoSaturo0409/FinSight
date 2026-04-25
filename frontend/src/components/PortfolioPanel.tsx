import { useState, useEffect, useCallback } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { apiFetch } from '../api';
import { useCurrency } from './CurrencyContext';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';
import { ArrowUpRight, ArrowDownRight, Search, RefreshCw, TrendingUp } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler);

interface PortfolioItem {
    symbol: string;
    name?: string;
    price: number;
    trend: 'up' | 'down';
    change_pct?: number;
    daily_prices?: Record<string, number>;
    stale?: boolean;
    shares?: number;
    average_price?: number;
    total_value?: number;
}

interface StockResult {
    symbol: string;
    name: string;
    price: number;
    trend: string;
    change_pct: number;
}

const PortfolioPanel = () => {
    const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
    const [allStocks, setAllStocks] = useState<StockResult[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedStock, setSelectedStock] = useState<PortfolioItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const { format } = useCurrency();

    const fetchPortfolio = useCallback(async () => {
        try {
            const data = await apiFetch('/investments/portfolio');
            setPortfolio(data.portfolio);
        } catch {
            setPortfolio([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    const fetchAllStocks = useCallback(async () => {
        try {
            const data = await apiFetch('/investments/all_stocks');
            setAllStocks(data.stocks || []);
        } catch {
            setAllStocks([]);
        }
    }, []);

    useEffect(() => {
        fetchPortfolio();
        fetchAllStocks();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchPortfolio, 30000);
        return () => clearInterval(interval);
    }, [fetchPortfolio, fetchAllStocks]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchPortfolio();
    };

    const handleStockClick = async (symbol: string) => {
        try {
            const data = await apiFetch(`/investments/quote/${symbol}`);
            setSelectedStock(data.quote);
        } catch {
            /* ignore */
        }
    };

    const filteredStocks = searchQuery.length > 0
        ? allStocks.filter(s =>
            s.symbol.includes(searchQuery.toUpperCase()) ||
            s.name.toLowerCase().includes(searchQuery.toLowerCase())
        )
        : [];

    const totalValue = portfolio.reduce((sum, item) => sum + item.price, 0);

    // Build chart for selected stock
    const buildLineChart = (stock: PortfolioItem) => {
        if (!stock.daily_prices) return null;
        const sortedDates = Object.keys(stock.daily_prices).sort();
        const prices = sortedDates.map(d => stock.daily_prices![d]);
        return {
            labels: sortedDates.map(d => d.slice(5)), // MM-DD
            datasets: [{
                label: stock.symbol,
                data: prices,
                borderColor: stock.trend === 'up' ? '#10b981' : '#f43f5e',
                backgroundColor: stock.trend === 'up'
                    ? 'rgba(16, 185, 129, 0.1)'
                    : 'rgba(244, 63, 94, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                borderWidth: 2,
            }],
        };
    };

    const lineOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (ctx: any) => `$${ctx.raw.toFixed(2)}`,
                },
            },
        },
        scales: {
            y: {
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: { color: 'rgba(255,255,255,0.4)', callback: (v: any) => `$${v}` },
            },
            x: {
                grid: { display: false },
                ticks: { color: 'rgba(255,255,255,0.4)', maxTicksLimit: 8 },
            },
        },
    };

    const barData = {
        labels: portfolio.map(p => p.symbol),
        datasets: [{
            label: 'Allocation',
            data: portfolio.map(p => ((p.price / (totalValue || 1)) * 100)),
            backgroundColor: [
                'rgba(99, 102, 241, 0.8)',
                'rgba(16, 185, 129, 0.8)',
                'rgba(245, 158, 11, 0.8)',
                'rgba(244, 63, 94, 0.8)',
                'rgba(168, 85, 247, 0.8)',
            ],
            borderRadius: 4,
        }],
    };

    const barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c: any) => `${c.raw.toFixed(1)}%` } } },
        scales: {
            y: { display: false },
            x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.5)' } },
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
            {/* Portfolio Summary */}
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <TrendingUp className="text-indigo-400" size={20} />
                        <h3 className="text-xl font-bold">Investment Portfolio</h3>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-1 rounded-md border ${portfolio.some(p => p.stale)
                            ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                            : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'}`}>
                            {portfolio.some(p => p.stale) ? 'Cached' : '● Live'}
                        </span>
                        <button onClick={handleRefresh} className="p-1.5 bg-neutral-800 rounded-lg hover:bg-neutral-700 transition-colors" title="Refresh">
                            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
                        </button>
                    </div>
                </div>

                <div className="text-center mb-4">
                    <div className="text-3xl font-bold text-white">{format(totalValue)}</div>
                    <div className="text-xs text-neutral-400">Total Portfolio Value</div>
                </div>

                <div className="h-[160px] mb-4">
                    <Bar data={barData} options={barOptions} />
                </div>

                <div className="space-y-2">
                    {portfolio.map((item) => (
                        <div key={item.symbol}
                            onClick={() => handleStockClick(item.symbol)}
                            className="flex items-center justify-between p-3 bg-neutral-800/50 rounded-xl border border-white/5 hover:bg-neutral-800 transition-colors cursor-pointer">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm border ${item.trend === 'up' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                                    {item.symbol.substring(0, 3)}
                                </div>
                                <div>
                                    <div className="font-bold text-sm">{item.symbol}</div>
                                    <div className="text-xs text-neutral-500">{item.name || 'ETF'}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold text-sm">{format(item.total_value || 0)}</div>
                                <div className="text-xs text-neutral-400 mb-1">
                                    {item.shares ? `${item.shares.toFixed(2)} shs @ ${format(item.price)}` : format(item.price)}
                                </div>
                                <div className={`text-xs flex items-center justify-end font-medium ${item.trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {item.trend === 'up' ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                                    <span>{item.change_pct ? `${item.change_pct > 0 ? '+' : ''}${item.change_pct}%` : item.trend}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Stock Detail Chart */}
            {selectedStock && selectedStock.daily_prices && Object.keys(selectedStock.daily_prices).length > 0 && (
                <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="font-bold">{selectedStock.symbol} — 30 Day Trend</h4>
                        <div className={`text-sm font-medium ${selectedStock.trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {format(selectedStock.price)} ({selectedStock.change_pct ? `${selectedStock.change_pct > 0 ? '+' : ''}${selectedStock.change_pct}%` : ''})
                        </div>
                    </div>

                    {/* Trade Box */}
                    <div className="flex items-center gap-4 mb-4 bg-neutral-800/30 p-4 rounded-xl border border-white/5">
                        <div className="flex-1">
                             <input 
                                type="number" 
                                min="0.1" 
                                step="0.1"
                                placeholder="Shares to trade" 
                                className="w-full bg-neutral-900 border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500/50"
                                id="trade-shares"
                             />
                        </div>
                        <button 
                            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                            onClick={async () => {
                                const input = document.getElementById('trade-shares') as HTMLInputElement;
                                const shares = parseFloat(input.value);
                                if (!shares || shares <= 0) return;
                                try {
                                    await apiFetch('/investments/buy', {
                                        method: 'POST',
                                        body: JSON.stringify({ symbol: selectedStock.symbol, shares })
                                    });
                                    input.value = '';
                                    handleRefresh();
                                    alert('Purchase successful');
                                } catch (e) {
                                    alert('Failed to buy');
                                }
                            }}
                        >
                            Buy
                        </button>
                        <button 
                            className="bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                            onClick={async () => {
                                const input = document.getElementById('trade-shares') as HTMLInputElement;
                                const shares = parseFloat(input.value);
                                if (!shares || shares <= 0) return;
                                try {
                                    await apiFetch('/investments/sell', {
                                        method: 'POST',
                                        body: JSON.stringify({ symbol: selectedStock.symbol, shares })
                                    });
                                    input.value = '';
                                    handleRefresh();
                                    alert('Sale successful');
                                } catch (e: any) {
                                    alert(e.message || 'Failed to sell');
                                }
                            }}
                        >
                            Sell
                        </button>
                    </div>

                    <div className="h-[200px]">
                        <Line data={buildLineChart(selectedStock)!} options={lineOptions} />
                    </div>
                </div>
            )}

            {/* Stock Search */}
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                <h4 className="font-bold mb-4 flex items-center gap-2"><Search size={16} /> Browse Stocks</h4>
                <div className="relative mb-4">
                    <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500" />
                    <input
                        type="text"
                        placeholder="Search by symbol (AAPL, TSLA, NVDA...)"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-neutral-800/50 border border-white/10 rounded-xl text-sm focus:outline-none focus:border-indigo-500/50 transition-colors"
                    />
                </div>
                {filteredStocks.length > 0 && (
                    <div className="space-y-2 max-h-[300px] overflow-y-auto">
                        {filteredStocks.map(stock => (
                            <div key={stock.symbol}
                                onClick={() => handleStockClick(stock.symbol)}
                                className="flex items-center justify-between p-3 bg-neutral-800/30 rounded-xl border border-white/5 hover:bg-neutral-700/50 transition-colors cursor-pointer">
                                <div>
                                    <span className="font-bold text-sm">{stock.symbol}</span>
                                    <span className="text-xs text-neutral-500 ml-2">{stock.name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="font-bold text-sm">${stock.price.toFixed(2)}</span>
                                    <span className={`text-xs ${stock.trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {stock.change_pct > 0 ? '+' : ''}{stock.change_pct}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                {searchQuery.length === 0 && (
                    <div className="grid grid-cols-2 gap-2">
                        {allStocks.slice(0, 6).map(stock => (
                            <div key={stock.symbol}
                                onClick={() => handleStockClick(stock.symbol)}
                                className="p-3 bg-neutral-800/30 rounded-xl border border-white/5 hover:bg-neutral-700/50 transition-colors cursor-pointer">
                                <div className="flex justify-between items-center">
                                    <span className="font-bold text-sm">{stock.symbol}</span>
                                    <span className={`text-xs ${stock.trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {stock.change_pct > 0 ? '+' : ''}{stock.change_pct}%
                                    </span>
                                </div>
                                <div className="text-xs text-neutral-500 mt-1">{stock.name}</div>
                                <div className="font-bold text-sm mt-1">${stock.price.toFixed(2)}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
export default PortfolioPanel;
