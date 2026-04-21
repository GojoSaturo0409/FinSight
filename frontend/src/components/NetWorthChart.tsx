import { Line } from 'react-chartjs-2';
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

const NetWorthChart = () => {
    const labels = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'];
    const netWorthData = [9200, 9800, 10500, 10100, 11200, 12450];

    const data = {
        labels,
        datasets: [
            {
                label: 'Net Worth',
                data: netWorthData,
                borderColor: 'rgba(99, 102, 241, 1)',
                backgroundColor: (context: any) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.25)');
                    gradient.addColorStop(0.5, 'rgba(99, 102, 241, 0.08)');
                    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                pointBorderColor: '#0a0a0a',
                pointBorderWidth: 2,
                pointHoverRadius: 8,
                borderWidth: 2.5,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index' as const,
        },
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                backgroundColor: 'rgba(10, 10, 10, 0.95)',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                titleColor: '#e5e5e5',
                bodyColor: '#a3a3a3',
                padding: 12,
                cornerRadius: 10,
                displayColors: false,
                callbacks: {
                    label: function (context: any) {
                        return `$${context.parsed.y.toLocaleString()}`;
                    },
                },
            },
        },
        scales: {
            x: {
                grid: { display: false },
                border: { color: 'rgba(255,255,255,0.05)' },
                ticks: { color: '#737373', font: { size: 12 } },
            },
            y: {
                grid: { color: 'rgba(255,255,255,0.03)' },
                border: { display: false },
                ticks: {
                    color: '#737373',
                    font: { size: 11 },
                    callback: function (value: any) {
                        return '$' + value.toLocaleString();
                    },
                },
            },
        },
    };

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">Net Worth</h3>
                <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-indigo-400">$12,450</span>
                    <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md">+35.3%</span>
                </div>
            </div>
            <div className="h-[280px]">
                <Line data={data} options={options} />
            </div>
        </div>
    );
};

export default NetWorthChart;
