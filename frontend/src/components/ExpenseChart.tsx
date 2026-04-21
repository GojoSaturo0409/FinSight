import { Doughnut } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const ExpenseChart = () => {
    const data = {
        labels: ['Housing', 'Food', 'Transport', 'Subscriptions'],
        datasets: [
            {
                data: [1500, 300, 150, 50],
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)', // Indigo
                    'rgba(244, 63, 94, 0.8)',  // Rose
                    'rgba(16, 185, 129, 0.8)', // Emerald
                    'rgba(245, 158, 11, 0.8)', // Amber
                ],
                borderWidth: 0,
            },
        ],
    };

    const options = {
        responsive: true,
        cutout: '75%',
        plugins: {
            legend: {
                position: 'right' as const,
                labels: {
                    color: '#a3a3a3',
                    padding: 20,
                    font: { family: 'inherit' }
                }
            }
        }
    };

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <h3 className="text-xl font-bold mb-6">Spending Breakdown</h3>
            <div className="h-[250px] flex items-center justify-center">
                <Doughnut data={data} options={options} />
            </div>
        </div>
    );
};

export default ExpenseChart;
