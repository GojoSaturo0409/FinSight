import { Doughnut } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

interface ExpenseChartProps {
    transactions?: any[];
}

const COLORS = [
    'rgba(99, 102, 241, 0.8)',
    'rgba(244, 63, 94, 0.8)',
    'rgba(16, 185, 129, 0.8)',
    'rgba(245, 158, 11, 0.8)',
    'rgba(168, 85, 247, 0.8)',
    'rgba(6, 182, 212, 0.8)',
    'rgba(236, 72, 153, 0.8)',
    'rgba(14, 165, 233, 0.8)',
];

const ExpenseChart = ({ transactions = [] }: ExpenseChartProps) => {
    const categoryTotals: Record<string, number> = {};
    for (const tx of transactions) {
        if (tx.category === 'Income') continue;
        const cat = tx.category || 'Uncategorized';
        categoryTotals[cat] = (categoryTotals[cat] || 0) + tx.amount;
    }

    const labels = Object.keys(categoryTotals).length > 0
        ? Object.keys(categoryTotals)
        : ['Housing', 'Food', 'Transport', 'Subscriptions'];
    const values = Object.keys(categoryTotals).length > 0
        ? Object.values(categoryTotals)
        : [1500, 300, 150, 50];

    const data = {
        labels,
        datasets: [
            {
                data: values,
                backgroundColor: COLORS.slice(0, labels.length),
                borderWidth: 0,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        plugins: {
            legend: {
                position: 'right' as const,
                labels: {
                    color: 'rgba(255, 255, 255, 0.7)',
                    usePointStyle: true,
                    padding: 20,
                    font: { family: 'inherit' }
                }
            },
            tooltip: {
                callbacks: {
                    label: function (context: any) {
                        const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                        const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : '0';
                        return `$${context.raw.toLocaleString()} (${pct}%)`;
                    },
                },
            }
        }
    };

    const total = values.reduce((a, b) => a + b, 0);

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">Spending Breakdown</h3>
                <span className="text-sm text-neutral-400">${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
            <div className="h-[250px] flex items-center justify-center">
                <Doughnut data={data} options={options} />
            </div>
        </div>
    );
};
export default ExpenseChart;
