import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { apiFetch } from '../api';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface NetWorthProps {
    transactions?: any[];
}

const NetWorthChart = ({ transactions = [] }: NetWorthProps) => {
    const [chartData, setChartData] = useState<{ labels: string[]; values: number[] }>({
        labels: [],
        values: [],
    });

    useEffect(() => {
        if (transactions.length > 0) {
            const monthlyTotals: Record<string, number> = {};
            const monthOrder: string[] = [];

            for (const tx of transactions) {
                const dateStr = tx.date || '';
                const parts = dateStr.split('-');
                if (parts.length >= 2) {
                    const key = `${parts[0]}-${parts[1]}`; // e.g. "2024-03"
                    const amount = tx.category === 'Income' ? -tx.amount : tx.amount;
                    monthlyTotals[key] = (monthlyTotals[key] || 0) + amount;
                    if (!monthOrder.includes(key)) monthOrder.push(key);
                }
            }

            monthOrder.sort();

            const monthNames: Record<string, string> = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec',
            };

            const monthlyIncome = 5000;
            let cumulative = 0;
            const labels: string[] = [];
            const values: number[] = [];

            for (const key of monthOrder) {
                const monthSpend = monthlyTotals[key] || 0;
                cumulative += (monthlyIncome - monthSpend);
                labels.push(monthNames[key.split('-')[1]] || key);
                values.push(Math.round(cumulative * 100) / 100);
            }

            if (labels.length > 0) {
                setChartData({ labels, values });
                return;
            }
        }

        fetchNetWorth();
    }, [transactions]);

    const fetchNetWorth = async () => {
        try {
            const data = await apiFetch('/reports/generate-auto', { method: 'POST' });
            const trend = data.report?.net_worth_trend || [];
            if (trend.length > 0) {
                setChartData({
                    labels: trend.map((t: any) => t.month),
                    values: trend.map((t: any) => t.net_worth),
                });
                return;
            }
        } catch {
            // fallback
        }

        setChartData({
            labels: [],
            values: [],
        });
    };

    const currentValue = chartData.values.length > 0 ? chartData.values[chartData.values.length - 1] : 0;
    const firstValue = chartData.values.length > 1 ? chartData.values[0] : currentValue;
    const growthPct = firstValue > 0 ? (((currentValue - firstValue) / firstValue) * 100).toFixed(1) : '0';

    const data = {
        labels: chartData.labels,
        datasets: [
            {
                label: 'Net Worth',
                data: chartData.values,
                borderColor: 'rgba(99, 102, 241, 1)',
                backgroundColor: (context: any) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
                    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(99, 102, 241, 1)',
                pointRadius: 4,
                pointHoverRadius: 6,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(23, 23, 23, 0.9)',
                titleColor: '#fff',
                bodyColor: '#fff',
                padding: 12,
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1,
                callbacks: {
                    label: function (context: any) {
                        return `$${context.raw.toLocaleString()}`;
                    },
                },
            },
        },
        scales: {
            y: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                    drawBorder: false,
                },
                ticks: {
                    color: 'rgba(255, 255, 255, 0.5)',
                    callback: function (value: any) {
                        return '$' + value.toLocaleString();
                    },
                },
            },
            x: {
                grid: { display: false, drawBorder: false },
                ticks: { color: 'rgba(255, 255, 255, 0.5)' },
            },
        },
    };

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">Net Worth</h3>
                <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-indigo-400">
                        ${currentValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-md ${parseFloat(growthPct) >= 0
                        ? 'text-emerald-400 bg-emerald-500/10'
                        : 'text-rose-400 bg-rose-500/10'
                        }`}>
                        {parseFloat(growthPct) >= 0 ? '+' : ''}{growthPct}%
                    </span>
                </div>
            </div>
            <div className="h-[280px]">
                <Line data={data} options={options} />
            </div>
        </div>
    );
};
export default NetWorthChart;
